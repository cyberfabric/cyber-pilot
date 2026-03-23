# Phase 1: New Dataclass Types

Module: `skills/cypilot/scripts/cypilot/utils/manifest.py`

## ComponentEntry (base, frozen dataclass)

| Field       | Type              | Default        |
|-------------|-------------------|----------------|
| id          | str               | (required)     |
| description | str               | ""             |
| prompt_file | str               | ""             |
| source      | str               | ""             |
| agents      | List[str]         | []             |
| append      | Optional[str]     | None           |

## AgentEntry(ComponentEntry) (frozen dataclass)

Inherits all ComponentEntry fields, plus:

| Field            | Type              | Default        |
|------------------|-------------------|----------------|
| mode             | str               | "readwrite"    |
| isolation        | bool              | False          |
| model            | str               | ""             |
| tools            | List[str]         | []             |
| disallowed_tools | List[str]         | []             |
| color            | str               | ""             |
| memory_dir       | str               | ""             |

Constraint: `tools` and `disallowed_tools` are mutually exclusive.

## SkillEntry(ComponentEntry) (frozen dataclass)

Inherits all ComponentEntry fields. No additional fields.

## WorkflowEntry(ComponentEntry) (frozen dataclass)

Inherits all ComponentEntry fields. No additional fields.

## RuleEntry(ComponentEntry) (frozen dataclass)

Inherits all ComponentEntry fields. No additional fields.

## ManifestV2 (frozen dataclass)

| Field      | Type                   | Default |
|------------|------------------------|---------|
| version    | str                    | (required) |
| includes   | List[str]              | []      |
| agents     | List[AgentEntry]       | []      |
| skills     | List[SkillEntry]       | []      |
| workflows  | List[WorkflowEntry]    | []      |
| rules      | List[RuleEntry]        | []      |
| resources  | List[ManifestResource] | []      |

## ManifestLayerState (Enum)

| Value         |
|---------------|
| UNDISCOVERED  |
| LOADED        |
| PARSE_ERROR   |
| INCLUDE_ERROR |

## ManifestLayer (frozen dataclass)

| Field    | Type                      | Default                        |
|----------|---------------------------|--------------------------------|
| scope    | str                       | (required)                     |
| path     | Path                      | (required)                     |
| manifest | Optional[ManifestV2]      | None                           |
| state    | ManifestLayerState        | ManifestLayerState.UNDISCOVERED |

## Function

### parse_manifest_v2(path: Path) -> ManifestV2

Parses `manifest.toml` at the given path. Supports version "2.0" (component sections) and "1.0" (backward compatibility wrapper). Raises `ValueError` on parse errors. Accepts and ignores `[[hooks]]` and `[[permissions]]` sections.
