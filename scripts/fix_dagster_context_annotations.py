#!/usr/bin/env python3
"""Fix `context` parameter annotations in Dagster assets + asset_checks.

Safer version of the earlier script: uses ast for detection but
in-place string manipulation (no token rewriting). Only adds the
annotation if the param is bare `context` (not already annotated).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = REPO_ROOT / "orchestration" / "defs"


def _get_decorator_info(func: ast.FunctionDef) -> tuple[bool, bool]:
    """Return (is_asset, is_asset_check) for a function based on its decorators."""
    is_asset = False
    is_asset_check = False
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                if dec.func.id == "asset":
                    is_asset = True
                elif dec.func.id == "asset_check":
                    is_asset_check = True
            elif isinstance(dec.func, ast.Attribute):
                if dec.func.attr == "asset":
                    is_asset = True
                elif dec.func.attr == "asset_check":
                    is_asset_check = True
    return is_asset, is_asset_check


def _context_param_to_fix(func: ast.FunctionDef) -> tuple[str, ast.arg] | None:
    """If the function has a bare `context` param, return the annotation + arg node."""
    is_asset, is_asset_check = _get_decorator_info(func)
    if not is_asset and not is_asset_check:
        return None
    target_annotation = (
        "AssetCheckExecutionContext" if is_asset_check else "AssetExecutionContext"
    )

    for arg in func.args.args:
        if arg.arg == "context" and arg.annotation is None:
            return target_annotation, arg
    return None


def fix_file(path: Path) -> int:
    """Fix context annotations in one file. Returns count of fixes."""
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError):
        return 0
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return 0

    # Find fixes to apply (line, col, length_of_context_token, annotation)
    fixes: list[tuple[int, int, int, str]] = []
    needs_imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result = _context_param_to_fix(node)
            if result:
                annotation, arg = result
                fixes.append((arg.lineno, arg.col_offset, len("context"), annotation))
                needs_imports.add(annotation)

    if not fixes:
        return 0

    # Convert to 0-based line indices
    lines = src.split("\n")

    # Apply fixes from the END of the file to the BEGINNING (so earlier
    # line indices don't shift)
    fixes_sorted = sorted(fixes, key=lambda x: (x[0], x[1]), reverse=True)

    for lineno, col_offset, ctx_len, annotation in fixes_sorted:
        line_idx = lineno - 1
        if 0 <= line_idx < len(lines):
            line = lines[line_idx]
            # Insert annotation right after the `context` token
            before = line[: col_offset + ctx_len]
            after = line[col_offset + ctx_len :]
            lines[line_idx] = f"{before}: {annotation}{after}"

    new_src = "\n".join(lines)

    # Add imports if needed
    if needs_imports:
        # Find existing dagster import
        import re

        for_annotation = (
            "AssetExecutionContext" in needs_imports
            or "AssetCheckExecutionContext" in needs_imports
        )

        if for_annotation:
            # Check what's already imported
            asset_exec_already = "AssetExecutionContext" in new_src
            asset_check_already = "AssetCheckExecutionContext" in new_src
            need_asset_exec = (
                "AssetExecutionContext" in needs_imports and not asset_exec_already
            )
            need_asset_check = (
                "AssetCheckExecutionContext" in needs_imports
                and not asset_check_already
            )

            if need_asset_exec or need_asset_check:
                # Find the first `from dagster import` line
                match = re.search(
                    r"^(from dagster import [^\n]+)$", new_src, re.MULTILINE
                )
                if match:
                    # Update existing import
                    old_line = match.group(1)
                    # Get the imports list
                    inside = old_line[len("from dagster import "):]
                    if inside.endswith(")"):
                        # multi-line
                        inside = inside[:-1]
                    imports = [i.strip() for i in inside.split(",") if i.strip()]
                    if need_asset_exec and "AssetExecutionContext" not in imports:
                        imports.append("AssetExecutionContext")
                    if need_asset_check and "AssetCheckExecutionContext" not in imports:
                        imports.append("AssetCheckExecutionContext")
                    new_line = f"from dagster import {', '.join(imports)},"
                    new_src = new_src[: match.start()] + new_line + new_src[match.end():]
                else:
                    # Insert new import after the last `from dagster` or `import dagster` line
                    insert_idx = 0
                    for i, line in enumerate(new_src.split("\n")):
                        if line.startswith("from dagster ") or line.startswith("import dagster"):
                            insert_idx = i + 1
                    imports_to_add = []
                    if need_asset_exec:
                        imports_to_add.append("AssetExecutionContext")
                    if need_asset_check:
                        imports_to_add.append("AssetCheckExecutionContext")
                    new_import_line = f"from dagster import {', '.join(imports_to_add)}\n"
                    lines = new_src.split("\n")
                    lines.insert(insert_idx, new_import_line)
                    new_src = "\n".join(lines)

    path.write_text(new_src)
    return len(fixes)


def main() -> int:
    total_fixes = 0
    files_fixed = 0
    for py_file in TARGET_DIR.rglob("*.py"):
        n = fix_file(py_file)
        if n > 0:
            print(f"  [ok] {py_file.relative_to(REPO_ROOT)}: {n} fix(es)")
            files_fixed += 1
            total_fixes += n

    print()
    print(f"Summary: {files_fixed} file(s) fixed, {total_fixes} annotation(s) added")
    return 0


if __name__ == "__main__":
    sys.exit(main())