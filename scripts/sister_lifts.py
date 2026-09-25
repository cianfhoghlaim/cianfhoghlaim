#!/usr/bin/env python3
"""Sister-lifts wholesale-copy helper.

Per `openspec/specs/sister-shared/spec.md` (Shared-1..5), every sister-repo
file lifted into cianfhoghlaim is wholesale-copied with provenance
metadata prepended + a MODIFICATIONS.md entry recorded.

Usage:
    python scripts/sister_lifts.py add ciancheiltis \\
        --src dlt_sources/language/clarin.py \\
        --dst dlt_sources/language/clarin.py \\
        --openspec-change 2026-09-25-clarin-uk-institutional-v1 \\
        --shared-rule Shared-2-JurisdictionPipelineBase

    python scripts/sister_lifts.py ledger            # print the wholesale-copy ledger
    python scripts/sister_lifts.py verify            # verify all provenance headers

This script is the canonical entry point for every wholesale-copy in
the 5-phase × 10-stage Celtic pipeline overhaul. It's deliberately
small (≤150 LOC) so it's easy to audit.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
SISTER_LIFTS_DIR = REPO_ROOT / "stedding" / "sister-lifts"
LEDGER_PATH = SISTER_LIFTS_DIR / "LEDGER.md"
INDEX_PATH = SISTER_LIFTS_DIR / "WHOLESALE_COPY_INDEX.md"

# Canonical sister-repo locations (all on local disk, no remotes needed)
SISTER_REPOS = {
    "ciancheiltis": Path("/Users/cianmacandeisigh/dev/ciancheiltis"),
    "gemini_hackathon": Path("/Users/cianmacandeisigh/dev/gemini_hackathon"),
    "cianchosaint": Path("/Users/cianmacandeisigh/dev/cianchosaint"),
    "ciandlithe": Path("/Users/cianmacandeisigh/dev/ciandlithe"),
    "tuatha": Path("/Users/cianmacandeisigh/dev/tuatha"),
    "bonneagar": Path("/Users/cianmacandeisigh/dev/bonneagar"),
}

PROVENANCE_HEADER_TEMPLATE = """# SisterLift: {sister} @ {commit} ({branch})
# Wholesale-copied per openspec/specs/sister-shared/spec.md ({shared_rule})
# Tracking change: openspec/changes/{openspec_change}/proposal.md
# Local modifications recorded in: stedding/sister-lifts/{sister}/MODIFICATIONS.md
"""


def get_sister_commit(sister: str, branch: str | None = None) -> tuple[str, str]:
    """Get the current commit hash + branch for a sister repo."""
    if sister not in SISTER_REPOS:
        raise ValueError(f"Unknown sister: {sister}. Known: {list(SISTER_REPOS)}")
    path = SISTER_REPOS[sister]
    branch = branch or _detect_branch(path)
    commit = subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()
    return commit, branch


def _detect_branch(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
        text=True,
    ).strip()


def prepend_provenance(dst: Path, header: str) -> None:
    """Prepend the SisterLift provenance header to a Python file.

    Idempotent: detects an existing SisterLift header and replaces it.
    Detects the file type by extension — .py uses # comments, .baml uses
    // comments, .md uses markdown header.
    """
    text = dst.read_text(encoding="utf-8")
    if "SisterLift:" in text[:500]:
        # Replace the existing provenance header (the first contiguous comment block)
        lines = text.splitlines(keepends=True)
        out_lines = []
        in_provenance = False
        for line in lines:
            if not in_provenance:
                if line.startswith("# SisterLift:") or line.startswith("# Wholesale-copied") or line.startswith("# Tracking change:") or line.startswith("# Local modifications"):
                    in_provenance = True
                    continue
                else:
                    out_lines.append(line)
            else:
                if line.startswith("# "):
                    continue
                else:
                    in_provenance = False
                    out_lines.append(line)
        text = "".join(out_lines)
    # Prepend the new header
    if dst.suffix == ".py":
        # Python: keep any module docstring at the top, then add the provenance after
        if text.startswith('"""') or text.startswith("'''"):
            quote = text[:3]
            end = text.find(quote, 3)
            docstring = text[: end + 3]
            rest = text[end + 3 :]
            text = docstring + "\n\n" + header + rest
        else:
            text = header + "\n" + text
    elif dst.suffix == ".baml":
        text = "// " + header.replace("\n# ", "\n// ").replace("\n", "\n// ") + "\n" + text
    dst.write_text(text, encoding="utf-8")


def append_to_modifications(sister: str, src: Path, dst: Path, openspec_change: str) -> None:
    """Append an entry to stedding/sister-lifts/<sister>/MODIFICATIONS.md."""
    mod_path = SISTER_LIFTS_DIR / sister / "MODIFICATIONS.md"
    mod_path.parent.mkdir(parents=True, exist_ok=True)
    if not mod_path.exists():
        mod_path.write_text(
            f"# {sister} — Local Modifications to Wholesale-Copied Files\n\n"
            "Per `openspec/specs/sister-shared/spec.md`, this file records every "
            "local modification applied to a wholesale-copied file. Each entry "
            "must include: (a) source path, (b) target path, (c) commit hash, "
            "(d) the openspec change that drives the modification, (e) the date.\n\n",
            encoding="utf-8",
        )
    today = dt.date.today().isoformat()
    entry = (
        f"\n## {today} — {openspec_change}\n\n"
        f"- **Source:** `{src}`\n"
        f"- **Target:** `{dst.relative_to(REPO_ROOT)}`\n"
        f"- **Local modifications:** None (wholesale-copy only)\n"
    )
    with mod_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def add(sister: str, src_rel: str, dst_rel: str, openspec_change: str, shared_rule: str, branch: str | None = None) -> None:
    """Wholesale-copy a file from a sister repo into cianfhoghlaim with provenance."""
    if sister not in SISTER_REPOS:
        raise ValueError(f"Unknown sister: {sister}")
    src = SISTER_REPOS[sister] / src_rel
    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    commit, branch_name = get_sister_commit(sister, branch)
    dst = REPO_ROOT / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"Copying {src} -> {dst} ({sister} @ {commit[:8]} on {branch_name})")
    # Use cp for portability
    subprocess.check_call(["cp", "-p", str(src), str(dst)])
    header = PROVENANCE_HEADER_TEMPLATE.format(
        sister=sister,
        commit=commit,
        branch=branch_name,
        shared_rule=shared_rule,
        openspec_change=openspec_change,
    )
    if dst.suffix in (".py", ".baml"):
        prepend_provenance(dst, header)
    append_to_modifications(sister, src, dst, openspec_change)
    _append_ledger_entry(sister, src_rel, dst_rel, commit, branch_name, openspec_change)


def _append_ledger_entry(sister: str, src_rel: str, dst_rel: str, commit: str, branch: str, openspec_change: str) -> None:
    today = dt.date.today().isoformat()
    if not LEDGER_PATH.exists():
        LEDGER_PATH.write_text(
            "# Sister-Lifts Ledger\n\n"
            "| Date | Sister | Source | Target | Commit | Branch | Phase change |\n"
            "|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(f"| {today} | {sister} | `{src_rel}` | `{dst_rel}` | `{commit[:8]}` | `{branch}` | `{openspec_change}` |\n")


def cmd_ledger() -> None:
    """Print the wholesale-copy ledger."""
    if not LEDGER_PATH.exists():
        print("No wholesale-copies yet — ledger is empty.")
        return
    print(LEDGER_PATH.read_text(encoding="utf-8"))


def cmd_verify() -> int:
    """Verify every file tracked in the ledger still has its SisterLift header.

    Logic: read the LEDGER.md to find every (sister, target-path) pair that's
    been wholesale-copied. For each, verify the target file still has the
    SisterLift provenance header in the first 500 chars. Files with "sister"
    in the name but not in the ledger are NOT flagged (they may be cianfhoghlaim-
    original code that legitimately references sister repos).
    """
    if not LEDGER_PATH.exists():
        print("No ledger yet — nothing to verify.")
        return 0
    violations = []
    # Parse the ledger markdown table for target paths
    target_paths: set[str] = set()
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        # Match the markdown table row: | date | sister | `src` | `target` | ...
        m = re.match(r"^\|\s*\S+\s*\|\s*\S+\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            target_paths.add(m.group(2))
    for target in sorted(target_paths):
        dst = REPO_ROOT / target
        if not dst.exists():
            violations.append((dst, "missing"))
            continue
        try:
            head = dst.read_text(encoding="utf-8")[:500]
        except (UnicodeDecodeError, OSError) as e:
            violations.append((dst, f"read-error: {e}"))
            continue
        if "SisterLift:" not in head:
            violations.append((dst, "missing SisterLift header"))
    if violations:
        print(f"ERROR: {len(violations)} ledger-tracked file(s) missing provenance:")
        for v, reason in violations:
            print(f"  - {v.relative_to(REPO_ROOT)}: {reason}")
        return 1
    print(f"OK: all {len(target_paths)} ledger-tracked wholesale-copied files have SisterLift headers")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sister-lifts wholesale-copy helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a wholesale-copy entry")
    p_add.add_argument("sister", choices=list(SISTER_REPOS))
    p_add.add_argument("--src", required=True, help="Source path relative to sister repo")
    p_add.add_argument("--dst", required=True, help="Target path relative to cianfhoghlaim root")
    p_add.add_argument("--openspec-change", required=True)
    p_add.add_argument("--shared-rule", default="Shared-2-JurisdictionPipelineBase")
    p_add.add_argument("--branch", default=None)

    sub.add_parser("ledger", help="Print the wholesale-copy ledger")
    sub.add_parser("verify", help="Verify SisterLift headers")

    args = parser.parse_args()
    if args.cmd == "add":
        add(args.sister, args.src, args.dst, args.openspec_change, args.shared_rule, args.branch)
        return 0
    if args.cmd == "ledger":
        cmd_ledger()
        return 0
    if args.cmd == "verify":
        return cmd_verify()
    return 1


if __name__ == "__main__":
    sys.exit(main())
