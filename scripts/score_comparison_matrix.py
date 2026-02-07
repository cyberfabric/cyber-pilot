import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


_SYMBOLS: Dict[str, str] = {
    "native": "✅",
    "supported": "⚠️",
    "emerging": "🚀",
    "out": "❌",
}


def _extract_matrix_table_lines(doc_text: str) -> List[str]:
    m = re.search(
        r"## Cross-capability matrix\n.*?\n\| Capability \|.*?\n(.*?)\n\n### Quantitative scoring analysis",
        doc_text,
        flags=re.S,
    )
    if not m:
        raise ValueError("Failed to locate cross-capability matrix block")

    return m.group(0).splitlines()


def _parse_table(
    lines: List[str],
) -> Tuple[List[str], List[List[str]]]:
    header_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.startswith("| Capability |"):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("Failed to locate matrix header row")

    headers = [h.strip() for h in lines[header_idx].strip("|").split("|")]

    rows: List[List[str]] = []
    for line in lines[header_idx + 2 :]:
        if not line.startswith("|"):
            break
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) != len(headers):
            continue
        rows.append(cols)

    return headers, rows


def _classify_cell(cell: str) -> str:
    for key, sym in _SYMBOLS.items():
        if sym in cell:
            return key
    return "info"


def _strip_bold(md: str) -> str:
    return md.replace("**", "")


def _compute(
    headers: List[str],
    rows: List[List[str]],
) -> Tuple[List[str], Dict[str, Dict[str, List[str]]], List[str]]:
    frameworks = headers[1:]

    caps: Dict[str, Dict[str, List[str]]] = {
        fw: {"native": [], "supported": [], "emerging": [], "out": [], "info": []}
        for fw in frameworks
    }

    informational_rows: List[str] = []

    for row in rows:
        cap = row[0]
        classes = []
        for fw, cell in zip(frameworks, row[1:]):
            cls = _classify_cell(cell)
            caps[fw][cls].append(cap)
            classes.append(cls)

        if all(cls == "info" for cls in classes):
            informational_rows.append(cap)

    return frameworks, caps, informational_rows


def _score_for(caps_for_fw: Dict[str, List[str]]) -> float:
    n = len(caps_for_fw["native"])
    s = len(caps_for_fw["supported"])
    e = len(caps_for_fw["emerging"])
    return 3.0 * n + 1.0 * s + 0.5 * e


def _render_markdown(
    frameworks: List[str],
    caps: Dict[str, Dict[str, List[str]]],
    informational_rows: List[str],
) -> str:
    lines: List[str] = []
    lines.append("Informational rows (excluded from scoring):")
    for cap in informational_rows:
        lines.append(f"- {_strip_bold(cap)}")

    lines.append("")
    lines.append("Scoring results (computed from matrix):")
    lines.append("")
    lines.append(
        "| Framework | Native (×3) | Supported (×1) | Out of scope (×0) | Emerging (×0.5) | Total |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")

    for fw in frameworks:
        c = caps[fw]
        n = len(c["native"])
        s = len(c["supported"])
        o = len(c["out"])
        e = len(c["emerging"])
        total = _score_for(c)

        lines.append(
            f"| {fw} | {n} | {s} | {o} | {e} | {total:g} |"
        )

    lines.append("")
    lines.append("Breakdown:")
    lines.append("")

    for fw in frameworks:
        c = caps[fw]
        total = _score_for(c)
        lines.append(f"## {fw} ({total:g} points)")

        def _list(label: str, items: List[str]) -> None:
            lines.append(f"- {label}:")
            for cap in items:
                lines.append(f"  - {_strip_bold(cap)}")

        _list("Native", c["native"])
        _list("Supported", c["supported"])
        if c["emerging"]:
            _list("Emerging", c["emerging"])
        _list("Out of scope", c["out"])
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _find_project_root(start: Path) -> Path:
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent

    for parent in [cur, *cur.parents]:
        if (parent / ".cypilot-config.json").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    return cur


def _resolve_default_comparison_file(project_root: Path) -> Path:
    preferred = project_root / "SDD_COMPARISON.md"
    if preferred.exists():
        return preferred

    matches = sorted(project_root.glob("*_COMPARISON.md"))
    if matches:
        return matches[0]

    raise ValueError(f"No *_COMPARISON.md found under project root: {project_root}")


def main() -> int:
    default_root = _find_project_root(Path(__file__).resolve())

    p = argparse.ArgumentParser(
        prog="score_comparison_matrix",
        description="Compute comparison scoring from cross-capability matrix",
    )
    p.add_argument(
        "--root",
        default=str(default_root),
        help="Project root (used to auto-locate comparison file)",
    )
    p.add_argument(
        "--file",
        default=None,
        help="Path to comparison markdown file (absolute or relative)",
    )
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")

    args = p.parse_args()

    project_root = Path(args.root).resolve()
    if args.file is None:
        path = _resolve_default_comparison_file(project_root)
    else:
        candidate = Path(args.file)
        path = candidate if candidate.is_absolute() else (project_root / candidate)

    doc_text = path.read_text(encoding="utf-8")

    table_lines = _extract_matrix_table_lines(doc_text)
    headers, rows = _parse_table(table_lines)
    frameworks, caps, informational_rows = _compute(headers, rows)

    if args.format == "json":
        payload = {
            "frameworks": frameworks,
            "informational_rows": [_strip_bold(x) for x in informational_rows],
            "scores": {
                fw: {
                    "native": len(caps[fw]["native"]),
                    "supported": len(caps[fw]["supported"]),
                    "out": len(caps[fw]["out"]),
                    "emerging": len(caps[fw]["emerging"]),
                    "total": _score_for(caps[fw]),
                }
                for fw in frameworks
            },
            "breakdown": {
                fw: {
                    k: [_strip_bold(x) for x in caps[fw][k]]
                    for k in ["native", "supported", "emerging", "out"]
                }
                for fw in frameworks
            },
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(_render_markdown(frameworks, caps, informational_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
