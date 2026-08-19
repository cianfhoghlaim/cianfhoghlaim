#!/usr/bin/env python3
"""Bulk-add catch_all blocks to every Extract* function in baml_src/.

Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3). This
script adds a `catch_all` block to every `Extract*` function that
doesn't already have one (per the BAML 0.223.0 catch error-handling
feature).

The catch block emits a safe-default value for the function's
return type by:
1. Reading the class definition (the @description decorators)
2. Generating a default value for each field (null for optional,
   "" for string, 0 for int/float, [] for array, null for enum)
3. Inserting the catch block before the closing brace

Usage:
    python scripts/baml_bulk_add_catch.py            # Apply
    python scripts/baml_bulk_add_catch.py --dry-run  # Preview
    python scripts/baml_bulk_add_catch.py --undo     # Restore from backup
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BAML_SRC = REPO_ROOT / "baml_src"
BACKUP_DIR = REPO_ROOT / ".baml_catch_backup"

# Match `function Extract*...(...) { ... }` (the whole function body)
FUNCTION_PATTERN = re.compile(
    r"function\s+(Extract\w+)\s*\([^)]*\)\s*(?:->\s*([^{}]*?))?\s*\{",
    re.MULTILINE,
)
CATCH_PATTERN = re.compile(r"\bcatch(?:_all)?\s*\(", re.MULTILINE)
CLASS_PATTERN = re.compile(r"^class\s+(\w+)\s*\{(.*?)\n\}", re.MULTILINE | re.DOTALL)
FIELD_PATTERN = re.compile(
    r"^\s*(\w+)\s+(\w+)(\[\])?\s*(\?)?\s*$",
    re.MULTILINE,
)


def find_function_end(content: str, start: int) -> int:
    """Find the matching closing brace for the function starting at `start`."""
    depth = 0
    i = start
    while i < len(content):
        c = content[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(content)


def parse_class_fields(content: str, class_name: str) -> list[tuple[str, str, bool]]:
    """Parse a class definition and return [(field_name, field_type, is_optional), ...]."""
    m = CLASS_PATTERN.search(content)
    if not m:
        return []
    class_name_match = m.group(1)
    if class_name_match != class_name:
        # Find the right class by searching for the exact class name
        for class_match in re.finditer(r"^class\s+(\w+)\s*\{(.*?)\n\}", content, re.MULTILINE | re.DOTALL):
            if class_match.group(1) == class_name:
                class_body = class_match.group(2)
                break
        else:
            return []
    else:
        class_body = m.group(2)
    fields = []
    for line in class_body.split("\n"):
        # Skip comments
        line = re.sub(r"//.*$", "", line).strip()
        if not line:
            continue
        # Match: name type  OR  name type?  OR  name type[]
        m = FIELD_PATTERN.match(line)
        if m:
            field_name, field_type, is_array, is_optional = m.groups()
            is_optional = is_optional == "?"
            fields.append((field_name, field_type, is_optional or is_array == "[]"))
    return fields


def default_value_for_type(field_type: str, is_optional: bool) -> str:
    """Return the default value for a BAML type."""
    if is_optional:
        return "null"
    ft = field_type.lower()
    if ft == "string":
        return '""'
    if ft in ("int", "float", "decimal"):
        return "0"
    if ft == "bool":
        return "false"
    if ft.startswith("map<"):
        return "{}"
    if "[]" in ft or ft.endswith("[]"):
        return "[]"
    if ft.startswith("["):
        return "[]"
    # Enum or class — use null for optional, or empty object for required
    if is_optional:
        return "null"
    return f"{ft} {{}}"


def generate_catch_block(return_type: str, content: str) -> str:
    """Generate a catch_all block for a function with the given return type."""
    if not return_type or return_type == "string":
        # Simple return types (string, int, etc.)
        if return_type == "string":
            return '\n  catch_all (err) {\n    ""\n  }\n'
        return ""

    # Class return type — emit safe defaults
    fields = parse_class_fields(content, return_type.strip())
    if not fields:
        # No class fields found — use a minimal catch
        return f'\n  catch_all (err) {{\n    {return_type.strip()} {{}}\n  }}\n'

    field_lines = []
    for fname, ftype, is_opt in fields:
        default = default_value_for_type(ftype, is_opt)
        field_lines.append(f"      {fname} {default},")

    fields_str = "\n".join(field_lines)
    return f"""
  catch_all (err) {{
    {return_type.strip()} {{
{fields_str}
    }}
  }}
"""


def process_file(baml_file: Path, dry_run: bool) -> tuple[int, int]:
    """Process one BAML file. Returns (added_count, remaining_count)."""
    content = baml_file.read_text()

    # Find all Extract* functions
    funcs_to_patch = []
    for m in FUNCTION_PATTERN.finditer(content):
        name = m.group(1)
        return_type = m.group(2) or ""
        brace_start = m.end() - 1
        body_end = find_function_end(content, brace_start)
        body = content[brace_start:body_end]
        if CATCH_PATTERN.search(body):
            continue
        funcs_to_patch.append((name, return_type.strip(), body_end))

    if not funcs_to_patch:
        return 0, 0

    if not dry_run:
        # Backup
        BACKUP_DIR.mkdir(exist_ok=True)
        backup_path = BACKUP_DIR / baml_file.relative_to(BAML_SRC)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(baml_file, backup_path)

    # Insert catch blocks (process in reverse to preserve offsets)
    new_content = content
    added = 0
    for name, return_type, body_end in reversed(funcs_to_patch):
        catch_block = generate_catch_block(return_type, new_content)
        if catch_block:
            # Insert just before the closing brace
            new_content = new_content[:body_end - 1] + catch_block + new_content[body_end - 1:]
            added += 1

    if added > 0 and not dry_run:
        baml_file.write_text(new_content)

    # Count remaining (re-scan)
    remaining = 0
    if not dry_run:
        updated = baml_file.read_text()
        for m in FUNCTION_PATTERN.finditer(updated):
            brace_start = m.end() - 1
            body_end = find_function_end(updated, brace_start)
            body = updated[brace_start:body_end]
            if not CATCH_PATTERN.search(body):
                remaining += 1
    return added, remaining


def main(dry_run: bool = False, undo: bool = False) -> int:
    if undo:
        if not BACKUP_DIR.exists():
            print("No backup directory found.")
            return 1
        print(f"Restoring from {BACKUP_DIR}")
        for src in BACKUP_DIR.rglob("*.baml"):
            dest = BAML_SRC / src.relative_to(BACKUP_DIR)
            shutil.copy(src, dest)
            print(f"  restored {dest}")
        return 0

    print(f"{'[DRY-RUN] ' if dry_run else ''}Adding catch_all blocks to Extract* functions")

    total_added = 0
    total_files = 0
    total_remaining = 0

    for baml_file in sorted(BAML_SRC.rglob("*.baml")):
        if baml_file.name.startswith("_test"):
            continue
        if baml_file.is_relative_to(REPO_ROOT / "baml_src" / "_shared" / "templates"):
            continue
        added, remaining = process_file(baml_file, dry_run)
        if added > 0:
            total_files += 1
            total_added += added
            total_remaining += remaining
            action = "would add" if dry_run else "added"
            print(f"  {action} {added} catch block(s) to {baml_file.relative_to(REPO_ROOT)}")

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Summary:")
    print(f"  Files modified: {total_files}")
    print(f"  Catch blocks added: {total_added}")
    print(f"  Extract* functions still missing catch: {total_remaining}")
    if not dry_run and total_added > 0:
        print(f"  Backups at: {BACKUP_DIR}")
    return 0 if total_remaining == 0 else 1


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    undo = "--undo" in sys.argv
    sys.exit(main(dry_run=dry_run, undo=undo))
