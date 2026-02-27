from pathlib import Path
import json

from skills.cypilot.scripts.cypilot.utils import error_codes as EC
from skills.cypilot.scripts.cypilot.utils.constraints import (
    ArtifactRecord,
    ArtifactKindConstraints,
    HeadingConstraint,
    cross_validate_artifacts,
    heading_constraint_ids_by_line,
    load_constraints_json,
    parse_kit_constraints,
    validate_artifact_file,
    validate_headings_contract,
)


def test_parse_kit_constraints_none_ok():
    kc, errs = parse_kit_constraints(None)
    assert kc is None
    assert errs == []


def test_parse_kit_constraints_root_must_be_object():
    kc, errs = parse_kit_constraints([1, 2, 3])
    assert kc is None
    assert errs


def test_parse_kit_constraints_rejects_non_string_kind_key():
    kc, errs = parse_kit_constraints({1: {"identifiers": {}}})
    assert kc is None
    assert any("non-string kind" in e for e in errs)


def test_parse_kit_constraints_requires_sections():
    kc, errs = parse_kit_constraints({"PRD": {}})
    assert kc is None
    assert any("must include" in e for e in errs)


def test_parse_kit_constraints_valid_happy_path_and_normalizations():
    data = {
        "prd": {
            "name": "PRD",
            "description": "desc",
            "identifiers": {
                "item": {
                    "name": "Item",
                    "description": "An item",
                    "examples": ["cpt-test-item-1"],
                    "task": True,
                    "priority": False,
                    "to_code": True,
                    "headings": ["  H1 ", "", "H2"],
                    "references": {
                        "DESIGN": {"coverage": True},
                        "SPEC": {"coverage": True},
                    },
                }
            },
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert errs == []
    assert kc is not None
    assert "PRD" in kc.by_kind

    prd = kc.by_kind["PRD"]
    assert prd.name == "PRD"
    assert prd.description == "desc"

    d0 = prd.defined_id[0]
    assert d0.kind == "item"
    assert d0.name == "Item"
    assert d0.description == "An item"
    assert d0.examples == ["cpt-test-item-1"]
    assert d0.task is True
    assert d0.priority is False
    assert d0.to_code is True
    assert d0.headings == ["H1", "H2"]
    assert d0.references is not None
    assert set(d0.references.keys()) == {"DESIGN", "SPEC"}
    assert d0.references["DESIGN"].coverage is True


def test_parse_kit_constraints_duplicate_kind_detection():
    data = {
        "PRD": {
            "identifiers": {
                "item": {"kind": "item"},
                "item ": {"kind": "item"},
            },
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert kc is None
    assert any("identifiers has duplicate kind" in e for e in errs)


def test_parse_kit_constraints_reports_field_type_errors():
    data = {
        "PRD": {
            "name": 123,
            "identifiers": {},
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert kc is None
    assert any("field 'name'" in e for e in errs)


def test_parse_kit_constraints_entry_must_be_object_and_kind_required():
    data1 = {"PRD": {"identifiers": {"item": "x"}}}
    kc, errs = parse_kit_constraints(data1)
    assert kc is None
    assert any("Constraint entry must be an object" in e for e in errs)

    data2 = {"PRD": {"identifiers": {"": {}}}}
    kc2, errs2 = parse_kit_constraints(data2)
    assert kc2 is None
    assert any("non-string kind key" in e for e in errs2)


def test_parse_kit_constraints_entry_type_validation():
    data = {
        "PRD": {
            "identifiers": {
                "item": {"task": "yes"},
                "item2": {"priority": "no"},
                "item3": {"to_code": "nope"},
                "item4": {"headings": "H"},
            },
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert kc is None
    assert any("field 'task'" in e for e in errs)
    assert any("field 'priority'" in e for e in errs)
    assert any("field 'to_code'" in e for e in errs)
    assert any("field 'headings'" in e for e in errs)


def test_parse_kit_constraints_tri_state_requires_string_or_bool():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"task": 123},
            },
        }
    })
    assert kc is None
    assert any("field 'task'" in e and "must be boolean" in e for e in errs)


def test_heading_constraint_ids_by_line_read_failure_returns_empty(tmp_path: Path):
    from unittest.mock import patch

    p = tmp_path / "x.md"
    p.write_text("# X\n", encoding="utf-8")

    with patch("skills.cypilot.scripts.cypilot.utils.document.read_text_safe", return_value=None):
        got = heading_constraint_ids_by_line(p, [])
    assert got == [[]]


def test_heading_constraint_ids_by_line_invalid_regex_never_matches(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text("## Hello\n\nText\n", encoding="utf-8")

    # Pattern contains regex metacharacters, but is invalid and triggers re.error.
    hc = HeadingConstraint(level=2, id="h2-hello", pattern="[")
    got = heading_constraint_ids_by_line(p, [hc])
    # Line 1 is a heading, but it must not match due to invalid regex.
    assert got[1] == []


def test_validate_headings_contract_detects_non_consecutive_numbering(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text(
        """
# T

## 3.1 A

## 3.2 B

## 3.3 C

## 3.4 D

## 3.5 E

## 3.6 F

## 3.8 H
""".lstrip(),
        encoding="utf-8",
    )

    constraints = ArtifactKindConstraints(
        name=None,
        description=None,
        defined_id=[],
        headings=[HeadingConstraint(level=2, pattern=None, required=True, multiple="allow", numbered="allow", id="h2")],
    )

    rep = validate_headings_contract(
        path=p,
        constraints=constraints,
        registered_systems=None,
        artifact_kind="DESIGN",
    )

    errs = rep.get("errors", [])
    assert any(
        ("not consecutive" in str(e.get("message", ""))) and (str(e.get("expected_prefix")) == "3.7")
        for e in errs
    )


def test_parse_id_constraint_examples_must_be_list():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"examples": "not-a-list"},
            },
        }
    })
    assert kc is None
    assert any("examples" in e and "must be a list" in e for e in errs)


def test_parse_id_constraint_name_and_description_must_be_string():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"name": 123},
            },
        }
    })
    assert kc is None
    assert any("field 'name'" in e for e in errs)

    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"description": 123},
            },
        }
    })
    assert kc2 is None
    assert any("field 'description'" in e for e in errs2)


def test_parse_references_must_be_object_and_keys_strings():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": "bad"},
            },
        }
    })
    assert kc is None
    assert any("references" in e and "must be an object" in e for e in errs)

    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {1: {"coverage": True}}},
            },
        }
    })
    assert kc2 is None
    assert any("non-string artifact kind key" in e for e in errs2)


def test_parse_reference_rule_validation_errors():
    # rule must be an object
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": "bad"}},
            },
        }
    })
    assert kc is None
    assert any("Reference rule must be an object" in e for e in errs)

    # invalid coverage (string not accepted)
    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {"coverage": "bad"}}},
            },
        }
    })
    assert kc2 is None
    assert any("coverage" in e and "must be boolean" in e for e in errs2)

    # boolean coverage: true → True (required), false → False (prohibited)
    kc_bool, errs_bool = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {"coverage": True}}},
            },
        }
    })
    assert errs_bool == []
    assert kc_bool.by_kind["PRD"].defined_id[0].references["DESIGN"].coverage is True

    kc_bool2, errs_bool2 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {"coverage": False}}},
            },
        }
    })
    assert errs_bool2 == []
    assert kc_bool2.by_kind["PRD"].defined_id[0].references["DESIGN"].coverage is False

    # omitted coverage → None (optional)
    kc_omit, errs_omit = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {}}},
            },
        }
    })
    assert errs_omit == []
    assert kc_omit.by_kind["PRD"].defined_id[0].references["DESIGN"].coverage is None

    # task must be boolean
    kc3, errs3 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {"coverage": True, "task": "x"}}},
            },
        }
    })
    assert kc3 is None
    assert any("references.task" in e and "must be boolean" in e for e in errs3)

    # priority must be boolean
    kc4, errs4 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {"coverage": True, "priority": "x"}}},
            },
        }
    })
    assert kc4 is None
    assert any("references.priority" in e and "must be boolean" in e for e in errs4)

    # headings must be list[str]
    kc5, errs5 = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "item": {"references": {"DESIGN": {"coverage": True, "headings": "H"}}},
            },
        }
    })
    assert kc5 is None
    assert any("Reference rule field 'headings'" in e for e in errs5)


def test_parse_kind_constraints_type_errors_for_kind_object():
    kc, errs = parse_kit_constraints({"PRD": []})
    assert kc is None
    assert any("constraints for PRD must be an object" in e for e in errs)

    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "identifiers": {},
            "description": 123,
        }
    })
    assert kc2 is None
    assert any("field 'description' must be string" in e for e in errs2)

    kc3, errs3 = parse_kit_constraints({
        "PRD": {
            "identifiers": [],
        }
    })
    assert kc3 is None
    assert any("field 'identifiers' must be an object" in e for e in errs3)


def test_load_constraints_json_missing_ok(tmp_path: Path):
    kc, errs = load_constraints_json(tmp_path)
    assert kc is None
    assert errs == []


def test_load_constraints_json_invalid_json(tmp_path: Path):
    (tmp_path / "constraints.json").write_text("{", encoding="utf-8")
    kc, errs = load_constraints_json(tmp_path)
    assert kc is None
    assert errs
    assert any("Failed to parse constraints.json" in e for e in errs)


def test_load_constraints_json_invalid_schema(tmp_path: Path):
    (tmp_path / "constraints.json").write_text("[]", encoding="utf-8")
    kc, errs = load_constraints_json(tmp_path)
    assert kc is None
    assert errs


def test_load_constraints_json_valid(tmp_path: Path):
    (tmp_path / "constraints.json").write_text(
        '{"PRD": {"identifiers": {"item": {}}}}',
        encoding="utf-8",
    )
    kc, errs = load_constraints_json(tmp_path)
    assert errs == []
    assert kc is not None
    assert "PRD" in kc.by_kind


def test_load_constraints_json_parses_valid_constraints(tmp_path: Path):
    (tmp_path / "constraints.json").write_text(
        '{"PRD": {"identifiers": {"item": {}}}}',
        encoding="utf-8",
    )
    kc, errs = load_constraints_json(tmp_path)
    assert errs == []
    assert kc is not None
    assert "PRD" in kc.by_kind


def test_validate_artifact_file_enforces_constraints_and_required_kinds(tmp_path: Path):
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "flow": {
                    "required": True,
                    "task": True,
                    "priority": True,
                    "headings": ["Allowed"],
                },
                "req": {"required": True},
            }
        }
    })
    assert errs == []
    prd_constraints = kc.by_kind["PRD"]

    p = tmp_path / "PRD.md"
    p.write_text(
        "# PRD\n\n## Wrong\n\n**ID**: `cpt-myapp-flow-login`\n\n**ID**: `cpt-myapp-x-bad`\n",
        encoding="utf-8",
    )
    rep = validate_artifact_file(
        artifact_path=p,
        artifact_kind="PRD",
        constraints=prd_constraints,
        registered_systems={"myapp"},
    )
    codes = [str(e.get("code")) for e in (rep.get("errors") or [])]
    assert EC.DEF_MISSING_TASK in codes
    assert EC.DEF_MISSING_PRIORITY in codes
    assert EC.DEF_WRONG_HEADINGS in codes
    assert EC.ID_KIND_NOT_ALLOWED in codes
    assert EC.REQUIRED_ID_KIND_MISSING in codes


def test_validate_artifact_file_prohibited_task_and_priority(tmp_path: Path):
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "flow": {"task": False, "priority": False}
            }
        }
    })
    assert errs == []
    prd_constraints = kc.by_kind["PRD"]

    p = tmp_path / "PRD.md"
    p.write_text("- [x] `p1` - **ID**: `cpt-myapp-flow-login`\n", encoding="utf-8")
    rep = validate_artifact_file(
        artifact_path=p,
        artifact_kind="PRD",
        constraints=prd_constraints,
        registered_systems={"myapp"},
    )
    codes = [str(e.get("code")) for e in (rep.get("errors") or [])]
    assert EC.DEF_PROHIBITED_TASK in codes
    assert EC.DEF_PROHIBITED_PRIORITY in codes


def test_cross_validate_artifacts_structure_and_reference_rules(tmp_path: Path):
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "flow": {
                    "required": False,
                    "task": True,
                    "headings": ["Allowed"],
                    "references": {
                        "DESIGN": {"coverage": True, "task": True, "priority": True, "headings": ["Design Heading"]},
                        "SPEC": {"coverage": True},
                        "ADR": {"coverage": False},
                    },
                },
                "note": {
                    "required": False,
                    "references": {
                        "DESIGN": {"task": False, "priority": False},
                    },
                },
                "req": {"required": True},
            }
        },
        "DESIGN": {"identifiers": {"principle": {"required": False}}},
        "ADR": {"identifiers": {"adr": {"required": False}}},
    })
    assert errs == []

    prd = tmp_path / "PRD.md"
    prd.write_text(
        "# PRD\n\n## Wrong\n\n"
        "- [ ] **ID**: `cpt-sys-flow-login`\n"
        "**ID**: `cpt-sys-flow-logout`\n"
        "- [ ] **ID**: `cpt-sys-flow-pay`\n"
        "**ID**: `cpt-sys-flow-missing`\n"
        "**ID**: `cpt-sys-note-doc`\n"
        "**ID**: `cpt-sys-x-bad`\n",
        encoding="utf-8",
    )

    design = tmp_path / "DESIGN.md"
    design.write_text(
        "# Design\n\n## Wrong Design Heading\n\n"
        "`cpt-sys-flow-login`\n"
        "- [x] `cpt-sys-flow-login`\n"
        "- [x] `cpt-sys-flow-logout`\n"
        "`cpt-sys-flow-pay`\n"
        "`cpt-sys-flow-ghost`\n"
        "- [x] `p1` - `cpt-sys-note-doc`\n",
        encoding="utf-8",
    )

    adr = tmp_path / "ADR.md"
    adr.write_text("`cpt-sys-flow-login`\n", encoding="utf-8")

    spec = tmp_path / "SPEC.md"
    spec.write_text("# Spec\n", encoding="utf-8")

    arts = [
        ArtifactRecord(path=prd, artifact_kind="PRD", constraints=kc.by_kind["PRD"]),
        ArtifactRecord(path=design, artifact_kind="DESIGN", constraints=kc.by_kind["DESIGN"]),
        ArtifactRecord(path=adr, artifact_kind="ADR", constraints=kc.by_kind["ADR"]),
        ArtifactRecord(path=spec, artifact_kind="SPEC", constraints=None),
    ]

    rep = cross_validate_artifacts(arts, registered_systems={"sys"}, known_kinds={"flow", "note", "req"})
    errs = rep.get("errors") or []
    warns = rep.get("warnings") or []
    messages = [str(e.get("message")) for e in errs]

    codes = [str(e.get("code")) for e in errs]
    assert EC.MISSING_CONSTRAINTS in codes
    assert EC.REF_NO_DEFINITION in codes
    assert EC.REF_TASK_DEF_NO_TASK in codes
    assert EC.DEF_WRONG_HEADINGS in codes
    assert EC.REQUIRED_ID_KIND_MISSING in codes
    assert EC.ID_KIND_NOT_ALLOWED in codes
    assert EC.REF_FROM_PROHIBITED_KIND in codes
    assert EC.REF_MISSING_FROM_KIND in codes
    assert EC.REF_MISSING_TASK in codes
    assert EC.REF_MISSING_PRIORITY in codes
    assert EC.REF_WRONG_HEADINGS in codes
    assert EC.REF_PROHIBITED_TASK in codes
    assert EC.REF_PROHIBITED_PRIORITY in codes

    warn_codes = [str(w.get("code")) for w in warns]
    assert EC.REF_TARGET_NOT_IN_SCOPE in warn_codes


def test_validate_artifact_file_no_registered_systems_uses_kind_tokens(tmp_path: Path):
    """When registered_systems=None, match_system uses rightmost kind-token split."""
    kc, errs = parse_kit_constraints({
        "FEATURE": {
            "identifiers": {
                "featstatus": {"required": False},
                "flow": {"required": False},
                "dod": {"required": False},
            }
        }
    })
    assert errs == []
    feat_constraints = kc.by_kind["FEATURE"]

    p = tmp_path / "FEATURE.md"
    # System name "task-flow" contains kind token "flow"
    p.write_text(
        "# Feature\n\n"
        "**ID**: `cpt-ex-task-flow-featstatus-crud`\n\n"
        "**ID**: `cpt-ex-task-flow-dod-create`\n",
        encoding="utf-8",
    )
    rep = validate_artifact_file(
        artifact_path=p,
        artifact_kind="FEATURE",
        constraints=feat_constraints,
        registered_systems=None,
    )
    errs = rep.get("errors") or []
    # Should NOT produce id-kind-not-allowed errors — system must be detected as
    # "ex-task-flow", not truncated to "ex-task" (which would make kind="flow").
    kind_errors = [e for e in errs if e.get("code") == EC.ID_KIND_NOT_ALLOWED]
    assert kind_errors == [], f"Unexpected kind errors: {kind_errors}"


def test_validate_artifact_file_id_system_unrecognized(tmp_path: Path):
    """IDs with unrecognized system prefix produce id-system-unrecognized error."""
    kc, errs = parse_kit_constraints({
        "PRD": {"identifiers": {"fr": {"required": False}}}
    })
    assert errs == []

    p = tmp_path / "PRD.md"
    p.write_text("**ID**: `cpt-unknown-fr-login`\n", encoding="utf-8")
    rep = validate_artifact_file(
        artifact_path=p,
        artifact_kind="PRD",
        constraints=kc.by_kind["PRD"],
        registered_systems={"myapp"},
    )
    codes = [str(e.get("code")) for e in (rep.get("errors") or [])]
    assert EC.ID_SYSTEM_UNRECOGNIZED in codes


def test_cross_validate_no_registered_systems_compound_system(tmp_path: Path):
    """cross_validate with registered_systems=None handles compound system names."""
    kc, errs = parse_kit_constraints({
        "PRD": {
            "identifiers": {
                "fr": {"required": False, "references": {"DESIGN": {"coverage": True}}},
            }
        },
        "DESIGN": {"identifiers": {"component": {"required": False}}},
    })
    assert errs == []

    prd = tmp_path / "PRD.md"
    prd.write_text("**ID**: `cpt-my-design-fr-login`\n", encoding="utf-8")

    design = tmp_path / "DESIGN.md"
    design.write_text("`cpt-my-design-fr-login`\n", encoding="utf-8")

    arts = [
        ArtifactRecord(path=prd, artifact_kind="PRD", constraints=kc.by_kind["PRD"]),
        ArtifactRecord(path=design, artifact_kind="DESIGN", constraints=kc.by_kind["DESIGN"]),
    ]
    rep = cross_validate_artifacts(arts, registered_systems=None, known_kinds={"fr", "component"})
    errs = rep.get("errors") or []
    # Should NOT have ref-no-definition (system must be "my-design", not "my")
    ref_no_def = [e for e in errs if e.get("code") == EC.REF_NO_DEFINITION]
    assert ref_no_def == [], f"Unexpected ref-no-definition: {ref_no_def}"


def test_cross_validate_reference_done_but_definition_not_done(tmp_path: Path):
    kc, errs = parse_kit_constraints({
        "PRD": {"identifiers": {"flow": {"required": False}}},
        "DESIGN": {"identifiers": {"principle": {"required": False}}},
    })
    assert errs == []

    prd = tmp_path / "PRD.md"
    prd.write_text("- [ ] **ID**: `cpt-sys-flow-login`\n", encoding="utf-8")

    design = tmp_path / "DESIGN.md"
    design.write_text("- [x] - `cpt-sys-flow-login`\n", encoding="utf-8")

    arts = [
        ArtifactRecord(path=prd, artifact_kind="PRD", constraints=kc.by_kind["PRD"]),
        ArtifactRecord(path=design, artifact_kind="DESIGN", constraints=kc.by_kind["DESIGN"]),
    ]

    rep = cross_validate_artifacts(arts, registered_systems={"sys"}, known_kinds={"flow"})
    errs = rep.get("errors") or []
    assert any(e.get("code") == EC.REF_DONE_DEF_NOT_DONE for e in errs)
