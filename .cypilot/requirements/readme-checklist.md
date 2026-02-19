---
cypilot: true
type: requirement
name: README Quality Checklist
version: 1.0
purpose: Comprehensive quality checklist for README file validation
---

# README Quality Expert Checklist

---

## Overview

This checklist defines mandatory and optional criteria for reviewing README quality across different project types, ensuring clarity, completeness, and usability for the target audience.

## Table of Contents

1. [Agent Instructions](#agent-instructions)
2. [Review Scope Selection](#review-scope-selection)
3. [Prerequisites](#prerequisites)
4. [Applicability Context](#applicability-context)
5. [Severity Dictionary](#severity-dictionary)
6. [MUST HAVE](#must-have)
   - [Identity & Purpose (IDENT)](#-identity--purpose-ident)
   - [Getting Started (START)](#-getting-started-start)
   - [Usage Documentation (USAGE)](#-usage-documentation-usage)
   - [Technical Information (TECH)](#-technical-information-tech)
   - [Community & Contribution (COMM)](#-community--contribution-comm)
   - [Maintenance & Quality (MAINT)](#-maintenance--quality-maint)
   - [Accessibility & Readability (ACCESS)](#-accessibility--readability-access)
7. [MUST NOT HAVE](#must-not-have)
8. [Error Handling](#error-handling)
9. [Validation Summary](#validation-summary)
   - [Final Checklist](#final-checklist)
   - [Reporting](#reporting)
10. [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: This file WHEN validating README.md files

**ALWAYS use**: Review Scope Selection to determine appropriate review mode

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this checklist
- [ ] Agent has identified the project type and target audience
- [ ] Agent will check ALL items in applicable MUST HAVE sections
- [ ] Agent will verify ALL items in MUST NOT HAVE sections
- [ ] Agent will use the specified reporting format

---

## Review Scope Selection

**Choose review mode based on project type and README scope**:

| Review Mode | When to Use | Sections to Check |
|-------------|-------------|-------------------|
| **Quick** | Minor updates, typo fixes | IDENT (core) + changed sections |
| **Standard** | New README, moderate changes | All applicable sections |
| **Full** | Open-source release, public API | All sections with evidence |

### Quick Review (Core Items Only)

**MUST CHECK** (blocking):
- [ ] IDENT-README-001: Project Identity
- [ ] START-README-001: Installation Instructions
- [ ] USAGE-README-001: Basic Usage Examples
- [ ] MAINT-README-001: License Information

### Project Type Prioritization

| Project Type | Priority Sections | Secondary | Often N/A |
|--------------|-------------------|-----------|-----------|
| **Open Source Library** | IDENT, START, USAGE, COMM, MAINT | TECH | - |
| **Internal Tool** | IDENT, START, USAGE, TECH | MAINT | COMM (external) |
| **API/Service** | IDENT, START, USAGE, TECH | COMM | - |
| **CLI Application** | IDENT, START, USAGE | TECH, COMM | - |
| **Data Project** | IDENT, TECH, USAGE | START | COMM |
| **Documentation-only** | IDENT, ACCESS | USAGE | START, TECH |

---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist validates README.md files
- [ ] I have access to the full README content
- [ ] I understand the project type and target audience
- [ ] I will check ALL items in MUST HAVE sections
- [ ] I will verify ALL items in MUST NOT HAVE sections
- [ ] I will document any violations found
- [ ] I will provide specific feedback for each failed check

---

## Applicability Context

Before evaluating each checklist item, the expert MUST:

1. **Understand the project type** — What kind of project is this? (library, CLI, API, data project, etc.)

2. **Identify the target audience** — Who will read this README? (developers, end-users, data scientists, etc.)

3. **Determine applicability for each requirement**:
   - A data-only repository may not need installation instructions
   - An internal tool may not need contribution guidelines
   - A CLI tool needs command examples more than API docs

4. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it
   - If not applicable: Should be omitted (no N/A explanation needed in README)
   - If partially applicable: Must cover the relevant parts

**Key principle**: README should be complete for its audience without being bloated

---

## Severity Dictionary

- **CRITICAL**: Missing essential information; users cannot understand or use the project
- **HIGH**: Major gap; significantly impacts user experience
- **MEDIUM**: Meaningful improvement; enhances usability
- **LOW**: Minor improvement; polish

---

# MUST HAVE

---

## 🎯 Identity & Purpose (IDENT)

### IDENT-README-001: Project Identity
**Severity**: CRITICAL

- [ ] Project name is clearly visible (H1 heading)
- [ ] Project name matches repository/package name
- [ ] One-line description/tagline present
- [ ] Purpose is clear within first 3 sentences
- [ ] Target audience is identifiable

### IDENT-README-002: Project Description
**Severity**: CRITICAL

- [ ] Description explains WHAT the project does
- [ ] Description explains WHY it exists (problem it solves)
- [ ] Description explains WHO should use it
- [ ] Key specs/capabilities listed
- [ ] Differentiators from alternatives mentioned (if applicable)

### IDENT-README-003: Visual Identity
**Severity**: MEDIUM

- [ ] Logo or banner present (for public projects)
- [ ] Screenshot or demo GIF included (for visual projects)
- [ ] Badges present and functional:
  - [ ] Build/CI status badge
  - [ ] Version/release badge
  - [ ] License badge
  - [ ] Test coverage badge (if applicable)
- [ ] Badges are up-to-date (not showing failures for working project)

### IDENT-README-004: Navigation Structure
**Severity**: HIGH

- [ ] Table of Contents present (for README > 100 lines)
- [ ] TOC links are functional
- [ ] Section headings are descriptive
- [ ] Logical section ordering (identity → setup → usage → contribution)

---

## 🚀 Getting Started (START)

### START-README-001: Prerequisites & Requirements
**Severity**: HIGH

- [ ] System requirements listed (OS, hardware if relevant)
- [ ] Software dependencies listed with versions
- [ ] Required accounts/API keys mentioned
- [ ] Links to dependency installation guides provided
- [ ] Minimum versions specified where critical

### START-README-002: Installation Instructions
**Severity**: CRITICAL

- [ ] Installation method clearly documented
- [ ] Copy-pasteable commands provided
- [ ] Multiple installation methods covered (if applicable):
  - [ ] Package manager (npm, pip, brew, etc.)
  - [ ] From source
  - [ ] Docker/container
- [ ] Platform-specific instructions (if different)
- [ ] Verification step included ("how to verify installation worked")

### START-README-003: Quick Start
**Severity**: HIGH

- [ ] Minimal working example provided
- [ ] Example is copy-pasteable
- [ ] Example produces visible output
- [ ] Time to first success < 5 minutes for simple cases
- [ ] Common setup issues addressed or linked

### START-README-004: Configuration
**Severity**: MEDIUM

- [ ] Configuration options documented
- [ ] Environment variables listed
- [ ] Config file location specified
- [ ] Default values documented
- [ ] Example configuration provided

---

## 📖 Usage Documentation (USAGE)

### USAGE-README-001: Basic Usage Examples
**Severity**: CRITICAL

- [ ] At least one complete usage example
- [ ] Examples show common use cases
- [ ] Code examples are syntactically correct
- [ ] Expected output shown or described
- [ ] Examples use realistic (not foo/bar) data

### USAGE-README-002: API/Interface Documentation
**Severity**: HIGH (for libraries/APIs)

- [ ] Main functions/methods documented
- [ ] Parameters and return values described
- [ ] Type information provided (for typed languages)
- [ ] Error handling explained
- [ ] Link to full API docs (if extensive)

### USAGE-README-003: CLI Documentation
**Severity**: HIGH (for CLI tools)

- [ ] Command syntax documented
- [ ] All flags/options listed with descriptions
- [ ] Usage examples for each major command
- [ ] Help command mentioned (`--help`)
- [ ] Exit codes documented (for scripting)

### USAGE-README-004: Advanced Usage
**Severity**: MEDIUM

- [ ] Advanced specs documented or linked
- [ ] Integration examples (with other tools)
- [ ] Performance tips (if relevant)
- [ ] Troubleshooting guide or FAQ
- [ ] Link to full documentation (if exists)

---

## 🔧 Technical Information (TECH)

### TECH-README-001: Architecture Overview
**Severity**: MEDIUM (for complex projects)

- [ ] High-level architecture described
- [ ] Key components explained
- [ ] Diagram included (for complex systems)
- [ ] Technology stack mentioned
- [ ] Design decisions linked (ADRs)

### TECH-README-002: Dependencies
**Severity**: HIGH

- [ ] Runtime dependencies listed
- [ ] Development dependencies listed (or linked)
- [ ] Dependency purpose explained (for non-obvious ones)
- [ ] Version constraints explained
- [ ] Security considerations noted

### TECH-README-003: Build & Test
**Severity**: MEDIUM

- [ ] Build instructions provided
- [ ] Test execution instructions provided
- [ ] Linting/formatting commands documented
- [ ] CI/CD pipeline mentioned
- [ ] Local development setup explained

### TECH-README-004: Compatibility
**Severity**: HIGH

- [ ] Supported platforms listed
- [ ] Supported language/runtime versions listed
- [ ] Browser support (for web projects)
- [ ] Breaking changes noted
- [ ] Migration guides linked (for major versions)

---

## 👥 Community & Contribution (COMM)

### COMM-README-001: Contribution Guidelines
**Severity**: HIGH (for open source)

- [ ] Contribution welcome statement
- [ ] Link to CONTRIBUTING.md (or inline guidelines)
- [ ] Issue reporting process explained
- [ ] Pull request process explained
- [ ] Code of Conduct linked

### COMM-README-002: Communication Channels
**Severity**: MEDIUM

- [ ] Primary contact method provided
- [ ] Issue tracker linked
- [ ] Discussion forum/chat linked (if exists)
- [ ] Maintainer(s) identified
- [ ] Response time expectations set (optional)

### COMM-README-003: Recognition
**Severity**: LOW

- [ ] Contributors acknowledged
- [ ] Sponsors/funders credited (if applicable)
- [ ] Inspiration/prior art credited
- [ ] Third-party assets attributed

### COMM-README-004: Support Information
**Severity**: MEDIUM

- [ ] How to get help explained
- [ ] Commercial support options (if available)
- [ ] Paid vs free support distinguished
- [ ] Self-help resources linked

---

## 🛡️ Maintenance & Quality (MAINT)

### MAINT-README-001: License Information
**Severity**: CRITICAL

- [ ] License type clearly stated
- [ ] License badge present
- [ ] Link to full LICENSE file
- [ ] License implications explained (for non-standard)
- [ ] Third-party license compatibility noted (if relevant)

### MAINT-README-002: Project Status
**Severity**: HIGH

- [ ] Current status indicated (active, maintenance, deprecated, archived)
- [ ] Latest version number visible
- [ ] Last update date visible (badges or text)
- [ ] Roadmap linked (if exists)
- [ ] Known issues/limitations documented

### MAINT-README-003: Versioning & Releases
**Severity**: MEDIUM

- [ ] Versioning scheme explained (SemVer, CalVer, etc.)
- [ ] Changelog linked
- [ ] Release notes linked
- [ ] Upgrade instructions provided
- [ ] Deprecation policy explained (for mature projects)

### MAINT-README-004: Citation
**Severity**: MEDIUM (for academic/research projects)

- [ ] How to cite the project explained
- [ ] DOI provided (if applicable)
- [ ] BibTeX entry provided
- [ ] Related publications linked
- [ ] CITATION.cff file mentioned

### MAINT-README-005: Security
**Severity**: HIGH

- [ ] Security policy linked (SECURITY.md)
- [ ] How to report vulnerabilities explained
- [ ] Security considerations documented
- [ ] Dependency security status (badges)

---

## ♿ Accessibility & Readability (ACCESS)

### ACCESS-README-001: Language Quality
**Severity**: HIGH

- [ ] Written in clear, simple language
- [ ] Technical jargon explained or linked
- [ ] No spelling or grammar errors
- [ ] Consistent terminology throughout
- [ ] Active voice preferred

### ACCESS-README-002: Formatting Quality
**Severity**: MEDIUM

- [ ] Proper Markdown syntax
- [ ] Consistent heading hierarchy
- [ ] Code blocks with language highlighting
- [ ] Lists used for enumerations
- [ ] Adequate whitespace between sections

### ACCESS-README-003: Scannability
**Severity**: HIGH

- [ ] Key information in first paragraph
- [ ] Section headings are descriptive
- [ ] Important terms **bolded**
- [ ] Links are descriptive (not "click here")
- [ ] Quick summary/TL;DR for long README

### ACCESS-README-004: Inclusivity
**Severity**: MEDIUM

- [ ] Alt text for images
- [ ] No assumptions about user background
- [ ] Multiple learning styles supported (text + examples + diagrams)
- [ ] Non-discriminatory language
- [ ] Accessible color choices (for diagrams)

### ACCESS-README-005: Internationalization
**Severity**: LOW

- [ ] Primary language clearly identified
- [ ] Translations linked (if available)
- [ ] ASCII-friendly content where possible
- [ ] Date/number formats unambiguous

---

# MUST NOT HAVE

---

## ❌ IDENT-README-NO-001: No Broken Elements
**Severity**: CRITICAL

**What to check**:
- [ ] No broken links (404s)
- [ ] No broken images
- [ ] No broken badges
- [ ] No broken TOC links
- [ ] No references to non-existent files

---

## ❌ IDENT-README-NO-002: No Outdated Information
**Severity**: HIGH

**What to check**:
- [ ] No deprecated installation methods
- [ ] No outdated version numbers
- [ ] No references to removed specs
- [ ] No old screenshots/GIFs
- [ ] No stale badges showing failures

---

## ❌ USAGE-README-NO-001: No Non-Working Examples
**Severity**: CRITICAL

**What to check**:
- [ ] No syntax errors in code examples
- [ ] No examples using deprecated APIs
- [ ] No examples with missing imports
- [ ] No examples with incorrect output
- [ ] No examples requiring unavailable resources

---

## ❌ TECH-README-NO-001: No Sensitive Information
**Severity**: CRITICAL

**What to check**:
- [ ] No API keys or tokens
- [ ] No passwords or credentials
- [ ] No internal URLs or IPs
- [ ] No personal email addresses (unless intended)
- [ ] No private repository references

---

## ❌ ACCESS-README-NO-001: No Barriers to Understanding
**Severity**: HIGH

**What to check**:
- [ ] No unexplained acronyms
- [ ] No undefined technical terms
- [ ] No assumed prior knowledge without links
- [ ] No incomplete sentences
- [ ] No placeholder text (TODO, TBD, FIXME, Lorem ipsum)

---

## ❌ MAINT-README-NO-001: No License Issues
**Severity**: CRITICAL

**What to check**:
- [ ] No "All Rights Reserved" without intent
- [ ] No conflicting license statements
- [ ] No missing license for open source
- [ ] No incompatible dependency licenses mentioned
- [ ] No license that contradicts project purpose

---

## ❌ COMM-README-NO-001: No Unwelcoming Content
**Severity**: HIGH

**What to check**:
- [ ] No discriminatory language
- [ ] No hostile tone
- [ ] No dismissive responses to questions
- [ ] No unrealistic expectations of users
- [ ] No gatekeeping language ("obviously", "simply", "just")

---

# Error Handling

## README File Not Found

**If README.md doesn't exist at expected location**:
```
⚠️ README not found: {path}
→ Expected at: {project_root}/README.md
→ Fix: Create README.md or specify correct path
```
**Action**: STOP — cannot validate non-existent file.

## README Unreadable

**If README file cannot be read**:
```
⚠️ Cannot read README: {path}
→ Check file permissions
→ Verify file encoding is UTF-8
```
**Action**: STOP — cannot validate unreadable file.

## Incomplete README (Partial Content)

**If README is truncated or has obvious missing sections**:
```
⚠️ README appears incomplete
→ File ends abruptly at: {location}
→ Missing expected sections: {list}
→ Fix: Complete the README before validation
```
**Action**: WARN and continue with available content.

## Corrupted Markdown

**If README contains malformed markdown**:
```
⚠️ Markdown parsing errors detected
→ Issues: {list of parsing errors}
→ Fix: Correct markdown syntax before full validation
```
**Action**: WARN and attempt validation, note formatting issues.

## External Links Inaccessible

**If external links cannot be verified**:
```
⚠️ Cannot verify external links (network unavailable)
→ Skipping link validation: IDENT-README-NO-001
→ Manual verification recommended
```
**Action**: Skip link validation, mark as INCOMPLETE in report.

---

# Validation Summary

## Final Checklist

Confirm before reporting results:

- [ ] I checked ALL items in MUST HAVE sections
- [ ] I verified ALL items in MUST NOT HAVE sections
- [ ] I documented all violations found
- [ ] I provided specific feedback for each failed check
- [ ] All critical issues have been reported

### Quality Score Calculation

| Severity | Weight | Impact on Score |
|----------|--------|-----------------|
| CRITICAL | 10 | -10 points each |
| HIGH | 5 | -5 points each |
| MEDIUM | 2 | -2 points each |
| LOW | 1 | -1 point each |

**Score Formula**: `100 - (sum of weighted violations)`

| Score | Quality Level | Recommendation |
|-------|---------------|----------------|
| 90-100 | Excellent | Ready for publication |
| 75-89 | Good | Minor improvements needed |
| 60-74 | Acceptable | Should improve before release |
| 40-59 | Poor | Significant work needed |
| 0-39 | Failing | Major rewrite required |

---

## Reporting Readiness Checklist

- [ ] I will report every identified issue
- [ ] I will report only issues (no "everything looks good" sections)
- [ ] Each reported issue will include location (section/line)
- [ ] Each reported issue will include why it matters
- [ ] Each reported issue will include a proposal to fix
- [ ] I will avoid vague statements

---

## Reporting

Report **only** problems (do not list what is OK).

### Compact Format (Quick Reviews)

```markdown
## README Review: {project-name}

| # | ID | Sev | Section | Issue | Fix |
|---|-----|-----|---------|-------|-----|
| 1 | START-001 | CRIT | Installation | No install instructions | Add npm/pip install command |
| 2 | IDENT-002 | HIGH | Description | Purpose unclear | Add one-line description |

**Score**: {N}/100 ({Quality Level})
**Review mode**: Quick
```

### Full Format (Standard/Full Reviews)

```markdown
## README Review Report

### Summary
- **Project**: {name}
- **Score**: {N}/100 ({Quality Level})
- **Critical Issues**: {count}
- **Total Issues**: {count}

### 1. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Location
{Section name, line number if applicable}

#### Issue
{What is wrong}

#### Why It Matters
{Impact on users}

#### Proposal
{Specific fix with example if helpful}

---

### 2. {Next issue}
...
```

---

## Reporting Commitment

- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist
- [ ] I included location and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I calculated and reported the quality score
- [ ] I did not hide or omit known problems

---

## References

- [Standard README](https://github.com/RichardLitt/standard-readme) — README specification and linter
- [Awesome README](https://github.com/matiassingers/awesome-readme) — Curated list of exemplary READMEs
- [Make a README](https://www.makeareadme.com/) — README best practices guide
- [jehna/readme-best-practices](https://github.com/jehna/readme-best-practices) — Templates and examples
- [pyOpenSci README Guidelines](https://www.pyopensci.org/python-package-guide/documentation/repository-files/readme-file-best-practices.html) — Python-specific guidance
- [readme-inspector](https://github.com/commonality/readme-inspector) — Quality scoring tool
- [freeCodeCamp README Guide](https://www.freecodecamp.org/news/how-to-write-a-good-readme-file/) — Comprehensive tutorial
