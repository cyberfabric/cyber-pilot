# Configure FDD Adapter from Existing Codebase

**Extends**: `adapter-config.md`  
**Purpose**: Propose adapter settings from code analysis instead of manual input

---

## AI Agent Instructions

Run `adapter-config.md` workflow with these modifications:

### Pre-Workflow

**Q0: Project Path** (insert before Q1)
```
Where is the codebase? (absolute path)
```

**Auto-scan**:
- Check for dependency files: `package.json`, `requirements.txt`, `go.mod`, `pom.xml`
- Detect web frameworks in dependencies (Express, Fastify, Next.js, FastAPI, Flask, Django)
- Identify primary language and ecosystem

---

### Modified Questions

**Q1: Domain Model** → Detect & propose

**Detection**: Locate domain model files
- Search for type definition files (e.g., `types/`, `models/`, `*.d.ts`)
- Search for model files (e.g., `models.py`, `*_model.py`, `schema.ts`)
- Identify primary location pattern

**Propose**: Format + Location + Reference pattern

**Q2: API Contract** → Detect & propose

**Detection**: Locate API specification files
- Search for OpenAPI/Swagger specs (`swagger.json`, `openapi.yaml`)
- Search for GraphQL schemas (`schema.graphql`, `*.gql`)
- Search for Protocol Buffers (`*.proto`)
- Identify API contract style

**Propose**: Style + Format + Location

**Q3: Tech Stack** → Extract from deps

**Detection**: Read dependency files
- Extract dependencies from `package.json` (JavaScript/TypeScript)
- Extract dependencies from `requirements.txt` (Python)
- Extract dependencies from `go.mod` (Go)
- Extract dependencies from `pom.xml` (Java)
- Identify database libraries and runtimes

**Propose**: Language + Framework + Database + Runtime

**Q4: Testing** → Detect config & files

**Detection**: Locate test configuration and files
- Check for test configs (`jest.config.js`, `pytest.ini`, `vitest.config.ts`)
- Search for test files (`*.test.ts`, `*_test.py`, `*_test.go`, `*.spec.js`)
- Identify test file naming pattern
- Count test files to verify testing presence

**Propose**: Framework + Pattern + Commands

**Q5: Build Commands** → Extract from scripts

**Detection**: Read build configuration
- Extract scripts from `package.json` (npm/yarn/pnpm)
- Extract targets from `Makefile`
- Check for `build.gradle` or `build.xml`
- Identify build tool (npm, make, gradle, maven)

**Propose**: Install + Build + Dev + Test + Lint

**Q6: Conventions** → Detect configs

**Detection**: Locate tooling configuration files
- Check for linter configs (`.eslintrc*`, `.pylintrc`, `tslint.json`)
- Check for formatter configs (`.prettierrc*`, `.black`, `.editorconfig`)
- Analyze source directory structure for naming patterns
- Identify primary source directory (`src/`, `lib/`, `app/`)

**Propose**: Linter + Formatter + Naming

---

### Generation Phase

Add to `spec/FDD-Adapter/AGENTS.md`:
```markdown
**Discovery Method**: Code analysis
<!-- Discovered from {PROJECT_PATH} on {DATE} -->
```

---

## Next Workflow

`01-init-project-from-code.md`
