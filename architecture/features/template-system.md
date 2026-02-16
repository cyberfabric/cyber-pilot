# Feature: Template System

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-template-system`

- [x] - `cpt-cypilot-feature-template-system`

## 1. Feature Context

### 1. Overview
The Template System provides deterministic parsing and validation for Cypilot artifacts. It enables ID extraction, heading/outline validation, and cross-artifact consistency checks.

Problem: AI agents need deterministic validation of artifacts to ensure consistent quality.
Primary value: Enables machine-readable artifact structure with automated validation.
Key assumptions: Artifact validation is based on artifact scanning and kit constraints.

### 2. Purpose
Enable deterministic parsing and validation of Cypilot artifacts, ensuring structural compliance and ID integrity across the artifact hierarchy.

Success criteria: All artifacts validate in <100ms; cross-validation detects orphaned and missing references.

### 3. Actors
- `cpt-cypilot-actor-developer`
- `cpt-cypilot-actor-architect`
- `cpt-cypilot-actor-ai-assistant`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)
- ADRs: `cpt-cypilot-adr-template-centric-architecture-v1`
- Related feature: [Rules Packages](./rules-packages.md)
- Implementation: `skills/cypilot/scripts/cypilot/utils/template.py`

## 2. Actor Flows

### Load Template

- [x] **ID**: `cpt-cypilot-flow-template-system-load`

**Actors**:
- `cpt-cypilot-actor-ai-assistant`

1. [x] - `p1` - CLI receives template path from kit package - `inst-receive-path`
2. [x] - `p1` - File: READ template content from `{kit}/artifacts/{KIND}/template.md` - `inst-read-file`
3. [x] - `p1` - Parse YAML frontmatter (version, kind, policy) - `inst-parse-frontmatter`
4. [x] - `p1` - **IF** frontmatter missing or invalid **RETURN** error "Invalid template frontmatter" - `inst-check-frontmatter`
5. [x] - `p1` - Algorithm: scan artifact for IDs/references/headings - `inst-parse-markers`
6. [x] - `p1` - State: transition template to LOADED using `cpt-cypilot-state-template-system-lifecycle` - `inst-set-loaded`
7. [x] - `p1` - **RETURN** Template object with blocks, version, policy - `inst-return-template`

### Validate Artifact

- [x] **ID**: `cpt-cypilot-flow-template-system-validate`

**Actors**:
- `cpt-cypilot-actor-developer`
- `cpt-cypilot-actor-ai-assistant`

1. [x] - `p1` - CLI receives artifact path and resolves template from registry - `inst-resolve-template`
2. [x] - `p1` - File: READ artifact content from path - `inst-read-artifact`
3. [x] - `p1` - Algorithm: scan artifact for IDs/references/headings - `inst-parse-artifact`
4. [x] - `p1` - Algorithm: extract and validate IDs/references - `inst-extract-ids`
7. [x] - `p1` - **IF** kind="FEATURE": validate filename matches main feature ID slug - `inst-validate-filename`
8. [x] - `p1` - **IF** errors exist **RETURN** ValidationResult(status=FAIL, errors) - `inst-return-fail`
9. [x] - `p1` - **RETURN** ValidationResult(status=PASS, ids, refs) - `inst-return-pass`

### Cross-Validate Artifacts

- [x] **ID**: `cpt-cypilot-flow-template-system-cross-validate`

**Actors**:
- `cpt-cypilot-actor-architect`
- `cpt-cypilot-actor-ai-assistant`

1. [x] - `p1` - CLI loads all artifacts from registry - `inst-load-all`
2. [x] - `p1` - **FOR EACH** artifact in registry: - `inst-loop-artifacts`
   1. [x] - `p1` - Flow: validate artifact using `cpt-cypilot-flow-template-system-validate` - `inst-validate-each`
   2. [x] - `p1` - Collect all defined IDs into global set - `inst-collect-ids`
   3. [x] - `p1` - Collect all referenced IDs into global set - `inst-collect-refs`
3. [x] - `p1` - **FOR EACH** reference in all refs: - `inst-loop-refs`
   1. [x] - `p1` - **IF** reference not in defined IDs AND not external **RETURN** error "Orphaned reference" - `inst-check-orphan`
4. [x] - `p1` - **RETURN** CrossValidationResult(artifacts, orphaned_refs, coverage) - `inst-return-cross`

## 3. Processes / Business Logic

### Parse Artifact Signals

- [x] **ID**: `cpt-cypilot-algo-template-system-parse-markers`

1. [x] - `p1` - Split content into lines - `inst-split-lines`
2. [x] - `p1` - Initialize empty block stack and results list - `inst-init-stack`
3. [x] - `p1` - **FOR EACH** line with index: - `inst-loop-lines`
   1. [x] - `p1` - Scan for ID definitions and references outside code fences - `inst-check-marker`
5. [x] - `p1` - **RETURN** list of parsed block spans - `inst-return-blocks`

### Match Blocks

- [x] **ID**: `cpt-cypilot-algo-template-system-match-blocks`

1. [x] - `p1` - Initialize matched pairs list and unmatched template blocks - `inst-init-match`
2. [x] - `p1` - **FOR EACH** template block: - `inst-loop-template`
   1. [x] - `p1` - Find corresponding artifact block by type and name - `inst-find-artifact`
   2. [x] - `p1` - **IF** found: add to matched pairs - `inst-add-matched`
   3. [x] - `p1` - **IF** not found AND block.required=true: add to errors - `inst-missing-required`
3. [x] - `p1` - **FOR EACH** artifact block not in matched: - `inst-loop-extra`
   1. [x] - `p1` - **IF** template.policy.unknown_sections="error": add to errors - `inst-unknown-error`
   2. [x] - `p1` - **IF** template.policy.unknown_sections="warn": add to warnings - `inst-unknown-warn`
4. [x] - `p1` - **RETURN** MatchResult(pairs, errors, warnings) - `inst-return-match`

### Extract IDs

- [x] **ID**: `cpt-cypilot-algo-template-system-extract-ids`

1. [x] - `p1` - Initialize definitions list and references list - `inst-init-lists`
2. [x] - `p1` - **FOR EACH** block with type="id": - `inst-loop-id-blocks`
   1. [x] - `p1` - Extract ID value using `_ID_DEF_RE` pattern - `inst-extract-def`
   2. [x] - `p1` - **IF** ID matches `cpt-{system}-{kind}-{slug}` format: add to definitions - `inst-add-def`
   3. [x] - `p1` - **IF** ID invalid format: add to errors - `inst-invalid-id`
3. [x] - `p1` - **FOR EACH** artifact line (outside code fences): - `inst-loop-ref-lines`
   1. [x] - `p1` - Extract referenced IDs using `_BACKTICK_ID_RE` pattern - `inst-extract-ref`
   2. [x] - `p1` - Treat `cpt-...` occurrences outside `**ID**` definition lines as references - `inst-classify-ref`
   3. [x] - `p1` - Add each reference to references list with source location - `inst-add-ref`
4. [x] - `p1` - Check for duplicate definitions - `inst-check-duplicates`
5. [x] - `p1` - **RETURN** IdResult(definitions, references, errors) - `inst-return-ids`

### Validate Block Content

- [x] **ID**: `cpt-cypilot-algo-template-system-validate-content`

1. [x] - `p1` - Dispatch based on block type from `VALID_MARKER_TYPES` - `inst-dispatch`
2. [x] - `p1` - **IF** type="paragraph": validate non-empty text content - `inst-validate-paragraph`
3. [x] - `p1` - **IF** type="list": validate bullet or numbered list format - `inst-validate-list`
4. [x] - `p1` - **IF** type="table": validate markdown table structure - `inst-validate-table`
5. [x] - `p1` - **IF** type="cdsl": validate CDSL instruction format with priorities - `inst-validate-cdsl`
6. [x] - `p1` - **IF** type starts with "#": validate heading level matches - `inst-validate-heading`
7. [x] - `p1` - **IF** type="code": validate fenced code block present - `inst-validate-code`
8. [x] - `p1` - **IF** type="free": skip validation (any content allowed) - `inst-validate-free`
9. [x] - `p1` - **IF** type="id": validate **ID**: format, priority if required - `inst-validate-id`
   1. [x] - `p1` - **IF** line has checkbox (`[ ]`/`[x]`) AND not list item **RETURN** error "Task checkbox must be in a list item" - `inst-validate-id-task-list`
10. [x] - `p1` - Validate reference occurrences: format, priority if required by constraints - `inst-validate-refs`
11. [x] - `p1` - **RETURN** list of content errors - `inst-return-content-errors`

## 4. States

### Template Loading Lifecycle

- [x] **ID**: `cpt-cypilot-state-template-system-lifecycle`

1. [x] - `p1` - **FROM** UNINITIALIZED **TO** LOADING **WHEN** from_path() called - `inst-start-load`
2. [x] - `p1` - **FROM** LOADING **TO** LOADED **WHEN** parsing succeeds - `inst-load-success`
3. [x] - `p1` - **FROM** LOADING **TO** ERROR **WHEN** parsing fails - `inst-load-error`
4. [x] - `p1` - **FROM** LOADED **TO** VALIDATING **WHEN** validate() called - `inst-start-validate`
5. [x] - `p1` - **FROM** VALIDATING **TO** LOADED **WHEN** validation completes - `inst-validate-complete`

## 5. Definitions of Done

### Template Parsing

- [x] `p1` - **ID**: `cpt-cypilot-dod-template-system-parsing`

Artifacts are scanned into structured blocks and extracted signals (IDs, references, headings, CDSL) with line ranges. Signal extraction ignores fenced code blocks.

**Implementation details**:
- API: `Template.from_path(path)` returns `(Template, errors)`
- Module: `skills/cypilot/scripts/cypilot/utils/template.py`
- Domain: `Template`, `TemplateBlock`, `TemplateVersion`, `TemplatePolicy`

**Implements**:
- `p1` - `cpt-cypilot-flow-template-system-load`

- `p1` - `cpt-cypilot-algo-template-system-parse-markers`

**Covers (PRD)**:
- `cpt-cypilot-fr-artifact-templates`
- `cpt-cypilot-fr-validation`

- `cpt-cypilot-nfr-validation-performance`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-machine-readable`
- `cpt-cypilot-principle-deterministic-gate`

- `cpt-cypilot-constraint-markdown`
- `cpt-cypilot-constraint-stdlib-only`

- `cpt-cypilot-component-cypilot-skill`

- `cpt-cypilot-seq-validate-overall-design`

- `cpt-cypilot-dbtable-na`

### Artifact Validation

- [x] `p1` - **ID**: `cpt-cypilot-dod-template-system-validation`

Artifacts are validated using signal extraction (IDs, references, headings, CDSL) and kit constraints. Returns structured ValidationResult with PASS/FAIL status, errors list, and extracted IDs/references.

**Implementation details**:
- API: `Template.validate(artifact_path)` returns `Dict[str, List[errors]]`
- API: `Artifact.validate()` returns validation result
- Module: `skills/cypilot/scripts/cypilot/utils/template.py`
- Domain: `Artifact`, `ArtifactBlock`, `IdDefinition`, `IdReference`

**Implements**:
- `p1` - `cpt-cypilot-flow-template-system-validate`

- `p1` - `cpt-cypilot-algo-template-system-match-blocks`
- `p1` - `cpt-cypilot-algo-template-system-extract-ids`
- `p1` - `cpt-cypilot-algo-template-system-validate-content`

**Covers (PRD)**:
- `cpt-cypilot-fr-validation`
- `cpt-cypilot-fr-template-qa`

- `cpt-cypilot-nfr-validation-performance`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-deterministic-gate`
- `cpt-cypilot-principle-machine-readable-artifacts`

- `cpt-cypilot-constraint-markdown`

- `cpt-cypilot-component-cypilot-skill`

- `cpt-cypilot-seq-validate-overall-design`

- `cpt-cypilot-dbtable-na`

### Cross-Artifact Validation

- [x] `p1` - **ID**: `cpt-cypilot-dod-template-system-cross-validation`

Multiple artifacts are validated together to detect orphaned references (refs pointing to undefined IDs) and missing references. Supports external system references via prefix detection.

**Implementation details**:
- API: `cross_validate_artifacts(artifacts, project_root)` returns cross-validation result
- Module: `skills/cypilot/scripts/cypilot/utils/template.py`
- Domain: Uses Artifact.list_ids(), Artifact.list_refs()

**Implements**:
- `p1` - `cpt-cypilot-flow-template-system-cross-validate`

- `p1` - `cpt-cypilot-algo-template-system-extract-ids`

**Covers (PRD)**:
- `cpt-cypilot-fr-cross-artifact-validation`
- `cpt-cypilot-fr-traceability`

- `cpt-cypilot-nfr-validation-performance`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-traceability`
- `cpt-cypilot-principle-deterministic-gate`

- `cpt-cypilot-constraint-stdlib-only`

- `cpt-cypilot-component-cypilot-skill`

- `cpt-cypilot-seq-traceability-query`

- `cpt-cypilot-dbtable-na`

## 6. Acceptance Criteria

- [ ] `cpt-cypilot-dod-template-system-parsing`
- [ ] `cpt-cypilot-dod-template-system-validation`
- [ ] `cpt-cypilot-dod-template-system-cross-validation`

## 7. Additional Context (optional)

**Implementation Notes**:

The Template System is implemented in `skills/cypilot/scripts/cypilot/utils/template.py` (~1200 LOC) with:
- `Template` class: Parses and holds template structure
- `Artifact` class: Parses artifacts against templates
- `TemplateBlock` dataclass: Represents a parsed block span
- Key regex patterns: `_ID_DEF_RE`, `_ID_REF_RE`, `_BACKTICK_ID_RE`

**Block Types Supported** (`VALID_MARKER_TYPES`):
- Content: `free`, `paragraph`, `list`, `numbered-list`, `task-list`, `table`, `code`
- Identity: `id`
- Structure: `#`, `##`, `###`, `####`, `#####`, `######`
- Special: `link`, `image`, `cdsl`

**CDSL (Cypilot DSL)** format:
```
N. [ ] - `pN` - Description - `inst-slug`
```

**Dependencies**: None (Python stdlib only per `cpt-cypilot-constraint-stdlib-only`)

