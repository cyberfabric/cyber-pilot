# Code Review Prompt

Review the following PR code changes.

Focus on:
- Correctness and edge cases
- Code style and idiomatic patterns
- Performance implications
- Test coverage
- Security vulnerabilities
- Cargo, clippy, dylint, and rustfmt conformance
- New code has unit tests and end to end tests in testing/ folder
- Mistakes and potential misbehaviors

Use `docs/checklists/CODE.md` as the structured review guide when available.
Refer to `guidelines/DNA/languages/RUST.md` for Rust-specific conventions.
Refer to `guidelines/SECURITY.md` for security requirements.
Refer to `clippy.toml` and `Cargo.toml` workspace lints for lint rules.
