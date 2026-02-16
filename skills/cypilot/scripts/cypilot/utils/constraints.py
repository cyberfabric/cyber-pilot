from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class ReferenceRule:
    coverage: str  # required|optional|prohibited
    task: Optional[str] = None  # required|allowed|prohibited
    priority: Optional[str] = None  # required|allowed|prohibited
    headings: Optional[List[str]] = None


@dataclass(frozen=True)
class HeadingConstraint:
    level: int
    pattern: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    multiple: str = "allow"  # allow|prohibited|required
    numbered: str = "allow"  # allow|prohibited|required
    id: Optional[str] = None
    prev: Optional[str] = None
    next: Optional[str] = None
    pointer: Optional[str] = None


@dataclass(frozen=True)
class IdConstraint:
    kind: str
    required: bool = True
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    examples: Optional[List[object]] = None
    task: Optional[str] = None  # required|allowed|prohibited
    priority: Optional[str] = None  # required|allowed|prohibited
    to_code: Optional[bool] = None
    headings: Optional[List[str]] = None
    references: Optional[Dict[str, ReferenceRule]] = None


def _parse_tri_state(v: object, field: str) -> Tuple[Optional[str], Optional[str]]:
    if v is None:
        return None, None
    if isinstance(v, bool):
        return ("required" if v else "prohibited"), None
    if isinstance(v, str):
        vv = v.strip().lower()
        if vv in {"required", "allowed", "prohibited"}:
            return vv, None
        return None, f"Constraint field '{field}' must be one of: required, allowed, prohibited"
    return None, f"Constraint field '{field}' must be string (required|allowed|prohibited)"


@dataclass(frozen=True)
class ArtifactKindConstraints:
    name: Optional[str]
    description: Optional[str]
    defined_id: List[IdConstraint]
    headings: Optional[List[HeadingConstraint]] = None


@dataclass(frozen=True)
class KitConstraints:
    by_kind: Dict[str, ArtifactKindConstraints]


def error(kind: str, message: str, *, path: Path | str, line: int = 1, **extra) -> Dict[str, object]:
    out: Dict[str, object] = {"type": kind, "message": message, "line": int(line)}
    out["path"] = str(path)
    extra = {k: v for k, v in extra.items() if v is not None}
    out.update(extra)
    return out


def heading_constraint_ids_by_line(path: Path, heading_constraints: Sequence[HeadingConstraint]) -> List[List[str]]:
    """Return active heading constraint ids for each line (1-indexed).

    This is similar to document.headings_by_line(), but instead of returning
    raw heading titles, it returns the list of *matched heading constraint ids*
    that are currently in scope at each line.

    Matching uses the same level/pattern rules as validate_headings_contract.
    """
    from .document import read_text_safe

    lines = read_text_safe(path)
    if lines is None:
        return [[]]

    headings = _scan_headings(path)

    matched_ids_by_line: Dict[int, str] = {}

    def _is_regex_pattern(pat: str) -> bool:
        # Heuristic: treat as regex only if it contains typical regex metacharacters.
        return any(ch in pat for ch in ".^$*+?{}[]\\|()")

    compiled: List[Tuple[HeadingConstraint, Optional[re.Pattern[str]]]] = []
    for hc in heading_constraints:
        pat = getattr(hc, "pattern", None)
        if not pat:
            compiled.append((hc, None))
            continue
        pat_s = str(pat)
        if not _is_regex_pattern(pat_s):
            compiled.append((hc, None))
            continue
        try:
            compiled.append((hc, re.compile(pat_s, flags=re.IGNORECASE)))
        except re.error:
            # Invalid regex should never match.
            compiled.append((hc, re.compile(r"$^")))

    idx_by_level: Dict[int, List[int]] = {}
    for idx, (hc, _) in enumerate(compiled):
        idx_by_level.setdefault(int(getattr(hc, "level", 0) or 0), []).append(idx)

    wildcard_lvl3_by_parent_lvl2_id: Dict[str, str] = {}
    lvl2_idxs = idx_by_level.get(2, [])
    for pos, i in enumerate(lvl2_idxs):
        hc2, _ = compiled[i]
        parent_id = str(getattr(hc2, "id", "") or "").strip()
        if not parent_id:
            continue
        next_lvl2 = lvl2_idxs[pos + 1] if pos + 1 < len(lvl2_idxs) else len(compiled)
        for j in range(i + 1, next_lvl2):
            hc3, _ = compiled[j]
            if int(getattr(hc3, "level", 0) or 0) != 3:
                continue
            if getattr(hc3, "pattern", None):
                continue
            cid = str(getattr(hc3, "id", "") or "").strip()
            if cid:
                wildcard_lvl3_by_parent_lvl2_id[parent_id] = cid
                break

    def _matches_level_title(level: int, title_text: str, idx: int) -> bool:
        hc, rx = compiled[idx]
        if int(getattr(hc, "level", 0) or 0) != int(level):
            return False
        pat = getattr(hc, "pattern", None)
        if not pat:
            return True

        if rx is not None:
            return bool(rx.search(title_text))
        return str(pat).strip().casefold() == str(title_text).strip().casefold()

    def _pick_best(level: int, title_text: str, *, include_wildcards: bool = True) -> Optional[int]:
        candidates: List[int] = []
        for idx in idx_by_level.get(level, []):
            hc, rx = compiled[idx]
            if not include_wildcards and not getattr(hc, "pattern", None):
                continue
            if _matches_level_title(level, title_text, idx):
                candidates.append(idx)
        if not candidates:
            return None
        candidates.sort(key=lambda i: (0 if getattr(compiled[i][0], "pattern", None) else 1, i))
        return candidates[0]

    current_lvl2_id: Optional[str] = None
    for h in headings:
        lvl = int(h.get("level", 0) or 0)
        title = str(h.get("title_text") or "")
        ln = int(h.get("line", 0) or 0)
        if ln <= 0 or lvl <= 0:
            continue

        matched_id: Optional[str] = None
        if lvl == 3:
            # Do not allow global wildcard matching for level-3 headings.
            # Otherwise, the first wildcard constraint (e.g. feature-actor-flow)
            # will match all level-3 headings across the document.
            idx = _pick_best(3, title, include_wildcards=False)
            if idx is not None:
                matched_id = str(getattr(compiled[idx][0], "id", "") or "").strip() or None
            elif current_lvl2_id:
                matched_id = wildcard_lvl3_by_parent_lvl2_id.get(current_lvl2_id)
        else:
            idx = _pick_best(lvl, title)
            if idx is not None:
                matched_id = str(getattr(compiled[idx][0], "id", "") or "").strip() or None
            if lvl == 2 and matched_id:
                current_lvl2_id = matched_id

        if matched_id:
            matched_ids_by_line[ln] = matched_id

    # Convert heading events into a per-line active stack.
    events_by_line: Dict[int, Tuple[int, Optional[str]]] = {}
    for h in headings:
        ln = int(h.get("line", 0) or 0)
        lvl = int(h.get("level", 0) or 0)
        if ln <= 0 or lvl <= 0:
            continue
        events_by_line[ln] = (lvl, matched_ids_by_line.get(ln))

    out: List[List[str]] = [[] for _ in range(len(lines) + 1)]
    stack: List[Tuple[int, str]] = []
    for idx0 in range(len(lines)):
        line_no = idx0 + 1
        ev = events_by_line.get(line_no)
        if ev is not None:
            lvl, hid = ev
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            if hid:
                stack.append((lvl, hid))
        out[line_no] = [hid for _, hid in stack]
    return out


@dataclass(frozen=True)
class ParsedCypilotId:
    system: str
    kind: str
    slug: str


def parse_cpt(
    cpt: str,
    expected_kind: str,
    registered_systems: Iterable[str],
    where_defined: Optional[callable] = None,
    known_kinds: Optional[Iterable[str]] = None,
) -> Optional[ParsedCypilotId]:
    if not cpt or not str(cpt).lower().startswith("cpt-"):
        return None

    cpt = str(cpt)
    expected_kind = str(expected_kind)
    parts = cpt.split("-")
    if len(parts) < 3:
        return None

    systems = sorted({str(s) for s in registered_systems if str(s).strip()}, key=len, reverse=True)
    system: Optional[str] = None
    for s in systems:
        prefix = f"cpt-{s}-"
        if cpt.lower().startswith(prefix.lower()):
            system = s
            break
    if system is None:
        return None

    remainder = cpt[len(f"cpt-{system}-"):]
    if not remainder:
        return None

    rem_parts = [p for p in remainder.split("-") if p]
    if not rem_parts:
        return None

    first_kind = rem_parts[0]

    kinds_set: Optional[set[str]] = None
    if known_kinds is not None:
        kinds_set = {str(k).strip().lower() for k in known_kinds if str(k).strip()}

    if kinds_set is not None and expected_kind.strip().lower() not in kinds_set:
        return None

    if first_kind.lower() == expected_kind.lower():
        slug = "-".join(rem_parts[1:]) if len(rem_parts) > 1 else ""
        return ParsedCypilotId(system=system, kind=expected_kind, slug=slug)

    # Composite ID support: look for `-{expected_kind}-` separator.
    sep = f"-{expected_kind}-"
    idx = remainder.lower().find(sep.lower())
    if idx == -1:
        return None

    left = f"cpt-{system}-" + remainder[:idx]
    slug = remainder[idx + len(sep):]
    if where_defined is not None and not where_defined(left):
        return None

    return ParsedCypilotId(system=system, kind=expected_kind, slug=slug)


@dataclass(frozen=True)
class ArtifactRecord:
    path: Path
    artifact_kind: str
    constraints: Optional[ArtifactKindConstraints] = None


def validate_artifact_file(
    *,
    artifact_path: Path,
    artifact_kind: str,
    constraints: Optional[ArtifactKindConstraints],
    registered_systems: Optional[Iterable[str]] = None,
    constraints_path: Optional[Path] = None,
    kit_id: Optional[str] = None,
) -> Dict[str, List[Dict[str, object]]]:
    from .document import headings_by_line, scan_cpt_ids, scan_cdsl_instructions

    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    kind = str(artifact_kind).strip().upper()

    # SPEC filename check (independent of constraints)
    if kind == "SPEC":
        hits = scan_cpt_ids(artifact_path)
        defs = [h for h in hits if str(h.get("type")) == "definition"]
        filename = artifact_path.stem
        nested_suffixes = ("-flow-", "-algo-", "-state-", "-req-")
        for h in defs:
            hid = str(h.get("id") or "")
            if "-spec-" not in hid:
                continue
            if any(s in hid for s in nested_suffixes):
                continue
            parts = hid.split("-spec-", 1)
            if len(parts) != 2:
                continue
            spec_slug = parts[1]
            if spec_slug != filename:
                errors.append(error(
                    "structure",
                    "Spec filename does not match ID slug",
                    path=artifact_path,
                    line=int(h.get("line", 1) or 1),
                    id=hid,
                    expected_filename=f"{spec_slug}.md",
                    actual_filename=f"{filename}.md",
                ))

    if constraints is None:
        return {"errors": errors, "warnings": warnings}

    # Phase 1: headings contract
    if getattr(constraints, "headings", None):
        rep = validate_headings_contract(
            path=artifact_path,
            constraints=constraints,
            registered_systems=registered_systems,
            artifact_kind=kind,
            constraints_path=constraints_path,
            kit_id=kit_id,
        )
        errors.extend(rep.get("errors", []))
        warnings.extend(rep.get("warnings", []))

        # Stop here: IDs are validated only after outline contract is satisfied.
        if rep.get("errors"):
            return {"errors": errors, "warnings": warnings}

    # Phase 2: identifier/content validation
    hits = scan_cpt_ids(artifact_path)
    defs = [h for h in hits if str(h.get("type")) == "definition"]
    refs = [h for h in hits if str(h.get("type")) == "reference"]

    defs_by_id: Dict[str, Dict[str, object]] = {}
    for d in defs:
        did = str(d.get("id") or "").strip()
        if did and did not in defs_by_id:
            defs_by_id[did] = d

    cdsl_hits = scan_cdsl_instructions(artifact_path)
    for ch in cdsl_hits:
        if bool(ch.get("checked", False)):
            continue
        pid = str(ch.get("parent_id") or "").strip()
        if not pid:
            continue
        parent_def = defs_by_id.get(pid)
        if not parent_def:
            continue
        if not bool(parent_def.get("has_task", False)):
            continue
        if not bool(parent_def.get("checked", False)):
            continue
        errors.append(error(
            "structure",
            "CDSL step is unchecked but parent ID is checked",
            path=artifact_path,
            line=int(ch.get("line", 1) or 1),
            id=pid,
            inst=str(ch.get("inst") or "") or None,
        ))

    headings_scanned = _scan_headings(artifact_path)

    def _heading_ctx_for_line(ln: int) -> Tuple[int, Optional[int]]:
        last_idx: Optional[int] = None
        for i, h in enumerate(headings_scanned):
            if int(h.get("line", 0) or 0) <= ln:
                last_idx = i
                continue
            break
        if last_idx is None:
            return 0, None
        lvl = int(headings_scanned[last_idx].get("level", 0) or 0)
        return lvl, last_idx

    def _scope_end_for_heading_idx(hidx: int) -> int:
        if hidx < 0 or hidx >= len(headings_scanned):
            return 10**9
        lvl = int(headings_scanned[hidx].get("level", 0) or 0)
        for j in range(hidx + 1, len(headings_scanned)):
            jlvl = int(headings_scanned[j].get("level", 0) or 0)
            if jlvl <= lvl:
                return int(headings_scanned[j].get("line", 1) or 1) - 1
        return 10**9

    defs_sorted = sorted(defs, key=lambda d: int(d.get("line", 0) or 0))
    refs_task_sorted = sorted(
        [r for r in refs if bool(r.get("has_task", False))],
        key=lambda r: int(r.get("line", 0) or 0),
    )
    for parent in defs_sorted:
        if not bool(parent.get("has_task", False)):
            continue
        parent_line = int(parent.get("line", 0) or 0)
        if parent_line <= 0:
            continue
        parent_id = str(parent.get("id") or "").strip()
        if not parent_id:
            continue

        parent_lvl, parent_hidx = _heading_ctx_for_line(parent_line)
        if parent_hidx is None:
            continue
        scope_end = _scope_end_for_heading_idx(parent_hidx)

        children: List[Dict[str, object]] = []
        for child in defs_sorted:
            child_line = int(child.get("line", 0) or 0)
            if child_line <= parent_line or child_line > scope_end:
                continue
            if not bool(child.get("has_task", False)):
                continue
            child_lvl, _child_hidx = _heading_ctx_for_line(child_line)
            if child_lvl <= parent_lvl:
                continue
            children.append(child)

        ref_children: List[Dict[str, object]] = []
        for rr in refs_task_sorted:
            rline = int(rr.get("line", 0) or 0)
            if rline <= parent_line or rline > scope_end:
                continue
            ref_children.append(rr)

        if (not children) and (not ref_children):
            continue

        parent_checked = bool(parent.get("checked", False))
        all_children_checked = all(bool(c.get("checked", False)) for c in children)
        any_child_unchecked = any(not bool(c.get("checked", False)) for c in children)
        all_ref_children_checked = all(bool(r.get("checked", False)) for r in ref_children)
        any_ref_child_unchecked = any(not bool(r.get("checked", False)) for r in ref_children)

        if all_children_checked and all_ref_children_checked and (not parent_checked):
            errors.append(error(
                "structure",
                "Parent ID is unchecked but all nested task-tracked items are checked",
                path=artifact_path,
                line=parent_line,
                id=parent_id,
            ))

        if parent_checked and (any_child_unchecked or any_ref_child_unchecked):
            first_unchecked = next((c for c in children if not bool(c.get("checked", False))), None)
            first_ref_unchecked = next((r for r in ref_children if not bool(r.get("checked", False))), None)
            first = first_unchecked or first_ref_unchecked or parent
            errors.append(error(
                "structure",
                "Parent ID is checked but some nested task-tracked items are unchecked",
                path=artifact_path,
                line=int(first.get("line", 1) or 1),
                id=str(first.get("id") or "") or parent_id,
                parent_id=parent_id,
            ))

    allowed_defs = {c.kind.strip().lower() for c in (constraints.defined_id or [])}
    constraint_by_kind = {c.kind.strip().lower(): c for c in (constraints.defined_id or []) if isinstance(getattr(c, "kind", None), str)}

    def _id_kind_hint(c: Optional[IdConstraint]) -> str:
        if c is None:
            return ""
        nm = str(getattr(c, "name", "") or "").strip()
        tpl = str(getattr(c, "template", "") or "").strip()
        desc = str(getattr(c, "description", "") or "").strip()
        parts: List[str] = []
        if nm:
            parts.append(nm)
        if tpl:
            parts.append(f"template={tpl}")
        if desc:
            parts.append(desc)
        return (" (" + "; ".join(parts) + ")") if parts else ""

    heading_desc_by_id: Dict[str, str] = {}
    for hc in (getattr(constraints, "headings", None) or []):
        hid = str(getattr(hc, "id", "") or "").strip()
        if not hid:
            continue
        desc = str(getattr(hc, "description", "") or "").strip()
        if desc:
            heading_desc_by_id[hid] = desc

    # Heading scope cache
    heading_constraints = getattr(constraints, "headings", None)
    if heading_constraints:
        headings_at = heading_constraint_ids_by_line(artifact_path, heading_constraints)
    else:
        headings_at = headings_by_line(artifact_path)

    # Use registered systems to extract id kind
    systems_set: set[str] = set()
    if registered_systems is not None:
        systems_set = {str(s).lower() for s in registered_systems}

    def match_system(cpt: str) -> Optional[str]:
        if not cpt.lower().startswith("cpt-"):
            return None
        matched: Optional[str] = None
        for sys in systems_set:
            prefix = f"cpt-{sys}-"
            if cpt.lower().startswith(prefix):
                if matched is None or len(sys) > len(matched):
                    matched = sys
        if matched is not None:
            return matched
        parts = cpt.split("-")
        return parts[1].lower() if len(parts) >= 3 else None

    composite_nested_by_base: Dict[str, set[str]] = {}
    base_kind = kind.strip().lower()
    nested = {str(getattr(ic, "kind", "") or "").strip().lower() for ic in (constraints.defined_id or []) if str(getattr(ic, "kind", "") or "").strip()}
    if nested:
        composite_nested_by_base[base_kind] = nested

    def extract_kind_from_id(cpt: str, system: Optional[str]) -> Optional[str]:
        if not cpt.lower().startswith("cpt-"):
            return None
        if system is None:
            return None
        prefix = f"cpt-{system}-"
        if not cpt.lower().startswith(prefix.lower()):
            return None
        remainder = cpt[len(prefix):]
        if not remainder:
            return None
        parts = [p for p in remainder.split("-") if p]
        if not parts:
            return None
        base = parts[0].strip().lower()
        nested_kinds = composite_nested_by_base.get(base)
        if nested_kinds and len(parts) >= 4:
            for p in reversed(parts[2:]):
                pp = p.strip().lower()
                if pp in nested_kinds and pp != base:
                    return pp
        return base

    defs_by_kind: Dict[str, List[Dict[str, object]]] = {}
    for h in defs:
        hid = str(h.get("id") or "").strip()
        if not hid:
            continue
        line = int(h.get("line", 1) or 1)
        system = match_system(hid)
        id_kind = extract_kind_from_id(hid, system)
        if not id_kind:
            continue
        defs_by_kind.setdefault(id_kind, []).append(h)

        if id_kind not in allowed_defs:
            hint = _id_kind_hint(constraint_by_kind.get(id_kind))
            errors.append(error(
                "constraints",
                f"ID kind not allowed by constraints{hint}",
                path=artifact_path,
                line=line,
                artifact_kind=kind,
                id_kind=id_kind,
                id=hid,
                section="defined-id",
                allowed=sorted(allowed_defs),
            ))

        c = constraint_by_kind.get(id_kind)
        if c is None:
            continue
        id_kind_name = str(getattr(c, "name", "") or "").strip() or None
        id_kind_description = str(getattr(c, "description", "") or "").strip() or None
        id_kind_template = str(getattr(c, "template", "") or "").strip() or None
        tk = str(getattr(c, "task", "allowed") or "allowed").strip().lower()
        pr = str(getattr(c, "priority", "allowed") or "allowed").strip().lower()

        has_task = bool(h.get("has_task", False))
        has_priority = bool(h.get("has_priority", False))

        if tk == "required" and not has_task:
            errors.append(error(
                "constraints",
                f"ID definition missing required task checkbox{_id_kind_hint(c)}",
                path=artifact_path,
                line=line,
                artifact_kind=kind,
                id_kind=id_kind,
                id=hid,
                section="defined-id",
                id_kind_name=id_kind_name,
                id_kind_description=id_kind_description,
                id_kind_template=id_kind_template,
            ))
        if tk == "prohibited" and has_task:
            errors.append(error(
                "constraints",
                f"ID definition has prohibited task checkbox{_id_kind_hint(c)}",
                path=artifact_path,
                line=line,
                artifact_kind=kind,
                id_kind=id_kind,
                id=hid,
                section="defined-id",
                id_kind_name=id_kind_name,
                id_kind_description=id_kind_description,
                id_kind_template=id_kind_template,
            ))

        if pr == "required" and not has_priority:
            errors.append(error(
                "constraints",
                f"ID definition missing required priority{_id_kind_hint(c)}",
                path=artifact_path,
                line=line,
                artifact_kind=kind,
                id_kind=id_kind,
                id=hid,
                section="defined-id",
                id_kind_name=id_kind_name,
                id_kind_description=id_kind_description,
                id_kind_template=id_kind_template,
            ))
        if pr == "prohibited" and has_priority:
            errors.append(error(
                "constraints",
                f"ID definition has prohibited priority{_id_kind_hint(c)}",
                path=artifact_path,
                line=line,
                artifact_kind=kind,
                id_kind=id_kind,
                id=hid,
                section="defined-id",
                id_kind_name=id_kind_name,
                id_kind_description=id_kind_description,
                id_kind_template=id_kind_template,
            ))

        allowed_headings = [
            str(x).strip() for x in (getattr(c, "headings", None) or [])
            if isinstance(x, str) and str(x).strip()
        ]
        if allowed_headings:
            allowed_norm = {str(x).strip().lower() for x in allowed_headings if str(x).strip()}
            active_raw = headings_at[line] if 0 <= line < len(headings_at) else []
            active_norm = [str(x).strip().lower() for x in active_raw if str(x).strip()]
            if not any(a in allowed_norm for a in active_norm):
                allowed_info = [
                    {"id": hid, "description": heading_desc_by_id.get(hid)}
                    for hid in sorted(allowed_norm)
                ]
                errors.append(error(
                    "constraints",
                    f"ID definition not under required headings{_id_kind_hint(c)}",
                    path=artifact_path,
                    line=line,
                    artifact_kind=kind,
                    id_kind=id_kind,
                    id=hid,
                    section="defined-id",
                    headings=sorted(allowed_norm),
                    headings_info=allowed_info,
                    found_headings=active_raw,
                    id_kind_name=id_kind_name,
                    id_kind_description=id_kind_description,
                    id_kind_template=id_kind_template,
                ))

    for c in constraints.defined_id:
        k = str(getattr(c, "kind", "") or "").strip().lower()
        if not k:
            continue
        is_required = bool(getattr(c, "required", True))
        if not is_required:
            continue
        if k in defs_by_kind and defs_by_kind[k]:
            continue
        errors.append(error(
            "constraints",
            f"Required ID kind missing in artifact{_id_kind_hint(c)}",
            path=artifact_path,
            line=1,
            artifact_kind=kind,
            id_kind=k,
            id_kind_name=str(getattr(c, "name", "") or "").strip() or None,
            id_kind_description=str(getattr(c, "description", "") or "").strip() or None,
            id_kind_template=str(getattr(c, "template", "") or "").strip() or None,
        ))

    return {"errors": errors, "warnings": warnings}


def cross_validate_artifacts(
    artifacts: Sequence[ArtifactRecord],
    registered_systems: Optional[Iterable[str]] = None,
    known_kinds: Optional[Iterable[str]] = None,
) -> Dict[str, List[Dict[str, object]]]:
    from .document import headings_by_line, scan_cpt_ids

    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    kinds_set: Optional[set] = None
    if known_kinds is not None:
        kinds_set = {str(k).lower() for k in known_kinds}

    constraints_by_artifact_kind: Dict[str, ArtifactKindConstraints] = {}
    missing_constraints_kinds: set[str] = set()
    composite_nested_kinds_by_base_kind: Dict[str, set[str]] = {}
    heading_desc_by_kind: Dict[str, Dict[str, str]] = {}

    for art in artifacts:
        ak = str(art.artifact_kind).strip().upper()
        c = art.constraints
        if c is None:
            missing_constraints_kinds.add(ak)
            continue
        constraints_by_artifact_kind[ak] = c

        hdesc: Dict[str, str] = {}
        for hc in (getattr(c, "headings", None) or []):
            hid = str(getattr(hc, "id", "") or "").strip()
            if not hid:
                continue
            d = str(getattr(hc, "description", "") or "").strip()
            if d:
                hdesc[hid] = d
        heading_desc_by_kind[ak] = hdesc

    for ak, c in constraints_by_artifact_kind.items():
        base_kind = str(ak).strip().lower()
        nested = {
            str(getattr(ic, "kind", "")).strip().lower()
            for ic in getattr(c, "defined_id", []) or []
            if str(getattr(ic, "kind", "")).strip()
        }
        if nested:
            composite_nested_kinds_by_base_kind[base_kind] = nested

    if missing_constraints_kinds:
        errors.append(error(
            "constraints",
            "Missing constraints for artifact kinds",
            path=Path("<constraints.json>"),
            line=1,
            kinds=sorted(missing_constraints_kinds),
        ))

    systems_set: set[str] = set()
    if registered_systems is not None:
        systems_set = {str(s).lower() for s in registered_systems}

    def match_system_from_id(cpt: str) -> Optional[str]:
        if not cpt.lower().startswith("cpt-"):
            return None
        if not systems_set:
            parts = cpt.split("-")
            return parts[1].lower() if len(parts) >= 3 else None
        matched: Optional[str] = None
        for sys in systems_set:
            prefix = f"cpt-{sys}-"
            if cpt.lower().startswith(prefix):
                if matched is None or len(sys) > len(matched):
                    matched = sys
        return matched

    def extract_kind_from_id(cpt: str, system: Optional[str]) -> Optional[str]:
        if not cpt.lower().startswith("cpt-"):
            return None
        if system is None:
            return None
        prefix = f"cpt-{system}-"
        if not cpt.lower().startswith(prefix.lower()):
            return None
        remainder = cpt[len(prefix):]
        if not remainder:
            return None
        parts = [p for p in remainder.split("-") if p]
        if not parts:
            return None

        base = parts[0].strip().lower()
        nested_kinds = composite_nested_kinds_by_base_kind.get(base)
        if nested_kinds and len(parts) >= 4:
            for p in reversed(parts[2:]):
                pp = p.strip().lower()
                if pp in nested_kinds and pp != base:
                    return pp
        return base

    def is_external_system_ref(cpt: str) -> bool:
        if not systems_set:
            return False
        if not cpt.lower().startswith("cpt-"):
            return False
        for sys in systems_set:
            prefix = f"cpt-{sys}-"
            if cpt.lower().startswith(prefix):
                return False
        return True

    def headings_info_for_kind(kind: str, heading_ids: Sequence[str]) -> List[Dict[str, object]]:
        km = heading_desc_by_kind.get(str(kind).strip().upper(), {})
        out: List[Dict[str, object]] = []
        for hid in heading_ids:
            hs = str(hid or "").strip()
            if not hs:
                continue
            out.append({"id": hs, "description": km.get(hs)})
        return out

    # Index scan results
    defs_by_id: Dict[str, List[Dict[str, object]]] = {}
    refs_by_id: Dict[str, List[Dict[str, object]]] = {}
    present_kinds_by_system: Dict[str, set[str]] = {}
    refs_by_system_kind: Dict[str, Dict[str, List[Dict[str, object]]]] = {}

    headings_cache: Dict[str, List[List[str]]] = {}
    for art in artifacts:
        ak = str(art.artifact_kind).strip().upper()
        hits = scan_cpt_ids(art.path)
        hkey = str(art.path)
        if hkey not in headings_cache:
            # Prefer constraint heading ids when available; else fallback to raw titles.
            hc = getattr(getattr(art, "constraints", None), "headings", None)
            if hc:
                headings_cache[hkey] = heading_constraint_ids_by_line(art.path, hc)
            else:
                headings_cache[hkey] = headings_by_line(art.path)
        headings_at = headings_cache[hkey]

        for h in hits:
            hid = str(h.get("id", "")).strip()
            if not hid:
                continue
            line = int(h.get("line", 1) or 1)
            checked = bool(h.get("checked", False))
            system = match_system_from_id(hid)
            id_kind = extract_kind_from_id(hid, system)
            active_headings = headings_at[line] if 0 <= line < len(headings_at) else []

            row = {
                "id": hid,
                "line": line,
                "checked": checked,
                "priority": h.get("priority"),
                "has_task": bool(h.get("has_task", False)),
                "has_priority": bool(h.get("has_priority", False)),
                "artifact_kind": ak,
                "artifact_path": art.path,
                "system": system,
                "id_kind": id_kind,
                "headings": active_headings,
            }

            if str(h.get("type")) == "definition":
                defs_by_id.setdefault(hid, []).append(row)
                if system:
                    present_kinds_by_system.setdefault(system, set()).add(ak)
            elif str(h.get("type")) == "reference":
                refs_by_id.setdefault(hid, []).append(row)
                if system:
                    present_kinds_by_system.setdefault(system, set()).add(ak)
                    refs_by_system_kind.setdefault(system, {}).setdefault(ak, []).append(row)

    # Definition existence for internal systems
    for rid, rows in refs_by_id.items():
        if is_external_system_ref(rid):
            continue
        if rid in defs_by_id:
            continue
        for r in rows:
            errors.append(error(
                "structure",
                "Reference has no definition",
                path=r.get("artifact_path"),
                line=int(r.get("line", 1) or 1),
                id=rid,
            ))

    # Done status consistency
    for rid, rrows in refs_by_id.items():
        for r in rrows:
            if not bool(r.get("has_task", False)):
                continue
            if not bool(r.get("checked", False)):
                continue
            defs = defs_by_id.get(rid, [])
            for d in defs:
                if not bool(d.get("has_task", False)):
                    continue
                if bool(d.get("checked", False)):
                    continue
                errors.append(error(
                    "structure",
                    "Reference marked done but definition not done",
                    path=r.get("artifact_path"),
                    line=int(r.get("line", 1) or 1),
                    id=rid,
                ))

    for rid, rrows in refs_by_id.items():
        defs = defs_by_id.get(rid, [])
        if not defs:
            continue
        for r in rrows:
            if not bool(r.get("has_task", False)):
                continue
            if any(bool(d.get("has_task", False)) for d in defs):
                continue
            errors.append(error(
                "structure",
                "Reference has task checkbox but definition has no task checkbox",
                path=r.get("artifact_path"),
                line=int(r.get("line", 1) or 1),
                id=rid,
            ))

    # Per-artifact kind required ID kind presence and headings
    for art in artifacts:
        ak = str(art.artifact_kind).strip().upper()
        c = constraints_by_artifact_kind.get(ak)
        if c is None:
            continue

        defs_in_file = [
            d for rows in defs_by_id.values() for d in rows
            if str(d.get("artifact_path")) == str(art.path) and d.get("system") is not None
        ]

        allowed_kinds = {str(getattr(ic, "kind", "")).strip().lower() for ic in getattr(c, "defined_id", []) or []}
        for d in defs_in_file:
            k = str(d.get("id_kind") or "").lower()
            if not k:
                continue
            if allowed_kinds and k not in allowed_kinds:
                errors.append(error(
                    "constraints",
                    "ID kind not allowed by constraints",
                    path=art.path,
                    line=int(d.get("line", 1) or 1),
                    artifact_kind=ak,
                    id_kind=k,
                    id=str(d.get("id")),
                ))

        for ic in getattr(c, "defined_id", []) or []:
            k = str(getattr(ic, "kind", "")).strip().lower()
            is_required = bool(getattr(ic, "required", True))
            defs_of_kind = [d for d in defs_in_file if str(d.get("id_kind") or "").lower() == k]
            if is_required and k and not defs_of_kind:
                errors.append(error(
                    "constraints",
                    "Required ID kind missing in artifact",
                    path=art.path,
                    line=1,
                    artifact_kind=ak,
                    id_kind=k,
                    id_kind_name=str(getattr(ic, "name", "") or "").strip() or None,
                    id_kind_description=str(getattr(ic, "description", "") or "").strip() or None,
                    id_kind_template=str(getattr(ic, "template", "") or "").strip() or None,
                ))
                continue

            allowed_headings = set([h.strip() for h in (getattr(ic, "headings", None) or []) if isinstance(h, str) and h.strip()])
            if allowed_headings and defs_of_kind:
                allowed_sorted = sorted(allowed_headings)
                allowed_info = headings_info_for_kind(ak, allowed_sorted)
                for d in defs_of_kind:
                    active = d.get("headings") or []
                    if any(h in allowed_headings for h in active):
                        continue
                    errors.append(error(
                        "constraints",
                        "ID definition not under required headings",
                        path=art.path,
                        line=int(d.get("line", 1) or 1),
                        artifact_kind=ak,
                        id_kind=k,
                        id=str(d.get("id")),
                        headings=allowed_sorted,
                        headings_info=allowed_info,
                        found_headings=active,
                        id_kind_name=str(getattr(ic, "name", "") or "").strip() or None,
                        id_kind_description=str(getattr(ic, "description", "") or "").strip() or None,
                        id_kind_template=str(getattr(ic, "template", "") or "").strip() or None,
                    ))

    # Reference coverage rules
    for ak, c in constraints_by_artifact_kind.items():
        for ic in getattr(c, "defined_id", []) or []:
            id_kind = str(getattr(ic, "kind", "")).strip().lower()
            id_kind_name = str(getattr(ic, "name", "") or "").strip() or None
            id_kind_description = str(getattr(ic, "description", "") or "").strip() or None
            id_kind_template = str(getattr(ic, "template", "") or "").strip() or None
            refs_rules = getattr(ic, "references", None) or {}
            if not isinstance(refs_rules, dict):
                continue

            for did, drows in defs_by_id.items():
                for drow in drows:
                    if str(drow.get("artifact_kind")) != ak:
                        continue
                    if str(drow.get("id_kind") or "").lower() != id_kind:
                        continue
                    system = drow.get("system")
                    if system is None:
                        continue

                    system_present_kinds = present_kinds_by_system.get(system, set())
                    system_refs_by_kind = refs_by_system_kind.get(system, {})

                    for target_kind, rule in refs_rules.items():
                        tk = str(target_kind).strip().upper()
                        cov = str(getattr(rule, "coverage", "optional")).strip().lower()
                        def_has_task = bool(drow.get("has_task", False))
                        def_checked = bool(drow.get("checked", False))
                        effective_cov = cov
                        task_rule = str(getattr(rule, "task", "allowed") or "allowed").strip().lower()
                        prio_rule = str(getattr(rule, "priority", "allowed") or "allowed").strip().lower()
                        allowed_headings = set([h.strip() for h in (getattr(rule, "headings", None) or []) if isinstance(h, str) and h.strip()])
                        allowed_headings_sorted = sorted(allowed_headings)
                        allowed_headings_info = headings_info_for_kind(tk, allowed_headings_sorted)

                        refs_in_kind = [r for r in system_refs_by_kind.get(tk, []) if str(r.get("id")) == did]

                        if effective_cov == "required":
                            if def_has_task and (not def_checked):
                                continue
                            if tk not in system_present_kinds:
                                warnings.append(error(
                                    "constraints",
                                    "Required reference target kind not in scope",
                                    path=drow.get("artifact_path"),
                                    line=int(drow.get("line", 1) or 1),
                                    id=did,
                                    artifact_kind=ak,
                                    target_kind=tk,
                                ))
                                continue
                            if not refs_in_kind:
                                errors.append(error(
                                    "constraints",
                                    "ID not referenced from required artifact kind",
                                    path=drow.get("artifact_path"),
                                    line=int(drow.get("line", 1) or 1),
                                    id=did,
                                    artifact_kind=ak,
                                    target_kind=tk,
                                    id_kind=id_kind,
                                    id_kind_name=id_kind_name,
                                    id_kind_description=id_kind_description,
                                    id_kind_template=id_kind_template,
                                ))
                                continue

                            if allowed_headings:
                                if not any(
                                    any(h in allowed_headings for h in (rr.get("headings") or []))
                                    for rr in refs_in_kind
                                ):
                                    first = refs_in_kind[0]
                                    errors.append(error(
                                        "constraints",
                                        "ID reference not under required headings",
                                        path=first.get("artifact_path"),
                                        line=int(first.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        headings=allowed_headings_sorted,
                                        headings_info=allowed_headings_info,
                                        found_headings=first.get("headings") or [],
                                        id_kind=id_kind,
                                        id_kind_name=id_kind_name,
                                        id_kind_description=id_kind_description,
                                        id_kind_template=id_kind_template,
                                    ))

                            if def_has_task:
                                refs_with_task = [rr for rr in refs_in_kind if bool(rr.get("has_task", False))]
                                if not refs_with_task:
                                    first = refs_in_kind[0]
                                    errors.append(error(
                                        "constraints",
                                        "ID reference missing required task checkbox for task-tracked definition",
                                        path=first.get("artifact_path"),
                                        line=int(first.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        id_kind=id_kind,
                                        id_kind_name=id_kind_name,
                                        id_kind_description=id_kind_description,
                                        id_kind_template=id_kind_template,
                                    ))

                        if effective_cov == "prohibited" and refs_in_kind:
                            first = refs_in_kind[0]
                            errors.append(error(
                                "constraints",
                                "ID referenced from prohibited artifact kind",
                                path=first.get("artifact_path"),
                                line=int(first.get("line", 1) or 1),
                                id=did,
                                artifact_kind=ak,
                                target_kind=tk,
                                id_kind=id_kind,
                                id_kind_name=id_kind_name,
                                id_kind_description=id_kind_description,
                                id_kind_template=id_kind_template,
                            ))
                            continue

                        if refs_in_kind:
                            if task_rule == "required":
                                for rr in refs_in_kind:
                                    if bool(rr.get("has_task", False)):
                                        continue
                                    errors.append(error(
                                        "constraints",
                                        "ID reference missing required task checkbox",
                                        path=rr.get("artifact_path"),
                                        line=int(rr.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        id_kind=id_kind,
                                        id_kind_name=id_kind_name,
                                        id_kind_description=id_kind_description,
                                        id_kind_template=id_kind_template,
                                    ))
                                    break
                            elif task_rule == "prohibited":
                                for rr in refs_in_kind:
                                    if not bool(rr.get("has_task", False)):
                                        continue
                                    errors.append(error(
                                        "constraints",
                                        "ID reference has prohibited task checkbox",
                                        path=rr.get("artifact_path"),
                                        line=int(rr.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        id_kind=id_kind,
                                        id_kind_name=id_kind_name,
                                        id_kind_description=id_kind_description,
                                        id_kind_template=id_kind_template,
                                    ))
                                    break

                            if prio_rule == "required":
                                for rr in refs_in_kind:
                                    if bool(rr.get("has_priority", False)):
                                        continue
                                    errors.append(error(
                                        "constraints",
                                        "ID reference missing required priority",
                                        path=rr.get("artifact_path"),
                                        line=int(rr.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        id_kind=id_kind,
                                        id_kind_name=id_kind_name,
                                        id_kind_description=id_kind_description,
                                        id_kind_template=id_kind_template,
                                    ))
                                    break
                            elif prio_rule == "prohibited":
                                for rr in refs_in_kind:
                                    if not bool(rr.get("has_priority", False)):
                                        continue
                                    errors.append(error(
                                        "constraints",
                                        "ID reference has prohibited priority",
                                        path=rr.get("artifact_path"),
                                        line=int(rr.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        id_kind=id_kind,
                                        id_kind_name=id_kind_name,
                                        id_kind_description=id_kind_description,
                                        id_kind_template=id_kind_template,
                                    ))
                                    break

    return {"errors": errors, "warnings": warnings}


def _parse_examples(v: object) -> Tuple[Optional[List[object]], Optional[str]]:
    if v is None:
        return None, None
    if not isinstance(v, list):
        return None, "Constraint field 'examples' must be a list"
    return list(v), None


def _parse_reference_rule(obj: object) -> Tuple[Optional[ReferenceRule], Optional[str]]:
    if not isinstance(obj, dict):
        return None, "Reference rule must be an object"
    coverage = obj.get("coverage")
    if not isinstance(coverage, str) or coverage.strip() not in {"required", "optional", "prohibited"}:
        return None, "Reference rule field 'coverage' must be one of: required, optional, prohibited"

    task, task_err = _parse_tri_state(obj.get("task"), "references.task")
    if task_err:
        return None, task_err

    priority, pr_err = _parse_tri_state(obj.get("priority"), "references.priority")
    if pr_err:
        return None, pr_err

    headings_raw = obj.get("headings")
    headings: Optional[List[str]] = None
    if headings_raw is not None:
        if not isinstance(headings_raw, list) or any(not isinstance(h, str) for h in headings_raw):
            return None, "Reference rule field 'headings' must be list[str]"
        headings = [h for h in (x.strip() for x in headings_raw) if h]

    return ReferenceRule(
        coverage=coverage.strip(),
        task=task,
        priority=priority,
        headings=headings,
    ), None


def _parse_heading_constraint(obj: object, *, pointer: Optional[str] = None) -> Tuple[Optional[HeadingConstraint], Optional[str]]:
    if not isinstance(obj, dict):
        return None, "Heading constraint must be an object"

    hid = obj.get("id")
    if hid is not None and not isinstance(hid, str):
        return None, "Heading constraint field 'id' must be string"
    hid_s = hid.strip() if isinstance(hid, str) and hid.strip() else None

    prev = obj.get("prev")
    if prev is not None and not isinstance(prev, str):
        return None, "Heading constraint field 'prev' must be string"
    prev_s = prev.strip() if isinstance(prev, str) and prev.strip() else None

    nxt = obj.get("next")
    if nxt is not None and not isinstance(nxt, str):
        return None, "Heading constraint field 'next' must be string"
    next_s = nxt.strip() if isinstance(nxt, str) and nxt.strip() else None

    level = obj.get("level")
    if not isinstance(level, int) or not (1 <= level <= 6):
        return None, "Heading constraint field 'level' must be integer 1-6"

    pattern = obj.get("pattern")
    if pattern is not None and not isinstance(pattern, str):
        return None, "Heading constraint field 'pattern' must be string"

    description = obj.get("description")
    if description is not None and not isinstance(description, str):
        return None, "Heading constraint field 'description' must be string"
    desc_s = description.strip() if isinstance(description, str) and description.strip() else None

    required = obj.get("required")
    if required is None:
        required_bool = True
    elif isinstance(required, bool):
        required_bool = required
    else:
        return None, "Heading constraint field 'required' must be boolean"

    multiple = obj.get("multiple")
    if multiple is None:
        multiple_s = "allow"
    elif isinstance(multiple, str) and multiple.strip() in {"allow", "prohibited", "required"}:
        multiple_s = multiple.strip()
    else:
        return None, "Heading constraint field 'multiple' must be one of: allow, prohibited, required"

    numbered = obj.get("numbered")
    if numbered is None:
        numbered_s = "allow"
    elif isinstance(numbered, str) and numbered.strip() in {"allow", "prohibited", "required"}:
        numbered_s = numbered.strip()
    else:
        return None, "Heading constraint field 'numbered' must be one of: allow, prohibited, required"

    # Validate regex early for better errors.
    if pattern is not None and pattern.strip():
        try:
            re.compile(pattern)
        except re.error as e:
            return None, f"Heading constraint 'pattern' invalid regex: {e}"

    return HeadingConstraint(
        id=hid_s,
        level=int(level),
        pattern=(pattern.strip() if isinstance(pattern, str) and pattern.strip() else None),
        description=desc_s,
        required=bool(required_bool),
        multiple=multiple_s,
        numbered=numbered_s,
        prev=prev_s,
        next=next_s,
        pointer=(pointer.strip() if isinstance(pointer, str) and pointer.strip() else None),
    ), None


def _slugify_heading_constraint_id(v: str) -> str:
    s = str(v or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def _parse_references(v: object) -> Tuple[Optional[Dict[str, ReferenceRule]], Optional[str]]:
    if v is None:
        return None, None
    if not isinstance(v, dict):
        return None, "Constraint field 'references' must be an object mapping artifact kinds to rules"
    out: Dict[str, ReferenceRule] = {}
    for k, raw in v.items():
        if not isinstance(k, str) or not k.strip():
            return None, "Constraint field 'references' has non-string artifact kind key"
        rule, err = _parse_reference_rule(raw)
        if err:
            return None, f"references[{k}]: {err}"
        if rule is not None:
            out[k.strip().upper()] = rule
    return out, None


def _parse_id_constraint(obj: object) -> Tuple[Optional[IdConstraint], Optional[str]]:
    if not isinstance(obj, dict):
        return None, "Constraint entry must be an object"
    kind = obj.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        return None, "Constraint entry missing required 'kind'"

    required = obj.get("required")
    if required is None:
        required_bool = True
    elif isinstance(required, bool):
        required_bool = required
    else:
        return None, "Constraint field 'required' must be boolean"

    name = obj.get("name")
    if name is not None and not isinstance(name, str):
        return None, "Constraint field 'name' must be string"

    description = obj.get("description")
    if description is not None and not isinstance(description, str):
        return None, "Constraint field 'description' must be string"

    template = obj.get("template")
    if template is not None and not isinstance(template, str):
        return None, "Constraint field 'template' must be string"
    template_s = template.strip() if isinstance(template, str) and template.strip() else None

    examples, ex_err = _parse_examples(obj.get("examples"))
    if ex_err:
        return None, ex_err

    task, task_err = _parse_tri_state(obj.get("task"), "task")
    if task_err:
        return None, task_err

    priority, pr_err = _parse_tri_state(obj.get("priority"), "priority")
    if pr_err:
        return None, pr_err

    to_code = obj.get("to_code")
    if to_code is not None and not isinstance(to_code, bool):
        return None, "Constraint field 'to_code' must be boolean"

    headings_raw = obj.get("headings")
    headings: Optional[List[str]] = None
    if headings_raw is not None:
        if not isinstance(headings_raw, list) or any(not isinstance(h, str) for h in headings_raw):
            return None, "Constraint field 'headings' must be list[str]"
        headings = [h for h in (x.strip() for x in headings_raw) if h]

    # New schema: embedded references map.
    references, ref_err = _parse_references(obj.get("references"))
    if ref_err:
        return None, ref_err

    return (
        IdConstraint(
            kind=kind.strip(),
            required=required_bool,
            name=name,
            description=description,
            template=template_s,
            examples=examples,
            task=task,
            priority=priority,
            to_code=to_code,
            headings=headings,
            references=references,
        ),
        None,
    )


def parse_kit_constraints(data: object) -> Tuple[Optional[KitConstraints], List[str]]:
    if data is None:
        return None, []
    if not isinstance(data, dict):
        return None, ["constraints.json root must be an object mapping artifact kinds to constraints"]

    out: Dict[str, ArtifactKindConstraints] = {}
    errors: List[str] = []

    for kind, raw in data.items():
        # Allow optional JSON Schema metadata keys.
        # Example: {"$schema": "../../schemas/kit-constraints.schema.json", "PRD": {...}}
        if isinstance(kind, str) and kind.strip().startswith("$"):
            continue
        if not isinstance(kind, str) or not kind.strip():
            errors.append("constraints.json has non-string kind key")
            continue
        if not isinstance(raw, dict):
            errors.append(f"constraints for {kind} must be an object")
            continue

        has_identifiers = "identifiers" in raw
        if not has_identifiers:
            errors.append(f"constraints for {kind} must include 'identifiers'")
            continue

        name = raw.get("name")
        if name is not None and not isinstance(name, str):
            errors.append(f"constraints for {kind} field 'name' must be string")
            continue

        description = raw.get("description")
        if description is not None and not isinstance(description, str):
            errors.append(f"constraints for {kind} field 'description' must be string")
            continue

        defined_id: List[IdConstraint] = []
        seen_defined: set[str] = set()

        headings: Optional[List[HeadingConstraint]] = None
        headings_raw = raw.get("headings")
        if headings_raw is not None:
            if not isinstance(headings_raw, list):
                errors.append(f"constraints for {kind} field 'headings' must be a list")
                continue
            parsed_headings: List[HeadingConstraint] = []
            for idx, hraw in enumerate(headings_raw):
                ptr = f"/{kind.strip().upper()}/headings/{idx}"
                hc, herr = _parse_heading_constraint(hraw, pointer=ptr)
                if herr:
                    errors.append(f"constraints for {kind} headings[{idx}]: {herr}")
                    continue
                if hc is not None:
                    parsed_headings.append(hc)

            # Normalize + auto-generate stable ids, and validate prev/next references.
            seen_ids: set[str] = set()
            out_headings: List[HeadingConstraint] = []
            for hidx, hc in enumerate(parsed_headings):
                eff_id = str(getattr(hc, "id", "") or "").strip()
                if not eff_id:
                    base = ""
                    if getattr(hc, "pattern", None):
                        base = _slugify_heading_constraint_id(str(hc.pattern))
                    if not base:
                        base = f"level-{int(hc.level)}-{hidx}"
                    eff_id = f"h{int(hc.level)}-{base}"
                eff_id = eff_id.strip()

                candidate = eff_id
                n = 2
                while candidate.lower() in seen_ids:
                    candidate = f"{eff_id}-{n}"
                    n += 1
                eff_id = candidate
                seen_ids.add(eff_id.lower())
                out_headings.append(replace(hc, id=eff_id))

            by_id: Dict[str, HeadingConstraint] = {str(hc.id): hc for hc in out_headings if getattr(hc, "id", None)}

            normalized_headings: List[HeadingConstraint] = []
            for hidx, hc in enumerate(out_headings):
                prev_id = getattr(hc, "prev", None)
                next_id = getattr(hc, "next", None)

                if not prev_id and hidx > 0:
                    prev_id = str(out_headings[hidx - 1].id)
                if not next_id and hidx + 1 < len(out_headings):
                    next_id = str(out_headings[hidx + 1].id)

                if prev_id and prev_id not in by_id:
                    errors.append(f"constraints for {kind} headings[{hidx}]: prev references unknown heading id '{prev_id}'")
                if next_id and next_id not in by_id:
                    errors.append(f"constraints for {kind} headings[{hidx}]: next references unknown heading id '{next_id}'")

                normalized_headings.append(replace(hc, prev=prev_id, next=next_id))

            headings = normalized_headings

        identifiers_raw = raw.get("identifiers")
        if not isinstance(identifiers_raw, dict):
            errors.append(f"constraints for {kind} field 'identifiers' must be an object")
            continue
        for kkind, entry in identifiers_raw.items():
            if not isinstance(kkind, str) or not kkind.strip():
                errors.append(f"constraints for {kind} field 'identifiers' has non-string kind key")
                continue
            if not isinstance(entry, dict):
                errors.append(f"constraints for {kind} identifiers[{kkind}]: Constraint entry must be an object")
                continue

            # Infer kind from map key when omitted.
            inferred_kind = kkind.strip()
            if "kind" in entry:
                vv = entry.get("kind")
                if not isinstance(vv, str) or not vv.strip():
                    errors.append(f"constraints for {kind} identifiers[{kkind}]: Constraint entry missing required 'kind'")
                    continue
                if vv.strip().lower() != inferred_kind.lower():
                    errors.append(f"constraints for {kind} identifiers[{kkind}]: Constraint entry kind does not match identifiers key")
                    continue
                normalized = dict(entry)
            else:
                normalized = dict(entry)
                normalized["kind"] = inferred_kind

            c, e = _parse_id_constraint(normalized)
            if e:
                errors.append(f"constraints for {kind} identifiers[{kkind}]: {e}")
                continue
            if c is not None:
                kk = c.kind.strip().lower()
                if kk in seen_defined:
                    errors.append(f"constraints for {kind} identifiers has duplicate kind '{c.kind.strip()}'")
                    continue
                seen_defined.add(kk)
                defined_id.append(c)

        out[kind.strip().upper()] = ArtifactKindConstraints(
            name=name,
            description=description,
            defined_id=defined_id,
            headings=headings,
        )

    if errors:
        return None, errors
    return KitConstraints(by_kind=out), []


def load_constraints_json(kit_root: Path) -> Tuple[Optional[KitConstraints], List[str]]:
    path = (kit_root / "constraints.json").resolve()
    if not path.is_file():
        return None, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, [f"Failed to parse constraints.json: {e}"]

    constraints, errs = parse_kit_constraints(data)
    if errs:
        return None, errs
    return constraints, []


__all__ = [
    "ReferenceRule",
    "HeadingConstraint",
    "IdConstraint",
    "ArtifactKindConstraints",
    "KitConstraints",
    "ArtifactRecord",
    "ParsedCypilotId",
    "cross_validate_artifacts",
    "error",
    "load_constraints_json",
    "parse_cpt",
    "parse_kit_constraints",
    "validate_artifact_file",
]


_HEADING_LINE_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_HEADING_NUMBER_PREFIX_RE = re.compile(r"^(?P<prefix>\d+(?:\.\d+)*)(?:\.)?\s+(?P<title>.+)$")


def _scan_headings(path: Path) -> List[Dict[str, object]]:
    from .document import read_text_safe

    lines = read_text_safe(path)
    if lines is None:
        return []

    out: List[Dict[str, object]] = []
    in_fence = False
    for idx0, raw in enumerate(lines):
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING_LINE_RE.match(raw)
        if not m:
            continue
        level = len(m.group(1))
        raw_title = str(m.group(2) or "").strip()
        numbered = False
        title_text = raw_title
        number_prefix: Optional[str] = None
        number_parts: Optional[List[int]] = None
        mp = _HEADING_NUMBER_PREFIX_RE.match(raw_title)
        if mp:
            numbered = True
            number_prefix = str(mp.group("prefix") or "").strip() or None
            if number_prefix:
                try:
                    number_parts = [int(x) for x in number_prefix.split(".") if x.strip()]
                except ValueError:
                    number_parts = None
            title_text = str(mp.group("title") or "").strip()
        out.append({
            "line": idx0 + 1,
            "level": level,
            "raw_title": raw_title,
            "title_text": title_text,
            "numbered": numbered,
            "number_prefix": number_prefix,
            "number_parts": number_parts,
        })
    return out


def validate_headings_contract(
    *,
    path: Path,
    constraints: ArtifactKindConstraints,
    registered_systems: Optional[Iterable[str]],
    artifact_kind: str,
    constraints_path: Optional[Path] = None,
    kit_id: Optional[str] = None,
) -> Dict[str, List[Dict[str, object]]]:
    """Validate artifact outline against constraints.headings.

    Current behavior is intentionally conservative:
    - Requires that each required heading constraint matches at least once.
    - Enforces multiple/prohibited/required counts for each constraint.
    - Enforces numbered required/prohibited for matched headings.
    """
    from .document import scan_cpt_ids

    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    heading_constraints = getattr(constraints, "headings", None) or []
    if not heading_constraints:
        return {"errors": errors, "warnings": warnings}

    def _hc_label(hc: HeadingConstraint) -> str:
        hid = str(getattr(hc, "id", "") or "").strip()
        pat = str(getattr(hc, "pattern", "") or "").strip()
        if pat:
            return f"{hid}({pat})" if hid else pat
        return hid or f"level={int(hc.level)}"

    def _hc_info(hc: Optional[HeadingConstraint]) -> Optional[Dict[str, object]]:
        if hc is None:
            return None
        return {
            "id": getattr(hc, "id", None),
            "level": int(getattr(hc, "level", 0) or 0),
            "pattern": getattr(hc, "pattern", None),
            "description": getattr(hc, "description", None),
            "pointer": getattr(hc, "pointer", None),
        }

    by_id: Dict[str, HeadingConstraint] = {}
    for hc in heading_constraints:
        hid = str(getattr(hc, "id", "") or "").strip()
        if hid and hid not in by_id:
            by_id[hid] = hc

    def _source_fields(hc: HeadingConstraint, idx: int) -> Dict[str, object]:
        ptr = getattr(hc, "pointer", None) or f"/<unknown-kind>/headings/{idx}"
        return {
            "constraints_path": str(constraints_path) if constraints_path is not None else None,
            "constraints_pointer": ptr,
            "kit": kit_id,
            "heading_id": getattr(hc, "id", None),
            "heading_description": getattr(hc, "description", None),
        }

    headings = _scan_headings(path)

    def _check_numbering_sequence() -> None:
        # If the document uses numbered headings, enforce that sibling sections under the same
        # numeric parent progress consecutively (e.g., 3.6 -> 3.7, not 3.8).
        last_child_by_key: Dict[Tuple[int, Tuple[Tuple[int, ...], int]], int] = {}
        last_prefix_by_key: Dict[Tuple[int, Tuple[Tuple[int, ...], int]], str] = {}

        for h in headings:
            parts = h.get("number_parts")
            if not parts:
                continue
            if not isinstance(parts, list) or not all(isinstance(x, int) for x in parts):
                continue

            # IMPORTANT: Do not mix numbering sequences across different Markdown heading levels.
            # Example: a template may have:
            # - level-2 headings: "## 1. Overview", "## 2. Entries"
            # - level-3 headings: "### 1. Feature A", "### 2. Feature B"
            # Both use numeric prefixes, but they are independent sequences.
            md_level = int(h.get("level", 0) or 0)

            parent = tuple(parts[:-1])
            depth = len(parts)
            child = int(parts[-1])
            key = (md_level, (parent, depth))

            prefix = str(h.get("number_prefix") or "").strip()
            if not prefix:
                prefix = ".".join(str(x) for x in parts)

            if key in last_child_by_key:
                expected = int(last_child_by_key[key]) + 1
                if child != expected:
                    expected_prefix = ".".join([*(str(x) for x in parent), str(expected)]) if parent else str(expected)
                    errors.append(error(
                        "structure",
                        "Heading numbering is not consecutive",
                        path=path,
                        line=int(h.get("line", 1) or 1),
                        artifact_kind=str(artifact_kind).strip().upper(),
                        found_prefix=prefix,
                        expected_prefix=expected_prefix,
                        previous_prefix=last_prefix_by_key.get(key),
                    ))

            last_child_by_key[key] = child
            last_prefix_by_key[key] = prefix

    _check_numbering_sequence()

    def _is_regex_pattern(pat: str) -> bool:
        return any(ch in pat for ch in ".^$*+?{}[]\\|()")

    def _matches(h: Dict[str, object], hc: HeadingConstraint) -> bool:
        if int(h.get("level", 0)) != int(hc.level):
            return False
        pat = getattr(hc, "pattern", None)
        if not pat:
            return True
        pat_s = str(pat).strip()
        title = str(h.get("title_text") or "").strip()
        if not _is_regex_pattern(pat_s):
            return pat_s.casefold() == title.casefold()
        try:
            return re.search(pat_s, title, flags=re.IGNORECASE) is not None
        except re.error:
            return False

    # Prepare matches for each constraint (in order) using hierarchical scope.
    cursor = 0
    matched_by_idx: Dict[int, List[Dict[str, object]]] = {}
    last_match_idx_by_level: Dict[int, int] = {}

    def _scope_end_for_parent(parent_idx: int, parent_level: int) -> int:
        k = parent_idx + 1
        while k < len(headings):
            if int(headings[k].get("level", 0) or 0) <= parent_level:
                return k
            k += 1
        return len(headings)

    for idx, hc in enumerate(heading_constraints):
        matches: List[Dict[str, object]] = []

        hc_level = int(getattr(hc, "level", 0) or 0)
        scope_start = cursor
        scope_end = len(headings)

        # Restrict search to the active parent section (nearest previously matched lower-level constraint).
        parent_level: Optional[int] = None
        parent_idx: Optional[int] = None
        for pl in range(hc_level - 1, 0, -1):
            if pl in last_match_idx_by_level:
                parent_level = pl
                parent_idx = last_match_idx_by_level[pl]
                break
        if parent_level is not None and parent_idx is not None:
            scope_start = max(scope_start, parent_idx + 1)
            scope_end = _scope_end_for_parent(parent_idx, parent_level)

        # Find first match within scope
        j = scope_start
        while j < scope_end and not _matches(headings[j], hc):
            j += 1

        if j >= scope_end:
            if hc.required:
                hc_desc = str(getattr(hc, "description", "") or "").strip()
                prev_id = getattr(hc, "prev", None) or (heading_constraints[idx - 1].id if idx > 0 else None)
                next_id = getattr(hc, "next", None) or (heading_constraints[idx + 1].id if idx + 1 < len(heading_constraints) else None)
                after_hc = by_id.get(str(prev_id)) if prev_id else None
                before_hc = by_id.get(str(next_id)) if next_id else None
                between = []
                if after_hc is not None:
                    between.append(f"after '{_hc_label(after_hc)}'")
                if before_hc is not None:
                    between.append(f"before '{_hc_label(before_hc)}'")
                between_s = (" (expected " + " and ".join(between) + ")") if between else ""
                desc_s = (f" ({hc_desc})" if hc_desc else "")
                errors.append(error(
                    "constraints",
                    f"Required heading missing in artifact{between_s}{desc_s}",
                    path=path,
                    line=1,
                    artifact_kind=str(artifact_kind).strip().upper(),
                    heading_level=int(hc.level),
                    heading_pattern=hc.pattern,
                    expected_after=_hc_info(after_hc),
                    expected_before=_hc_info(before_hc),
                    **_source_fields(hc, idx),
                ))
            continue

        # Always include the first match
        matches.append(headings[j])

        # Consume further matches for allow/required, but only within the same scope
        if hc.multiple in {"allow", "required"}:
            k = j + 1
            while k < scope_end and _matches(headings[k], hc):
                matches.append(headings[k])
                k += 1
            cursor = k
            last_idx = k - 1
        else:
            cursor = j + 1
            last_idx = j

        # Update hierarchy tracking
        last_match_idx_by_level[hc_level] = last_idx
        for lvl in list(last_match_idx_by_level.keys()):
            if lvl > hc_level:
                del last_match_idx_by_level[lvl]

        matched_by_idx[idx] = matches

        # multiple enforcement
        if hc.multiple == "prohibited" and len(matches) > 1:
            hc_desc = str(getattr(hc, "description", "") or "").strip()
            desc_s = (f" ({hc_desc})" if hc_desc else "")
            errors.append(error(
                "constraints",
                f"Heading constraint prohibits multiple occurrences{desc_s}",
                path=path,
                line=int(matches[1].get("line", 1) or 1),
                artifact_kind=str(artifact_kind).strip().upper(),
                heading_level=int(hc.level),
                heading_pattern=hc.pattern,
                **_source_fields(hc, idx),
            ))
        if hc.multiple == "required" and len(matches) < 2:
            hc_desc = str(getattr(hc, "description", "") or "").strip()
            desc_s = (f" ({hc_desc})" if hc_desc else "")
            errors.append(error(
                "constraints",
                f"Heading constraint requires multiple occurrences{desc_s}",
                path=path,
                line=int(matches[0].get("line", 1) or 1),
                artifact_kind=str(artifact_kind).strip().upper(),
                heading_level=int(hc.level),
                heading_pattern=hc.pattern,
                **_source_fields(hc, idx),
            ))

        # numbered enforcement
        if hc.numbered in {"required", "prohibited"}:
            want_numbered = hc.numbered == "required"
            for mh in matches:
                is_numbered = bool(mh.get("numbered", False))
                if is_numbered == want_numbered:
                    continue
                hc_desc = str(getattr(hc, "description", "") or "").strip()
                desc_s = (f" ({hc_desc})" if hc_desc else "")
                errors.append(error(
                    "constraints",
                    f"Heading numbering does not match constraint{desc_s}",
                    path=path,
                    line=int(mh.get("line", 1) or 1),
                    artifact_kind=str(artifact_kind).strip().upper(),
                    heading_level=int(hc.level),
                    heading_pattern=hc.pattern,
                    numbered=hc.numbered,
                    **_source_fields(hc, idx),
                ))

    return {"errors": errors, "warnings": warnings}
