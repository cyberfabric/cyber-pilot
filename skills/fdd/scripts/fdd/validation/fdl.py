"""
FDD Validator - FDL Validation

FDL (FDD Description Language) validation: coverage, completion, code implementation checks.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..constants import FDL_SCOPE_ID_RE, FDL_STEP_LINE_RE


def extract_fdl_instructions(text: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Extract FDL instruction IDs marked as implemented [x] from feature design.
    
    Returns:
        Dict with structure:
        {
            "fdd-{project}-{type}-{name}": {
                "instructions": ["inst-id-1", "inst-id-2", ...],  # Only [x] marked
                "completed": ["inst-id-1", ...]  # Same as instructions (kept for compatibility)
            }
        }
    """
    result: Dict[str, Dict[str, List[str]]] = {}
    current_scope_id: Optional[str] = None
    
    for line in text.splitlines():
        # Match FDL scope ID line: - [ ] **ID**: `fdd-{project}-{type}-{name}`
        if FDL_SCOPE_ID_RE.match(line):
            m = re.search(r"`(fdd-[a-z0-9-]+)`", line)
            if m:
                current_scope_id = m.group(1)
                if current_scope_id not in result:
                    result[current_scope_id] = {"instructions": [], "completed": []}
        
        # Extract instruction IDs ONLY from [x] marked FDL step lines
        if current_scope_id and FDL_STEP_LINE_RE.match(line):
            # Check if marked as implemented [x]
            if re.match(r"^\s*\d+\.\s*\[x\]", line, re.I):
                m_inst = re.search(r"`(inst-[a-z0-9-]+)`\s*$", line.strip())
                if m_inst:
                    inst_id = m_inst.group(1)
                    result[current_scope_id]["instructions"].append(inst_id)
                    result[current_scope_id]["completed"].append(inst_id)
    
    return result


def extract_inst_tags_from_code(feature_root: Path) -> Dict[str, Dict[str, object]]:
    """
    Scan codebase for FDL instruction tags (fdd-begin/fdd-end pairs). Extracts inst-{id} only.
    
    Returns:
        Dict mapping inst-{id} to {"has_begin": bool, "has_end": bool, "complete": bool}
    """
    inst_tags: Dict[str, Dict[str, bool]] = {}
    
    # File extensions to scan
    code_extensions = {".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".cs", ".sql", ".md"}
    
    # Skip directories
    skip_dirs = {".git", "node_modules", "venv", "__pycache__", ".pytest_cache", "target", "build", "dist", "tests", "examples"}
    
    def scan_file(file_path: Path) -> None:
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").split('\n')
            
            # Match: fdd-begin fdd-{project}-feature-{slug}-...:ph-N:inst-{id}
            begin_pattern = r'fdd-begin\s+(fdd-[a-z0-9-]+(?:-flow|-algo|-state|-req|-test)-[a-z0-9-]+):ph-\d+:(inst-[a-z0-9-]+)'
            # Match: fdd-end fdd-{project}-feature-{slug}-...:ph-N:inst-{id}
            end_pattern = r'fdd-end\s+(fdd-[a-z0-9-]+(?:-flow|-algo|-state|-req|-test)-[a-z0-9-]+):ph-\d+:(inst-[a-z0-9-]+)'
            
            for line in lines:
                # Check for fdd-begin
                begin_match = re.search(begin_pattern, line)
                if begin_match:
                    scope_id, inst_id = begin_match.groups()
                    if inst_id not in inst_tags:
                        inst_tags[inst_id] = {"has_begin": False, "has_end": False, "complete": False, "scopes": []}
                    inst_tags[inst_id]["has_begin"] = True
                    if scope_id not in inst_tags[inst_id]["scopes"]:
                        inst_tags[inst_id]["scopes"].append(scope_id)
                
                # Check for fdd-end
                end_match = re.search(end_pattern, line)
                if end_match:
                    scope_id, inst_id = end_match.groups()
                    if inst_id not in inst_tags:
                        inst_tags[inst_id] = {"has_begin": False, "has_end": False, "complete": False, "scopes": []}
                    inst_tags[inst_id]["has_end"] = True
                    if scope_id not in inst_tags[inst_id]["scopes"]:
                        inst_tags[inst_id]["scopes"].append(scope_id)
            
        except Exception:
            pass
    
    def scan_directory(directory: Path) -> None:
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    if item.name not in skip_dirs:
                        scan_directory(item)
                elif item.is_file() and item.suffix in code_extensions:
                    scan_file(item)
        except (PermissionError, OSError):
            pass
    
    # Start scanning from feature root or project root
    if feature_root and feature_root.exists():
        # Scan from project root (parent of architecture/features/feature-X)
        project_root = feature_root.parent.parent.parent
        if project_root.exists():
            scan_directory(project_root)
    
    # Mark complete if both begin and end tags present
    for inst_id in inst_tags:
        inst_tags[inst_id]["complete"] = inst_tags[inst_id]["has_begin"] and inst_tags[inst_id]["has_end"]
    
    return inst_tags


def validate_fdl_code_to_design(
    feature_root: Path,
    design_text: str
) -> List[Dict[str, object]]:
    """
    Reverse validation: Check that all fdd tags in code are marked [x] in DESIGN.md.
    
    If code has fdd-begin/fdd-end tags but instruction is not marked [x],
    this means implementation exists but not documented as complete.
    """
    errors: List[Dict[str, object]] = []
    
    # Extract all inst-{id} tags from code
    code_inst_tags = extract_inst_tags_from_code(feature_root)
    
    # Extract all [x] marked instructions from DESIGN.md
    design_fdl = extract_fdl_instructions(design_text)
    
    # Build set of all [x] marked inst-ids from DESIGN
    marked_instructions = set()
    for scope_id, data in design_fdl.items():
        marked_instructions.update(data["instructions"])
    
    # Extract feature slug from feature_root path
    feature_slug = feature_root.name.replace("feature-", "") if feature_root.name.startswith("feature-") else None
    
    # Find tags in code that are NOT marked [x] in DESIGN, filtering by feature slug
    untracked_implementations = []
    for inst_id, tag_info in code_inst_tags.items():
        if not tag_info["complete"]:
            continue
        if inst_id in marked_instructions:
            continue
        
        # Check if any scope belongs to current feature
        belongs_to_feature = False
        if feature_slug:
            for scope_id in tag_info.get("scopes", []):
                if f"-feature-{feature_slug}-" in scope_id:
                    belongs_to_feature = True
                    break
        
        # Only report if it belongs to this feature
        if belongs_to_feature:
            untracked_implementations.append(inst_id)
    
    if untracked_implementations:
        errors.append({
            "type": "fdl_untracked_implementation",
            "message": f"Found {len(untracked_implementations)} fdd tags in code not marked [x] in DESIGN.md",
            "count": len(untracked_implementations),
            "instructions": untracked_implementations[:10],
            "suggestion": "Mark these instructions as [x] in DESIGN.md or remove tags from code"
        })
    
    return errors


def validate_fdl_code_implementation(
    feature_root: Path,
    design_fdl: Dict[str, Dict[str, List]]
) -> List[Dict[str, object]]:
    """
    Validate that all FDL instructions from DESIGN.md are implemented in code.
    
    Checks for presence of paired fdd-begin/fdd-end blocks wrapping implementation code.
    """
    errors: List[Dict[str, object]] = []
    
    # Extract all inst-{id} tags from code with begin/end status
    code_inst_tags = extract_inst_tags_from_code(feature_root)
    
    # Collect missing and incomplete implementations
    missing_implementations: List[Tuple[str, str]] = []
    incomplete_implementations: List[Tuple[str, str, str]] = []  # (scope, inst, reason)
    
    for scope_id, data in design_fdl.items():
        for inst_id in data["instructions"]:
            if inst_id not in code_inst_tags:
                # Completely missing
                missing_implementations.append((scope_id, inst_id))
            elif not code_inst_tags[inst_id]["complete"]:
                # Present but incomplete (missing begin or end tag)
                if not code_inst_tags[inst_id]["has_begin"]:
                    reason = "missing fdd-begin tag"
                elif not code_inst_tags[inst_id]["has_end"]:
                    reason = "missing fdd-end tag"
                else:
                    reason = "incomplete"
                incomplete_implementations.append((scope_id, inst_id, reason))
    
    if missing_implementations:
        errors.append({
            "type": "fdl_code_missing",
            "message": f"FDL instructions not found in code (missing {len(missing_implementations)} inst-{{id}} implementations)",
            "missing_count": len(missing_implementations),
            "examples": [
                {"scope": scope, "instruction": inst}
                for scope, inst in missing_implementations[:10]
            ]
        })
    
    if incomplete_implementations:
        errors.append({
            "type": "fdl_code_incomplete",
            "message": f"FDL instructions have incomplete fdd-begin/fdd-end tags ({len(incomplete_implementations)} incomplete)",
            "incomplete_count": len(incomplete_implementations),
            "examples": [
                {"scope": scope, "instruction": inst, "reason": reason}
                for scope, inst, reason in incomplete_implementations[:10]
            ]
        })
    
    return errors
def validate_fdl_completion(
    changes_text: str,
    design_fdl: Dict[str, Dict[str, List]],
    *,
    feature_root: Optional[Path] = None
) -> List[Dict[str, object]]:
    """
    Validate that COMPLETED feature has all FDL instructions marked [x] in DESIGN.md.
    For IMPLEMENTED status, verify all [x] instructions have fdd-begin/end tags in code.
    """
    errors: List[Dict[str, object]] = []
    
    # Check if feature is marked as COMPLETED
    status_match = re.search(r"\*\*Status\*\*:\s*(✅\s*COMPLETED|🔄\s*IN_PROGRESS|⏳\s*NOT_STARTED|✨\s*IMPLEMENTED)", changes_text)
    if not status_match:
        return errors
    
    status = status_match.group(1).strip()
    if not status:
        return errors
    
    # For IMPLEMENTED status, verify all [x] instructions have fdd-begin/end tags in code
    if "IMPLEMENTED" in status and feature_root:
        code_inst_tags = extract_inst_tags_from_code(feature_root)
        
        missing_implementations = []
        incomplete_implementations = []
        
        for scope_id, data in design_fdl.items():
            for inst_id in data["instructions"]:
                if inst_id not in code_inst_tags:
                    missing_implementations.append((scope_id, inst_id))
                elif not code_inst_tags[inst_id]["complete"]:
                    incomplete_implementations.append((scope_id, inst_id))
        
        if missing_implementations or incomplete_implementations:
            errors.append({
                "type": "fdl_implemented_incomplete",
                "message": f"Feature status is IMPLEMENTED but {len(missing_implementations)} [x] instructions missing fdd tags and {len(incomplete_implementations)} have incomplete tags",
                "missing_count": len(missing_implementations),
                "incomplete_count": len(incomplete_implementations),
                "examples": [
                    {"scope": s, "instruction": i, "issue": "missing tags"}
                    for s, i in missing_implementations[:5]
                ] + [
                    {"scope": s, "instruction": i, "issue": "incomplete tags"}
                    for s, i in incomplete_implementations[:5]
                ]
            })
        
        return errors
    
    # For COMPLETED status only, verify all instructions are marked [x]
    if "COMPLETED" not in status:
        return errors
    
    uncompleted_instructions: List[Tuple[str, str]] = []
    for scope_id, data in design_fdl.items():
        for i, inst_id in enumerate(data["instructions"]):
            if not data["completed"][i]:
                uncompleted_instructions.append((scope_id, inst_id))
    
    if uncompleted_instructions:
        errors.append({
            "type": "premature_completion",
            "message": "Feature marked COMPLETED but FDL instructions not all implemented ([x])",
            "uncompleted_count": len(uncompleted_instructions),
            "examples": [
                {"scope": scope, "instruction": inst}
                for scope, inst in uncompleted_instructions[:10]
            ]
        })
    
    return errors
