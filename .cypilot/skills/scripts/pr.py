#!/usr/bin/env python3
"""PR review helper – fetch PR diffs, metadata, and generate status reports.

Cypilot skill: lives in .cypilot/skills/scripts/pr.py
Resolves all paths relative to the project root (detected via git).

All review is done in read-only mode: the script downloads diffs and
metadata from GitHub but never modifies the local working tree.
"""

import json
import os
import re
import subprocess
import sys


def _find_project_root():
    """Find project root via git rev-parse."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    # Fallback: walk up from this script until a repo marker is found
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(current, ".git")):
            return current
        cfg = os.path.join(
            current, ".cypilot", ".cypilot-config.json",
        )
        if os.path.isfile(cfg):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Last resort: four levels up (original heuristic)
    return os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__),
                )
            )
        )
    )


ROOT = _find_project_root()

# Resolve adapter path from cypilot core config, then load PR config
_CYPILOT_CONFIG_PATH = os.path.join(
    ROOT, ".cypilot", ".cypilot-config.json",
)


def _load_pr_config():
    """Load PR review config from adapter's pr-review.json.

    Resolution order:
    1. {project_root}/{cypilotAdapterPath}/pr-review.json
    2. {project_root}/.cypilot-adapter/pr-review.json (default)
    """
    adapter_path = ".cypilot-adapter"
    if os.path.exists(_CYPILOT_CONFIG_PATH):
        with open(_CYPILOT_CONFIG_PATH) as f:
            core = json.load(f)
        adapter_path = core.get(
            "cypilotAdapterPath", adapter_path,
        )
    pr_cfg_path = os.path.join(
        ROOT, adapter_path, "pr-review.json",
    )
    if not os.path.exists(pr_cfg_path):
        return {}
    with open(pr_cfg_path) as f:
        return json.load(f)


_PR_CFG = _load_pr_config()

# PR data directory (default .prs/, overridable in pr-review.json)
PRS_DIR = os.path.join(
    ROOT, _PR_CFG.get("dataDir", ".prs"),
)
TEMPLATES_DIR = os.path.join(
    ROOT,
    _PR_CFG.get(
        "templatesDir", ".cypilot/templates/pr",
    ),
)
# Local config path (exclude list, etc.)
CONFIG_PATH = os.path.join(PRS_DIR, "config.yaml")


def _run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, **kwargs)
    if result.returncode != 0 and kwargs.get("check", False):
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result


def _load_exclude_list():
    """Load exclude_prs list from .prs/config.yaml.

    Parses lines under `exclude_prs:` that start with `- `.
    Returns a set of PR number strings.
    """
    excludes = set()
    if not os.path.exists(CONFIG_PATH):
        return excludes
    in_section = False
    with open(CONFIG_PATH) as f:
        for line in f:
            stripped = line.strip()
            if stripped == "exclude_prs:":
                in_section = True
                continue
            if in_section:
                if stripped.startswith("- "):
                    val = stripped[2:].strip().strip('"').strip("'")
                    if val:
                        excludes.add(val)
                elif stripped and not stripped.startswith("#"):
                    in_section = False
    return excludes


def _list_open_prs():
    """Return list of open PR numbers via gh CLI."""
    result = _run([
        "gh", "pr", "list",
        "--json", "number,title,author,state,url",
        "--limit", "100",
    ])
    if result.returncode != 0:
        print(
            f"Failed to list PRs: {result.stderr}",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(result.stdout)


def _owner_repo():
    """Return (owner, repo) from gh CLI."""
    r = _run([
        "gh", "repo", "view",
        "--json", "nameWithOwner",
        "-q", ".nameWithOwner",
    ])
    if r.returncode != 0:
        return None, None
    parts = r.stdout.strip().split("/", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (None, None)


_META_FIELDS = ",".join([
    "title", "body", "files", "comments",
    "reviews", "labels", "author", "state",
    "baseRefName", "headRefName",
    "url", "createdAt", "updatedAt",
    "reviewRequests", "statusCheckRollup",
    "mergeStateStatus", "reviewDecision",
])

_REVIEW_THREADS_QUERY = (
    "query($owner:String!,$repo:String!,$n:Int!){"
    "repository(owner:$owner,name:$repo){"
    "pullRequest(number:$n){"
    "reviewThreads(first:100){nodes{"
    "id isResolved isOutdated path line startLine "
    "comments(first:50){nodes{"
    "id author{login}body createdAt url"
    "}}}}"
    "}}}"
)


_PR_NUMBER_RE = re.compile(r"^\d+$")


def _validate_pr_number(pr_number: str) -> str:
    """Validate pr_number is a plain integer.

    Also checks the resulting path is inside PRS_DIR.
    """
    if not _PR_NUMBER_RE.match(pr_number):
        print(
            f"Invalid PR number: {pr_number!r} "
            f"(must be digits only)",
            file=sys.stderr,
        )
        sys.exit(1)
    pr_dir = os.path.normpath(
        os.path.join(PRS_DIR, pr_number),
    )
    prs_real = os.path.realpath(PRS_DIR)
    if not pr_dir.startswith(prs_real + os.sep):
        print(
            f"PR path escapes PRS_DIR: {pr_dir}",
            file=sys.stderr,
        )
        sys.exit(1)
    return pr_dir


def fetch(pr_number: str):
    pr_dir = _validate_pr_number(pr_number)
    os.makedirs(pr_dir, exist_ok=True)

    # 1. PR metadata (expanded fields)
    meta = _run([
        "gh", "pr", "view", pr_number,
        "--json", _META_FIELDS,
    ])
    if meta.returncode != 0:
        print(
            f"Failed to fetch PR #{pr_number}: "
            f"{meta.stderr}",
            file=sys.stderr,
        )
        sys.exit(1)

    meta_path = os.path.join(pr_dir, "meta.json")
    with open(meta_path, "w") as f:
        json.dump(
            json.loads(meta.stdout), f,
            indent=2, ensure_ascii=False,
        )
        f.write("\n")
    print(
        f"  Saved metadata → "
        f"{os.path.relpath(meta_path, ROOT)}"
    )

    # 2. Diff
    diff_path = os.path.join(pr_dir, "diff.patch")
    diff = _run(["gh", "pr", "diff", pr_number])
    if diff.returncode != 0:
        err = (diff.stderr or "").strip()
        too_large = (
            "PullRequest.diff too_large" in err
            or "diff exceeded the maximum number of lines" in err
        )
        if too_large:
            with open(diff_path, "w") as f:
                f.write(
                    f"# WARNING: PR #{pr_number} diff is too large to fetch via gh\n"
                    f"# Original error:\n# {err.replace(chr(10), chr(10) + '# ')}\n"
                )
            print(
                f"  Saved diff placeholder → "
                f"{os.path.relpath(diff_path, ROOT)}",
                file=sys.stderr,
            )
        else:
            print(
                f"Failed to fetch diff for PR "
                f"#{pr_number}: {diff.stderr}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        with open(diff_path, "w") as f:
            f.write(diff.stdout)
        print(
            f"  Saved diff → "
            f"{os.path.relpath(diff_path, ROOT)}"
        )

    # 3. Review comments (REST — keeps diff_hunk etc.)
    comments = _run([
        "gh", "api",
        f"repos/{{owner}}/{{repo}}/pulls/"
        f"{pr_number}/comments",
        "--paginate",
    ])
    if comments.returncode == 0:
        rc_path = os.path.join(
            pr_dir, "review_comments.json"
        )
        with open(rc_path, "w") as f:
            json.dump(
                json.loads(comments.stdout), f,
                indent=2, ensure_ascii=False,
            )
            f.write("\n")
        print(
            f"  Saved review comments → "
            f"{os.path.relpath(rc_path, ROOT)}"
        )

    # 4. Review threads via GraphQL (isResolved)
    owner, repo = _owner_repo()
    if owner and repo:
        threads = _run([
            "gh", "api", "graphql",
            "-f", f"query={_REVIEW_THREADS_QUERY}",
            "-F", f"n={pr_number}",
            "-f", f"owner={owner}",
            "-f", f"repo={repo}",
        ])
        if threads.returncode == 0:
            threads_path = os.path.join(
                pr_dir, "review_threads.json"
            )
            with open(threads_path, "w") as f:
                json.dump(
                    json.loads(threads.stdout), f,
                    indent=2, ensure_ascii=False,
                )
                f.write("\n")
            print(
                f"  Saved review threads → "
                f"{os.path.relpath(threads_path, ROOT)}"
            )

    print(f"  ✓ PR #{pr_number} fetched")


BOTS = {
    "coderabbitai", "coderabbitai[bot]",
    "qodo-code-review", "qodo-code-review[bot]",
    "github-actions", "github-actions[bot]",
    "github-advanced-security", "github-advanced-security[bot]",
    "dependabot", "dependabot[bot]",
    "renovate", "renovate[bot]",
}


def _is_bot(login: str) -> bool:
    return login in BOTS or login.endswith("[bot]")


def _quote(text: str) -> str:
    lines = (text or "").strip().splitlines()
    return "\n".join("> " + ln for ln in lines) if lines else "> (empty)"


_STATE_ICON = {
    "OPEN": "🟢", "CLOSED": "🔴", "MERGED": "🟣",
}
_REVIEW_ICON = {
    "APPROVED": "✅",
    "CHANGES_REQUESTED": "❌",
    "COMMENTED": "💬",
    "DISMISSED": "👀",
    "PENDING": "⏳",
}
_CI_ICON = {
    "SUCCESS": "✅", "FAILURE": "❌",
    "PENDING": "⏳", "ERROR": "⚠️",
}


def _load_diff_hunks(pr_dir):
    """Build url → diff_hunk lookup from REST data."""
    rc_path = os.path.join(
        pr_dir, "review_comments.json"
    )
    if not os.path.exists(rc_path):
        return {}
    with open(rc_path) as f:
        comments = json.loads(f.read())
    hunks = {}
    for c in comments:
        url = c.get("html_url", "")
        hunk = c.get("diff_hunk", "")
        if url and hunk:
            hunks[url] = hunk
    return hunks


def _has_quote_match(original_body, reply_body):
    """Check if reply quotes text from the original."""
    quoted = []
    for line in reply_body.splitlines():
        s = line.strip()
        if s.startswith(">"):
            txt = s.lstrip(">").strip()
            if txt and not txt.startswith("@"):
                quoted.append(txt.lower())
    if not quoted:
        return False
    orig_lower = original_body.lower()
    return any(q in orig_lower for q in quoted)


def _detect_pr_replies(comments, pr_author):
    """Return set of comment URLs that the author replied to."""
    replied = set()
    human = [
        c for c in comments
        if not _is_bot(
            c.get("author", {}).get("login", "")
        )
    ]
    for i, c in enumerate(human):
        c_author = (
            c.get("author", {}).get("login", "")
        )
        if c_author == pr_author:
            continue
        c_body = c.get("body") or ""
        c_url = c.get("url", "")
        # Check subsequent author comments for quote
        for j in range(i + 1, len(human)):
            r = human[j]
            r_author = (
                r.get("author", {}).get("login", "")
            )
            if r_author != pr_author:
                continue
            r_body = r.get("body") or ""
            if _has_quote_match(c_body, r_body):
                replied.add(c_url)
                break
    return replied


def _format_conversation(comments, diff_hunk=""):
    """Format a thread as a chat with optional code."""
    ln = []
    if diff_hunk:
        ln.append("```diff")
        hunk_lines = diff_hunk.strip().splitlines()
        # Keep last 12 lines for context
        if len(hunk_lines) > 12:
            ln.append("  ...")
            hunk_lines = hunk_lines[-12:]
        for hl in hunk_lines:
            ln.append(hl)
        ln.append("```")
        ln.append("")
    for c in comments:
        author = c.get("author", {}).get("login", "?")
        date = c.get("createdAt", "")[:10]
        body = (c.get("body") or "").strip()
        ln.append(f"> **@{author}** ({date}):")
        ln.append(">")
        for bl in body.splitlines():
            ln.append(f"> {bl}")
        ln.append("")
    return ln


def _load_review_threads(pr_dir):
    """Load review threads from GraphQL data."""
    path = os.path.join(pr_dir, "review_threads.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    try:
        return (
            data["data"]["repository"]
            ["pullRequest"]["reviewThreads"]["nodes"]
        )
    except (KeyError, TypeError):
        return []


def _reviewer_table(meta):
    """Build deduplicated reviewer list with latest state."""
    pr_author = meta["author"]["login"]
    reviewers = {}
    # Submitted reviews (last state wins)
    for r in meta.get("reviews", []):
        login = r.get("author", {}).get("login", "?")
        if login == pr_author:
            continue
        state = r.get("state", "COMMENTED")
        reviewers[login] = state
    # Pending review requests (only if no review yet)
    for rr in meta.get("reviewRequests", []):
        login = rr.get("login", "")
        if not login:
            # Team review request
            login = rr.get("name", "?")
        if login and login not in reviewers:
            reviewers[login] = "PENDING"
    return reviewers


def _ci_summary(meta):
    """Summarise CI status from statusCheckRollup."""
    checks = meta.get("statusCheckRollup", [])
    if not checks:
        return "—"
    states = {}
    for c in checks:
        # gh CLI normalises to __typename/state/status
        s = (
            c.get("conclusion")
            or c.get("state")
            or c.get("status")
            or "PENDING"
        ).upper()
        states[s] = states.get(s, 0) + 1
    parts = []
    for s in ["SUCCESS", "FAILURE", "ERROR", "PENDING",
              "NEUTRAL", "SKIPPED"]:
        if s in states:
            icon = _CI_ICON.get(s, "")
            parts.append(f"{icon} {s}: {states[s]}")
    return ", ".join(parts) if parts else "—"


def status(pr_number: str):
    # Always fetch the latest PR data before report
    fetch(pr_number)

    pr_dir = os.path.join(PRS_DIR, pr_number)
    meta_path = os.path.join(pr_dir, "meta.json")

    with open(meta_path) as f:
        meta = json.load(f)

    pr_author = meta["author"]["login"]
    pr_title = meta.get("title", "")
    pr_url = meta.get("url", "")
    pr_state = meta.get("state", "?")
    pr_created = meta.get("createdAt", "")[:10]
    pr_updated = meta.get("updatedAt", "")[:10]
    merge_state = meta.get("mergeStateStatus", "—")
    review_decision = meta.get("reviewDecision") or "Requires Review"
    state_icon = _STATE_ICON.get(pr_state, "")
    ci_text = _ci_summary(meta)

    # --- Load data ---
    all_threads = _load_review_threads(pr_dir)
    diff_hunks = _load_diff_hunks(pr_dir)
    resolved_threads = [
        t for t in all_threads if t.get("isResolved")
    ]
    unresolved_threads = [
        t for t in all_threads
        if not t.get("isResolved")
    ]

    # --- Unresolved → unreplied code threads ---
    code_threads = []
    for t in unresolved_threads:
        comments = (
            t.get("comments", {}).get("nodes", [])
        )
        if not comments:
            continue
        humans = [
            c for c in comments
            if not _is_bot(
                c.get("author", {}).get("login", "")
            )
        ]
        if not humans:
            continue
        last = comments[-1]
        last_author = (
            last.get("author", {}).get("login", "")
        )
        if last_author == pr_author:
            continue
        first = comments[0]
        participants = list(dict.fromkeys(
            c.get("author", {}).get("login", "?")
            for c in comments
        ))
        code_threads.append({
            "path": t.get("path", "?"),
            "line": (
                t.get("line")
                or t.get("startLine")
                or "?"
            ),
            "url": first.get("url", ""),
            "last_author": last_author,
            "participants": participants,
            "comments": comments,
        })

    # --- PR-level comments: split unreplied vs replied ---
    replied_urls = _detect_pr_replies(
        meta.get("comments", []), pr_author
    )
    pr_unreplied = []
    pr_replied = []
    for c in meta.get("comments", []):
        author = c.get("author", {}).get("login", "?")
        if _is_bot(author) or author == pr_author:
            continue
        entry = {
            "url": c.get("url", ""),
            "author": author,
            "date": c.get("createdAt", "")[:10],
            "body": c.get("body", ""),
        }
        if entry["url"] in replied_urls:
            pr_replied.append(entry)
        else:
            pr_unreplied.append(entry)

    # --- Reviewers ---
    reviewers = _reviewer_table(meta)

    # --- Counts for summary table ---
    n_code_unresolved = len(code_threads)
    n_code_resolved = len(resolved_threads)
    n_pr_unreplied = len(pr_unreplied)
    n_pr_replied = len(pr_replied)

    # ===== Build report =====
    ln = []

    # ── Header ──
    ln.append(f"# PR #{pr_number}: {pr_title}")
    ln.append("")
    ln.append("| Field | Value |")
    ln.append("|---|---|")
    ln.append(f"| **URL** | {pr_url} |")
    ln.append(f"| **Author** | @{pr_author} |")
    ln.append(
        f"| **State** | {state_icon} {pr_state} |"
    )
    ln.append(f"| **Created** | {pr_created} |")
    ln.append(f"| **Updated** | {pr_updated} |")
    ln.append(f"| **CI Status** | {ci_text} |")
    ln.append(
        f"| **Merge Status** | {merge_state} |"
    )
    ln.append(
        f"| **Review Decision** | {review_decision} |"
    )
    ln.append(
        f"| **Code comments** "
        f"| {n_code_unresolved} unresolved / "
        f"{n_code_resolved} resolved / "
        f"0 suspicious |"
    )
    ln.append(
        f"| **PR comments** "
        f"| {n_pr_unreplied} unreplied / "
        f"{n_pr_replied} replied / "
        f"0 suspicious |"
    )
    ln.append("")

    # ── PR Description ──
    body = (meta.get("body") or "").strip()
    if body:
        ln.append("## PR Description")
        ln.append("")
        preview = body[:2000]
        if len(body) > 2000:
            preview += "\n\n_(truncated)_"
        ln.append(_quote(preview))
        ln.append("")

    # ── Reviewers ──
    ln.append("## Reviewers")
    ln.append("")
    if reviewers:
        ln.append("| Reviewer | Status |")
        ln.append("|---|---|")
        for login, st in sorted(reviewers.items()):
            icon = _REVIEW_ICON.get(st, "")
            ln.append(
                f"| @{login} | {icon} {st} |"
            )
    else:
        ln.append("No reviewers assigned.")
    ln.append("")

    # ── Action Items ──
    ln.append("## Action Items")
    ln.append("")
    action_idx = 0
    for login, st in sorted(reviewers.items()):
        if st == "CHANGES_REQUESTED":
            action_idx += 1
            ln.append(
                f"{action_idx}. ❌ **@{login}** "
                f"requested changes — "
                f"needs re-review"
            )
    for login, st in sorted(reviewers.items()):
        if st == "PENDING":
            action_idx += 1
            ln.append(
                f"{action_idx}. ⏳ Awaiting review "
                f"from **@{login}**"
            )
    for ct in code_threads:
        action_idx += 1
        ln.append(
            f"{action_idx}. 💬 Reply to "
            f"**@{ct['last_author']}** on "
            f"`{ct['path']}:{ct['line']}`"
        )
    for pc in pr_unreplied:
        action_idx += 1
        ln.append(
            f"{action_idx}. 💬 Address "
            f"**@{pc['author']}**'s "
            f"PR comment ({pc['date']})"
        )
    if action_idx == 0:
        ln.append("None — all caught up! 🎉")
    ln.append("")

    # ── Unreplied Code Comments ──
    ln.append("## Unreplied Code Comments")
    ln.append("")
    if not code_threads:
        ln.append("None.")
        ln.append("")
    for ct in code_threads:
        path = ct["path"]
        line = ct["line"]
        url = ct["url"]
        participants = ", ".join(
            f"@{p}" for p in ct["participants"]
        )
        ln.append(f"### [{path}:{line}]({url})")
        ln.append("")
        ln.append("- **Severity**: TBD")
        ln.append(
            f"- **Awaiting reply from**: @{pr_author}"
        )
        ln.append(
            f"- **Participants**: {participants}"
        )
        ln.append("")
        hunk = diff_hunks.get(url, "")
        ln.extend(
            _format_conversation(
                ct["comments"], hunk
            )
        )
        ln.append("---")
        ln.append("")

    # ── Unreplied PR Comments ──
    ln.append("## Unreplied PR Comments")
    ln.append("")
    if not pr_unreplied:
        ln.append("None.")
        ln.append("")
    for pc in pr_unreplied:
        ln.append(
            f"### [PR Comment]({pc['url']})"
        )
        ln.append("")
        ln.append("- **Severity**: TBD")
        ln.append(
            f"- **Asked by**: @{pc['author']}"
        )
        ln.append(
            f"- **Awaiting reply from**: @{pr_author}"
        )
        ln.append(f"- **Date**: {pc['date']}")
        ln.append("")
        ln.append(_quote(pc["body"]))
        ln.append("")
        ln.append("---")
        ln.append("")

    # ── Suspicious Resolutions ──
    ln.append("## Suspicious Resolutions")
    ln.append("")
    ln.append("None.")
    ln.append("")

    # ── Resolved Comments (Audit Required) ──
    ln.append("## Resolved Comments (Audit Required)")
    ln.append("")
    if not resolved_threads:
        ln.append("None.")
        ln.append("")
    for rt in resolved_threads:
        comments = (
            rt.get("comments", {}).get("nodes", [])
        )
        if not comments:
            continue
        first = comments[0]
        path = rt.get("path", "?")
        line = (
            rt.get("line")
            or rt.get("startLine")
            or "?"
        )
        url = first.get("url", "")
        participants = list(dict.fromkeys(
            c.get("author", {}).get("login", "?")
            for c in comments
        ))
        parts_str = ", ".join(
            f"@{p}" for p in participants
        )
        ln.append(f"### [{path}:{line}]({url})")
        ln.append("")
        ln.append(
            "- **Status**: "
            "✅ RESOLVED — AI VERIFIED"
        )
        ln.append(
            f"- **Participants**: {parts_str}"
        )
        ln.append("")
        hunk = diff_hunks.get(url, "")
        ln.extend(
            _format_conversation(comments, hunk)
        )
        ln.append("---")
        ln.append("")

    report_path = os.path.join(
        pr_dir, "status.md"
    )
    with open(report_path, "w") as f:
        f.write("\n".join(ln))
    print(
        f"  ✓ Status report → "
        f"{os.path.relpath(report_path, ROOT)}"
    )


_SEV_ORDER = {
    "CRITICAL": 0, "HIGH": 1,
    "MEDIUM": 2, "LOW": 3, "TBD": 4,
}


def reorder(pr_number: str):
    pr_dir = _validate_pr_number(pr_number)
    report_path = os.path.join(pr_dir, "status.md")
    if not os.path.exists(report_path):
        print(
            f"No status report for PR #{pr_number}.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(report_path) as f:
        content = f.read()

    # Split into sections by "## Unreplied Code Comments"
    # and "## Unreplied PR Comments", reorder each block.
    def _reorder_section(text):
        # Split into individual comment blocks by "---"
        blocks = re.split(r"\n---\n", text)
        blocks = [b for b in blocks if b.strip()]

        def _sev(block):
            m = re.search(
                r"\*\*Severity\*\*:\s*(\w+)", block
            )
            if m:
                return _SEV_ORDER.get(m.group(1), 99)
            return 99

        blocks.sort(key=_sev)
        return "\n---\n\n".join(blocks)

    # Find and reorder code comments section
    code_match = re.search(
        r"(## Unreplied Code Comments\n\n)(.*?)"
        r"(## Unreplied PR Comments)",
        content, re.DOTALL,
    )
    if code_match:
        body = code_match.group(2)
        if "None." not in body:
            reordered = _reorder_section(body)
            content = (
                content[:code_match.start(2)]
                + reordered + "\n\n"
                + content[code_match.start(3):]
            )

    # Find and reorder PR comments section
    # (ends at "## Suspicious" or "## Resolved" or EOF)
    pr_match = re.search(
        r"(## Unreplied PR Comments\n\n)(.*?)"
        r"(## Suspicious Resolutions"
        r"|## Resolved Comments|$)",
        content, re.DOTALL,
    )
    if pr_match:
        body = pr_match.group(2)
        if "None." not in body:
            reordered = _reorder_section(body)
            content = (
                content[:pr_match.start(2)]
                + reordered + "\n\n"
                + content[pr_match.start(3):]
            )

    with open(report_path, "w") as f:
        f.write(content)
    print(f"  ✓ PR #{pr_number} status report reordered")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: pr.py "
            "{list|fetch|status|reorder} "
            "[PR_NUMBER]",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        prs = _list_open_prs()
        excludes = _load_exclude_list()
        for pr in prs:
            num = str(pr["number"])
            marker = " [excluded]" if num in excludes else ""
            author = pr.get("author", {}).get("login", "?")
            title = pr.get("title", "")
            print(f"  #{num}\t@{author}\t{title}{marker}")
        total = len(prs)
        excluded = sum(
            1 for pr in prs
            if str(pr["number"]) in excludes
        )
        print(
            f"\n  {total} open PR(s), "
            f"{excluded} excluded"
        )

    elif cmd == "fetch":
        if len(sys.argv) < 3:
            print(
                "Usage: pr.py fetch <PR_NUMBER|ALL>",
                file=sys.stderr,
            )
            sys.exit(1)
        arg = sys.argv[2]
        if arg.upper() == "ALL":
            prs = _list_open_prs()
            excludes = _load_exclude_list()
            for pr in prs:
                num = str(pr["number"])
                if num in excludes:
                    print(f"  Skipping PR #{num} (excluded)")
                    continue
                fetch(num)
        else:
            fetch(arg)

    elif cmd == "status":
        if len(sys.argv) < 3:
            print(
                "Usage: pr.py status <PR_NUMBER|ALL>",
                file=sys.stderr,
            )
            sys.exit(1)
        arg = sys.argv[2]
        if arg.upper() == "ALL":
            prs = _list_open_prs()
            excludes = _load_exclude_list()
            failures = []
            for pr in prs:
                num = str(pr["number"])
                if num in excludes:
                    print(
                        f"  Skipping PR #{num} (excluded)",
                    )
                    continue
                try:
                    status(num)
                except SystemExit as e:
                    print(
                        f"  Failed to generate status for PR #{num} (exit={e.code})",
                        file=sys.stderr,
                    )
                    failures.append(num)
            if failures:
                sys.exit(1)
        else:
            status(arg)

    elif cmd == "reorder":
        if len(sys.argv) < 3:
            print(
                "Usage: pr.py reorder <PR_NUMBER>",
                file=sys.stderr,
            )
            sys.exit(1)
        reorder(sys.argv[2])

    else:
        print(
            f"Unknown command: {cmd}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
