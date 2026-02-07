"""Tests for codebase.py - Cypilot code traceability marker parsing."""
import pytest
from pathlib import Path
from textwrap import dedent

from cypilot.utils.codebase import (
    CodeFile,
    ScopeMarker,
    BlockMarker,
    CodeReference,
    load_code_file,
    validate_code_file,
    cross_validate_code,
)


class TestScopeMarkerParsing:
    """Test parsing of scope markers like @cpt-flow:{id}:p{N}."""

    def test_parse_flow_marker(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login_flow(request):
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs
        assert cf is not None
        assert len(cf.scope_markers) == 1
        assert cf.scope_markers[0].kind == "flow"
        assert cf.scope_markers[0].id == "cpt-myapp-spec-auth-flow-login"
        assert cf.scope_markers[0].phase == 1

    def test_parse_algo_marker(self, tmp_path: Path):
        code = dedent("""
            // @cpt-algo:cpt-myapp-spec-search-algo-rank:p2
            function rankResults(items) {
                return items;
            }
        """)
        code_file = tmp_path / "search.ts"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs
        assert len(cf.scope_markers) == 1
        assert cf.scope_markers[0].kind == "algo"
        assert cf.scope_markers[0].id == "cpt-myapp-spec-search-algo-rank"
        assert cf.scope_markers[0].phase == 2

    def test_parse_multiple_markers(self, tmp_path: Path):
        code = dedent("""
            # @cpt-req:cpt-myapp-spec-auth-req-validate:p1
            def validate_input(data):
                pass

            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login(request):
                pass

            # @cpt-test:cpt-myapp-spec-auth-test-login:p3
            def test_login():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs
        assert len(cf.scope_markers) == 3
        kinds = [m.kind for m in cf.scope_markers]
        assert "req" in kinds
        assert "flow" in kinds
        assert "test" in kinds


class TestBlockMarkerParsing:
    """Test parsing of block markers @cpt-begin/end."""

    def test_parse_block_marker(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate-creds
            def validate_credentials(username, password):
                if not username or not password:
                    raise ValidationError("Missing credentials")
                return authenticate(username, password)
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate-creds
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs
        assert len(cf.block_markers) == 1
        assert cf.block_markers[0].id == "cpt-myapp-spec-auth-flow-login"
        assert cf.block_markers[0].phase == 1
        assert cf.block_markers[0].inst == "validate-creds"
        assert len(cf.block_markers[0].content) > 0

    def test_block_markers_not_parsed_as_scope_markers(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate
            def validate():
                return True
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs
        assert cf is not None
        assert len(cf.scope_markers) == 0
        assert len(cf.block_markers) == 1

    def test_unclosed_block_error(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate
            def validate():
                pass
            # missing @cpt-end
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert len(errs) == 1
        assert "without matching @cpt-end" in errs[0]["message"]

    def test_orphan_end_error(self, tmp_path: Path):
        code = dedent("""
            def validate():
                pass
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert len(errs) == 1
        assert "without matching @cpt-begin" in errs[0]["message"]

    def test_empty_block_error(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert len(errs) == 1
        assert "Empty block" in errs[0]["message"]


class TestCodeFileInterface:
    """Test CodeFile interface methods (similar to Artifact)."""

    def test_list_ids(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login():
                pass

            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate
            def validate():
                pass
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        ids = cf.list_ids()
        assert "cpt-myapp-spec-auth-flow-login" in ids

    def test_list_refs_same_as_list_ids(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        assert cf.list_ids() == cf.list_refs()

    def test_list_defined_empty(self, tmp_path: Path):
        """Code files don't define IDs, only reference them."""
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        assert cf.list_defined() == []

    def test_get_content(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate
            def validate():
                return True
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        content = cf.get("cpt-myapp-spec-auth-flow-login")
        assert content is not None
        assert "def validate" in content

    def test_get_by_inst(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-validate
            def validate():
                return True
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-validate

            # @cpt-begin:cpt-myapp-spec-auth-flow-login:p1:inst-authenticate
            def authenticate():
                return True
            # @cpt-end:cpt-myapp-spec-auth-flow-login:p1:inst-authenticate
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        content = cf.get_by_inst("validate")
        assert content is not None
        assert "def validate" in content

        content2 = cf.get_by_inst("authenticate")
        assert content2 is not None
        assert "def authenticate" in content2


class TestCrossValidation:
    """Test cross-validation between code and artifacts."""

    def test_orphaned_marker_error(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-unknown-flow-missing:p1
            def unknown():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        artifact_ids = {"cpt-myapp-spec-auth-flow-login"}  # different ID
        to_code_ids = set()

        result = cross_validate_code([cf], artifact_ids, to_code_ids, "FULL")
        assert len(result["errors"]) == 1
        assert "not defined in any artifact" in result["errors"][0]["message"]

    def test_missing_coverage_error(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        artifact_ids = {"cpt-myapp-spec-auth-flow-login", "cpt-myapp-spec-auth-flow-logout"}
        to_code_ids = {"cpt-myapp-spec-auth-flow-login", "cpt-myapp-spec-auth-flow-logout"}

        result = cross_validate_code([cf], artifact_ids, to_code_ids, "FULL")
        # Should have error for missing logout marker
        coverage_errors = [e for e in result["errors"] if e["type"] == "coverage"]
        assert len(coverage_errors) == 1
        assert "cpt-myapp-spec-auth-flow-logout" in coverage_errors[0]["id"]

    def test_docs_only_prohibits_markers(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        result = cross_validate_code([cf], set(), set(), "DOCS-ONLY")
        assert len(result["errors"]) == 1
        assert "DOCS-ONLY" in result["errors"][0]["message"]

    def test_full_traceability_pass(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-spec-auth-flow-login:p1
            def login():
                pass
        """)
        code_file = tmp_path / "auth.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        artifact_ids = {"cpt-myapp-spec-auth-flow-login"}
        to_code_ids = {"cpt-myapp-spec-auth-flow-login"}

        result = cross_validate_code([cf], artifact_ids, to_code_ids, "FULL")
        assert len(result["errors"]) == 0


class TestLoadCodeFile:
    """Test load_code_file wrapper function."""

    def test_load_existing_file(self, tmp_path: Path):
        code = "# @cpt-flow:cpt-myapp-flow-test:p1\ndef foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, errs = load_code_file(code_file)
        assert cf is not None
        assert not errs
        assert len(cf.scope_markers) == 1

    def test_load_nonexistent_file(self, tmp_path: Path):
        cf, errs = load_code_file(tmp_path / "nonexistent.py")
        assert cf is None
        assert len(errs) == 1
        assert errs[0]["type"] == "file"


class TestValidateCodeFile:
    """Test validate_code_file wrapper function."""

    def test_validate_valid_file(self, tmp_path: Path):
        code = "# @cpt-flow:cpt-myapp-flow-test:p1\ndef foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        result = validate_code_file(code_file)
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_file_with_errors(self, tmp_path: Path):
        code = "# @cpt-begin:cpt-myapp-flow-test:p1:inst-foo\n# missing end\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        result = validate_code_file(code_file)
        assert len(result["errors"]) == 1
        assert "without matching @cpt-end" in result["errors"][0]["message"]

    def test_validate_nonexistent_file(self, tmp_path: Path):
        result = validate_code_file(tmp_path / "nonexistent.py")
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "file"


class TestCodeFileList:
    """Test CodeFile.list() method."""

    def test_list_multiple_ids(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-flow-a:p1:inst-a
            def a(): pass
            # @cpt-end:cpt-myapp-flow-a:p1:inst-a

            # @cpt-begin:cpt-myapp-flow-b:p1:inst-b
            def b(): pass
            # @cpt-end:cpt-myapp-flow-b:p1:inst-b
        """)
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        results = cf.list(["cpt-myapp-flow-a", "cpt-myapp-flow-b", "cpt-myapp-flow-c"])

        assert len(results) == 3
        assert "def a" in results[0]
        assert "def b" in results[1]
        assert results[2] is None  # Non-existent ID


class TestCodeFileGetScopeMarker:
    """Test getting content from scope markers (not just blocks)."""

    def test_get_scope_marker_content(self, tmp_path: Path):
        code = "# @cpt-flow:cpt-myapp-flow-test:p1\ndef foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        content = cf.get("cpt-myapp-flow-test")
        # For scope markers, returns the raw line
        assert content is not None
        assert "@cpt-flow" in content

    def test_get_nonexistent_id(self, tmp_path: Path):
        code = "def foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        content = cf.get("cpt-myapp-nonexistent")
        assert content is None

    def test_get_by_inst_nonexistent(self, tmp_path: Path):
        code = "def foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        content = cf.get_by_inst("nonexistent")
        assert content is None


class TestDuplicateMarkerWarnings:
    """Test duplicate marker detection."""

    def test_duplicate_scope_marker_warning(self, tmp_path: Path):
        code = dedent("""
            # @cpt-flow:cpt-myapp-flow-test:p1
            def foo(): pass

            # @cpt-flow:cpt-myapp-flow-test:p1
            def bar(): pass
        """)
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, _ = CodeFile.from_path(code_file)
        result = cf.validate()

        # Duplicate scope markers should produce an error
        assert len(result["errors"]) == 1
        assert "Duplicate scope marker" in result["errors"][0]["message"]

    def test_duplicate_begin_without_end(self, tmp_path: Path):
        code = dedent("""
            # @cpt-begin:cpt-myapp-flow-test:p1:inst-foo
            def foo(): pass
            # @cpt-begin:cpt-myapp-flow-test:p1:inst-foo
            def bar(): pass
            # @cpt-end:cpt-myapp-flow-test:p1:inst-foo
        """)
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        # Should have error about duplicate @cpt-begin
        assert any("Duplicate @cpt-begin" in e["message"] for e in errs)


class TestStateMarker:
    """Test state marker kind parsing."""

    def test_parse_state_marker(self, tmp_path: Path):
        code = "# @cpt-state:cpt-myapp-state-auth:p1\nauth_state = {}\n"
        code_file = tmp_path / "state.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs
        assert len(cf.scope_markers) == 1
        assert cf.scope_markers[0].kind == "state"


class TestCodeFileLoad:
    """Test CodeFile.load() method edge cases."""

    def test_already_loaded(self, tmp_path: Path):
        code = "# @cpt-flow:cpt-myapp-flow-test:p1\ndef foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        cf, errs = CodeFile.from_path(code_file)
        assert not errs

        # Call load again - should return empty errors (already loaded)
        errs2 = cf.load()
        assert errs2 == []


class TestCrossValidationEdgeCases:
    """Test edge cases in cross-validation."""

    def test_docs_only_with_no_markers(self, tmp_path: Path):
        code = "def foo(): pass\n"
        code_file = tmp_path / "test.py"
        code_file.write_text(code)

        code_obj, _ = CodeFile.from_path(code_file)
        result = cross_validate_code([code_obj], set(), set(), "DOCS-ONLY")
        # No markers in DOCS-ONLY mode should be fine
        assert len(result["errors"]) == 0

    def test_empty_code_files_list(self):
        result = cross_validate_code([], {"cpt-myapp-id"}, {"cpt-myapp-id"}, "FULL")
        # No code files - missing coverage errors for to_code IDs
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "coverage"

    def test_multiple_code_files(self, tmp_path: Path):
        code1 = "# @cpt-flow:cpt-myapp-flow-a:p1\ndef a(): pass\n"
        code2 = "# @cpt-flow:cpt-myapp-flow-b:p1\ndef b(): pass\n"

        (tmp_path / "a.py").write_text(code1)
        (tmp_path / "b.py").write_text(code2)

        cf1, _ = CodeFile.from_path(tmp_path / "a.py")
        cf2, _ = CodeFile.from_path(tmp_path / "b.py")

        artifact_ids = {"cpt-myapp-flow-a", "cpt-myapp-flow-b"}
        to_code_ids = {"cpt-myapp-flow-a", "cpt-myapp-flow-b"}

        result = cross_validate_code([cf1, cf2], artifact_ids, to_code_ids, "FULL")
        assert len(result["errors"]) == 0


class TestErrorFunction:
    """Test the error helper function."""

    def test_error_with_extra_fields(self, tmp_path: Path):
        from cypilot.utils.codebase import error

        err = error("test", "Test message", path=tmp_path / "test.py", line=10, custom="value")

        assert err["type"] == "test"
        assert err["message"] == "Test message"
        assert err["line"] == 10
        assert err["custom"] == "value"

    def test_error_none_extra_fields_ignored(self, tmp_path: Path):
        from cypilot.utils.codebase import error

        err = error("test", "Message", path=tmp_path, line=1, skip_none=None)

        assert "skip_none" not in err
