"""
FDD Validator - Document Utilities

Functions for working with documents and file paths.
"""

import fnmatch
from pathlib import Path
from typing import List, Optional


def detect_artifact_kind(artifact_path: Path) -> str:
    """
    Detect artifact kind from file path.
    
    Args:
        artifact_path: Path to artifact file
    
    Returns:
        Artifact kind string
    """
    name = artifact_path.name
    if artifact_path.exists() and artifact_path.is_dir() and name == "ADR":
        return "adr"
    if name == "FEATURES.md":
        return "features-manifest"
    if name == "DESIGN.md" and "features" in artifact_path.parts and any(p.startswith("feature-") for p in artifact_path.parts):
        return "feature-design"
    if name == "DESIGN.md":
        return "overall-design"
    return "generic"


def iter_text_files(
    root: Path,
    *,
    includes: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    max_bytes: int = 1_000_000,
) -> List[Path]:
    """
    Iterate over text files in directory.
    
    Args:
        root: Root directory to search
        includes: Glob patterns to include
        excludes: Glob patterns to exclude
        max_bytes: Maximum file size in bytes
    
    Returns:
        List of file paths
    """
    import os
    import fnmatch
    
    if excludes is None:
        excludes = []
    
    skip_dirs = {
        ".git", ".hg", ".svn", ".idea", ".vscode", "__pycache__",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "node_modules", "target", "dist", "build", ".venv", "venv",
    }
    
    out: List[Path] = []
    root = root.resolve()
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out skip directories
        dirnames[:] = sorted([d for d in dirnames if d not in skip_dirs and not d.startswith(".")])
        
        for fn in sorted(filenames):
            fp = Path(dirpath) / fn
            
            # Get relative path for pattern matching
            try:
                rel = fp.relative_to(root).as_posix()
            except ValueError:
                continue
            
            # Check excludes
            if excludes and any(fnmatch.fnmatch(rel, ex) for ex in excludes):
                continue
            
            # Check includes (when provided)
            if includes is not None and not any(fnmatch.fnmatch(rel, inc) for inc in includes):
                continue
            
            # Check file size
            try:
                st = fp.stat()
                if st.st_size > max_bytes:
                    continue
            except OSError:
                continue
            
            out.append(fp)
    
    return out


def read_text_safe(path: Path) -> Optional[List[str]]:
    """
    Safely read text file to lines.
    
    Args:
        path: File path to read
    
    Returns:
        List of lines or None if error
    """
    import os

    try:
        raw = path.read_bytes()
    except OSError:
        return None

    if b"\x00" in raw:
        return None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="ignore")

    if os.linesep != "\n":
        text = text.replace("\r\n", "\n")

    return text.splitlines()


def to_relative_posix(path: Path, root: Path) -> str:
    """
    Convert path to relative POSIX string from root.
    
    Args:
        path: Path to convert
        root: Root path
    
    Returns:
        Relative POSIX path string
    """
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception:
        return path.as_posix()
    return rel.as_posix()


__all__ = [
    "detect_artifact_kind",
    "iter_text_files",
    "read_text_safe",
    "to_relative_posix",
]
