"""
Skill Bundle Cache Management

Downloads skill bundle from GitHub releases into ~/.cypilot/cache/.
Uses only Python stdlib (urllib.request) — no third-party dependencies.

@cpt-algo:cpt-cypilot-algo-core-infra-cache-skill:p1
@cpt-dod:cpt-cypilot-dod-core-infra-skill-cache:p1
"""

import io
import json
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cypilot_proxy.resolve import get_cache_dir, get_version_file

# GitHub repository for skill bundle releases
GITHUB_OWNER = "cyberfabric"
GITHUB_REPO = "cyber-pilot"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
USER_AGENT = "cypilot-proxy/3.0"


def _resolve_api_base(url: str) -> str:
    """
    Resolve GitHub API base URL from a custom repo URL or owner/repo shorthand.

    Accepts:
        - "owner/repo" → "https://api.github.com/repos/owner/repo"
        - "https://github.com/owner/repo" → "https://api.github.com/repos/owner/repo"
        - "https://api.github.com/repos/owner/repo" → as-is
    """
    url = url.strip().rstrip("/")
    if url.startswith("https://api.github.com/repos/"):
        return url
    if url.startswith("https://github.com/"):
        # https://github.com/owner/repo → owner/repo
        path = url[len("https://github.com/"):]
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return f"https://api.github.com/repos/{parts[0]}/{parts[1]}"
    if "/" in url and not url.startswith("http"):
        # owner/repo shorthand
        return f"https://api.github.com/repos/{url}"
    return url


def resolve_latest_version(
    api_base: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Query GitHub API for the latest release tag and asset download URL.

    Args:
        api_base: Custom GitHub API base URL (for forks). Defaults to GITHUB_API_BASE.

    Returns (version_tag, asset_url) or (None, None) on failure.
    """
    # inst-resolve-version
    base = api_base or GITHUB_API_BASE
    url = f"{base}/releases/latest"
    req = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    })
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError, OSError):
        return None, None

    tag = data.get("tag_name")
    if not tag:
        return None, None

    # Look for a .tar.gz or .zip asset named cypilot-skill-*
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.startswith("cypilot-skill") and (
            name.endswith(".tar.gz") or name.endswith(".zip")
        ):
            return tag, asset.get("browser_download_url")

    # Fallback: use the source tarball
    tarball_url = data.get("tarball_url")
    return tag, tarball_url


def copy_from_local(
    source_dir: str,
    force: bool = False,
) -> Tuple[bool, str]:
    """
    Copy skill bundle from a local directory to cache.

    Args:
        source_dir: Path to local directory containing the skill bundle.
        force: If True, overwrite even if cache exists.

    Returns:
        (success, message) tuple.
    """
    source = Path(source_dir).resolve()
    if not source.is_dir():
        return False, f"Source directory not found: {source}"

    cache_dir = get_cache_dir()
    version_file = get_version_file()

    # Determine version from source (read __init__.py or fallback to "local")
    local_version = "local"
    for init_candidate in [
        source / "skills" / "cypilot" / "scripts" / "cypilot" / "__init__.py",
        source / "cypilot" / "skills" / "cypilot" / "scripts" / "cypilot" / "__init__.py",
    ]:
        if init_candidate.is_file():
            try:
                text = init_candidate.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if "__version__" in line and "=" in line:
                        local_version = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            except OSError:
                pass
            break

    if not force and version_file.is_file():
        cached_version = version_file.read_text(encoding="utf-8").strip()
        if cached_version == f"local:{local_version}":
            return True, f"Cache already up to date (local:{local_version})"

    # Remove old cache and copy
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Copy source contents to cache
    for item in source.iterdir():
        dst = cache_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        elif item.is_file():
            shutil.copy2(item, dst)

    version_file.write_text(f"local:{local_version}", encoding="utf-8")

    return True, (
        f"Cached: local:{local_version}\n"
        f"  from: {source}\n"
        f"  to:   {cache_dir}"
    )


def download_and_cache(
    version: Optional[str] = None,
    force: bool = False,
    url: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Download skill bundle from GitHub and extract to cache directory.

    Args:
        version: Target version tag. If None, resolves to "latest".
        force: If True, re-download even if cache version matches.
        url: Custom GitHub repo URL (for forks). Format: "owner/repo" or full URL.

    Returns:
        (success, message) tuple.
    """
    cache_dir = get_cache_dir()
    version_file = get_version_file()

    # Resolve API base for custom URL (fork support)
    api_base = GITHUB_API_BASE
    if url is not None:
        api_base = _resolve_api_base(url)

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-resolve-version
    if version is None or version == "latest":
        resolved_version, asset_url = resolve_latest_version(api_base=api_base)
        if resolved_version is None:
            return False, "Failed to resolve latest version from GitHub API. Check network connectivity."
    else:
        resolved_version = version
        # GitHub API /tarball/{ref} works uniformly for tags, branches, and SHAs
        asset_url = f"{api_base}/tarball/{version}"
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-resolve-version

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-if-cache-fresh
    if not force and version_file.is_file():
        cached_version = version_file.read_text(encoding="utf-8").strip()
        if cached_version == resolved_version:
            # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-return-cache-hit
            return True, f"Cache already up to date (version {resolved_version})"
            # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-return-cache-hit
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-if-cache-fresh

    if asset_url is None:
        return False, f"No download URL found for version {resolved_version}"

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-download-archive
    req = Request(asset_url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    })
    try:
        with urlopen(req, timeout=120) as resp:
            archive_data = resp.read()
    except HTTPError as e:
        # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-if-download-error
        # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-return-download-fail
        return False, f"Download failed: HTTP {e.code} — {e.reason}. URL: {asset_url}"
        # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-return-download-fail
        # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-if-download-error
    except URLError as e:
        return False, f"Download failed: {e.reason}. Check network connectivity."
    except OSError as e:
        return False, f"Download failed: {e}. Check network connectivity."
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-download-archive

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-mkdir-cache
    # Remove old cache to prevent version mixing
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-mkdir-cache

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-extract-archive
    extracted = False
    try:
        # Try tar.gz first
        buf = io.BytesIO(archive_data)
        if tarfile.is_tarfile(buf):
            buf.seek(0)
            with tarfile.open(fileobj=buf, mode="r:*") as tf:
                # GitHub tarballs have a top-level directory; strip it
                members = tf.getmembers()
                prefix = _find_common_prefix(members)
                _extract_stripped(tf, members, prefix, cache_dir)
                extracted = True
    except (tarfile.TarError, OSError):
        pass

    if not extracted:
        try:
            buf = io.BytesIO(archive_data)
            with zipfile.ZipFile(buf) as zf:
                members = zf.namelist()
                prefix = _find_zip_prefix(members)
                _extract_zip_stripped(zf, members, prefix, cache_dir)
                extracted = True
        except (zipfile.BadZipFile, OSError):
            pass

    if not extracted:
        return False, "Failed to extract archive: unrecognized format"
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-extract-archive

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-write-version
    version_file.write_text(resolved_version, encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-write-version

    # @cpt-begin:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-return-cache-path-new
    return True, (
        f"Cached: {resolved_version}\n"
        f"  from: {asset_url}\n"
        f"  to:   {cache_dir}"
    )
    # @cpt-end:cpt-cypilot-algo-core-infra-cache-skill:p1:inst-return-cache-path-new


def _find_common_prefix(members: list) -> str:
    """Find common top-level directory prefix in tar members."""
    names = [m.name for m in members if m.name and "/" in m.name]
    if not names:
        return ""
    first_parts = {n.split("/", 1)[0] for n in names}
    if len(first_parts) == 1:
        return first_parts.pop() + "/"
    return ""


def _extract_stripped(
    tf: tarfile.TarFile,
    members: list,
    prefix: str,
    dest: Path,
) -> None:
    """Extract tar members, stripping the common prefix."""
    for member in members:
        if not member.name.startswith(prefix):
            continue
        rel = member.name[len(prefix):]
        if not rel:
            continue
        # Security: skip absolute paths and parent references
        if rel.startswith("/") or ".." in rel.split("/"):
            continue
        member_copy = tarfile.TarInfo(name=rel)
        member_copy.size = member.size
        member_copy.mode = member.mode
        target = dest / rel
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
        elif member.isfile():
            target.parent.mkdir(parents=True, exist_ok=True)
            f = tf.extractfile(member)
            if f is not None:
                target.write_bytes(f.read())


def _find_zip_prefix(members: list) -> str:
    """Find common top-level directory prefix in zip members."""
    dirs = [m for m in members if "/" in m]
    if not dirs:
        return ""
    first_parts = {m.split("/", 1)[0] for m in dirs}
    if len(first_parts) == 1:
        return first_parts.pop() + "/"
    return ""


def _extract_zip_stripped(
    zf: zipfile.ZipFile,
    members: list,
    prefix: str,
    dest: Path,
) -> None:
    """Extract zip members, stripping the common prefix."""
    for name in members:
        if not name.startswith(prefix):
            continue
        rel = name[len(prefix):]
        if not rel:
            continue
        if rel.startswith("/") or ".." in rel.split("/"):
            continue
        target = dest / rel
        if name.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(name))
