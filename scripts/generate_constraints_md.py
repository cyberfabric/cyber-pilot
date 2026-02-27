"""Generate a Markdown table view of SDLC constraints.

Reads `kits/sdlc/example/constraints.toml` and produces `kits/sdlc/guides/constraints.md`.
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path
from typing import Any


def _md_escape(value: str) -> str:
    return value.replace("|", r"\\|")


def _fmt_bool(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    return str(value)


def _fmt_list(values: Any) -> str:
    if not values:
        return ""
    return ", ".join(map(str, values))


def _fmt_refs(refs: Any) -> str:
    if not refs:
        return ""

    parts: list[str] = []
    for doc, rules in refs.items():
        if not isinstance(rules, dict):
            parts.append(f"{doc}: {rules}")
            continue

        fields: list[str] = []
        for key in ["coverage", "task", "priority"]:
            if key in rules:
                fields.append(f"{key}={rules[key]}")

        if "headings" in rules:
            fields.append("headings=[" + ",".join(rules["headings"]) + "]")

        parts.append(doc + ": " + "; ".join(fields))

    return "<br>".join(parts)


def render_constraints_md(data: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append("# Constraints (cypilot-sdlc)")
    lines.append("")
    lines.append("Source: `kits/sdlc/example/constraints.toml`")
    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("- `required` / `optional`: whether the identifier is required in the artifact")
    lines.append("- `task`: whether a Task checkbox is required/allowed/prohibited")
    lines.append("- `priority`: whether a priority marker is required/allowed/prohibited")
    lines.append("- `to_code`: whether the identifier is expected to be carried into CODE")
    lines.append("- `references`: downstream constraints (coverage + optional headings anchors)")
    lines.append("")
    lines.append("## Contents")
    lines.append("")

    for artifact in data.keys():
        lines.append(f"- [{artifact}](#{artifact.lower()})")

    lines.append("")

    for artifact, spec in data.items():
        lines.append(f"## {artifact}")
        lines.append("")

        name = spec.get("name")
        desc = spec.get("description")
        if name:
            lines.append(f"**Name**: {_md_escape(str(name))}")
        if desc:
            lines.append(f"**Description**: {_md_escape(str(desc))}")
        lines.append("")

        lines.append("### Headings")
        lines.append("")
        lines.append("| id | level | pattern | required | multiple | numbered | description |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")

        for heading in spec.get("headings", []):
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md_escape(str(heading.get("id", ""))),
                        _md_escape(str(heading.get("level", ""))),
                        _md_escape("" if heading.get("pattern") is None else str(heading.get("pattern"))),
                        _md_escape(str(heading.get("required", ""))),
                        _md_escape(str(heading.get("multiple", ""))),
                        _md_escape(str(heading.get("numbered", ""))),
                        _md_escape(str(heading.get("description", ""))),
                    ]
                )
                + " |"
            )

        lines.append("")
        lines.append("### Identifiers")
        lines.append("")
        lines.append(
            "| key | kind | name | required | task | priority | to_code | template | headings | references | examples | description |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")

        identifiers = spec.get("identifiers") or {}
        for key, ident in identifiers.items():
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md_escape(str(key)),
                        _md_escape(str(ident.get("kind", ""))),
                        _md_escape(str(ident.get("name", ""))),
                        _md_escape(str(ident.get("required", ""))),
                        _md_escape(str(ident.get("task", ""))),
                        _md_escape(str(ident.get("priority", ""))),
                        _md_escape(_fmt_bool(ident.get("to_code"))),
                        _md_escape(str(ident.get("template", ""))),
                        _md_escape(_fmt_list(ident.get("headings", []))),
                        _md_escape(_fmt_refs(ident.get("references", {}))),
                        _md_escape(_fmt_list(ident.get("examples", []))),
                        _md_escape(str(ident.get("description", ""))),
                    ]
                )
                + " |"
            )

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate kits/sdlc/guides/constraints.md from constraints.toml")
    parser.add_argument(
        "--input",
        default="kits/sdlc/example/constraints.toml",
        help="Path to constraints.toml (default: kits/sdlc/example/constraints.toml)",
    )
    parser.add_argument(
        "--output",
        default="kits/sdlc/guides/constraints.md",
        help="Path to write constraints.md (default: kits/sdlc/guides/constraints.md)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it exists",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)

    with open(input_path, "rb") as f:
        raw = tomllib.load(f)
    data = raw.get("artifacts", raw)
    markdown = render_constraints_md(data)

    if output_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {output_path} (use --force)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
