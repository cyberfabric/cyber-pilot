"""
Git utilities for workspace source resolution.

Handles parsing Git URLs, namespace mapping, clone operations,
and explicit sync operations using subprocess (stdlib-only constraint).

@cpt-algo:cpt-cypilot-algo-workspace-resolve-git-url:p1
@cpt-algo:cpt-cypilot-algo-workspace-sync-git-source:p1
@cpt-dod:cpt-cypilot-dod-workspace-git-url-sources:p1
@cpt-dod:cpt-cypilot-dod-workspace-sync:p1
"""

# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-datamodel
import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from .workspace import NamespaceRule, ResolveConfig, SourceEntry

# Patterns for parsing Git URLs
# HTTPS: https://gitlab.com/org/repo.git
_HTTPS_RE = re.compile(r"^https://([^/]+)/(.+?)(?:\.git)?$")
# SSH shorthand: git@gitlab.com:org/repo.git
_SSH_SHORT_RE = re.compile(r"^[\w.-]+@([^:]+):(.+?)(?:\.git)?$")
# SSH URL: ssh://git@gitlab.com/org/repo.git
_SSH_URL_RE = re.compile(r"^ssh://[\w.-]+@([^/]+)/(.+?)(?:\.git)?$")

_GIT_TIMEOUT = 120  # seconds


def _redact_url(url: str) -> str:
    """Strip credentials from a Git URL before displaying it."""
    # SCP-style SSH: user@host:path — redact the user part
    if "://" not in url and "@" in url and ":" in url:
        at_idx = url.index("@")
        return f"***{url[at_idx:]}"
    # Standard URLs: https://<user>:<token>@host/path
    from urllib.parse import urlsplit, urlunsplit
    parts = urlsplit(url)
    if parts.username or parts.password:
        netloc = parts.hostname or ""
        if parts.port:
            netloc += f":{parts.port}"
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    return url
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-datamodel


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-parse-url
def _parse_git_url(url: str) -> Optional[Tuple[str, str, str]]:
    """Parse a Git URL into (host, org, repo) components.

    Supports HTTPS, SSH shorthand (git@host:path), and ssh:// URLs.
    Returns None if the URL cannot be parsed.
    """
    for pattern in (_HTTPS_RE, _SSH_URL_RE, _SSH_SHORT_RE):
        m = pattern.match(url.strip())
        if m:
            host = m.group(1)
            path_part = m.group(2).strip("/")
            # Split path into org (everything before last /) and repo (last segment)
            parts = path_part.rsplit("/", 1)
            if len(parts) == 2:
                return (host, parts[0], parts[1])
            # Single segment: no org, just repo
            return (host, "", parts[0])
    return None
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-parse-url


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-lookup-namespace
def _lookup_namespace(host: str, rules: list) -> "Optional[NamespaceRule]":
    """Find a namespace rule matching the given host by exact match."""
    for rule in rules:
        if rule.host == host:
            return rule
    return None
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-lookup-namespace


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-apply-template
def _apply_template(template: str, org: str, repo: str) -> str:
    """Apply {org}/{repo} substitution to a namespace template.

    Raises ValueError if the result is an absolute path or contains '..'
    segments that could escape the workspace directory.
    """
    result = template.replace("{org}", org).replace("{repo}", repo)
    # Strip leading slash that appears when org is empty ("{org}/{repo}" → "/repo")
    result = result.lstrip("/")
    # Reject path traversal: absolute paths or ".." segments
    if not result or result.startswith("/") or ".." in Path(result).parts:
        raise ValueError(f"Unsafe path template result: {result!r}")
    return result
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-apply-template


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-clone-or-fetch
def _clone_if_missing(url: str, local_path: Path, branch: str) -> Optional[Path]:
    """Clone a git repo or return existing local path.

    For existing repos, returns local_path without network operations.
    Use sync_git_source() to fetch and update worktrees explicitly.
    Returns local_path on success, None on clone failure.
    """
    if _parse_git_url(url) is None:
        print(f"Warning: refusing to clone unrecognized URL: {_redact_url(url)}", file=sys.stderr)
        return None
    if local_path.is_dir() and (local_path / ".git").exists():
        return local_path
    # Clone
    clone_args = ["clone", "--quiet"]
    if branch != "HEAD":
        clone_args.extend(["--branch", branch])
    clone_args.extend([url, str(local_path)])
    rc, _out, err = _run_git(clone_args)
    if rc != 0:
        print(f"Warning: git clone failed for {_redact_url(url)}: {err}", file=sys.stderr)
        return None
    return local_path
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-clone-or-fetch


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-run-command
def _run_git(args: list, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a git command via subprocess with timeout.

    Returns (returncode, stdout, stderr).
    Returns (1, "", error_message) if git is not found.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT,
        )
        return (result.returncode, result.stdout, result.stderr)
    except FileNotFoundError:
        return (1, "", "git command not found")
    except subprocess.TimeoutExpired:
        return (1, "", f"git command timed out after {_GIT_TIMEOUT}s")
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-run-command


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-compute-path
def _compute_local_path(
    source: "SourceEntry",
    resolve_config: "ResolveConfig",
    workspace_parent: Path,
) -> Optional[Path]:
    """Compute the expected local directory path for a Git URL source.

    Shared core of resolve_git_source() and peek_git_source_path().
    Parses the URL, applies namespace rules, resolves the template,
    and verifies path safety. Never performs network I/O.
    Returns the expected local path or None if computation fails.
    """
    url = getattr(source, "url", None)
    if not url:
        return None

    parsed = _parse_git_url(url)
    if parsed is None:
        return None

    host, org, repo = parsed

    # Look up namespace rule (exact match → default fallback)
    namespace_rules = getattr(resolve_config, "namespace", []) or []
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-if-no-rule
    rule = _lookup_namespace(host, namespace_rules)
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-if-no-rule

    # Apply template and compute local path
    _DEFAULT_TEMPLATE = "{org}/{repo}"
    template = getattr(rule, "template", _DEFAULT_TEMPLATE) if rule else _DEFAULT_TEMPLATE
    try:
        templated = _apply_template(template, org, repo)
    except ValueError:
        return None

    workdir = getattr(resolve_config, "workdir", ".workspace-sources")
    local_path = (workspace_parent / workdir / templated).resolve()

    # Defence-in-depth: ensure resolved path is inside the workspace
    expected_base = (workspace_parent / workdir).resolve()
    try:
        local_path.relative_to(expected_base)
    except ValueError:
        return None

    return local_path
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-compute-path


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-determine-branch
# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-if-exists-fetch
# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-else-clone
# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-if-fail
# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-return-path
def resolve_git_source(
    source: "SourceEntry",
    resolve_config: "ResolveConfig",
    workspace_parent: Path,
) -> Optional[Path]:
    """Resolve a Git URL source to a local directory path.

    Parses the URL, applies namespace rules, clones on first access.
    For existing repos, returns local path without network operations.
    Use sync_git_source() to update worktrees explicitly.
    Returns the local path on success, None on failure (with stderr warning).
    """
    local_path = _compute_local_path(source, resolve_config, workspace_parent)
    if local_path is None:
        url = getattr(source, "url", None)
        if url:
            print(f"Warning: cannot compute local path for git URL: {_redact_url(url)}", file=sys.stderr)
        return None

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Warning: cannot create directory {local_path.parent}: {exc}", file=sys.stderr)
        return None

    # Determine branch
    branch = getattr(source, "branch", None) or "HEAD"

    # Clone or fetch
    return _clone_if_missing(getattr(source, "url", ""), local_path, branch)
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-return-path
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-if-fail
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-else-clone
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-if-exists-fetch
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-determine-branch


# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-resolve-path
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-no-path
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-not-repo
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-fetch
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-fetch-fail
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-determine-branch
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-head
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-else-branch
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-update-fail
# @cpt-begin:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-return-ok
def is_worktree_dirty(local_path: Path) -> bool:
    """Check if a git worktree has uncommitted changes.

    Returns True if there are staged, unstaged, or untracked changes.
    """
    rc, out, _err = _run_git(["status", "--porcelain"], cwd=local_path)
    if rc != 0:
        return True  # Assume dirty on error (safe default)
    return bool(out.strip())


def sync_git_source(
    source: "SourceEntry",
    resolve_config: "ResolveConfig",
    workspace_parent: Path,
    *,
    force: bool = False,
) -> dict:
    """Fetch and update worktree for a Git URL source.

    Resolves the local path (clone if needed), then fetches from origin
    and updates the worktree to match the remote branch.
    If the worktree has uncommitted changes, aborts unless force=True.

    WARNING: when force=True, uncommitted changes WILL be destroyed.
    For sources with no configured branch (HEAD mode), the update runs
    ``git reset --hard FETCH_HEAD`` which discards all local commits and
    working-tree changes.  For named branches, uses
    ``git checkout -B {branch} origin/{branch}`` which has the same effect.

    Returns dict with 'status' ('synced'|'failed') and optional 'error'.
    """
    local_path = resolve_git_source(source, resolve_config, workspace_parent)
    if local_path is None:
        return {"status": "failed", "error": "resolve failed"}

    if not local_path.is_dir() or not (local_path / ".git").exists():
        return {"status": "failed", "error": "not a git repo"}

    # Safety check: abort if worktree has uncommitted changes
    if not force and is_worktree_dirty(local_path):
        return {
            "status": "failed",
            "error": "dirty worktree — commit or stash changes, or use --force",
        }

    branch = getattr(source, "branch", None) or "HEAD"

    # Fetch from origin
    fetch_args = ["fetch", "--quiet", "origin"]
    if branch != "HEAD":
        fetch_args.append(branch)
    rc, _out, err = _run_git(fetch_args, cwd=local_path)
    if rc != 0:
        return {"status": "failed", "error": f"git fetch failed: {err}"}

    # Update worktree
    if branch == "HEAD":
        rc, _out, err = _run_git(["reset", "--hard", "FETCH_HEAD"], cwd=local_path)
    else:
        rc, _out, err = _run_git(
            ["checkout", "--quiet", "-B", branch, f"origin/{branch}"],
            cwd=local_path,
        )
    if rc != 0:
        return {"status": "failed", "error": f"git update failed: {err}"}

    return {"status": "synced"}
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-return-ok
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-update-fail
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-else-branch
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-head
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-determine-branch
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-fetch-fail
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-fetch
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-not-repo
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-if-no-path
# @cpt-end:cpt-cypilot-algo-workspace-sync-git-source:p1:inst-sync-resolve-path


def peek_git_source_path(
    source: "SourceEntry",
    resolve_config: "ResolveConfig",
    workspace_parent: Path,
) -> Optional[Path]:
    """Compute the expected local path for a Git URL source without cloning.

    Same path logic as resolve_git_source() but never performs network I/O.
    Returns the expected local path (which may or may not exist yet), or None
    if the URL cannot be parsed or the template produces an unsafe path.
    """
    return _compute_local_path(source, resolve_config, workspace_parent)


__all__ = [
    "is_worktree_dirty",
    "peek_git_source_path",
    "resolve_git_source",
    "sync_git_source",
]
