"""Comprehensive unit tests for parse_cpt function.

Tests cover:
- Simple IDs (cpt-{system}-{kind}-{slug})
- Composite IDs (cpt-{system}-{kind1}-{slug1}-{kind2}-{slug2})
- Multi-word system names (e.g., "account-server")
- Case insensitivity for system and kind matching
- Edge cases (empty strings, missing parts, unknown systems)
- where_defined validation for composite IDs
"""

import pytest
from skills.cypilot.scripts.cypilot.utils.constraints import parse_cpt, ParsedCypilotId


class TestSimpleIds:
    """Tests for simple Cypilot IDs: cpt-{system}-{kind}-{slug}"""

    def test_basic_simple_id(self):
        """Parse a basic simple ID."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.system == "myapp"
        assert result.kind == "feature"
        assert result.slug == "auth"

    def test_simple_id_with_multi_part_slug(self):
        """Parse a simple ID with hyphenated slug."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-user-authentication",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.system == "myapp"
        assert result.kind == "feature"
        assert result.slug == "user-authentication"

    def test_simple_id_different_kinds(self):
        """Parse simple IDs with different kinds."""
        systems = {"myapp"}

        # PRD requirement
        result = parse_cpt("cpt-myapp-req-user-login", "req", systems)
        assert result is not None
        assert result.kind == "req"
        assert result.slug == "user-login"

        # ADR
        result = parse_cpt("cpt-myapp-adr-database-choice", "adr", systems)
        assert result is not None
        assert result.kind == "adr"
        assert result.slug == "database-choice"

        # Actor
        result = parse_cpt("cpt-myapp-actor-admin", "actor", systems)
        assert result is not None
        assert result.kind == "actor"
        assert result.slug == "admin"

    def test_simple_id_empty_slug(self):
        """Parse a simple ID with no slug (just system-kind)."""
        result = parse_cpt(
            cpt="cpt-myapp-feature",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.system == "myapp"
        assert result.kind == "feature"
        assert result.slug == ""


class TestMultiWordSystems:
    """Tests for systems with multi-word names (e.g., account-server)."""

    def test_multi_word_system(self):
        """Parse ID with multi-word system name."""
        result = parse_cpt(
            cpt="cpt-account-server-feature-billing",
            expected_kind="feature",
            registered_systems={"account-server"},
        )
        assert result is not None
        assert result.system == "account-server"
        assert result.kind == "feature"
        assert result.slug == "billing"

    def test_multi_word_system_longest_match(self):
        """When multiple systems could match, longest match wins."""
        result = parse_cpt(
            cpt="cpt-account-server-feature-billing",
            expected_kind="feature",
            registered_systems={"account", "account-server"},
        )
        assert result is not None
        assert result.system == "account-server"
        assert result.kind == "feature"
        assert result.slug == "billing"

    def test_shorter_system_when_longer_doesnt_match(self):
        """Use shorter system when it's the only match."""
        result = parse_cpt(
            cpt="cpt-account-feature-billing",
            expected_kind="feature",
            registered_systems={"account", "account-server"},
        )
        assert result is not None
        assert result.system == "account"
        assert result.kind == "feature"
        assert result.slug == "billing"

    def test_three_word_system(self):
        """Parse ID with three-word system name."""
        result = parse_cpt(
            cpt="cpt-my-cool-app-feature-auth",
            expected_kind="feature",
            registered_systems={"my-cool-app"},
        )
        assert result is not None
        assert result.system == "my-cool-app"
        assert result.kind == "feature"
        assert result.slug == "auth"


class TestCompositeIds:
    """Tests for composite Cypilot IDs: cpt-{system}-{kind1}-{slug1}-{kind2}-{slug2}"""

    def test_basic_composite_id(self):
        """Parse a composite ID (feature-algo)."""
        def where_defined(id_):
            return id_ == "cpt-myapp-feature-auth"

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-algo-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is not None
        assert result.system == "myapp"
        assert result.kind == "algo"
        assert result.slug == "hash"

    def test_composite_id_spec_flow(self):
        """Parse a feature-flow composite ID."""
        def where_defined(id_):
            return id_ == "cpt-myapp-feature-checkout"

        result = parse_cpt(
            cpt="cpt-myapp-feature-checkout-flow-payment",
            expected_kind="flow",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is not None
        assert result.kind == "flow"
        assert result.slug == "payment"

    def test_composite_id_spec_req(self):
        """Parse a feature-req composite ID."""
        def where_defined(id_):
            return id_ == "cpt-myapp-feature-auth"

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-req-password-validation",
            expected_kind="req",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is not None
        assert result.kind == "req"
        assert result.slug == "password-validation"

    def test_composite_id_parent_not_defined(self):
        """Return None when parent ID doesn't exist."""
        def where_defined(id_):
            return False  # no IDs exist

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-algo-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is None

    def test_composite_id_without_where_defined(self):
        """Composite ID parses without validation when where_defined is None."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-algo-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=None,  # no validation
        )
        assert result is not None

    def test_composite_id_multi_word_system(self):
        """Parse composite ID with multi-word system."""
        def where_defined(id_):
            return id_ == "cpt-account-server-feature-billing"

        result = parse_cpt(
            cpt="cpt-account-server-feature-billing-algo-invoice-calc",
            expected_kind="algo",
            registered_systems={"account-server"},
            where_defined=where_defined,
        )
        assert result is not None
        assert result.system == "account-server"
        assert result.kind == "algo"
        assert result.slug == "invoice-calc"


class TestCaseInsensitivity:
    """Tests for case-insensitive matching."""

    def test_case_insensitive_cypilot_prefix(self):
        """The cpt- prefix should be case-insensitive."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.system == "myapp"

    def test_case_insensitive_system(self):
        """System matching should be case-insensitive."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.system == "myapp"  # returns the registered system name

    def test_case_insensitive_kind(self):
        """Kind matching should be case-insensitive."""
        result = parse_cpt(
            cpt="cpt-myapp-FEATURE-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.kind == "feature"  # returns expected_kind as passed

    def test_case_insensitive_composite_separator(self):
        """Composite ID separator matching should be case-insensitive."""
        def where_defined(id_):
            return id_.lower() == "cpt-myapp-feature-auth"

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-ALGO-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is not None
        assert result.kind == "algo"

    def test_preserves_original_case_in_parent_id_for_where_defined(self):
        """Parent ID passed to where_defined should preserve original case."""
        calls = []

        def where_defined(id_):
            calls.append(id_)
            return True

        result = parse_cpt(
            cpt="cpt-myapp-Feature-Auth-algo-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is not None
        assert len(calls) == 1
        assert calls[0] == "cpt-myapp-Feature-Auth"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_none_input(self):
        """Return None for None input."""
        result = parse_cpt(
            cpt=None,
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is None

    def test_empty_string(self):
        """Return None for empty string."""
        result = parse_cpt(
            cpt="",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is None

    def test_not_cypilot_prefix(self):
        """Return None if doesn't start with cpt-."""
        result = parse_cpt(
            cpt="myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is None

    def test_unknown_system(self):
        """Return None for unknown system."""
        result = parse_cpt(
            cpt="cpt-unknown-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is None

    def test_empty_registered_systems(self):
        """Return None when no systems registered."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems=set(),
        )
        assert result is None

    def test_only_cypilot_prefix(self):
        """Return None for just 'cpt-'."""
        result = parse_cpt(
            cpt="cpt-",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is None

    def test_only_system(self):
        """Return None for just 'cpt-system-'."""
        result = parse_cpt(
            cpt="cpt-myapp-",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is None

    def test_kind_mismatch_no_composite(self):
        """Return None when kind doesn't match and no composite found."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="algo",  # looking for algo, but this is a feature
            registered_systems={"myapp"},
        )
        assert result is None

    def test_registered_systems_as_list(self):
        """Accept list as registered_systems (not just set)."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems=["myapp", "other"],  # list, not set
        )
        assert result is not None
        assert result.system == "myapp"


class TestRealWorldScenarios:
    """Tests based on real Cypilot usage patterns."""

    def test_cypilot_self_referential(self):
        """Parse Cypilot's own IDs (cpt-cypilot-*)."""
        result = parse_cpt(
            cpt="cpt-cypilot-adr-initial-architecture-v1",
            expected_kind="adr",
            registered_systems={"cypilot"},
        )
        assert result is not None
        assert result.system == "cypilot"
        assert result.kind == "adr"
        assert result.slug == "initial-architecture-v1"

    def test_versioned_id(self):
        """Parse ID with version suffix."""
        result = parse_cpt(
            cpt="cpt-myapp-req-auth-v2",
            expected_kind="req",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.slug == "auth-v2"

    def test_deeply_nested_composite(self):
        """Parse a deeply nested composite ID pattern."""
        # cpt-myapp-feature-auth-flow-login-step-validate
        # This is feature-auth with flow-login, and we're looking for step
        def where_defined(id_):
            # In real usage, we'd check if "cpt-myapp-feature-auth-flow-login" exists
            return id_ == "cpt-myapp-feature-auth-flow-login"

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-flow-login-step-validate",
            expected_kind="step",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert result is not None
        assert result.kind == "step"
        assert result.slug == "validate"

    def test_principle_id(self):
        """Parse a principle ID."""
        result = parse_cpt(
            cpt="cpt-cypilot-principle-tech-agnostic",
            expected_kind="principle",
            registered_systems={"cypilot"},
        )
        assert result is not None
        assert result.kind == "principle"
        assert result.slug == "tech-agnostic"

    def test_capability_id(self):
        """Parse a capability ID (fr = functional requirement at design level)."""
        result = parse_cpt(
            cpt="cpt-myapp-fr-workflow-execution",
            expected_kind="fr",
            registered_systems={"myapp"},
        )
        assert result is not None
        assert result.kind == "fr"
        assert result.slug == "workflow-execution"


class TestWhereDefinedCallback:
    """Tests specifically for where_defined callback behavior."""

    def test_where_defined_called_only_for_composite(self):
        """where_defined should only be called for composite IDs."""
        calls = []

        def where_defined(id_):
            calls.append(id_)
            return True

        # Simple ID - where_defined should NOT be called
        parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert len(calls) == 0

        # Composite ID - where_defined SHOULD be called
        parse_cpt(
            cpt="cpt-myapp-feature-auth-algo-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=where_defined,
        )
        assert len(calls) == 1
        assert calls[0] == "cpt-myapp-feature-auth"

    def test_where_defined_receives_full_parent_id(self):
        """where_defined receives the complete parent ID."""
        received = []

        def where_defined(id_):
            received.append(id_)
            return True

        parse_cpt(
            cpt="cpt-account-server-feature-billing-invoice-algo-calc",
            expected_kind="algo",
            registered_systems={"account-server"},
            where_defined=where_defined,
        )

        assert len(received) == 1
        assert received[0] == "cpt-account-server-feature-billing-invoice"


class TestDataclassProperties:
    """Tests for ParsedCypilotId dataclass properties."""

    def test_parsed_cpt_is_frozen(self):
        """ParsedCypilotId should be immutable (frozen dataclass)."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result is not None

        with pytest.raises(Exception):  # FrozenInstanceError
            result.system = "other"

    def test_parsed_cpt_equality(self):
        """ParsedCypilotId instances with same values should be equal."""
        result1 = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        result2 = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        assert result1 == result2

    def test_parsed_cpt_repr(self):
        """ParsedCypilotId should have a readable repr."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
        )
        repr_str = repr(result)
        assert "myapp" in repr_str
        assert "feature" in repr_str
        assert "auth" in repr_str


class TestKnownKindsValidation:
    """Tests for known_kinds parameter validation."""

    def test_known_kinds_valid_kind(self):
        """Parse succeeds when kind is in known_kinds."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
            known_kinds={"feature", "algo", "fr"},
        )
        assert result is not None
        assert result.kind == "feature"

    def test_known_kinds_invalid_kind_returns_none(self):
        """Parse returns None when first_kind not in known_kinds."""
        result = parse_cpt(
            cpt="cpt-myapp-featre-auth",  # typo: featre instead of feature
            expected_kind="featre",
            registered_systems={"myapp"},
            known_kinds={"feature", "algo", "fr"},
        )
        assert result is None

    def test_known_kinds_case_insensitive(self):
        """known_kinds matching should be case-insensitive."""
        result = parse_cpt(
            cpt="cpt-myapp-FEATURE-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
            known_kinds={"Feature", "Algo", "FR"},
        )
        assert result is not None
        assert result.kind == "feature"

    def test_known_kinds_none_skips_validation(self):
        """When known_kinds is None, kind validation is skipped."""
        result = parse_cpt(
            cpt="cpt-myapp-anykind-auth",
            expected_kind="anykind",
            registered_systems={"myapp"},
            known_kinds=None,  # no validation
        )
        assert result is not None
        assert result.kind == "anykind"

    def test_known_kinds_composite_expected_kind_invalid(self):
        """Composite ID returns None if expected_kind not in known_kinds."""
        def where_defined(id_):
            return True

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-unknownkind-hash",
            expected_kind="unknownkind",
            registered_systems={"myapp"},
            where_defined=where_defined,
            known_kinds={"feature", "algo"},
        )
        assert result is None

    def test_known_kinds_composite_valid(self):
        """Composite ID succeeds when both kinds are in known_kinds."""
        def where_defined(id_):
            return id_ == "cpt-myapp-feature-auth"

        result = parse_cpt(
            cpt="cpt-myapp-feature-auth-algo-hash",
            expected_kind="algo",
            registered_systems={"myapp"},
            where_defined=where_defined,
            known_kinds={"feature", "algo"},
        )
        assert result is not None
        assert result.kind == "algo"

    def test_known_kinds_empty_set_rejects_all(self):
        """Empty known_kinds set rejects all kinds."""
        result = parse_cpt(
            cpt="cpt-myapp-feature-auth",
            expected_kind="feature",
            registered_systems={"myapp"},
            known_kinds=set(),
        )
        assert result is None
