"""
Kit Manifest Parser and Validator

Parses and validates ``manifest.toml`` — the declarative kit installation
manifest.  When present in a kit package root, the manifest governs
installation and update: only declared resources are installed.

@cpt-algo:cpt-cypilot-algo-kit-manifest-install:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-resolve-includes:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-merge-components:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-section-appending:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-includes:p1
"""

# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-datamodel
from __future__ import annotations

import re
import string
import tomllib
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ManifestResource:
    """A single resource declared in ``manifest.toml``."""

    id: str
    source: str
    default_path: str
    type: str  # "file" or "directory"
    description: str = ""
    user_modifiable: bool = True


@dataclass(frozen=True)
class Manifest:
    """Parsed representation of a kit ``manifest.toml``."""

    version: str
    root: str
    user_modifiable: bool
    resources: list[ManifestResource] = field(default_factory=list)
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-datamodel


# ---------------------------------------------------------------------------
# Manifest V2 Dataclasses
# @cpt-state:cpt-cypilot-state-project-extensibility-manifest-layer:p1
# @cpt-dod:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-component-entry
@dataclass(frozen=True)
class ComponentEntry:
    """Base class for V2 manifest component entries."""

    id: str
    description: str = ""
    prompt_file: str = ""
    source: str = ""
    agents: List[str] = field(default_factory=list)
    append: Optional[str] = None  # Trusted content appended to generated output; not sanitized
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-component-entry


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-agent-entry
@dataclass(frozen=True)
class AgentEntry(ComponentEntry):
    """Agent component with extended schema fields."""

    mode: str = "readwrite"
    isolation: bool = False
    model: str = ""
    tools: List[str] = field(default_factory=list)
    disallowed_tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    color: str = ""
    memory_dir: str = ""
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-agent-entry


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-skill-entry
@dataclass(frozen=True)
class SkillEntry(ComponentEntry):
    """Skill component entry."""

    pass
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-skill-entry


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-workflow-entry
@dataclass(frozen=True)
class WorkflowEntry(ComponentEntry):
    """Workflow component entry."""

    pass
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-workflow-entry


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-rule-entry
@dataclass(frozen=True)
class RuleEntry(ComponentEntry):
    """Rule component entry."""

    pass
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-rule-entry


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-manifest-v2
@dataclass(frozen=True)
class ManifestV2:
    """Parsed representation of a V2 manifest.toml."""

    version: str
    includes: List[str] = field(default_factory=list)
    agents: List[AgentEntry] = field(default_factory=list)
    skills: List[SkillEntry] = field(default_factory=list)
    workflows: List[WorkflowEntry] = field(default_factory=list)
    rules: List[RuleEntry] = field(default_factory=list)
    resources: List[ManifestResource] = field(default_factory=list)
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-manifest-v2


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-layer-state
class ManifestLayerState(Enum):
    """State of a manifest layer in the discovery state machine."""

    UNDISCOVERED = "UNDISCOVERED"
    LOADED = "LOADED"
    PARSE_ERROR = "PARSE_ERROR"
    INCLUDE_ERROR = "INCLUDE_ERROR"
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-layer-state


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-manifest-layer
@dataclass(frozen=True)
class ManifestLayer:
    """Envelope for a discovered manifest layer."""

    scope: str
    path: Path
    manifest: Optional[ManifestV2] = None
    state: ManifestLayerState = ManifestLayerState.UNDISCOVERED
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-manifest-layer


# ---------------------------------------------------------------------------
# Manifest V2 Parsing
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-component-helpers
_COMPONENT_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-component-helpers


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-v2
def parse_manifest_v2(path: Path) -> ManifestV2:
    """Parse a ``manifest.toml`` file and return a ``ManifestV2``.

    Supports both version ``"2.0"`` (component sections) and ``"1.0"``
    (resources-only, backward compatibility wrapper).

    Raises ``ValueError`` on parse errors with path and details.
    """
    if not path.is_file():
        raise ValueError(f"{path}: manifest.toml not found")

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{path}: TOML parse error: {exc}") from exc

    # Determine version — support both [manifest].version and top-level version
    meta = data.get("manifest", {})
    version = meta.get("version")
    if version is None:
        version = data.get("version")
    if not version:
        raise ValueError(f"{path}: missing [manifest].version")
    version = str(version).strip()

    if version == "1.0":
        return _parse_v1_as_v2(path, data)
    elif version == "2.0":
        return _parse_v2_sections(path, data)
    else:
        raise ValueError(f"{path}: unsupported manifest version '{version}'")
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-v2


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-v1-compat
def _parse_v1_as_v2(_path: Path, data: Dict[str, Any]) -> ManifestV2:
    """Wrap a v1.0 manifest as a ManifestV2 with only resources populated."""
    raw_resources = data.get("resources", [])
    resources: List[ManifestResource] = []
    for r in raw_resources:
        resources.append(ManifestResource(
            id=str(r.get("id", "")).strip(),
            source=str(r.get("source", "")).strip(),
            default_path=str(r.get("default_path", "")).strip(),
            type=str(r.get("type", "")).strip(),
            description=str(r.get("description", "")).strip(),
            user_modifiable=bool(r.get("user_modifiable", True)),
        ))
    return ManifestV2(version="1.0", resources=resources)
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-v1-compat


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-v2-sections
def _parse_v2_sections(path: Path, data: Dict[str, Any]) -> ManifestV2:
    """Parse v2.0 manifest with component sections."""
    meta = data.get("manifest", {})
    # Support includes under [manifest] or at top level
    inc = meta.get("includes")
    if inc is None:
        inc = data.get("includes", [])
    includes = list(inc)

    agents = _parse_agents(path, data.get("agents", []))
    skills = _parse_skills(path, data.get("skills", []))
    workflows = _parse_workflows(path, data.get("workflows", []))
    rules = _parse_rules(path, data.get("rules", []))

    # Backward-compat: v2.0 may still have [[resources]]
    resources = _parse_resources(data.get("resources", []))

    # Reserved sections: accept and ignore [[hooks]] and [[permissions]]

    return ManifestV2(
        version="2.0",
        includes=includes,
        agents=agents,
        skills=skills,
        workflows=workflows,
        rules=rules,
        resources=resources,
    )
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-v2-sections


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-section-helpers
def _validate_component_id(path: Path, section: str, idx: int, cid: str) -> None:
    """Validate a component id matches the required pattern."""
    if not cid:
        raise ValueError(f"{path}: [[{section}]][{idx}].id is required")
    if not _COMPONENT_ID_RE.match(cid):
        raise ValueError(
            f"{path}: [[{section}]][{idx}].id '{cid}' must match "
            "^[a-z][a-z0-9_-]*$"
        )


def _parse_base_fields(raw: Dict[str, Any], manifest_path: Optional[Path] = None) -> Dict[str, Any]:
    """Extract base ComponentEntry fields from a raw TOML dict."""
    raw_append = raw.get("append")
    raw_append_file = raw.get("append_file")
    comp_id = str(raw.get("id", "")).strip()
    if raw_append is not None and raw_append_file is not None:
        raise ValueError(f"Component '{comp_id}': 'append' and 'append_file' are mutually exclusive")
    if raw_append is not None and not isinstance(raw_append, str):
        raise ValueError(f"Component '{comp_id}': 'append' must be a string, got {type(raw_append).__name__}")
    # append_file: read content from a file path relative to the project root
    # (the nearest ancestor directory containing .git).
    # Must be relative — absolute paths are rejected to prevent arbitrary file reads.
    if raw_append_file is not None:
        if not isinstance(raw_append_file, str):
            raise ValueError(f"Component '{comp_id}': 'append_file' must be a string, got {type(raw_append_file).__name__}")
        if manifest_path is None:
            raise ValueError(f"Component '{comp_id}': 'append_file' requires manifest_path context")
        append_path = Path(raw_append_file)
        if append_path.is_absolute():
            raise ValueError(f"Component '{comp_id}': 'append_file' must be a relative path, got '{raw_append_file}'")
        # Resolve relative to the project root (nearest .git ancestor)
        repo_root = manifest_path.parent
        found_root = False
        while repo_root != repo_root.parent:
            if (repo_root / ".git").exists():
                found_root = True
                break
            repo_root = repo_root.parent
        if not found_root:
            raise ValueError(f"Component '{comp_id}': no .git ancestor found for append_file resolution")
        append_path = (repo_root / append_path).resolve()
        # Path containment: resolved path must stay within the repo root
        try:
            append_path.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValueError(
                f"Component '{comp_id}': append_file '{raw_append_file}' escapes repo root '{repo_root}'"
            ) from exc
        if not append_path.is_file():
            raise ValueError(f"Component '{comp_id}': append_file '{raw_append_file}' not found at {append_path}")
        raw_append = append_path.read_text(encoding="utf-8")
    return {
        "id": comp_id,
        "description": str(raw.get("description", "")).strip(),
        "prompt_file": str(raw.get("prompt_file", "")).strip(),
        "source": str(raw.get("source", "")).strip(),
        "agents": list(raw.get("agents", [])),
        "append": raw_append,
    }
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-section-helpers


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-agents
def _parse_agents(path: Path, raw_agents: List[Any]) -> List[AgentEntry]:
    """Parse [[agents]] section with extended schema validation."""
    agents: List[AgentEntry] = []
    for idx, raw in enumerate(raw_agents):
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: [[agents]][{idx}] must be a table")
        base = _parse_base_fields(raw, manifest_path=path)
        _validate_component_id(path, "agents", idx, base["id"])

        tools = list(raw.get("tools", []))
        disallowed_tools = list(raw.get("disallowed_tools", []))

        # Mutual exclusivity check
        if tools and disallowed_tools:
            raise ValueError(
                f"{path}: [[agents]][{idx}] ('{base['id']}'): "
                "tools and disallowed_tools are mutually exclusive"
            )

        agents.append(AgentEntry(
            **base,
            mode=str(raw.get("mode", "readwrite")).strip(),
            isolation=bool(raw.get("isolation", False)),
            model=str(raw.get("model", "")).strip(),
            tools=tools,
            disallowed_tools=disallowed_tools,
            skills=list(raw.get("skills", [])),
            color=str(raw.get("color", "")).strip(),
            memory_dir=str(raw.get("memory_dir", "")).strip(),
        ))
    return agents
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-agents


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-other-sections
def _parse_skills(path: Path, raw_skills: List[Any]) -> List[SkillEntry]:
    """Parse [[skills]] section."""
    skills: List[SkillEntry] = []
    for idx, raw in enumerate(raw_skills):
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: [[skills]][{idx}] must be a table")
        base = _parse_base_fields(raw, manifest_path=path)
        _validate_component_id(path, "skills", idx, base["id"])
        skills.append(SkillEntry(**base))
    return skills


def _parse_workflows(path: Path, raw_workflows: List[Any]) -> List[WorkflowEntry]:
    """Parse [[workflows]] section."""
    workflows: List[WorkflowEntry] = []
    for idx, raw in enumerate(raw_workflows):
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: [[workflows]][{idx}] must be a table")
        base = _parse_base_fields(raw, manifest_path=path)
        _validate_component_id(path, "workflows", idx, base["id"])
        workflows.append(WorkflowEntry(**base))
    return workflows


def _parse_rules(path: Path, raw_rules: List[Any]) -> List[RuleEntry]:
    """Parse [[rules]] section."""
    rules: List[RuleEntry] = []
    for idx, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: [[rules]][{idx}] must be a table")
        base = _parse_base_fields(raw, manifest_path=path)
        _validate_component_id(path, "rules", idx, base["id"])
        rules.append(RuleEntry(**base))
    return rules


def _parse_resources(raw_resources: List[Any]) -> List[ManifestResource]:
    """Parse [[resources]] section (shared between v1 and v2)."""
    resources: List[ManifestResource] = []
    for r in raw_resources:
        if not isinstance(r, dict):
            continue
        resources.append(ManifestResource(
            id=str(r.get("id", "")).strip(),
            source=str(r.get("source", "")).strip(),
            default_path=str(r.get("default_path", "")).strip(),
            type=str(r.get("type", "")).strip(),
            description=str(r.get("description", "")).strip(),
            user_modifiable=bool(r.get("user_modifiable", True)),
        ))
    return resources
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-parse-other-sections


# ---------------------------------------------------------------------------
# Includes Resolution
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-includes-helpers
_MAX_INCLUDE_DEPTH = 3


def _rewrite_component_paths(
    component: Any,
    included_dir: Path,
    trusted_root: Path,
) -> Any:
    """Return a copy of *component* with prompt_file and source rewritten.

    Paths that are non-empty and not already absolute are made absolute by
    resolving them relative to *included_dir*.  The resolved path must stay
    within *trusted_root* or a ``ValueError`` is raised.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-rewrite-paths
    kwargs: Dict[str, Any] = {}
    for fname in ("prompt_file", "source"):
        val: str = getattr(component, fname, "")
        if val and not Path(val).is_absolute():
            resolved = (included_dir / val).resolve()
            try:
                resolved.relative_to(trusted_root)
            except ValueError as exc:
                raise ValueError(
                    f"Component path '{val}' in included manifest escapes trusted root"
                ) from exc
            kwargs[fname] = str(resolved)
        else:
            kwargs[fname] = val
    # Copy all other fields unchanged by rebuilding via __class__
    import dataclasses
    existing = {f.name: getattr(component, f.name) for f in dataclasses.fields(component)}
    existing.update(kwargs)
    return component.__class__(**existing)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-rewrite-paths
# @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-includes-helpers


# @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-resolve-includes-header
def resolve_includes(
    manifest: ManifestV2,
    manifest_dir: Path,
    include_chain: Optional[Set[Path]] = None,
    trusted_root: Optional[Path] = None,
) -> ManifestV2:
    """Resolve the ``includes`` array in *manifest*, merging sub-manifests in.

    Loads each included ``manifest.toml``, rewrites their component paths to
    be absolute (relative to the *included* manifest's directory), checks for
    ID collisions, and merges the included components into the returned
    ``ManifestV2``.

    Args:
        manifest:      Parsed v2 manifest whose ``includes`` list to process.
        manifest_dir:  Directory that contains the current manifest file.
        include_chain: Set of already-visited absolute manifest file paths
                       (used for circular detection). Pass ``None`` for the
                       initial call.
        trusted_root:  Absolute directory that all include paths must stay
                       within (path-traversal guard). Defaults to
                       ``manifest_dir`` on the initial call and is propagated
                       unchanged through recursion.

    Returns:
        A new ``ManifestV2`` instance with all included components merged in.

    Raises:
        ValueError: On path traversal, circular includes, depth exceeded, or
                    ID collision.
    """
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-resolve-includes-header
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step1-read-includes
    if not manifest.includes:
        return manifest
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step1-read-includes

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-init-collections
    if include_chain is None:
        include_chain = set()
    if trusted_root is None:
        trusted_root = manifest_dir.resolve()

    # Working copies of component lists
    agents: List[AgentEntry] = list(manifest.agents)
    skills: List[SkillEntry] = list(manifest.skills)
    workflows: List[WorkflowEntry] = list(manifest.workflows)
    rules: List[RuleEntry] = list(manifest.rules)
    resources: List[ManifestResource] = list(manifest.resources)

    # Track the IDs declared directly in the includer (not from any included
    # manifest).  These IDs take priority: when an includee declares the same
    # ID, the includer's definition silently wins.  We also track the IDs that
    # have been accumulated from previously-processed includees so that a
    # collision *between two includees* remains an error.
    includer_ids: set = (
        {("agents", c.id) for c in manifest.agents}
        | {("skills", c.id) for c in manifest.skills}
        | {("workflows", c.id) for c in manifest.workflows}
        | {("rules", c.id) for c in manifest.rules}
    )
    accumulated_includee_ids: set = set()
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-init-collections

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2-foreach-include
    for include_path_str in manifest.includes:
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.1-resolve-path
        resolved: Path = (manifest_dir / include_path_str).resolve()
        # Guard against path traversal: all includes must stay within the
        # trusted root established by the top-level caller.
        try:
            resolved.relative_to(trusted_root)
        except ValueError as exc:
            raise ValueError(
                f"Include path '{include_path_str}' escapes the trusted root "
                f"'{trusted_root}' — path traversal is not allowed"
            ) from exc
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.1-resolve-path

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.2-circular-check
        if resolved in include_chain:
            chain_str = " -> ".join(str(p) for p in sorted(include_chain)) + f" -> {resolved}"
            raise ValueError(
                f"Circular include detected: {chain_str}"
            )
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.2-circular-check

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.3-depth-check
        if len(include_chain) >= _MAX_INCLUDE_DEPTH:
            raise ValueError(
                f"Max include depth of {_MAX_INCLUDE_DEPTH} exceeded "
                f"while resolving '{include_path_str}' "
                f"(chain depth: {len(include_chain)})"
            )
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.3-depth-check

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.4-parse-included
        included_manifest = parse_manifest_v2(resolved)
        included_dir = resolved.parent
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.4-parse-included

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.5-recurse
        new_chain: Set[Path] = include_chain | {resolved}
        included_manifest = resolve_includes(included_manifest, included_dir, new_chain, trusted_root)
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.5-recurse

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.6-rewrite-paths
        rewritten_agents = [_rewrite_component_paths(c, included_dir, trusted_root) for c in included_manifest.agents]
        rewritten_skills = [_rewrite_component_paths(c, included_dir, trusted_root) for c in included_manifest.skills]
        rewritten_workflows = [_rewrite_component_paths(c, included_dir, trusted_root) for c in included_manifest.workflows]
        rewritten_rules = [_rewrite_component_paths(c, included_dir, trusted_root) for c in included_manifest.rules]
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.6-rewrite-paths

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.7-collision-check
        included_ids: set = (
            {("agents", c.id) for c in rewritten_agents}
            | {("skills", c.id) for c in rewritten_skills}
            | {("workflows", c.id) for c in rewritten_workflows}
            | {("rules", c.id) for c in rewritten_rules}
        )
        # Collisions between two different includees are always an error.
        inter_includee_collisions = accumulated_includee_ids & included_ids
        if inter_includee_collisions:
            raise ValueError(
                f"Component ID collision between included manifests at '{resolved}': "
                f"{sorted(inter_includee_collisions)}"
            )
        # Collisions between the includer and an includee: includer wins
        # silently — filter the shadowed components out of the included set.
        shadowed_by_includer = includer_ids & included_ids
        if shadowed_by_includer:
            shadowed_agent_ids = {cid for sec, cid in shadowed_by_includer if sec == "agents"}
            shadowed_skill_ids = {cid for sec, cid in shadowed_by_includer if sec == "skills"}
            shadowed_workflow_ids = {cid for sec, cid in shadowed_by_includer if sec == "workflows"}
            shadowed_rule_ids = {cid for sec, cid in shadowed_by_includer if sec == "rules"}
            rewritten_agents = [c for c in rewritten_agents if c.id not in shadowed_agent_ids]
            rewritten_skills = [c for c in rewritten_skills if c.id not in shadowed_skill_ids]
            rewritten_workflows = [c for c in rewritten_workflows if c.id not in shadowed_workflow_ids]
            rewritten_rules = [c for c in rewritten_rules if c.id not in shadowed_rule_ids]
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.7-collision-check

        # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.8-merge
        agents.extend(rewritten_agents)
        skills.extend(rewritten_skills)
        workflows.extend(rewritten_workflows)
        rules.extend(rewritten_rules)
        resources.extend(included_manifest.resources)
        # Track the IDs we just merged in (excluding those shadowed by the
        # includer, since they were dropped) so subsequent includees can be
        # checked against them.
        merged_ids = included_ids - shadowed_by_includer
        accumulated_includee_ids |= merged_ids
        # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2.8-merge
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step2-foreach-include

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step3-return
    return ManifestV2(
        version=manifest.version,
        includes=manifest.includes,
        agents=agents,
        skills=skills,
        workflows=workflows,
        rules=rules,
        resources=resources,
    )
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-includes:p1:inst-step3-return


# ---------------------------------------------------------------------------
# Multi-Layer Merging + Section Appending
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-provenance-record
@dataclass
class ProvenanceRecord:
    """Provenance metadata for a merged component.

    Records which layer won and which layers were overridden.
    """

    component_id: str
    component_type: str  # "agents", "skills", "workflows", or "rules"
    winning_scope: str
    winning_path: Path
    overridden: List[Tuple[str, Path]] = field(default_factory=list)
# @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-provenance-record


# @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-merged-components
@dataclass
class MergedComponents:
    """Result of merging multiple manifest layers.

    Contains one dict per component type mapping component IDs to the winning
    component entry, plus provenance metadata for each component.
    """

    agents: Dict[str, AgentEntry] = field(default_factory=dict)
    skills: Dict[str, SkillEntry] = field(default_factory=dict)
    workflows: Dict[str, WorkflowEntry] = field(default_factory=dict)
    rules: Dict[str, RuleEntry] = field(default_factory=dict)
    provenance: Dict[str, ProvenanceRecord] = field(default_factory=dict)
# @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-merged-components


# @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-merge-entry
def _merge_component_entry(
    outer: "ComponentEntry",
    inner: "ComponentEntry",
) -> "ComponentEntry":
    """Merge two component entries from adjacent layers.

    Applies two cross-layer composition rules:
    - **Source inheritance**: if the inner entry has no ``source`` or
      ``prompt_file``, inherit those fields from the outer entry so that an
      append-only inner entry can still locate its base content.
    - **Append accumulation**: concatenate outer ``append`` content (if any)
      before inner ``append`` content so all layer appends are preserved in
      resolution order (outermost first).

    All other fields follow inner-scope-wins (taken from *inner*).
    """
    inherited_source = inner.source or outer.source
    inherited_prompt_file = inner.prompt_file or outer.prompt_file

    parts = []
    if outer.append:
        parts.append(outer.append)
    if inner.append:
        parts.append(inner.append)
    accumulated_append: Optional[str] = "\n".join(parts) if parts else None

    return replace(
        inner,
        source=inherited_source,
        prompt_file=inherited_prompt_file,
        append=accumulated_append,
    )
# @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-merge-entry


# @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-merge-components-header
def merge_components(layers: List[ManifestLayer]) -> MergedComponents:
    """Merge component entries from multiple manifest layers.

    Iterates layers in resolution order (as provided — outermost first).
    Later (inner/higher-priority) layers overwrite earlier layers on the same
    component ID (last-writer-wins / inner-scope-wins).

    Only layers with ``state == ManifestLayerState.LOADED`` are processed.
    Layers with ``None`` manifest are skipped.

    Provenance is recorded for every component: the winning layer scope/path
    and a list of (scope, path) tuples for overridden layers.

    Args:
        layers: List of ``ManifestLayer`` in resolution order, outermost first.

    Returns:
        ``MergedComponents`` with all merged dicts and provenance metadata.
    """
    # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-merge-components-header
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step1-init
    merged = MergedComponents()
    # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step1-init

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-foreach-layer
    for layer in layers:
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2.1-skip-non-loaded
        if layer.state != ManifestLayerState.LOADED or layer.manifest is None:
            continue
        # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2.1-skip-non-loaded

        manifest = layer.manifest

        # Iterate all component sections with their type labels
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-inner
        sections: List[Tuple[str, Dict, List]] = [
            ("agents", merged.agents, manifest.agents),
            ("skills", merged.skills, manifest.skills),
            ("workflows", merged.workflows, manifest.workflows),
            ("rules", merged.rules, manifest.rules),
        ]
        for component_type, merged_dict, component_list in sections:
            for component in component_list:
                cid = component.id

                # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-overwrite
                if cid in merged_dict:
                    # Record previous winner as overridden
                    prov_key = f"{component_type}:{cid}"
                    prev_prov = merged.provenance[prov_key]
                    overridden = list(prev_prov.overridden)
                    overridden.insert(0, (prev_prov.winning_scope, prev_prov.winning_path))
                    merged.provenance[prov_key] = ProvenanceRecord(
                        component_id=cid,
                        component_type=component_type,
                        winning_scope=layer.scope,
                        winning_path=layer.path,
                        overridden=overridden,
                    )
                    # Inherit source and accumulate appends from the outer entry
                    component = _merge_component_entry(merged_dict[cid], component)  # type: ignore[arg-type]
                else:
                    # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-newentry
                    prov_key = f"{component_type}:{cid}"
                    merged.provenance[prov_key] = ProvenanceRecord(
                        component_id=cid,
                        component_type=component_type,
                        winning_scope=layer.scope,
                        winning_path=layer.path,
                        overridden=[],
                    )
                    # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-newentry

                merged_dict[cid] = component  # type: ignore[assignment]
                # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-overwrite
        # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-inner
    # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step2-foreach-layer

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step3-return
    return merged
    # @cpt-end:cpt-cypilot-algo-project-extensibility-merge-components:p1:inst-step3-return


# @cpt-begin:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-appends-header
def apply_section_appends(
    base_content: str,
    components: List[ComponentEntry],
    component_id: str,
    component_type: Optional[str] = None,
) -> str:
    """Compose content by appending pre-merged append content from components.

    Starts with *base_content* (the winning component's content), then looks
    up *component_id* in the already-merged *components* list and appends its
    accumulated ``.append`` field (which was built during layer merging).

    This avoids re-scanning raw layers and prevents double-append.

    Args:
        base_content:   The base content (e.g. prompt file contents) from the
                        winning component definition.
        components:     List of already-merged ``ComponentEntry`` instances
                        (from ``MergedComponents``).
        component_id:   The component ID whose append content to collect.
        component_type: Optional component type (``"agents"``, ``"skills"``,
                        ``"workflows"``, ``"rules"``).  When provided, only
                        components of that type are matched — prevents
                        cross-type ID collisions from injecting wrong content.

    Returns:
        Composed content string.
    """
    # @cpt-end:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-appends-header
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-step1-base
    composed = base_content
    # @cpt-end:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-step1-base

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-step2-foreach-component
    _TYPE_CLASS_MAP = {
        "agents": AgentEntry,
        "skills": SkillEntry,
        "workflows": WorkflowEntry,
        "rules": RuleEntry,
    }
    expected_cls = _TYPE_CLASS_MAP.get(component_type) if component_type else None
    for component in components:
        if expected_cls is not None and not isinstance(component, expected_cls):
            continue
        if component.id == component_id and component.append:
            composed = composed + "\n" + component.append
            # The component's .append field already contains all accumulated
            # layer appends (built by _merge_component_entry), so we only
            # need to apply it once.
            break
    # @cpt-end:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-step2-foreach-component

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-step3-return
    return composed
    # @cpt-end:cpt-cypilot-algo-project-extensibility-section-appending:p1:inst-step3-return


# ---------------------------------------------------------------------------
# Schema validation helper
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-schema-validator
def _validate_against_schema(data: Dict[str, Any]) -> List[str]:
    """Validate *data* against ``kit-manifest.schema.json`` (best-effort).

    Uses a lightweight structural check — no third-party jsonschema library.
    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    # --- [manifest] section ---
    manifest = data.get("manifest")
    if not isinstance(manifest, dict):
        errors.append("Missing or invalid [manifest] section")
        return errors

    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("[manifest].version is required and must be a non-empty string")

    root = manifest.get("root")
    if root is not None and (not isinstance(root, str) or not root.strip()):
        errors.append("[manifest].root must be a non-empty string when present")

    um = manifest.get("user_modifiable")
    if um is not None and not isinstance(um, bool):
        errors.append("[manifest].user_modifiable must be a boolean when present")

    # --- [[resources]] ---
    resources = data.get("resources")
    if not isinstance(resources, list) or len(resources) == 0:
        errors.append("[[resources]] must be a non-empty array")
        return errors

    _VALID_TYPES = {"file", "directory"}
    _ID_CHARS = set(string.ascii_lowercase + string.digits + "_")

    for idx, res in enumerate(resources):
        prefix = f"[[resources]][{idx}]"
        if not isinstance(res, dict):
            errors.append(f"{prefix}: must be a table")
            continue

        # id
        rid = res.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append(f"{prefix}.id is required and must be a non-empty string")
        elif not rid[0].islower() or not all(c in _ID_CHARS for c in rid):
            errors.append(
                f"{prefix}.id '{rid}' must match ^[a-z][a-z0-9_]*$ "
                "(lowercase letter start, then lowercase alphanumeric or underscore)"
            )

        # source
        source = res.get("source")
        if not isinstance(source, str) or not source.strip():
            errors.append(f"{prefix}.source is required and must be a non-empty string")

        # default_path
        dp = res.get("default_path")
        if not isinstance(dp, str) or not dp.strip():
            errors.append(f"{prefix}.default_path is required and must be a non-empty string")

        # type
        rtype = res.get("type")
        if not isinstance(rtype, str) or rtype not in _VALID_TYPES:
            errors.append(f"{prefix}.type must be one of {sorted(_VALID_TYPES)}, got {rtype!r}")

        # description (optional)
        desc = res.get("description")
        if desc is not None and not isinstance(desc, str):
            errors.append(f"{prefix}.description must be a string when present")

        # user_modifiable (optional)
        rum = res.get("user_modifiable")
        if rum is not None and not isinstance(rum, bool):
            errors.append(f"{prefix}.user_modifiable must be a boolean when present")

    return errors
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-schema-validator


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-read
def load_manifest(kit_source: Path) -> Optional[Union[Manifest, ManifestV2]]:
    """Read and parse ``manifest.toml`` from *kit_source*.

    Returns ``None`` if the file does not exist.  V2 manifests are delegated
    to ``parse_manifest_v2`` and return a ``ManifestV2`` instance.
    Raises ``ValueError`` if the file exists but is invalid.
    """
    manifest_path = kit_source / "manifest.toml"
    if not manifest_path.is_file():
        return None

    try:
        with open(manifest_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid manifest.toml: {exc}") from exc

    # Detect V2 manifests early and delegate to V2 parser, skipping V1 validation
    meta = data.get("manifest", {})
    if str(meta.get("version", "")).strip() == "2.0":
        return parse_manifest_v2(manifest_path)

    # Schema-level structural validation (V1 only)
    schema_errors = _validate_against_schema(data)
    if schema_errors:
        raise ValueError(
            f"Invalid manifest.toml: {'; '.join(schema_errors)}"
        )

    meta = data["manifest"]
    raw_resources = data.get("resources", [])

    resources: list[ManifestResource] = []
    for r in raw_resources:
        resources.append(ManifestResource(
            id=str(r["id"]).strip(),
            source=str(r["source"]).strip(),
            default_path=str(r["default_path"]).strip(),
            type=str(r["type"]).strip(),
            description=str(r.get("description", "")).strip(),
            user_modifiable=bool(r.get("user_modifiable", True)),
        ))

    return Manifest(
        version=str(meta["version"]).strip(),
        root=str(meta.get("root", "{cypilot_path}/config/kits/{slug}")).strip(),
        user_modifiable=bool(meta.get("user_modifiable", True)),
        resources=resources,
    )
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-read


# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-validate
def validate_manifest(manifest: Manifest, kit_source: Path) -> list[str]:
    """Validate a parsed *manifest* against the actual *kit_source* directory.

    Checks:
    - All resource ``id`` values are unique.
    - All ``source`` paths exist in the kit package.
    - ``default_path`` values are valid relative paths (no ``..`` escapes).
    - ``type`` matches the actual source (file vs directory).

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    # 1. Unique ids
    seen_ids: dict[str, int] = {}
    for idx, res in enumerate(manifest.resources):
        if res.id in seen_ids:
            errors.append(
                f"Duplicate resource id '{res.id}' "
                f"(first at index {seen_ids[res.id]}, again at {idx})"
            )
        else:
            seen_ids[res.id] = idx

    for res in manifest.resources:
        source_path = kit_source / res.source

        # 2. Source path exists
        if not source_path.exists():
            errors.append(
                f"Resource '{res.id}': source path '{res.source}' "
                f"does not exist in kit package"
            )
            continue

        # 3. Type matches actual source
        if res.type == "file" and not source_path.is_file():
            errors.append(
                f"Resource '{res.id}': type is 'file' but "
                f"source '{res.source}' is a directory"
            )
        elif res.type == "directory" and not source_path.is_dir():
            errors.append(
                f"Resource '{res.id}': type is 'directory' but "
                f"source '{res.source}' is a file"
            )

    # 4. default_path — valid relative paths
    for res in manifest.resources:
        dp = res.default_path
        if dp.startswith("/") or dp.startswith("\\"):
            errors.append(
                f"Resource '{res.id}': default_path '{dp}' must be a relative path"
            )
        # Check for path traversal
        try:
            from pathlib import PurePosixPath
            resolved = PurePosixPath(dp).as_posix()
            if ".." in resolved.split("/"):
                errors.append(
                    f"Resource '{res.id}': default_path '{dp}' "
                    f"must not contain '..' path components"
                )
        except (ValueError, OSError, NotImplementedError):
            errors.append(
                f"Resource '{res.id}': default_path '{dp}' is not a valid path"
            )

    # 5. source — check for path traversal
    for res in manifest.resources:
        if res.source and ".." in str(res.source):
            errors.append(
                f"Resource '{res.id}': source path contains '..' traversal: {res.source}"
            )

    return errors
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-validate


# ---------------------------------------------------------------------------
# Resource Resolution API
# ---------------------------------------------------------------------------

def _resolve_binding_path(cypilot_dir: Path, identifier: str, binding_path: str) -> Path:
    from ..commands.kit import _normalize_path_string, _resolve_registered_kit_dir

    normalized_path = _normalize_path_string(binding_path)
    resolved_path = _resolve_registered_kit_dir(cypilot_dir, normalized_path)
    if resolved_path is None:
        raise ValueError(
            f"Resource '{identifier}' binding path '{normalized_path}' is an absolute path that is not accessible on this OS"
        )
    return resolved_path


# @cpt-begin:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-read-bindings
def resolve_resource_bindings(
    config_dir: Path, slug: str, cypilot_dir: Path,
) -> dict[str, Path]:
    """Resolve resource bindings for kit *slug* to absolute paths.

    Reads ``[kits.{slug}.resources]`` from ``core.toml`` in *config_dir*,
    then resolves each relative path against *cypilot_dir* (the adapter
    directory).  Paths may contain ``..`` components for resources placed
    outside the adapter tree.

    Returns a dict mapping resource identifiers to absolute ``Path`` objects.
    Returns an empty dict if no resources section exists.
    Raises ``ValueError`` if a configured binding path cannot be resolved on
    the current OS.

    @cpt-algo:cpt-cypilot-algo-kit-manifest-resolve:p1
    """
    result, binding_errors = resolve_resource_bindings_with_errors(
        config_dir,
        slug,
        cypilot_dir,
    )
    if binding_errors:
        raise ValueError("; ".join(binding_errors))
    return result


def resolve_resource_bindings_with_errors(
    config_dir: Path,
    slug: str,
    cypilot_dir: Path,
) -> tuple[dict[str, Path], list[str]]:
    """Resolve resource bindings while preserving valid entries and collecting errors."""
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return {}, []

    try:
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        return {}, [f"Failed to parse {core_toml}: {exc}"]
    except OSError as exc:
        return {}, [f"Failed to read {core_toml}: {exc}"]

    kits = data.get("kits")
    if not isinstance(kits, dict):
        return {}, []
    kit_entry = kits.get(slug)
    if not isinstance(kit_entry, dict):
        return {}, []
    resources = kit_entry.get("resources")
    if not isinstance(resources, dict):
        return {}, []
    # @cpt-end:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-read-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-to-absolute
    result: dict[str, Path] = {}
    binding_errors: list[str] = []
    for identifier, binding in resources.items():
        if isinstance(binding, dict):
            binding_path = str(binding.get("path", "")).strip()
        elif isinstance(binding, str):
            binding_path = binding.strip()
        else:
            continue
        if not binding_path:
            continue
        try:
            result[identifier] = _resolve_binding_path(cypilot_dir, identifier, binding_path)
        except ValueError as exc:
            binding_errors.append(str(exc))
    # @cpt-end:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-to-absolute

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-return
    return result, binding_errors
    # @cpt-end:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-return


# ---------------------------------------------------------------------------
# Source Path Mapping API
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-resource-info
@dataclass(frozen=True)
class ResourceInfo:
    """Metadata about a manifest resource for target path resolution."""

    type: str  # "file" or "directory"
    source_base: str  # source path in manifest (e.g., "artifacts/ADR")
# @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-resource-info


# @cpt-begin:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-build-mapping-header
# @cpt-algo:cpt-cypilot-algo-kit-manifest-source-mapping:p1
def build_source_to_resource_mapping(
    kit_source: Path,
) -> tuple[dict[str, str], dict[str, ResourceInfo]]:
    """Build mapping from source file paths to resource identifiers.

    For manifest-driven kit updates, this mapping allows determining which
    resource binding applies to each source file.

    Args:
        kit_source: Kit source directory (containing manifest.toml).

    Returns:
        Tuple of:
        - source_to_resource_id: Dict mapping each source file's relative path
          to its resource identifier. For directory resources, all files within
          the directory are mapped to the same resource id.
        - resource_info: Dict mapping resource id to ResourceInfo (type and
          source_base path for computing relative paths within directories).

    Returns (empty_dict, empty_dict) if no manifest.toml exists.

    @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-load-manifest
    """
    manifest = load_manifest(kit_source)
    if manifest is None:
        return {}, {}
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-load-manifest

    source_to_resource_id: Dict[str, str] = {}
    resource_info: Dict[str, ResourceInfo] = {}
    # @cpt-end:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1:inst-build-mapping-header

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-record-resource-info
    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-map-file-resources
    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-expand-directories
    for res in manifest.resources:
        resource_info[res.id] = ResourceInfo(
            type=res.type,
            source_base=res.source,
        )
        if res.type == "file":
            source_to_resource_id[res.source] = res.id
        elif res.type == "directory":
            source_dir = kit_source / res.source
            if source_dir.is_dir():
                for fpath in source_dir.rglob("*"):
                    if fpath.is_file():
                        rel_path = fpath.relative_to(kit_source).as_posix()
                        source_to_resource_id[rel_path] = res.id
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-expand-directories
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-map-file-resources
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-record-resource-info

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-return-mapping
    return source_to_resource_id, resource_info
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-return-mapping
