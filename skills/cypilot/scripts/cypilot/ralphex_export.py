"""
ralphex Plan Export Compiler - Compile Cypilot plans into ralphex-compatible format.

Transforms Cypilot plan manifests and phase files into ralphex Markdown plans
with ``## Validation Commands`` and ``### Task N:`` sections. Includes post-run
handoff reporting, delegation lifecycle state tracking, and bootstrap detection.

@cpt-algo:cpt-cypilot-algo-ralphex-delegation-compile-plan:p1
@cpt-algo:cpt-cypilot-algo-ralphex-delegation-map-phase:p1
@cpt-flow:cpt-cypilot-flow-ralphex-delegation-handoff:p1
@cpt-state:cpt-cypilot-state-ralphex-delegation-lifecycle:p1
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .utils._tomllib_compat import tomllib
from .utils.files import _read_cypilot_var, core_subpath

logger = logging.getLogger(__name__)

# Rules subsections to include as bounded guidance
_GUIDANCE_SUBSECTIONS = {"Engineering", "Quality"}


def compile_delegation_plan(plan_dir: str) -> str:
    """Compile a Cypilot plan into a ralphex-compatible Markdown plan.

    Reads the plan manifest (``plan.toml``) and phase files from *plan_dir*,
    assembles them into ralphex grammar order: title, overview,
    ``## Validation Commands``, and ``### Task N:`` blocks.

    Args:
        plan_dir: Path to the Cypilot plan directory containing ``plan.toml``
                  and phase files.

    Returns:
        The compiled ralphex Markdown plan content as a string.
    """
    # @cpt-begin:inst-read-manifest
    plan_path = Path(plan_dir) / "plan.toml"
    with open(plan_path, "rb") as f:
        manifest = tomllib.load(f)

    plan_meta = manifest.get("plan", {})
    if not plan_meta:
        raise ValueError(f"plan.toml missing required [plan] section: {plan_path}")
    phases = manifest.get("phases", [])
    logger.info("Read plan manifest with %d phases: %s", len(phases), plan_meta.get("task"))
    # @cpt-end:inst-read-manifest

    # @cpt-begin:inst-gen-title
    task_name = plan_meta.get("task")
    if not task_name:
        raise ValueError(f"plan.toml [plan] section missing required 'task' key: {plan_path}")
    title = f"# {task_name}"
    # @cpt-end:inst-gen-title

    # @cpt-begin:inst-gen-validation
    overview = _generate_overview(plan_meta, phases)
    validation = _generate_validation_section(manifest)
    # @cpt-end:inst-gen-validation

    # @cpt-begin:inst-loop-phases
    task_blocks: list[str] = []
    for phase in phases:
        phase_file = Path(plan_dir) / phase["file"]
        if not phase_file.exists():
            raise FileNotFoundError(
                f"Phase file not found: {phase_file} "
                f"(declared in plan.toml but missing from {plan_dir})"
            )
        phase_content = phase_file.read_text(encoding="utf-8")
        task_block = map_phase_to_task(
            phase_content,
            phase["number"],
            _format_phase_reference_path(phase_file, plan_dir),
        )
        task_blocks.append(task_block)
    actual_phase_numbers = [int(phase.get("number", 0) or 0) for phase in phases]
    next_task_num = max(actual_phase_numbers, default=0) + 1
    lifecycle_block = _generate_lifecycle_task(manifest, plan_dir, next_task_num, actual_phase_numbers)
    if lifecycle_block:
        task_blocks.append(lifecycle_block)
    # @cpt-end:inst-loop-phases

    # @cpt-begin:inst-assemble
    sections = [title, "", overview, "", validation, ""]
    for block in task_blocks:
        sections.append(block)
        sections.append("")
    plan_content = "\n".join(sections).rstrip() + "\n"
    # @cpt-end:inst-assemble

    # @cpt-begin:inst-resolve-paths
    plan_content = _resolve_paths(plan_content, plan_dir)
    # @cpt-end:inst-resolve-paths

    # @cpt-begin:inst-return-plan
    logger.info("Compiled plan: %d chars, %d task blocks", len(plan_content), len(task_blocks))
    return plan_content
    # @cpt-end:inst-return-plan


def map_phase_to_task(
    phase_content: str,
    phase_num: int,
    phase_file: Optional[str] = None,
) -> str:
    """Map a single Cypilot phase to a ralphex ``### Task N:`` block.

    Emits a compact handoff prompt that points ralphex back to the original
    phase file, summarizes the phase focus, highlights bounded guidance, and
    states what to ignore outside the declared phase scope.

    Args:
        phase_content: Raw Markdown content of the Cypilot phase file.
        phase_num: The phase number (used for ``### Task N:`` header).
        phase_file: Optional original phase file path to reference explicitly.

    Returns:
        Formatted ``### Task N:`` block content.
    """
    # @cpt-begin:inst-extract-title
    frontmatter = _parse_toml_frontmatter(phase_content)
    phase_meta = frontmatter.get("phase", {})
    title = phase_meta.get("title", f"Phase {phase_num}")
    # @cpt-end:inst-extract-title

    lines: list[str] = [f"### Task {phase_num}: {title}", ""]

    if phase_file:
        lines.append("**Original Phase File:**")
        lines.append(f"- `{phase_file}`")
        lines.append("")

    lines.append("**Execution Prompt:**")
    lines.append("- [ ] Load the original phase file and use it as the authoritative source for this task.")
    lines.append("- [ ] Prioritize the phase frontmatter plus `What`, `Rules`, `Input`, `Task`, `Acceptance Criteria`, and `Output Format`.")
    lines.append("- [ ] Treat `Preamble` as boilerplate and use `Prior Context` only as supporting background, not as new requirements.")
    lines.append("")

    what_text = _extract_section_body(phase_content, "What")
    if what_text:
        lines.append("**Phase Focus:**")
        lines.append(f"- {what_text}")

    task_steps = _extract_section_items(phase_content, "Task")
    if task_steps:
        if not what_text:
            lines.append("**Phase Focus:**")
        for step in task_steps:
            lines.append(f"- {step}")
        lines.append("")

    criteria = _extract_section_items(phase_content, "Acceptance Criteria")
    if criteria:
        lines.append("**Success Checks:**")
        for criterion in criteria:
            lines.append(f"- {criterion}")
        lines.append("")

    guidance = _distill_guidance(phase_content)
    if guidance:
        lines.append("**Guidance:**")
        for item in guidance:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("**Ignore:**")
    lines.append("- Other phases unless they are required by `depends_on` or explicitly referenced by the original phase file.")
    lines.append("- Files outside this phase's declared scope unless the original phase explicitly tells you to read them at runtime.")
    lines.append("- Any compiled-plan summary text if it conflicts with the original phase file.")
    lines.append("")

    depends_on = phase_meta.get("depends_on", [])
    inputs = phase_meta.get("inputs", [])
    output_files = phase_meta.get("output_files", [])
    input_files = phase_meta.get("input_files", [])
    outputs = phase_meta.get("outputs", [])
    if depends_on or inputs:
        lines.append("**Dependencies:**")
        if depends_on:
            lines.append(f"- Depends on phase(s): {', '.join(str(dep) for dep in depends_on)}")
        for item in inputs:
            lines.append(f"- Required prior artifact: `{item}`")
        lines.append("")

    if input_files or output_files:
        lines.append("**Declared Scope:**")
        for fp in input_files:
            lines.append(f"- Input file: `{fp}`")
        for fp in output_files:
            lines.append(f"- Output file: `{fp}`")
        lines.append("")

    if outputs:
        lines.append("**Expected Deliverables:**")
        for item in outputs:
            lines.append(f"- `{item}`")
        lines.append("")

    # @cpt-begin:inst-return-task
    return "\n".join(lines).rstrip()
    # @cpt-end:inst-return-task


def _find_project_root(start_path: Path) -> Path:
    """Find the nearest project root for path formatting.

    A project root is a directory containing ``.git`` or ``.bootstrap``.
    If no marker is found, fall back to the parent of ``start_path`` so plan
    references remain relative to the containing workspace area.
    """
    resolved_start = start_path.resolve()
    for parent in [resolved_start] + list(resolved_start.parents):
        if (parent / ".git").exists() or (parent / ".bootstrap").exists():
            return parent
        if (parent / "cypilot").exists() or (parent / ".cypilot").exists() or (parent / ".cpt").exists():
            return parent
    return resolved_start.parent


def _format_phase_reference_path(phase_file: Path, plan_dir: str) -> str:
    """Format an original phase file path as project-root-relative text."""
    raw_plan_dir = Path(plan_dir)
    raw_phase_file = phase_file
    resolved_phase_file = phase_file.resolve()
    resolved_root = _find_project_root(raw_plan_dir)
    raw_root = raw_plan_dir.parent

    for candidate_file, candidate_root in (
        (resolved_phase_file, resolved_root),
        (raw_phase_file, raw_root),
    ):
        try:
            return candidate_file.relative_to(candidate_root).as_posix()
        except ValueError:
            continue

    return phase_file.name


def _resolve_plan_manifest_path(path_value: str, plan_dir: str) -> Path:
    """Resolve a plan-manifest path value relative to the project root when needed."""
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate

    project_root = _find_project_root(Path(plan_dir))
    rooted = project_root / candidate
    if rooted.exists() or str(candidate).startswith((".bootstrap/", "cypilot/", ".plans/")):
        return rooted

    return Path(plan_dir) / candidate


def _resolve_lifecycle_action(manifest: dict) -> Optional[str]:
    """Resolve the concrete lifecycle action to export from plan metadata."""
    plan_meta = manifest.get("plan", {})
    lifecycle = str(plan_meta.get("lifecycle", "") or "").strip().lower()
    decisions = manifest.get("decisions", {})

    if lifecycle == "archive":
        return "archive"

    if lifecycle == "manual":
        action = str(
            plan_meta.get("lifecycle_action")
            or decisions.get("lifecycle_action")
            or ""
        ).strip().lower()
        if action in {"archive", "delete"}:
            return action
        return None

    # 'cleanup', 'gitignore', and 'active' are valid planning-time lifecycle
    # values but require no synthesized lifecycle task during export:
    # - cleanup: the Cleanup phase already exists as a real phase in the plan
    # - gitignore: a planning-time repo hygiene action, not an export concern
    # - active: a plan status indicator, not an export lifecycle action
    if lifecycle in {"active", "cleanup", "gitignore"}:
        return None

    if lifecycle:
        raise ValueError(
            f"Unrecognized plan.lifecycle value '{lifecycle}'. "
            f"Supported values: 'active', 'archive', 'cleanup', 'gitignore', 'manual'. "
            f"Use lifecycle = 'manual' with lifecycle_action = 'delete' for delete semantics."
        )

    return None


def _format_task_dependency_label(phase_numbers: list[int]) -> str:
    """Format a human-readable dependency label from sorted phase numbers."""
    nums = sorted(phase_numbers)
    if not nums:
        return ""
    if nums == list(range(nums[0], nums[-1] + 1)):
        return f"Tasks {nums[0]}-{nums[-1]}"
    return "Tasks " + ", ".join(str(n) for n in nums)


def _generate_lifecycle_task(
    manifest: dict, plan_dir: str, task_num: int, phase_numbers: list[int] | None = None,
) -> Optional[str]:
    """Generate a synthesized final lifecycle task for exported plans."""
    plan_meta = manifest.get("plan", {})
    lifecycle_action = _resolve_lifecycle_action(manifest)

    if lifecycle_action not in {"archive", "delete"}:
        return None

    plan_manifest_ref = _format_phase_reference_path(Path(plan_dir) / "plan.toml", plan_dir)
    active_plan_dir = _resolve_plan_manifest_path(
        str(plan_meta.get("active_plan_dir") or plan_meta.get("plan_dir") or plan_dir),
        plan_dir,
    )
    active_plan_ref = _format_phase_reference_path(active_plan_dir, plan_dir)
    _phase_numbers = sorted(phase_numbers) if phase_numbers else []

    if lifecycle_action == "archive":
        archive_dir = active_plan_dir.parent / ".archive" / active_plan_dir.name
        archive_ref = _format_phase_reference_path(archive_dir, plan_dir)
        lines = [
            f"### Task {task_num}: Plan lifecycle — archive plan files",
            "",
            "**Original Plan Manifest:**",
            f"- `{plan_manifest_ref}`",
            "",
            "**Execution Prompt:**",
            "- [ ] Run this task only after all prior delegated tasks complete successfully.",
            "- [ ] Re-read `plan.toml` and treat `plan.lifecycle`, `plan.lifecycle_status`, `plan_dir`, and `active_plan_dir` as authoritative.",
            "- [ ] Set `lifecycle_status = \"ready\"` before moving the completed plan directory.",
            f"- [ ] Move the active plan directory from `{active_plan_ref}` to `{archive_ref}`.",
            "- [ ] Update the moved `plan.toml` so `active_plan_dir` points at the archived location and `lifecycle_status = \"done\"`.",
            "- [ ] If archiving fails, report the lifecycle task as failed and leave delivery outputs untouched.",
            "",
            "**Phase Focus:**",
            "- Finalize plan-file lifecycle handling by archiving the completed plan directory.",
            "",
        ]
        if _phase_numbers:
            dep_label = _format_task_dependency_label(_phase_numbers)
            lines.extend([
                "**Dependencies:**",
                f"- Run after {dep_label} complete successfully.",
                "",
            ])
        lines.extend([
            "**Success Checks:**",
            f"- `{archive_ref}` exists.",
            "- The archived `plan.toml` records the archived `active_plan_dir`.",
            "- `lifecycle_status` is `done`.",
            "",
            "**Ignore:**",
            "- Do not modify delivery outputs produced by earlier tasks.",
            "- Do not archive the plan if any earlier delegated task failed or remains incomplete.",
            "",
        ])
        return "\n".join(lines).rstrip()

    lines = [
        f"### Task {task_num}: Plan lifecycle — delete plan files",
        "",
        "**Original Plan Manifest:**",
        f"- `{plan_manifest_ref}`",
        "",
        "**Execution Prompt:**",
        "- [ ] Run this task only after all prior delegated tasks complete successfully.",
        "- [ ] Re-read `plan.toml` and treat `plan.lifecycle`, `plan.lifecycle_status`, `plan_dir`, and `active_plan_dir` as authoritative.",
        f"- [ ] Delete the active plan directory at `{active_plan_ref}` after confirming the delivery work is complete.",
        "- [ ] Remove only plan-tracking files; leave delivery outputs in the project intact.",
        "- [ ] Because the plan directory is deleted, do not attempt a follow-up manifest update on disk.",
        "",
        "**Phase Focus:**",
        "- Finalize plan-file lifecycle handling by deleting the completed plan directory.",
        "",
    ]
    if _phase_numbers:
        dep_label = _format_task_dependency_label(_phase_numbers)
        lines.extend([
            "**Dependencies:**",
            f"- Run after {dep_label} complete successfully.",
            "",
        ])
    lines.extend([
        "**Success Checks:**",
        f"- `{active_plan_ref}` no longer exists.",
        "- Delivery outputs from earlier tasks remain intact.",
        "",
        "**Ignore:**",
        "- Do not delete project files outside the plan directory.",
        "- Do not delete the plan if any earlier delegated task failed or remains incomplete.",
        "",
    ])
    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------------------
# Delegation orchestration — plans_dir resolution, mode selection, preconditions
# ---------------------------------------------------------------------------


def resolve_plans_dir(
    repo_root: str,
    override: Optional[str] = None,
    default_dir: Optional[str] = None,
) -> str:
    """Resolve the ralphex plans directory from config precedence.

    Search order:
    1. Explicit *override* (CLI flag or caller-supplied value)
    2. Local ``.ralphex/config`` in the repo root
    3. Global ``~/.config/ralphex/config`` (respects ``XDG_CONFIG_HOME``)
    4. Caller-provided *default_dir* if supplied
    5. Default ``docs/plans/``

    Args:
        repo_root: Absolute path to the repository root.
        override: Optional explicit plans directory that takes highest priority.
        default_dir: Optional fallback plans directory used only when no
            override or ralphex config value exists.

    Returns:
        Absolute path to the resolved plans directory.
    """
    if override is not None:
        plans_dir = override
    else:
        plans_dir = _read_plans_dir_from_config(
            Path(repo_root) / ".ralphex" / "config"
        )
        if plans_dir is None:
            xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            plans_dir = _read_plans_dir_from_config(
                Path(xdg) / "ralphex" / "config"
            )
        if plans_dir is None:
            plans_dir = default_dir if default_dir is not None else "docs/plans"

    if os.path.isabs(plans_dir):
        return plans_dir
    return os.path.join(repo_root, plans_dir)


def build_delegation_command(
    ralphex_path: str,
    plan_file: Optional[str],
    mode: str,
    worktree: bool = False,
    serve: bool = False,
) -> list[str]:
    """Build the ralphex CLI command for a delegation mode.

    Mode constraints:
    - ``execute``: ``ralphex <plan.md> [--worktree] [--serve]``
    - ``tasks-only``: ``ralphex <plan.md> --tasks-only [--worktree] [--serve]``
    - ``review``: ``ralphex --review [plan.md]`` — ``--worktree`` is NOT appended

    Args:
        ralphex_path: Absolute path to the ralphex executable.
        plan_file: Path to the exported plan file, or None for review-only.
        mode: One of ``"execute"``, ``"tasks-only"``, ``"review"``.
        worktree: Whether to request worktree isolation.
        serve: Whether to request dashboard serving.

    Returns:
        List of command arguments suitable for ``subprocess.run``.
    """
    cmd: list[str] = [ralphex_path]

    if mode == "review":
        cmd.append("--review")
        if plan_file:
            cmd.append(plan_file)
    else:
        if plan_file:
            cmd.append(plan_file)
        if mode == "tasks-only":
            cmd.append("--tasks-only")
        # --worktree valid only for execute and tasks-only
        if worktree:
            cmd.append("--worktree")

    # --serve is valid for execute and tasks-only, not review
    if serve and mode != "review":
        cmd.append("--serve")

    return cmd


def check_review_precondition(default_branch: str = "main", repo_root: str | None = None) -> dict:
    """Check that the current branch has committed changes for review.

    Verifies that ``HEAD`` has commits ahead of *default_branch* by running
    ``git rev-list {default_branch}..HEAD``.

    Args:
        default_branch: Name of the default branch to diff against.
        repo_root: Repository root to run the git command in. If ``None``,
            uses the process's current working directory.

    Returns:
        Dict with keys:
        - ``ok``: bool — True if review precondition is met
        - ``commit_count``: int — number of commits ahead (0 on error)
        - ``message``: str — human-readable status
    """
    try:
        proc = subprocess.run(
            ["git", "rev-list", f"{default_branch}..HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_root,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("Review precondition check failed: %s", exc)
        return {
            "ok": False,
            "commit_count": 0,
            "message": f"Failed to check git history: {exc}",
        }

    if proc.returncode != 0:
        logger.warning("git rev-list failed: %s", proc.stderr.strip())
        return {
            "ok": False,
            "commit_count": 0,
            "message": f"Failed to check git history: {proc.stderr.strip()}",
        }

    commits = [line for line in proc.stdout.strip().splitlines() if line]
    if not commits:
        return {
            "ok": False,
            "commit_count": 0,
            "message": (
                f"No committed changes ahead of {default_branch}. "
                "Review mode requires committed changes on the feature branch."
            ),
        }

    return {
        "ok": True,
        "commit_count": len(commits),
        "message": f"{len(commits)} commit(s) ahead of {default_branch}, ready for review.",
    }


# ---------------------------------------------------------------------------
# Post-run handoff — exit status, completed plans, validation, reporting
# ---------------------------------------------------------------------------


def _classify_exit_status(exit_code: int, partial: bool) -> str:
    """Return ``"success"``, ``"partial"``, or ``"failed"`` from *exit_code*."""
    if exit_code == 0:
        return "success"
    return "partial" if partial else "failed"


# @cpt-begin:inst-read-status
def read_handoff_status(
    exit_code: int,
    output_refs: list[str],
    partial: bool = False,
) -> dict:
    """Read ralphex exit status and classify delegation outcome.

    Args:
        exit_code: The ralphex process exit code.
        output_refs: List of output reference paths from the delegation run.
        partial: If True and exit_code != 0, report partial rather than failed.

    Returns:
        Dict with keys ``status``, ``exit_code``, ``output_refs``.
    """
    return {
        "status": _classify_exit_status(exit_code, partial),
        "exit_code": exit_code,
        "output_refs": output_refs,
    }
# @cpt-end:inst-read-status


# @cpt-begin:inst-check-completed
def check_completed_plans(plans_dir: str, task_slug: str) -> dict:
    """Check the ralphex-managed ``completed/`` subdirectory for lifecycle artifacts.

    Args:
        plans_dir: Resolved plans directory (absolute path).
        task_slug: The task slug to look for in ``completed/``.

    Returns:
        Dict with keys:
        - ``found``: bool — whether the task's completed plan exists
        - ``completed_path``: str or None — path to the completed plan
        - ``artifacts``: list[str] — all files in ``completed/``
    """
    completed_dir = Path(plans_dir) / "completed"
    if not completed_dir.is_dir():
        return {"found": False, "completed_path": None, "artifacts": []}

    artifacts = sorted(f.name for f in completed_dir.iterdir() if f.is_file())
    target = f"{task_slug}.md"
    found = target in artifacts
    completed_path = str(completed_dir / target) if found else None

    logger.info(
        "Completed plans check: found=%s, artifacts=%d, dir=%s",
        found, len(artifacts), completed_dir,
    )
    return {"found": found, "completed_path": completed_path, "artifacts": artifacts}
# @cpt-end:inst-check-completed


# @cpt-begin:inst-run-validation
def run_validation_commands(commands: list[str], cwd: Optional[str] = None) -> dict:
    """Re-run deterministic validation commands from the original Cypilot plan.

    Executes each command independently and aggregates results. All commands
    are run regardless of individual failures.

    Trust boundary: commands originate from developer-authored plan manifests
    (``plan.toml`` validation_commands or derived from output_files). They are
    NOT user-supplied at runtime. ``shell=True`` is intentional because
    validation commands may use shell syntax (pipes, globs, ``&&``).

    Args:
        commands: Shell command strings to execute (e.g. ``["python -m pytest tests/"]``).
        cwd: Working directory for command execution. When ``None``, inherits
            the current process working directory. Should be set to the
            delegated repository root so repo-relative commands resolve correctly.

    Returns:
        Dict with keys:
        - ``passed``: bool — True if all commands returned exit code 0
        - ``results``: list of per-command result dicts with ``command``,
          ``returncode``, ``stdout``, ``stderr``, ``error``
    """
    if not commands:
        return {"passed": True, "results": []}

    results: list[dict] = []
    all_passed = True

    for cmd in commands:
        if not isinstance(cmd, str) or not cmd.strip():
            results.append({
                "command": cmd,
                "returncode": -1,
                "stdout": "",
                "stderr": "",
                "error": "Skipped: empty or non-string command",
            })
            all_passed = False
            continue
        logger.info("Running validation command: %s", cmd)
        entry: dict = {"command": cmd, "returncode": -1, "stdout": "", "stderr": "", "error": ""}
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=cwd,
                check=False,
            )
            entry["returncode"] = proc.returncode
            entry["stdout"] = proc.stdout
            entry["stderr"] = proc.stderr
            if proc.returncode != 0:
                all_passed = False
        except subprocess.TimeoutExpired:
            entry["error"] = f"Timeout after 120s: {cmd}"
            all_passed = False
        except OSError as exc:
            entry["error"] = f"OS error running {cmd}: {exc}"
            all_passed = False

        results.append(entry)

    return {"passed": all_passed, "results": results}
# @cpt-end:inst-run-validation


# @cpt-begin:inst-report-handoff
def report_handoff(
    plan_file: str,
    mode: str,
    exit_code: int,
    output_refs: list[str],
    completed_plan_path: Optional[str],
    validation_passed: bool,
    partial: bool = False,
) -> dict:
    """Assemble a delegation summary report after ralphex completes.

    Args:
        plan_file: Path to the exported plan file.
        mode: Delegation mode used (execute, tasks-only, review).
        exit_code: The ralphex process exit code.
        output_refs: Output reference paths from the run.
        completed_plan_path: Path to the completed plan in ``completed/``, or None.
        validation_passed: Whether Cypilot validation commands passed.
        partial: If True and exit_code != 0, report partial status.

    Returns:
        Dict summarizing the delegation outcome.
    """
    return {
        "status": _classify_exit_status(exit_code, partial),
        "plan_file": plan_file,
        "mode": mode,
        "exit_code": exit_code,
        "output_refs": output_refs,
        "completed_plan_path": completed_plan_path,
        "validation_passed": validation_passed,
    }
# @cpt-end:inst-report-handoff


# ---------------------------------------------------------------------------
# Delegation lifecycle state machine
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-state-ralphex-delegation-lifecycle:p1
_VALID_TRANSITIONS: dict[str, list[str]] = {
    "not_exported": ["exported", "failed"],  # inst-export / inst-fail (review mode)
    "exported": ["delegated", "failed"],  # inst-delegate / inst-fail
    "delegated": ["completed", "failed"],  # inst-complete / inst-fail
    "failed": ["exported"],             # inst-re-export
    "completed": [],
}


class DelegationLifecycle:
    """Track delegation lifecycle state transitions.

    States: not_exported, exported, delegated, completed, failed.

    Transitions:
    - not_exported → exported (plan compiled and written)
    - exported → delegated (ralphex invoked)
    - exported → failed (error during post-export steps, e.g. review artifacts)
    - delegated → completed (success + validation passes)
    - delegated → failed (error or validation fails)
    - failed → exported (re-export after fixing)
    """

    def __init__(self) -> None:
        self.state: str = "not_exported"
        self.history: list[tuple[str, str]] = []

    def _transition(self, target: str) -> None:
        """Execute a state transition, raising ValueError if invalid."""
        valid = _VALID_TRANSITIONS.get(self.state, [])
        if target not in valid:
            raise ValueError(
                f"Invalid transition: {self.state} → {target}. "
                f"Valid targets: {valid}"
            )
        old = self.state
        self.state = target
        self.history.append((old, target))
        logger.info("Lifecycle transition: %s → %s", old, target)

    # @cpt-begin:inst-export
    def export(self) -> None:
        """Transition to exported (from not_exported or failed)."""
        self._transition("exported")
    # @cpt-end:inst-export

    # @cpt-begin:inst-delegate
    def delegate(self) -> None:
        """Transition to delegated (from exported)."""
        self._transition("delegated")
    # @cpt-end:inst-delegate

    # @cpt-begin:inst-complete
    def complete(self) -> None:
        """Transition to completed (from delegated)."""
        self._transition("completed")
    # @cpt-end:inst-complete

    # @cpt-begin:inst-fail
    def fail(self) -> None:
        """Transition to failed (from delegated)."""
        self._transition("failed")
    # @cpt-end:inst-fail
# @cpt-end:cpt-cypilot-state-ralphex-delegation-lifecycle:p1


# ---------------------------------------------------------------------------
# Bootstrap detection — opt-in .ralphex/config gate
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-dod-ralphex-delegation-bootstrap:p1
def check_bootstrap_needed(repo_root: str) -> dict:
    """Detect whether ralphex bootstrap (``ralphex --init``) is needed.

    Checks for the presence of ``.ralphex/config`` in the repo root.
    NEVER executes ``ralphex --init`` automatically — only reports the need
    and requests explicit user approval.

    Args:
        repo_root: Absolute path to the repository root.

    Returns:
        Dict with keys:
        - ``needed``: bool — True if ``.ralphex/config`` is missing
        - ``message``: str — user-facing message explaining the situation
    """
    config_path = Path(repo_root) / ".ralphex" / "config"
    if config_path.is_file():
        return {
            "needed": False,
            "message": f"ralphex config found at {config_path}",
        }

    return {
        "needed": True,
        "message": (
            "Local ralphex configuration is missing (.ralphex/config not found). "
            "To initialize, run `ralphex --init` in the repo root. "
            "This requires your explicit approval — Cypilot will never run "
            "`ralphex --init` automatically."
        ),
    }
# @cpt-end:cpt-cypilot-dod-ralphex-delegation-bootstrap:p1


# ---------------------------------------------------------------------------
# Canonical runtime orchestration entrypoint
# ---------------------------------------------------------------------------

def run_delegation(
    config: dict,
    plan_dir: str,
    repo_root: str,
    mode: str = "execute",
    worktree: bool = False,
    serve: bool = True,
    default_branch: str = "main",
    config_path: Optional[Path] = None,
    dry_run: bool = False,
    plans_dir_override: Optional[str] = None,
    stream_output: bool = False,
) -> dict:
    """Canonical runtime entrypoint for ralphex delegation.

    Orchestrates the full delegation flow by composing existing helpers:

    1. Discover ralphex executable (via :func:`ralphex_discover.discover`)
    2. Validate availability (via :func:`ralphex_discover.validate`)
    3. Persist discovered path (via :func:`ralphex_discover.persist_path`)
    4. Check bootstrap gate (via :func:`check_bootstrap_needed`)
    5. Check review precondition if mode is ``review``
    6. Compile plan (via :func:`compile_delegation_plan`)
    7. Resolve plans directory and write exported plan
    8. Build delegation command (via :func:`build_delegation_command`)
    9. Track lifecycle state transitions

    When *dry_run* is True, the command is assembled but not executed.
    When *stream_output* is True, the ralphex subprocess inherits the current
    stdin/stdout/stderr streams so interactive prompts and live output are
    visible to the caller.
    Subprocess invocation (step 10) and post-run handoff are intentionally
    separated — handoff occurs after ralphex completes and is called via
    :func:`read_handoff_status`, :func:`run_validation_commands`, and
    :func:`report_handoff`.

    Args:
        config: Parsed core.toml data dict.
        plan_dir: Path to the Cypilot plan directory containing ``plan.toml``.
        repo_root: Absolute path to the repository root.
        mode: Delegation mode — ``"execute"``, ``"tasks-only"``, or ``"review"``.
        worktree: Whether to request worktree isolation.
        serve: Whether to request dashboard serving.
        default_branch: Default branch name for review precondition check.
        config_path: Optional path to core.toml for persisting discovered path.
        dry_run: If True, assemble the command but do not invoke ralphex.
        plans_dir_override: Explicit plans directory override (highest precedence).

    Returns:
        Dict with keys:

        - ``status``: ``"ready"`` (dry_run), ``"delegated"``, or ``"error"``
        - ``ralphex_path``: discovered executable path or None
        - ``validation``: ralphex availability validation result
        - ``bootstrap``: bootstrap check result
        - ``plan_file``: path to the written exported plan (or None)
        - ``command``: assembled command list
        - ``mode``: delegation mode used
        - ``lifecycle_state``: final lifecycle state
        - ``error``: error message if status is ``"error"``
    """
    from .ralphex_discover import discover, validate, persist_path as _persist_path

    result: dict = {
        "status": "error",
        "ralphex_path": None,
        "validation": None,
        "bootstrap": None,
        "plan_file": None,
        "command": [],
        "mode": mode,
        "dashboard_url": None,
        "lifecycle_state": "not_exported",
        "error": None,
    }

    lifecycle = DelegationLifecycle()

    # 1. Discover
    ralphex_path = discover(config)
    result["ralphex_path"] = ralphex_path

    # 2. Validate
    validation = validate(ralphex_path)
    result["validation"] = validation

    if validation["status"] != "available":
        result["error"] = validation["message"]
        return result

    # 3. Bootstrap gate (blocking — fail if not initialized)
    bootstrap = check_bootstrap_needed(repo_root)
    result["bootstrap"] = bootstrap
    if bootstrap["needed"]:
        result["error"] = bootstrap["message"]
        return result

    # 4. Persist discovered path (after bootstrap gate to avoid dirtying
    #    the worktree with a machine-specific path on uninitialized repos)
    if config_path is not None and ralphex_path is not None:
        _persist_path(config_path, ralphex_path)

    # 5. Review precondition
    if mode == "review":
        precondition = check_review_precondition(default_branch, repo_root=repo_root)
        if not precondition["ok"]:
            result["error"] = precondition["message"]
            return result

    # 6. Compile plan (skip for review-only — no compilable plan needed)
    plan_content: Optional[str] = None
    plan_file: Optional[str] = None
    if mode != "review":
        try:
            plan_content = compile_delegation_plan(plan_dir)
        except (FileNotFoundError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
            result["error"] = str(exc)
            return result

    # 7. Resolve plans dir and write (only when a plan was compiled)
    if plan_content is not None:
        plans_dir = resolve_plans_dir(
            repo_root,
            override=plans_dir_override,
        )
        plan_path = Path(plans_dir)

        try:
            plan_path.mkdir(parents=True, exist_ok=True)

            # Extract task name from compiled plan title (avoids re-reading plan.toml)
            first_line = plan_content.split("\n", 1)[0]
            task = first_line.removeprefix("# ").strip() or "delegation"
            task_slug = re.sub(r"[^a-z0-9]+", "-", task.lower()).strip("-")
            if not task_slug:
                task_slug = "delegation"

            plan_file = str(plan_path / f"{task_slug}.md")
            Path(plan_file).write_text(plan_content, encoding="utf-8")
        except OSError as exc:
            result["status"] = "error"
            result["error"] = f"Failed to write plan to {plans_dir}: {exc}"
            result["plan_file"] = None
            return result

        result["plan_file"] = plan_file

        lifecycle.export()
        result["lifecycle_state"] = lifecycle.state
        logger.info("Exported plan to %s", plan_file)

    # 7b. Generate review artifacts when in review mode
    if mode == "review":
        try:
            review_result = generate_review_artifacts(plan_dir, repo_root)
            result["review_artifacts"] = review_result
            logger.info(
                "Generated %d review artifact(s) for %s mode",
                len(review_result["artifacts"]),
                mode,
            )
        except OSError as exc:
            lifecycle.fail()
            if plan_file is not None:
                try:
                    Path(plan_file).unlink(missing_ok=True)
                except OSError:
                    pass
            result["plan_file"] = None
            result["status"] = "error"
            result["lifecycle_state"] = lifecycle.state
            result["error"] = f"Failed to generate review artifacts: {exc}"
            return result

    # 8. Build command
    command = build_delegation_command(
        ralphex_path, plan_file, mode, worktree=worktree, serve=serve,
    )
    result["command"] = command
    if serve and mode != "review":
        port = os.environ.get("RALPHEX_PORT", "8080").strip() or "8080"
        result["dashboard_url"] = f"http://localhost:{port}"

    # 9. Execute or return ready
    if dry_run:
        result["status"] = "ready"
        return result

    # 10. Invoke ralphex subprocess
    lifecycle.delegate()
    result["lifecycle_state"] = lifecycle.state
    logger.info("Delegation command: %s", " ".join(command))

    max_non_interactive_retries = 2  # cap total wait at ~3 hours in CI
    non_interactive_retries = 0

    def _should_continue_after_timeout(timeout_seconds: int) -> bool:
        nonlocal non_interactive_retries
        if not sys.stdin.isatty():
            non_interactive_retries += 1
            if non_interactive_retries > max_non_interactive_retries:
                logger.warning(
                    "ralphex still running after %d seconds in non-interactive mode; "
                    "giving up after %d retries",
                    timeout_seconds * (max_non_interactive_retries + 1),
                    max_non_interactive_retries,
                )
                return False
            return True
        sys.stderr.write(
            "\n"
            f"ralphex is still running after {timeout_seconds} seconds. "
            "Continue waiting? [y] [n] [Enter=continue]: "
        )
        sys.stderr.flush()
        try:
            tty = open("/dev/tty", "r")  # noqa: SIM115
            try:
                answer = tty.readline().strip().lower()
            finally:
                tty.close()
        except OSError:
            # /dev/tty unavailable (e.g. Windows) — fall back to stdin
            try:
                answer = input().strip().lower()
            except EOFError:
                return True
            except KeyboardInterrupt:
                return False
        except KeyboardInterrupt:
            return False
        return answer not in ("n", "no")

    try:
        if stream_output:
            proc = subprocess.Popen(command)
        else:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

        timeout_seconds = 3600
        while True:
            try:
                stdout, stderr = proc.communicate(timeout=timeout_seconds)
                break
            except subprocess.TimeoutExpired:
                if _should_continue_after_timeout(timeout_seconds):
                    continue
                proc.terminate()
                try:
                    stdout, stderr = proc.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                lifecycle.fail()
                result["status"] = "error"
                result["lifecycle_state"] = lifecycle.state
                result["returncode"] = proc.returncode
                result["stdout"] = None if stream_output else stdout
                result["stderr"] = None if stream_output else stderr
                result["error"] = (
                    f"ralphex timed out after {timeout_seconds} seconds and was stopped"
                )
                return result

        result["stdout"] = None if stream_output else stdout
        result["stderr"] = None if stream_output else stderr
        result["returncode"] = proc.returncode
        if proc.returncode == 0:
            lifecycle.complete()
            result["status"] = "delegated"
            result["lifecycle_state"] = lifecycle.state
        else:
            lifecycle.fail()
            result["status"] = "error"
            result["lifecycle_state"] = lifecycle.state
            if stream_output:
                result["error"] = f"ralphex exited with code {proc.returncode}"
            else:
                result["error"] = (
                    f"ralphex exited with code {proc.returncode}: "
                    f"{(stderr or '').strip() or (stdout or '').strip()}"
                )
    except FileNotFoundError:
        lifecycle.fail()
        result["status"] = "error"
        result["lifecycle_state"] = lifecycle.state
        result["error"] = f"ralphex executable not found at: {command[0]}"
    except OSError as exc:
        lifecycle.fail()
        result["status"] = "error"
        result["lifecycle_state"] = lifecycle.state
        result["error"] = f"Failed to invoke ralphex: {exc}"

    return result


# ---------------------------------------------------------------------------
# Review artifact generation — derived .ralphex review overrides
# ---------------------------------------------------------------------------

REVIEW_PROMPT_RELATIVES = (
    ".ralphex/prompts/review_first.txt",
    ".ralphex/prompts/review_second.txt",
)
_REVIEW_OVERRIDE_BEGIN = "<!-- @cpt-begin:cypilot-review-override -->"
_REVIEW_OVERRIDE_END = "<!-- @cpt-end:cypilot-review-override -->"
_REVIEW_OVERRIDE_INTRO = (
    "Cypilot-managed final review step."
)


def generate_review_artifacts(plan_dir: str, repo_root: str) -> dict:  # pylint: disable=unused-argument
    """Generate derived review override artifacts for ralphex review mode.

    Injects a managed final analyze step into local ralphex review prompts.

    Args:
        plan_dir: Path to the Cypilot plan directory containing ``plan.toml``.
        repo_root: Absolute path to the project/repository root.

    Returns:
        Dict with keys:
        - ``artifacts``: list of absolute paths to generated artifacts
        - ``relative_paths``: list of project-root-relative paths
    """
    root = Path(repo_root)
    analyze_workflow = _resolve_analyze_workflow_path(root)
    managed_prompt_paths = _sync_review_override_prompts(root, analyze_workflow)

    logger.info("Injected Cypilot final analyze step into %d review prompt(s)", len(managed_prompt_paths))

    return {
        "artifacts": [str(path) for path in managed_prompt_paths],
        "relative_paths": list(REVIEW_PROMPT_RELATIVES),
    }


def _resolve_analyze_workflow_path(repo_root: Path) -> str:
    adapter_rel = _read_cypilot_var(repo_root)
    candidates: list[str] = []
    if adapter_rel:
        candidates.append(adapter_rel)
    for candidate in ("cypilot", ".cypilot", ".bootstrap", ".cpt"):
        if candidate not in candidates:
            candidates.append(candidate)

    for candidate in candidates:
        adapter_root = repo_root / candidate
        analyze_workflow = core_subpath(adapter_root, "workflows", "analyze.md")
        if analyze_workflow.is_file():
            return analyze_workflow.relative_to(repo_root).as_posix()

    raise OSError(
        "Could not resolve Cypilot install directory for final analyze step. "
        "Ensure root AGENTS.md defines `cypilot_path` or install Cypilot in a standard adapter directory."
    )


def _sync_review_override_prompts(repo_root: Path, analyze_workflow: str) -> list[Path]:
    managed_block = _compose_managed_review_block(analyze_workflow)

    # Phase 1: validate all prompts exist and collect updated contents
    updates: list[tuple[Path, str]] = []
    for relative_path in REVIEW_PROMPT_RELATIVES:
        prompt_path = repo_root / relative_path
        if not prompt_path.is_file():
            raise OSError(
                f"Missing ralphex review prompt: {prompt_path}. "
                "Re-run `ralphex --init` in the repo root."
            )
        existing = prompt_path.read_text(encoding="utf-8")
        updates.append((prompt_path, _upsert_managed_review_block(existing, managed_block)))

    # Phase 2: write to temp files, then atomically replace originals
    temp_files: list[Path] = []
    try:
        for prompt_path, content in updates:
            tmp = prompt_path.with_suffix(prompt_path.suffix + ".tmp")
            tmp.write_text(content, encoding="utf-8")
            temp_files.append(tmp)
        for (prompt_path, _content), tmp in zip(updates, temp_files):
            tmp.replace(prompt_path)
    except OSError:
        for tmp in temp_files:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    return [p for p, _ in updates]


def _compose_managed_review_block(analyze_workflow: str) -> str:
    return "\n".join(
        [
            _REVIEW_OVERRIDE_BEGIN,
            _REVIEW_OVERRIDE_INTRO,
            "",
            f"- Final review step: load and follow `{analyze_workflow}`.",
            "- Run this after the standard ralphex review flow and before deciding the final outcome.",
            f"- Immediately before loading analyze, output exactly: `CYPILOT_ANALYZE_START: {analyze_workflow}`.",
            "- After the analyze step completes, output exactly one of: `CYPILOT_ANALYZE_DONE: no_findings`, `CYPILOT_ANALYZE_DONE: findings_found`, or `CYPILOT_ANALYZE_DONE: unable_to_complete`.",
            "- Treat actionable issues from analyze like normal review findings: fix them, validate, commit, and do not emit `<<<RALPHEX:REVIEW_DONE>>>` in that iteration.",
            "- Never emit `<<<RALPHEX:REVIEW_DONE>>>` unless you already logged `CYPILOT_ANALYZE_DONE: no_findings` in the same iteration.",
            "- Emit `<<<RALPHEX:REVIEW_DONE>>>` only when both the standard ralphex review and the final analyze step find nothing to fix.",
            _REVIEW_OVERRIDE_END,
        ]
    )


def _upsert_managed_review_block(existing: str, managed_block: str) -> str:
    start = existing.find(_REVIEW_OVERRIDE_BEGIN)
    end = existing.find(_REVIEW_OVERRIDE_END, start if start != -1 else 0)
    if start != -1 and end != -1 and end >= start:
        end += len(_REVIEW_OVERRIDE_END)
        # Strip the leading newline from the tail to avoid accumulating
        # blank lines on repeated upserts.
        tail = existing[end:].lstrip("\n")
        if tail:
            tail = "\n" + tail
        updated = existing[:start] + managed_block + tail
        return updated.rstrip() + "\n"
    prefix = managed_block.rstrip() + "\n\n"
    return prefix + existing.lstrip("\n")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _read_plans_dir_from_config(config_path: Path) -> Optional[str]:
    """Read plans_dir from a ralphex config file.

    Expects a simple key=value format (``plans_dir = "path"``).
    Returns None if the file doesn't exist or has no plans_dir key.
    """
    if not config_path.is_file():
        return None
    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError:
        return None

    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r"plans_dir\b", stripped):
            # Parse: plans_dir = "value" or plans_dir = 'value' or plans_dir = value
            match = re.match(
                r'plans_dir\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^#\s]+))',
                stripped,
            )
            if match:
                value = (match.group(1) or match.group(2) or match.group(3) or "").strip()
                if value:
                    return value
    return None


def _extract_markdown_section_lines(content: str, section_name: str) -> list[str]:
    target_heading = f"## {section_name}"
    lines = content.splitlines()
    section_lines: list[str] = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_section:
                break
            if stripped == target_heading:
                in_section = True
            continue
        if in_section:
            section_lines.append(line)

    return section_lines


def _extract_fenced_toml_block(content: str) -> str:
    # Only match a ```toml fence at the very start of the file (frontmatter).
    stripped = content.lstrip("\ufeff")
    m = re.match(r"\s*```toml[ \t]*\r?\n(.*?)```", stripped, re.DOTALL)
    if not m:
        return ""
    return m.group(1)


def _parse_toml_frontmatter(content: str) -> dict:
    """Extract and parse TOML frontmatter from a phase file.

    Expects the TOML to be enclosed in a ```toml ... ``` code fence at the
    start of the file.
    """
    toml_block = _extract_fenced_toml_block(content)
    if not toml_block:
        return {}
    try:
        return tomllib.loads(toml_block)
    except (tomllib.TOMLDecodeError, ValueError):
        logger.warning("Failed to parse TOML frontmatter")
        return {}


def _extract_section_items(content: str, section_name: str) -> list[str]:
    """Extract items from a named Markdown section.

    For 'Task' sections, extracts numbered list items.
    For 'Acceptance Criteria' sections, extracts checkbox items.
    Stops at the next ## heading or end of content.
    """
    items: list[str] = []
    numbered_item_re = re.compile(r"^\d+\.\s+[^\n]+$")
    checkbox_item_re = re.compile(r"^-\s+\[[ xX]\]\s+[^\n]+$")

    for line in _extract_markdown_section_lines(content, section_name):
        stripped = line.strip()
        if numbered_item_re.fullmatch(stripped):
            _, _, item = stripped.partition(".")
            items.append(item.strip().rstrip("."))
            continue
        if checkbox_item_re.fullmatch(stripped):
            items.append(stripped.split("]", 1)[1].strip())
            continue

    return items


def _extract_section_body(content: str, section_name: str) -> str:
    """Extract plain-text body from a named Markdown section.

    Returns the normalized paragraph/list text between ``## {section_name}``
    and the next ``##`` heading, excluding empty lines.
    """
    lines = [line.strip() for line in _extract_markdown_section_lines(content, section_name) if line.strip()]
    return " ".join(lines)


def _distill_guidance(content: str) -> list[str]:
    """Extract bounded SDLC guidance from Rules section.

    Only includes items from Engineering and Quality subsections to keep
    the exported guidance bounded.
    """
    guidance: list[str] = []
    in_target_subsection = False
    subsection_header_re = re.compile(r"^###\s+[^\n]+$")

    for line in _extract_markdown_section_lines(content, "Rules"):
        stripped = line.strip()
        if subsection_header_re.fullmatch(stripped):
            subsection_name = stripped[4:].strip()
            in_target_subsection = subsection_name in _GUIDANCE_SUBSECTIONS
            continue

        if in_target_subsection and stripped.startswith("- "):
            item = stripped[2:].strip()
            if item:
                guidance.append(item)

    return guidance


def _generate_overview(plan_meta: dict, phases: list[dict]) -> str:
    """Generate a compact overview section from plan metadata."""
    plan_type = plan_meta.get("type", "unknown")
    phase_count = len(phases)
    phase_titles = ", ".join(p.get("title", f"Phase {p['number']}") for p in phases)

    return (
        f"**Type**: {plan_type} | **Phases**: {phase_count}\n\n"
        f"**Scope**: {phase_titles}"
    )


def extract_validation_commands(manifest: dict) -> list[str]:
    """Extract deterministic validation commands from a plan manifest.

    This is the canonical source for validation commands used both during
    plan export (``## Validation Commands`` section) and post-run handoff
    validation (``run_validation_commands``).

    Sources checked in priority order:

    1. **Plan-level** ``validation_commands`` — explicit commands in ``[plan]``
    2. **Phase-level** ``validation_commands`` — explicit commands per phase
    3. **Derived** — collected from ``output_files`` matching ``tests/*.py``

    Args:
        manifest: Parsed ``plan.toml`` data dict.

    Returns:
        Ordered list of shell command strings.
    """
    # 1. Plan-level explicit commands (highest priority)
    plan_cmds = manifest.get("plan", {}).get("validation_commands", [])
    if plan_cmds:
        return list(plan_cmds)

    # 2. Phase-level explicit commands
    phase_cmds: list[str] = []
    for phase in manifest.get("phases", []):
        phase_cmds.extend(phase.get("validation_commands", []))
    if phase_cmds:
        return phase_cmds

    # 3. Derive from output_files — collect unique test files
    test_files: list[str] = []
    seen: set[str] = set()
    for phase in manifest.get("phases", []):
        for fp in phase.get("output_files", []):
            if fp.startswith("tests/") and fp.endswith(".py") and fp not in seen:
                test_files.append(fp)
                seen.add(fp)

    if test_files:
        return [f"python -m pytest {' '.join(sorted(test_files))}"]

    return []


def _generate_validation_section(manifest: dict) -> str:
    """Generate ``## Validation Commands`` section from the deterministic contract.

    Delegates to :func:`extract_validation_commands` for command derivation.

    Args:
        manifest: Parsed ``plan.toml`` data dict.

    Returns:
        Formatted Markdown section string.
    """
    commands = extract_validation_commands(manifest)
    lines = ["## Validation Commands", ""]

    if commands:
        lines.append("```bash")
        for cmd in commands:
            lines.append(cmd)
        lines.append("```")
    else:
        lines.append("No validation commands defined.")

    return "\n".join(lines)


def _resolve_paths(content: str, plan_dir: str) -> str:
    """Resolve absolute file paths to project-root-relative forms.

    Strips the plan directory prefix and any parent project path from
    file references in the output.
    """
    input_plan_path = Path(plan_dir)
    plan_path = input_plan_path.resolve()

    project_root = _find_project_root(plan_path)

    root_candidates = [str(project_root)]
    plan_candidates = [str(plan_path)]
    raw_root = str(input_plan_path.parent)
    raw_plan = str(input_plan_path)
    if raw_root not in root_candidates:
        root_candidates.append(raw_root)
    if raw_plan not in plan_candidates:
        plan_candidates.append(raw_plan)

    # Replace absolute paths with relative ones.
    # Only strip path prefixes when followed by a separator (/ or \),
    # meaning they are part of a longer file path. Standalone occurrences
    # in prose text are left untouched to avoid corrupting content.
    result = content
    for plan_str in sorted(plan_candidates, key=len, reverse=True):
        for root_str in sorted(root_candidates, key=len, reverse=True):
            if plan_str != root_str:
                result = result.replace(plan_str + "/", "")
                result = result.replace(plan_str + "\\", "")
        result = result.replace(plan_str + "/", "")
        result = result.replace(plan_str + "\\", "")
    for root_str in sorted(root_candidates, key=len, reverse=True):
        result = result.replace(root_str + "/", "")
        result = result.replace(root_str + "\\", "")

    return result
