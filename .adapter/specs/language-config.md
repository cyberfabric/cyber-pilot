# Language Configuration

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define language-specific settings for code scanning and traceability

---

## Overview

This spec defines which file types to scan for FDD tags and how to recognize comments in different languages.

**Why needed**: FDD must work with ANY codebase - Python, JavaScript, Go, Rust, Java, etc.

**Configuration levels**:
1. **Defaults** (FDD core) - Sensible defaults for common languages
2. **Adapter** (this file) - Project-specific overrides
3. **Runtime** (CLI flags) - Temporary overrides for specific commands

---

## File Extensions

**Scanned for FDD tags**:
```
.py      # Python
.md      # Markdown (only files with FDD tags)
.js      # JavaScript
.ts      # TypeScript
.tsx     # TypeScript JSX
.go      # Go
.rs      # Rust
.java    # Java
.cs      # C#
.sql     # SQL
```

**Note**: `.md` files are scanned only if they contain `fdd-begin`, `fdd-end`, or `@fdd-` tags to avoid scanning unrelated documentation.

---

## Comment Formats

### Single-Line Comments

**Pattern**: Comment prefix at line start (with optional whitespace)

**Recognized prefixes**:
```
#        # Python, Shell, Ruby, YAML, Makefile
//       # JavaScript, TypeScript, Go, Rust, Java, C++, C#
--       # SQL, Lua, Haskell
```

### Multi-Line Comments

**Recognized patterns**:
```
/* ... */       # C-style (JavaScript, TypeScript, Go, Rust, Java, C++)
<!-- ... -->    # XML/HTML/Markdown
```

### Block Comment Continuation

**Inside multi-line blocks**:
```
*        # Continuation marker (Java, C-style)
```

---

## FDD Tag Patterns

### fdd-begin / fdd-end

**Format**: `{comment} fdd-begin {tag}`

**Valid examples**:
```python
# fdd-begin fdd-project-feature-x-flow-y:ph-1:inst-step
do_something()
# fdd-end fdd-project-feature-x-flow-y:ph-1:inst-step
```

```javascript
// fdd-begin fdd-project-feature-x-flow-y:ph-1:inst-step
doSomething();
// fdd-end fdd-project-feature-x-flow-y:ph-1:inst-step
```

```sql
-- fdd-begin fdd-project-feature-x-flow-y:ph-1:inst-step
SELECT 1;
-- fdd-end fdd-project-feature-x-flow-y:ph-1:inst-step
```

### @fdd-* inline tags

**Format**: `{comment} @fdd-{kind}:{scope-id}:ph-{N}`

**Valid examples**:
```python
# @fdd-flow:fdd-project-feature-x-flow-y:ph-1
```

```javascript
// @fdd-flow:fdd-project-feature-x-flow-y:ph-2
```

### Exclusion blocks

**Format**: `{comment} !no-fdd-begin` ... `{comment} !no-fdd-end`

**Valid examples**:
```python
# !no-fdd-begin
# ... auto-generated code, no validation needed
# !no-fdd-end
```

---

## Source

**Derived from**:
- Code analysis of `skills/fdd/scripts/fdd/validation/traceability.py`
- `skills/fdd/scripts/fdd/constants.py` regex patterns
- Current hardcoded extensions: `.rs`, `.py`, `.ts`, `.tsx`, `.js`, `.go`, `.java`, `.cs`, `.sql`, `.md`
- Current hardcoded comment prefixes: `#`, `//`, `<!--`, `/*`, `*`, `--`

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] All file extensions used in project are listed
- [ ] All comment styles in project are listed
- [ ] FDD tags work with all listed comment formats
- [ ] Markdown scanning limited to files with FDD tags only
- [ ] No conflicting patterns between languages

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are extensions from actual project files?
- [ ] Do comment patterns match project languages?
