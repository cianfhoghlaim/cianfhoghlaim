#!/usr/bin/env python3
"""Bulk-replace BAML stub prompts with the canonical domain templates.

Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3). This
script replaces every `Auto-generated extraction prompt.` stub in
`baml_src/**/*.baml` with the appropriate template body from
`baml_src/_shared/templates/`.

The template is selected by parent directory (e.g.
`processing/author_archive.baml` → `processing_author_archive.baml`
template). Functions that don't match a known template get a
generic "expert extractor" template.

Usage:
    python scripts/baml_bulk_replace_stubs.py            # Apply
    python scripts/baml_bulk_replace_stubs.py --dry-run  # Preview
    python scripts/baml_bulk_replace_stubs.py --undo     # Restore from backup
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BAML_SRC = REPO_ROOT / "baml_src"
TEMPLATES_DIR = BAML_SRC / "_shared" / "templates"
BACKUP_DIR = REPO_ROOT / ".baml_stubs_backup"

STUB_LITERAL = "Auto-generated extraction prompt."

# Map from parent dir (relative to baml_src) to template filename
TEMPLATE_MAP: dict[str, str] = {
    "processing/author_archive.baml": "processing_author_archive.baml",
    "processing/style_transfer.baml": "processing_style_transfer.baml",
    "processing/game_content.baml": "processing_game_content.baml",
    "processing/circular_extraction.baml": "processing_circular_extraction.baml",
    "processing/cv_extraction.baml": "processing_cv_extraction.baml",
    "processing/gemini_deep_research": "processing_gemini_report.baml",
    "celtic/gaois/tearma.baml": "celtic_tearma.baml",
    "celtic/grammar_patterns.baml": "celtic_grammar_patterns.baml",
    "celtic/curriculum/celtic_curriculum.baml": "celtic_curriculum.baml",
    "british_isles/ireland/education/stages/upper_secondary.baml": "ireland_lc_stage.baml",
    "british_isles/ireland/education/stages/junior_cycle.baml": "ireland_jc_stage.baml",
    "british_isles/ireland/education/university": "ireland_university_module.baml",
    "british_isles/ireland/education/web": "ireland_web_content.baml",
    "british_isles/_shared/marking": "isles_marking_scheme.baml",
    "british_isles/_shared/statistics": "isles_statistics.baml",
    "british_isles/_shared/grading": "isles_grading.baml",
    "european_nations/_shared/curriculum": "european_nations_curriculum.baml",
    "american_nations/_shared/law": "american_nations_law.baml",
}

GENERIC_TEMPLATE_BODY = """  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
"""


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


def find_template(rel_path: str) -> str | None:
    """Find the canonical template for the given BAML file path."""
    # Direct match first
    if rel_path in TEMPLATE_MAP:
        template_name = TEMPLATE_MAP[rel_path]
        template_path = TEMPLATES_DIR / template_name
        if template_path.exists():
            return template_path.read_text()
    # Prefix match (for directories)
    for prefix, template_name in TEMPLATE_MAP.items():
        if rel_path.startswith(prefix):
            template_path = TEMPLATES_DIR / template_name
            if template_path.exists():
                return template_path.read_text()
    return None


def extract_prompt_body(template_content: str) -> str:
    """Extract just the prompt body from a template file."""
    m = re.search(r'prompt\s+#"(.*?)"#', template_content, re.DOTALL)
    if m:
        # Return with 2-space indent + the trailing "#
        return f'  prompt #"{m.group(1)}"#\n'
    return None


def process_file(baml_file: Path, dry_run: bool, backup: bool) -> tuple[int, int]:
    """Process one BAML file. Returns (replaced_count, remaining_count)."""
    content = baml_file.read_text()
    if STUB_LITERAL not in content:
        return 0, content.count(STUB_LITERAL)

    rel_path = str(baml_file.relative_to(BAML_SRC))

    # Get the appropriate template body
    template_content = find_template(rel_path)
    if template_content:
        new_prompt = extract_prompt_body(template_content)
    else:
        new_prompt = GENERIC_TEMPLATE_BODY

    if new_prompt is None:
        return 0, content.count(STUB_LITERAL)

    # Backup original if requested
    if backup and not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
        backup_path = BACKUP_DIR / baml_file.relative_to(BAML_SRC)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(baml_file, backup_path)

    # Replace each stub function's prompt body
    # Match: function <name>(...) { ... prompt #"Auto-generated extraction prompt."# ... }
    new_content = content
    count = 0
    pattern = re.compile(
        r'(function\s+\w+\s*\([^)]*\)(?:[^}{]*\([^)]*\))*[^}{]*\{[^}]*?)prompt\s+#"Auto-generated extraction prompt\."#',
        re.DOTALL,
    )
    new_content, n = pattern.subn(lambda m: m.group(1) + new_prompt.rstrip(), new_content)
    count = n

    if count > 0 and not dry_run:
        baml_file.write_text(new_content)

    remaining = new_content.count(STUB_LITERAL) if not dry_run else 0
    return count, remaining


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

    print(f"{'[DRY-RUN] ' if dry_run else ''}Replacing stub prompts in baml_src/**/*.baml")

    total_replaced = 0
    total_files = 0
    total_stubs_remaining = 0

    for baml_file in sorted(BAML_SRC.rglob("*.baml")):
        if baml_file.name.startswith("_test"):
            continue
        if baml_file.is_relative_to(TEMPLATES_DIR):
            continue
        replaced, remaining = process_file(baml_file, dry_run, backup=not dry_run)
        if replaced > 0:
            total_files += 1
            total_replaced += replaced
            total_stubs_remaining += remaining
            action = "would replace" if dry_run else "replaced"
            print(f"  {action} {replaced} stub(s) in {baml_file.relative_to(REPO_ROOT)}")

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Summary:")
    print(f"  Files modified: {total_files}")
    print(f"  Stubs replaced: {total_replaced}")
    print(f"  Stubs remaining: {total_stubs_remaining}")
    if not dry_run and total_replaced > 0:
        print(f"  Backups at: {BACKUP_DIR}")
    return 0 if total_stubs_remaining == 0 else 1


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    undo = "--undo" in sys.argv
    sys.exit(main(dry_run=dry_run, undo=undo))
