#!/usr/bin/env python3
"""
migrate-baml-syntax.py — Migrate .baml files from Pydantic-style `field: type`
to BAML v0.212+ canonical `field type` (whitespace-separated).

This is part of the 2026-07-10-fix-baml-codegen-v4-syntax-v1 openspec change
(unblocks ~4,479 BAML validator errors caused by the v0.212+ syntax break).

Usage:
    uv run python scripts/migrate-baml-syntax.py --dry-run --diff
    uv run python scripts/migrate-baml-syntax.py --apply
    uv run python scripts/migrate-baml-syntax.py --verify

Modes:
    --dry-run   Report what would change WITHOUT touching files
    --apply     Apply the migration in place
    --verify    Check for remaining Pydantic-style lines (exits 1 if any)

By default, only files under cianfhoghlaim/baml/processing/ are touched
(the 17-file scope of this openspec change). Pass --all to scan every
.baml file under cianfhoghlaim/baml/.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Resolve the repo root (this script lives at <repo_root>/scripts/).
REPO_ROOT = Path(__file__).resolve().parent.parent
BAML_ROOT = REPO_ROOT / "cianfhoghlaim" / "baml"

# The 17 processing files in scope for this openspec change.
DEFAULT_TARGETS = [
    "processing/topic_profile.baml",
    "processing/player_assessment.baml",
    "processing/game_content.baml",
    "processing/author_archive.baml",
    "processing/ireland_legal_extraction.baml",
    "processing/legal_case_profile.baml",
    "processing/email.baml",
    "processing/audio_extraction.baml",
    "processing/image_generation.baml",
    "processing/style_transfer.baml",
    "processing/culture_extraction.baml",
    "processing/circular_extraction.baml",
    "processing/ocr_extraction.baml",
    "processing/ocr_validation.baml",
    "processing/official_media.baml",
    "processing/portfolio_extraction.baml",
    "processing/ui_components.baml",
]

# Files explicitly OUT OF SCOPE for this openspec change.
OUT_OF_SCOPE_GLOBS = [
    "education/lc_extraction/*.baml",  # BIEP v1 canonical contract
    "clients.baml",                     # T4 already rewrote to generator {} blocks
    "clients_llama_swap.baml",
    "**/*.bak",                         # backup files (deleted in step 4)
]


# ---------------------------------------------------------------------------
# Regex for matching Pydantic-style attribute lines
# ---------------------------------------------------------------------------
#
# Captures:
#   group 1: leading indent
#   group 2: field name (lowercase start)
#   group 3: type (string/int/float/bool OR custom class with []/?)
#   group 4: remainder of the line (attrs, comma, etc.)
#
# Replaces:
#   indent + name + ': ' + type + rest  →  indent + name + ' ' + type + rest

_TYPE_ALTERNATIVES = (
    r"string(?:\[\])?(?:\?)?"   # primitives (with optional [] and ?)
    r"|int(?:\[\])?(?:\?)?"
    r"|float(?:\[\])?(?:\?)?"
    r"|bool(?:\[\])?(?:\?)?"
    r"|image(?:\[\])?(?:\?)?"   # alias used in image_generation.baml
    r"|[A-Z][a-zA-Z0-9_]*(?:\[\])?(?:\?)?"   # custom class with optional array/optional
    r"|list<[^>]+>(?:\?)?"  # list<T> (rare)
    r"|map<[^,]+,\s*[^>]+>(?:\?)?"           # map<K,V> (rare)
    r"|class\s+[a-zA-Z0-9_]+"
    r"|enum\s+[a-zA-Z0-9_]+"
    r"|optional\s+[a-zA-Z<>,\s\[\]]+"
)

ATTR_LINE_RE = re.compile(
    r"^(\s+)"                                # group 1: leading indent
    r"([a-z_][a-zA-Z0-9_]*)"                # group 2: field name
    r"\s*:\s+"                               # the Pydantic colon + spaces
    r"(" + _TYPE_ALTERNATIVES + r")"        # group 3: type
    r"(?![\w])"                              # type boundary (no word char after)
    r"(.*)$"                                 # group 4: rest of line
)


# Heuristic regexes for lines we must NOT rewrite (even if they look like
# attribute lines).
JINJA_TOKEN_RE = re.compile(r"\{\{|\}\}")
BAML_RAW_STRING_OPENER_RE = re.compile(r'#"')      # opens a BAML #"..."# block
BAML_RAW_STRING_CLOSER_RE = re.compile(r'"#')      # closes a BAML #"..."# block
TRIPLE_HASH_RE = re.compile(r'"""')


# ---------------------------------------------------------------------------
# Per-file tracking
# ---------------------------------------------------------------------------


@dataclass
class FileResult:
    """The outcome of processing a single .baml file."""

    path: Path
    changes: list[tuple[int, str, str]] = field(default_factory=list)
    skipped: list[tuple[int, str, str]] = field(default_factory=list)

    @property
    def num_changed(self) -> int:
        return len(self.changes)

    @property
    def num_skipped(self) -> int:
        return len(self.skipped)


def is_in_raw_string(line: str, in_raw_string: bool) -> tuple[bool, bool]:
    """
    Decide whether `line` is inside a BAML multi-line raw string (`#"...content...#`).

    Detection rules:
      - A line opens a raw string when it contains an UNMATCHED `#"` token
        (i.e. no later `"#` on the same line).
      - A line closes a raw string when it contains an UNMATCHED `"#` token
        (i.e. no earlier `#"` on the same line).
      - A line containing BOTH `#"` and `"#` is a one-shot `#"...content..."#`
        literal; do not enter raw-string mode.

    Returns (skip_line, new_in_raw_string).
    """
    has_open = bool(BAML_RAW_STRING_OPENER_RE.search(line))
    has_close = bool(BAML_RAW_STRING_CLOSER_RE.search(line))

    if has_open and not has_close:
        # Opening a multi-line raw string — skip this line, enter raw mode.
        return True, True
    if has_close and not has_open:
        # Closing a multi-line raw string — skip this line, exit raw mode.
        return True, False
    if has_open and has_close:
        # Single-shot #"..."# literal on one line — skip the line itself.
        return True, False
    if in_raw_string:
        # Inside a multi-line raw string body.
        return True, True

    return False, False


def is_in_prompt(line: str, in_prompt: bool, in_triple_quote: bool) -> tuple[bool, bool]:
    """
    Decide whether a line is inside a BAML prompt block (prompt RAW ... RAW) or a
    Python-style triple-quoted block (used for test-arg docs).

    Returns (skip_line, new_in_prompt).
    """
    # Triple-quote (Python-style) tracking, used for test-arg docs.
    if '"""' in line:
        # Flip the flag on every triple-quote; skip the line itself.
        return True, in_triple_quote

    # Prompt block: opens with `prompt` plus a BAML raw-string opener.
    if not in_prompt and re.search(r'prompt\s+#?"', line):
        return True, True

    # While inside a prompt block, every line is part of the prompt body.
    if in_prompt:
        # Close when we hit the matching terminator.
        if re.search(r'"#\s*$', line) or '"#' in line:
            return True, False
        return True, True

    # Jinja tokens inside a non-prompt line are still safe. Those are the body
    # of ctx.output_format and similar. The field-name regex already avoids
    # these, so we just defend against accidental matches.
    if JINJA_TOKEN_RE.search(line):
        return True, False

    return False, False


def migrate_line(line: str) -> tuple[str, str | None]:
    """
    Try to rewrite one line from Pydantic-style `field: type` to
    BAML v0.212+ canonical `field type`.

    Returns (new_line, reason_if_skipped).
    """
    m = ATTR_LINE_RE.match(line)
    if not m:
        return line, None

    indent, name, type_, rest = m.group(1), m.group(2), m.group(3), m.group(4)

    # Defensive: make sure this isn't a comment disguised as a field.
    if name.startswith("//"):
        return line, "comment-prefix"

    # Defensive: ensure `rest` doesn't look like a function-body continuation
    # (e.g. `(args...) { ... }` chains). If `rest` begins with a non-attribute
    # token, skip.
    if rest and not re.match(r"\s*(?:[@,]|$)", rest):
        # The remainder might still be a valid attribute chain or comma; if it
        # doesn't start with whitespace-or-@/comma, treat as suspicious.
        # Allow lines like `field: Type @description(...)` (rest starts with
        # whitespace) and `field: Type,` (rest starts with comma).
        if not rest.startswith(" "):
            return line, "non-attribute-rest"

    new_line = f"{indent}{name} {type_}{rest}"
    return new_line, None


def process_file(path: Path, apply: bool) -> FileResult:
    """Walk through `path` line by line, rewriting Pydantic attribute lines."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    result = FileResult(path=path)
    in_prompt = False
    in_raw_string = False
    in_triple_quote = False

    for idx, raw_line in enumerate(lines, start=1):
        # Strip newline for matching; preserve it for writeback.
        line = raw_line.rstrip("\n")

        # Raw-string block tracking covers both `prompt #"..."#` and other
        # `#"...content...#` literals (e.g. test-args `pdf_text #"..."#`).
        skip_raw, new_in_raw = is_in_raw_string(line, in_raw_string)
        if new_in_raw != in_raw_string:
            in_raw_string = new_in_raw

        if skip_raw:
            result.skipped.append((idx, line, "inside-raw-string"))
            continue

        skip_prompt, new_in_prompt = is_in_prompt(line, in_prompt, in_triple_quote)
        if new_in_prompt != in_prompt:
            in_prompt = new_in_prompt
        if '"""' in line:
            in_triple_quote = not in_triple_quote

        if skip_prompt:
            result.skipped.append((idx, line, "inside-prompt-or-docstring"))
            continue

        new_line, reason = migrate_line(line)
        if reason is not None:
            result.skipped.append((idx, line, reason))
            continue

        if new_line == line:
            continue

        # Preserve original line ending (LF or CRLF).
        if raw_line.endswith("\r\n"):
            new_line_with_eol = new_line + "\r\n"
        else:
            new_line_with_eol = new_line + "\n"

        result.changes.append((idx, line, new_line))
        lines[idx - 1] = new_line_with_eol

    if apply and result.num_changed > 0:
        path.write_text("".join(lines), encoding="utf-8")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def resolve_targets(include_all: bool) -> list[Path]:
    """Resolve the list of files to process."""
    if include_all:
        return sorted(BAML_ROOT.rglob("*.baml"))
    return sorted(BAML_ROOT / rel for rel in DEFAULT_TARGETS)


def cmd_dry_run(targets: list[Path]) -> int:
    """Print what would change, per file."""
    grand_changes = 0
    grand_skipped = 0
    for path in targets:
        if not path.exists():
            print(f"[MISSING] {path}", file=sys.stderr)
            continue
        result = process_file(path, apply=False)
        if result.num_changed == 0 and result.num_skipped == 0:
            print(f"[OK] {path.relative_to(REPO_ROOT)} — no Pydantic lines")
            continue
        print(
            f"[CHG] {path.relative_to(REPO_ROOT)} — "
            f"{result.num_changed} to change, {result.num_skipped} skipped"
        )
        for idx, before, after in result.changes[:10]:
            print(f"  L{idx}: {before.strip()!r}  →  {after.strip()!r}")
        if result.num_changed > 10:
            print(f"  ... +{result.num_changed - 10} more")
        for idx, line, reason in result.skipped[:5]:
            print(f"  [skip] L{idx}: {line.strip()!r}  ({reason})")
        grand_changes += result.num_changed
        grand_skipped += result.num_skipped
    print(
        f"\n[SUMMARY] {grand_changes} changes pending, {grand_skipped} lines skipped"
    )
    return 0


def cmd_apply(targets: list[Path]) -> int:
    """Apply the migration in place."""
    grand_changes = 0
    grand_skipped = 0
    for path in targets:
        if not path.exists():
            print(f"[MISSING] {path}", file=sys.stderr)
            continue
        result = process_file(path, apply=True)
        if result.num_changed == 0:
            print(f"[OK] {path.relative_to(REPO_ROOT)}")
            continue
        print(
            f"[APPLIED] {path.relative_to(REPO_ROOT)} — "
            f"{result.num_changed} lines rewritten"
        )
        grand_changes += result.num_changed
        grand_skipped += result.num_skipped
    print(
        f"\n[SUMMARY] {grand_changes} lines rewritten, {grand_skipped} skipped"
    )
    return 0


def cmd_verify(targets: list[Path]) -> int:
    """Verify that no Pydantic-style lines remain (exits 1 if any)."""
    remaining = 0
    for path in targets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        in_prompt = False
        in_raw_string = False
        in_triple_quote = False
        for idx, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line
            skip_raw, new_in_raw = is_in_raw_string(line, in_raw_string)
            if new_in_raw != in_raw_string:
                in_raw_string = new_in_raw
            if skip_raw:
                continue
            if '"""' in line:
                in_triple_quote = not in_triple_quote
                continue
            if in_triple_quote:
                continue
            if not in_prompt and re.search(r'prompt\s+#?"', line):
                in_prompt = True
                continue
            if in_prompt:
                if '"#' in line:
                    in_prompt = False
                continue
            if ATTR_LINE_RE.match(line):
                print(f"[REMAIN] {path.relative_to(REPO_ROOT)}:L{idx}: {line.strip()}")
                remaining += 1
    if remaining:
        print(f"\n[FAIL] {remaining} Pydantic-style lines remain", file=sys.stderr)
        return 1
    print("\n[OK] No Pydantic-style attribute lines remain")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate .baml files from Pydantic `field: type` to BAML v0.212+ `field type`"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Print diffs without modifying")
    mode.add_argument("--apply", action="store_true", help="Rewrite files in place")
    mode.add_argument("--verify", action="store_true", help="Exit 1 if any Pydantic-style lines remain")
    parser.add_argument(
        "--diff",
        action="store_true",
        help="(dry-run only) show before/after for each change",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process every .baml file under cianfhoghlaim/baml/ (default: only the 17 processing files)",
    )
    args = parser.parse_args()

    # Default to --dry-run if nothing was specified.
    if not (args.dry_run or args.apply or args.verify):
        args.dry_run = True

    targets = resolve_targets(include_all=args.all)
    if not targets:
        print("[ERROR] No target files resolved", file=sys.stderr)
        return 2

    if args.apply:
        return cmd_apply(targets)
    if args.verify:
        return cmd_verify(targets)
    return cmd_dry_run(targets)


if __name__ == "__main__":
    sys.exit(main())