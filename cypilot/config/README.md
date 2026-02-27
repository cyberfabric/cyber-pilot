# config — User Configuration

This directory contains **user-editable** configuration files.

## Files

- `core.toml` — project settings (system name, slug, kit references)
- `artifacts.toml` — artifacts registry (systems, ignore patterns)
- `AGENTS.md` — custom agent navigation rules (add your own WHEN rules here)
- `SKILL.md` — custom skill extensions (add your own skill instructions here)

## Directories

- `kits/{slug}/blueprints/` — editable copies of kit blueprints.
  Modify these to customize generated artifacts, then run `cpt generate-resources`.

## Tips

- `AGENTS.md` and `SKILL.md` start empty. Add any project-specific rules or
  skill instructions here — they will be picked up alongside the generated ones.
- Changes to blueprints take effect after running `cpt generate-resources`.
