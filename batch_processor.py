"""
Batch Processor — Multi-file Code Repair

Handles processing multiple Python files with glob pattern support.
"""

import json
from pathlib import Path
from typing import List, Dict
from judge import judge_code
from loop_controller import run_loop


MAX_FILES = 1000


def find_python_files(
    patterns: List[str],
    exclude_patterns: List[str] = None,
    recursive: bool = True
) -> List[Path]:
    """
    Find all Python files matching patterns.
    
    Args:
        patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        recursive: Search subdirectories
    
    Returns:
        List of Python file paths
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    all_files = set()
    cwd = Path.cwd()
    
    # Find files matching include patterns
    for pattern in patterns:
        if recursive and '**' not in pattern:
            pattern = f"**/{pattern}"
        
        matched = list(cwd.glob(pattern))
        all_files.update(matched)
    
    # Filter out excluded patterns
    excluded_files = set()
    for pattern in exclude_patterns:
        if recursive and '**' not in pattern:
            pattern = f"**/{pattern}"
        
        matched = list(cwd.glob(pattern))
        excluded_files.update(matched)
    
    # Keep only Python files that aren't excluded
    result = []
    for f in all_files:
        if f.is_file() and f.suffix == '.py' and f not in excluded_files:
            result.append(f)
    
    return sorted(result)


def process_batch(
    paths: List[str],
    profile: str = "strict",
    enable_repair: bool = False,
    apply_repairs: bool = False,
    recursive: bool = True,
    exclude_patterns: List[str] = None
) -> Dict:
    """
    Process multiple files.
    
    Args:
        paths: List of file patterns to process
        profile: Quality profile
        enable_repair: Whether to generate repairs
        apply_repairs: Whether to apply repairs (dry-run if False)
        recursive: Search subdirectories
        exclude_patterns: Patterns to exclude
    
    Returns:
        Batch processing summary
    """
    
    # Find all matching files
    all_files = find_python_files(paths, exclude_patterns, recursive)
    
    # Safety limit
    if len(all_files) > MAX_FILES:
        return {
            "total_files": len(all_files),
            "ci_pass": False,
            "error": f"Refusing to process {len(all_files)} files (limit {MAX_FILES})"
        }
    
    results = {
        "total_files": len(all_files),
        "compliant_files": 0,
        "non_compliant_files": 0,
        "files_repaired": 0,
        "total_failures": 0,
        "total_repairs": 0,
        "repair_confidence": 1.0,
        "files": [],
    }
    
    confidence_scores = []
    
    for filepath in all_files:
        try:
            code = filepath.read_text()
            
            judge_result = judge_code(code, profile)
            
            file_entry = {
                "filepath": str(filepath),
                "judge": judge_result,
            }
            
            if judge_result.get("compliant", False):
                results["compliant_files"] += 1
            else:
                results["non_compliant_files"] += 1
                results["total_failures"] += judge_result.get("failure_count", 0)
                
                if enable_repair:
                    loop_result = run_loop(
                        filepath=str(filepath),
                        judge_result=judge_result,
                        profile=profile,
                        enable_repair=True,
                        dry_run=not apply_repairs,
                        max_iterations=3,
                    )
                    
                    file_entry["repair"] = loop_result
                    
                    confidence_scores.append(loop_result.get("repair_confidence", 1.0))
                    results["total_repairs"] += len(loop_result.get("history", []))
            
            results["files"].append(file_entry)
            
        except Exception as e:
            results["files"].append({
                "filepath": str(filepath),
                "error": str(e)
            })
    
    # Aggregate confidence
    if confidence_scores:
        results["repair_confidence"] = round(
            sum(confidence_scores) / len(confidence_scores), 3
        )
    
    # CI decision (STRICT)
    results["ci_pass"] = results["non_compliant_files"] == 0
    
    return results
