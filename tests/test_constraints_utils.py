from pathlib import Path

from skills.cypilot.scripts.cypilot.utils.constraints import load_constraints_json, parse_kit_constraints


def test_parse_kit_constraints_none_ok():
    kc, errs = parse_kit_constraints(None)
    assert kc is None
    assert errs == []


def test_parse_kit_constraints_root_must_be_object():
    kc, errs = parse_kit_constraints([1, 2, 3])
    assert kc is None
    assert errs


def test_parse_kit_constraints_rejects_non_string_kind_key():
    kc, errs = parse_kit_constraints({1: {"defined-id": []}})
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
            "defined-id": [
                {
                    "kind": "item",
                    "name": "Item",
                    "description": "An item",
                    "examples": ["cpt-test-item-1"],
                    "task": True,
                    "priority": False,
                    "to_code": True,
                    "headings": ["  H1 ", "", "H2"],
                    "references": {
                        "DESIGN": {"coverage": "required"},
                        "SPEC": {"coverage": "required"},
                    },
                }
            ],
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
    assert d0.references["DESIGN"].coverage == "required"


def test_parse_kit_constraints_duplicate_kind_detection():
    data = {
        "PRD": {
            "defined-id": [{"kind": "item"}, {"kind": "item"}],
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert kc is None
    assert any("defined-id has duplicate kind" in e for e in errs)


def test_parse_kit_constraints_reports_field_type_errors():
    data = {
        "PRD": {
            "name": 123,
            "defined-id": [],
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert kc is None
    assert any("field 'name'" in e for e in errs)


def test_parse_kit_constraints_entry_must_be_object_and_kind_required():
    data1 = {"PRD": {"defined-id": ["x"]}}
    kc, errs = parse_kit_constraints(data1)
    assert kc is None
    assert any("Constraint entry must be an object" in e for e in errs)

    data2 = {"PRD": {"defined-id": [{}]}}
    kc2, errs2 = parse_kit_constraints(data2)
    assert kc2 is None
    assert any("missing required 'kind'" in e for e in errs2)


def test_parse_kit_constraints_entry_type_validation():
    data = {
        "PRD": {
            "defined-id": [
                {"kind": "item", "task": "yes"},
                {"kind": "item2", "priority": "no"},
                {"kind": "item3", "to_code": "nope"},
                {"kind": "item4", "headings": "H"},
            ],
        }
    }
    kc, errs = parse_kit_constraints(data)
    assert kc is None
    assert any("field 'task'" in e for e in errs)
    assert any("field 'priority'" in e for e in errs)
    assert any("field 'to_code'" in e for e in errs)
    assert any("field 'headings'" in e for e in errs)


def test_parse_id_constraint_examples_must_be_list():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "examples": "not-a-list"},
            ],
        }
    })
    assert kc is None
    assert any("examples" in e and "must be a list" in e for e in errs)


def test_parse_id_constraint_name_and_description_must_be_string():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "name": 123},
            ],
        }
    })
    assert kc is None
    assert any("field 'name'" in e for e in errs)

    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "description": 123},
            ],
        }
    })
    assert kc2 is None
    assert any("field 'description'" in e for e in errs2)


def test_parse_references_must_be_object_and_keys_strings():
    kc, errs = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": "bad"},
            ],
        }
    })
    assert kc is None
    assert any("references" in e and "must be an object" in e for e in errs)

    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": {1: {"coverage": "required"}}},
            ],
        }
    })
    assert kc2 is None
    assert any("non-string artifact kind key" in e for e in errs2)


def test_parse_reference_rule_validation_errors():
    # rule must be an object
    kc, errs = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": {"DESIGN": "bad"}},
            ],
        }
    })
    assert kc is None
    assert any("Reference rule must be an object" in e for e in errs)

    # invalid coverage
    kc2, errs2 = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": {"DESIGN": {"coverage": "bad"}}},
            ],
        }
    })
    assert kc2 is None
    assert any("coverage" in e and "must be one of" in e for e in errs2)

    # task must be boolean
    kc3, errs3 = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": {"DESIGN": {"coverage": "required", "task": "x"}}},
            ],
        }
    })
    assert kc3 is None
    assert any("Reference rule field 'task'" in e for e in errs3)

    # priority must be boolean
    kc4, errs4 = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": {"DESIGN": {"coverage": "required", "priority": "x"}}},
            ],
        }
    })
    assert kc4 is None
    assert any("Reference rule field 'priority'" in e for e in errs4)

    # headings must be list[str]
    kc5, errs5 = parse_kit_constraints({
        "PRD": {
            "defined-id": [
                {"kind": "item", "references": {"DESIGN": {"coverage": "required", "headings": "H"}}},
            ],
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
            "defined-id": [],
            "description": 123,
        }
    })
    assert kc2 is None
    assert any("field 'description' must be string" in e for e in errs2)

    kc3, errs3 = parse_kit_constraints({
        "PRD": {
            "defined-id": {},
        }
    })
    assert kc3 is None
    assert any("field 'defined-id' must be a list" in e for e in errs3)


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
        '{"PRD": {"defined-id": [{"kind": "item"}]}}',
        encoding="utf-8",
    )
    kc, errs = load_constraints_json(tmp_path)
    assert errs == []
    assert kc is not None
    assert "PRD" in kc.by_kind
