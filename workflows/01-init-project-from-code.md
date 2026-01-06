# Initialize FDD Project from Existing Codebase

**Extends**: `01-init-project.md`  
**Purpose**: Propose answers from code analysis instead of manual input

---

## Prerequisites

- Adapter exists (via `adapter-config-from-code.md`)
- Code access

---

## AI Agent Instructions

Run `01-init-project.md` workflow with these modifications:

### Pre-Workflow: Code Analysis

**Load adapter config**: Read `spec/FDD-Adapter/AGENTS.md` to get:
- `DOMAIN_MODEL_LOCATION`
- `API_CONTRACT_LOCATION`
- Project structure patterns

**Scan codebase**: Analyze project structure to identify:
- **Entry points**: Main application files (main.*, app.*, index.*, server.*)
- **Routes/API**: Route definitions, API endpoints, controllers
- **Domain types**: Files at `DOMAIN_MODEL_LOCATION`
- **API specifications**: Files at `API_CONTRACT_LOCATION`

**Extract information**:
- Actors (from auth/permission/role patterns)
- Capabilities (from endpoint groups, service names)
- Domain entities (from type definitions)
- API endpoints (from route definitions or specs)

---

### Modified Questions

**Q1: Project Name** → Propose from project metadata
- Source: package.json, go.mod, Cargo.toml, pom.xml, etc.
- Extract: name field or module name

**Q2: Vision** → Analyze README.md, propose based on capabilities
- Source: README.md, project description
- Synthesize: high-level project purpose from documentation and code structure

**Q3: Actors** → Detect from code patterns
- Source: authentication/authorization code, role definitions, permission checks
- Patterns: "role", "permission", "auth", "user types"
- Propose: User, Admin, Guest, System, etc.

**Q4: Capabilities** → Extract from code organization
- Sources: API endpoint groups, service/controller names, feature directories
- Analyze: logical grouping of functionality
- Propose: "User Management", "Content Publishing", "Payment Processing", etc.

**Q5: Domain Model** → List from `{DOMAIN_MODEL_LOCATION}`
- Source: Files at location specified in adapter
- Format: Entity name with key attributes
- Example: User (id, email, name, role), Post (id, title, content, authorId)

**Q6: API Contract** → Extract from `{API_CONTRACT_LOCATION}`
- Source: Files at location specified in adapter
- Format: HTTP method and endpoint path
- Example: POST /api/users, GET /api/users/:id, POST /api/posts

**Q7: Existing Docs** (additional) → Check for documentation
- Sources: docs/, README.md, architecture/, DESIGN.md
- Action: Reference existing docs in Overall Design if found

**Q8: Code Quality** (additional) → Assess implementation quality
- Test coverage: detect from test files, coverage reports, or ask
- Documentation: scan inline comments and doc comments
- Code style: assess as GOOD/FAIR/POOR based on patterns

---

### Generation Phase

Mark `architecture/DESIGN.md`:
```markdown
<!-- REVERSE-ENGINEERED FROM CODE -->
<!-- Date: {DATE} -->
<!-- Adapter: {ADAPTER_PATH} -->
```

Lower validation threshold: **70/100** (vs standard 90/100)

Add Section D:
```markdown
## D. Current Implementation State

### Reverse-Engineering Notes
- Source: {PROJECT_PATH}
- Date: {DATE}
- Quality: {ASSESSMENT}

### Known Gaps
- [ ] Missing design docs
- [ ] Incomplete types
- [ ] Partial API docs

### Strategy
1. Document existing (this step)
2. Validate with team
3. Improve iteratively
4. Use FDD for new features
```

---

### Feature Identification

**Scan code structure**: Analyze project organization to identify features
- Sources: feature directories, module directories, service/controller files
- Patterns: `/features/`, `/modules/`, files ending with `Service.*`, `Controller.*`, etc.
- Extract: logical feature groupings based on code organization

**Generate `FEATURES.md`**: Create manifest with `status: reverse-engineered`

**For each feature**: Create feature directory + DESIGN.md from code analysis

---

## Next Workflow

`02-validate-architecture.md` (accept ≥70/100)
