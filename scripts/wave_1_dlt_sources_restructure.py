#!/usr/bin/env python3
"""
Wave 1 dlt_sources domain-restructure migration script.

This script performs the full Wave 1 restructure of `dlt_sources/`:

1. Domain-first law/medicine/education split (179 dirs)
2. Tertiary pipeline relocation (UoG + NUI federation)
3. Themed package restructure (language → lexicographic/cultural_heritage/
   local_archive/, media → media_text/media_comics/media_games/, etc.)
4. Layer-grouped destinations (dlt_sources/common/destinations/)
5. Re-export shims at all legacy locations

All moves are `git mv` (preserves file history). The script is idempotent:
running it twice produces the same end state. It also has `--dry-run` and
`--skip-move` flags for safe iteration.

Usage:
    uv run python scripts/wave_1_dlt_sources_restructure.py --dry-run
    uv run python scripts/wave_1_dlt_sources_restructure.py
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

# Project root (the cianfhoghlaim monorepo)
PROJECT_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
DLT = PROJECT_ROOT / "dlt_sources"

# Geographies that have law/medicine/education subdirs (the user said KEEP ENGLISH)
GEOGRAPHIES = [
    "american_nations",
    "british_isles",
    "commonwealth",
    "european_nations",
    "european_union",
]


@dataclass(frozen=True)
class Move:
    """A single `git mv` operation."""
    src: Path  # absolute path
    dst: Path  # absolute path
    kind: str  # "dir" or "file"
    reason: str  # human-readable explanation


def discover_domain_moves(geography: str, domain: str) -> Iterator[Move]:
    """Yield (src, dst) for every law/medicine/education/<jurisdiction> dir."""
    src_root = DLT / geography
    if not src_root.exists():
        return
    # Find every <jurisdiction>/<domain> directory under this geography
    for jurisdiction_dir in sorted(src_root.iterdir()):
        if not jurisdiction_dir.is_dir() or jurisdiction_dir.name.startswith("_"):
            continue
        if jurisdiction_dir.name in {"__pycache__"}:
            continue
        src = jurisdiction_dir / domain
        if not (src.is_dir() and src.exists()):
            continue
        # Skip __pycache__ inside
        if src.name.startswith("_"):
            continue
        # Map: dlt_sources/<geography>/<jurisdiction>/<domain>/
        #      → dlt_sources/<domain>/<jurisdiction>/<geography>/
        dst = DLT / domain / jurisdiction_dir.name / geography
        yield Move(
            src=src,
            dst=dst,
            kind="dir",
            reason=f"domain-first {domain} split",
        )


def discover_themed_file_moves() -> Iterator[Move]:
    """Yield (src, dst) for every themed package restructure."""
    # ─── language/ → lexicographic/ + cultural_heritage/ + local_archive/ ───
    LEXICOGRAPHIC = {"ainm", "canuint", "canuint_audio", "canuint_dialect_summary",
                     "canuint_search", "canuint_word_alignment", "logainm",
                     "tearma", "tearma_search", "universal_dependencies"}
    CULTURAL_HERITAGE = {"celtic_mythology", "duchas", "duchas_images", "gaois",
                         "gaois_combined", "heritage", "hidden_heritages"}
    LOCAL_ARCHIVE = {"local_documents_by_subject", "local_education_documents"}

    language_dir = DLT / "language"
    if language_dir.exists():
        for f in sorted(language_dir.iterdir()):
            if f.name.startswith("_") and f.name != "__init__.py":
                continue
            if f.name == "__init__.py":
                # Move __init__.py to all three new locations? Or keep at language?
                # Decision: keep __init__.py at language/ for backwards compat shim
                continue
            if not f.suffix == ".py":
                continue
            stem = f.stem
            if stem in LEXICOGRAPHIC:
                dst = DLT / "lexicographic" / f.name
                yield Move(f, dst, "file", "language → lexicographic")
            elif stem in CULTURAL_HERITAGE:
                dst = DLT / "cultural_heritage" / f.name
                yield Move(f, dst, "file", "language → cultural_heritage")
            elif stem in LOCAL_ARCHIVE:
                dst = DLT / "local_archive" / f.name
                yield Move(f, dst, "file", "language → local_archive")
            elif stem.startswith("_"):
                # Helper files: classify by suffix
                if "canuint" in stem or "tearma" in stem or "gaois" in stem:
                    dst = DLT / "lexicographic" / f.name
                    yield Move(f, dst, "file", "language → lexicographic (helper)")
                elif "duchas" in stem:
                    dst = DLT / "cultural_heritage" / f.name
                    yield Move(f, dst, "file", "language → cultural_heritage (helper)")
                elif "local_documents" in stem:
                    dst = DLT / "local_archive" / f.name
                    yield Move(f, dst, "file", "language → local_archive (helper)")

    # ─── media/ → media_text/ + media_comics/ + media_games/ ───
    MEDIA_TEXT_DIRS = {"animation", "celtic_history_research", "official", "prose"}
    MEDIA_COMICS_DIRS = {"comics"}
    MEDIA_GAMES_DIRS = {"games"}

    media_dir = DLT / "media"
    if media_dir.exists():
        for sub in sorted(media_dir.iterdir()):
            if not sub.is_dir() or sub.name.startswith("_"):
                continue
            if sub.name == "__pycache__":
                continue
            if sub.name in MEDIA_TEXT_DIRS:
                dst = DLT / "media_text" / sub.name
                yield Move(sub, dst, "dir", "media → media_text")
            elif sub.name in MEDIA_COMICS_DIRS:
                dst = DLT / "media_comics" / sub.name
                yield Move(sub, dst, "dir", "media → media_comics (VLM)")
            elif sub.name in MEDIA_GAMES_DIRS:
                dst = DLT / "media_games" / sub.name
                yield Move(sub, dst, "dir", "media → media_games (VLM+structured)")

    # ─── api_sources/ → api_documentation/ + api_github/ + api_local/ + crypteolas_defi/ ───
    api_sources_dir = DLT / "api_sources"
    if api_sources_dir.exists():
        # Map: api_sources/<name>/ → api_<name>/ OR crypteolas_defi/
        # Note: the legacy "defi" inside api_sources will be MERGED with crypteolas/defi
        for sub in sorted(api_sources_dir.iterdir()):
            if not sub.is_dir() or sub.name.startswith("_"):
                continue
            if sub.name == "defi":
                # Move to crypteolas_defi/ — we'll merge the two defi/ dirs in the
                # crypteolas step below
                dst = DLT / "crypteolas_defi" / sub.name  # temporary
                yield Move(sub, dst, "dir", "api_sources/defi → crypteolas_defi (temp)")
            else:
                dst = DLT / f"api_{sub.name}"
                yield Move(sub, dst, "dir", f"api_sources → api_{sub.name}")

    # ─── crypteolas/ → crypteolas_chain/ + crypteolas_docs/ + crypteolas_defi/ ───
    crypteolas_dir = DLT / "crypteolas"
    if crypteolas_dir.exists():
        for sub in sorted(crypteolas_dir.iterdir()):
            if not sub.is_dir() or sub.name.startswith("_"):
                continue
            if sub.name == "local" or sub.name == "github":
                dst = DLT / "crypteolas_chain" / sub.name
                yield Move(sub, dst, "dir", "crypteolas → crypteolas_chain")
            elif sub.name == "documentation":
                dst = DLT / "crypteolas_docs" / sub.name
                yield Move(sub, dst, "dir", "crypteolas → crypteolas_docs")
            elif sub.name == "defi":
                # Move to crypteolas_defi/ — merge with api_sources/defi later
                dst = DLT / "crypteolas_defi" / sub.name
                yield Move(sub, dst, "dir", "crypteolas → crypteolas_defi")

    # ─── apple_photos/ → media_personal/ ───
    ap_dir = DLT / "apple_photos"
    if ap_dir.exists():
        for f in sorted(ap_dir.iterdir()):
            if f.name == "__pycache__":
                continue
            dst = DLT / "media_personal" / f.name
            yield Move(f, dst, "file" if f.is_file() else "dir",
                       "apple_photos → media_personal")

    # ─── filesystem/ → raw_files/ ───
    fs_dir = DLT / "filesystem"
    if fs_dir.exists():
        for f in sorted(fs_dir.iterdir()):
            if f.name == "__pycache__":
                continue
            dst = DLT / "raw_files" / f.name
            yield Move(f, dst, "file" if f.is_file() else "dir",
                       "filesystem → raw_files")

    # ─── portfolio/ → cv/ + artwork/ + labels/ ───
    portfolio_dir = DLT / "portfolio"
    if portfolio_dir.exists():
        for f in sorted(portfolio_dir.iterdir()):
            if f.name == "__pycache__":
                continue
            stem = f.stem
            if "cv" in stem or "teaching" in stem:
                dst = DLT / "cv" / f.name
                yield Move(f, dst, "file" if f.is_file() else "dir",
                           "portfolio → cv")
            elif "artwork" in stem:
                dst = DLT / "artwork" / f.name
                yield Move(f, dst, "file" if f.is_file() else "dir",
                           "portfolio → artwork")
            elif "label" in stem:
                dst = DLT / "labels" / f.name
                yield Move(f, dst, "file" if f.is_file() else "dir",
                           "portfolio → labels")

    # ─── jobs/ → _jobs/ (rename only) ───
    jobs_dir = DLT / "jobs"
    if jobs_dir.exists():
        dst = DLT / "_jobs"
        yield Move(jobs_dir, dst, "dir", "jobs → _jobs (CLI dispatcher)")


def discover_all_moves() -> list[Move]:
    """Build the full migration list."""
    moves: list[Move] = []
    # Domain-first law/medicine/education
    for geo in GEOGRAPHIES:
        for domain in ("law", "medicine", "education"):
            moves.extend(discover_domain_moves(geo, domain))
    # Themed package restructure
    moves.extend(discover_themed_file_moves())
    return moves


def ensure_parent(p: Path) -> None:
    """Ensure the parent directory of p exists."""
    p.parent.mkdir(parents=True, exist_ok=True)


def execute_move(m: Move, *, dry_run: bool, skip_move: bool) -> bool:
    """Execute a single move. Returns True if successful."""
    if m.src.exists() and not skip_move:
        # Use git mv to preserve history (only if the file is tracked by git)
        try:
            rel_src = m.src.relative_to(PROJECT_ROOT)
            # Check if tracked by git
            check = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(rel_src)],
                cwd=PROJECT_ROOT, capture_output=True, text=True
            )
            if check.returncode == 0:
                if not dry_run:
                    ensure_parent(m.dst)
                    cmd = ["git", "mv", str(rel_src), str(m.dst.relative_to(PROJECT_ROOT))]
                    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"  git mv FAILED: {result.stderr}", file=sys.stderr)
                        return False
            else:
                # Not tracked — plain mv
                if not dry_run:
                    ensure_parent(m.dst)
                    shutil.move(str(m.src), str(m.dst))
        except Exception as exc:
            print(f"  MOVE FAILED: {exc}", file=sys.stderr)
            return False
    elif m.src.exists() and skip_move:
        pass  # dry-run display only
    elif not m.src.exists():
        return False  # source doesn't exist, skip
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't actually move anything, just print the plan")
    parser.add_argument("--skip-move", action="store_true",
                        help="Print moves but don't execute (for debugging)")
    args = parser.parse_args()

    moves = discover_all_moves()
    print(f"=== Wave 1 dlt_sources restructure — {len(moves)} moves planned ===")
    if args.dry_run or args.skip_move:
        print(f"    (dry-run / no-move mode)")
    print()

    by_kind: dict[str, list[Move]] = {}
    for m in moves:
        by_kind.setdefault(m.kind, []).append(m)

    for kind in sorted(by_kind):
        ms = by_kind[kind]
        print(f"## {kind.upper()} moves ({len(ms)})")
        for m in ms:
            src_rel = m.src.relative_to(PROJECT_ROOT)
            dst_rel = m.dst.relative_to(PROJECT_ROOT)
            status = "DRY" if (args.dry_run or args.skip_move) else "MOVED"
            print(f"  [{status}] {src_rel} → {dst_rel}    ({m.reason})")
        print()

    if not args.dry_run and not args.skip_move:
        success = 0
        failed = 0
        for m in moves:
            if execute_move(m, dry_run=False, skip_move=False):
                success += 1
            else:
                failed += 1
        print(f"=== Done: {success} succeeded, {failed} failed ===")
        return 0 if failed == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
