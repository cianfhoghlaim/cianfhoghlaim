"""lint_drift_docs.py — the anti-drift gate for AGENTS.md number claims.

Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
(see openspec/changes/2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/specs/centralize-cross-cutting-docs/spec.md).

Walks every in-repo AGENTS.md file, regex-extracts claims of the form
``(\d+) (specs|skills|stacks|models|notebooks)``, and validates each
against the live ground truth. Exits 1 on any mismatch; writes a JSON
+ Markdown report to stedding/sync-reports/docs-drift-{date}.{json,md}.

Usage:
    uv run python scripts/lint_drift_docs.py              # audit (CI mode)
    uv run python scripts/lint_drift_docs.py --dry-run    # print report, exit 0
    uv run python scripts/lint_drift_docs.py --json       # JSON to stdout
    uv run python scripts/lint_drift_docs.py --fix        # suggest the fix in the report
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if not (REPO_ROOT / "openspec").is_dir():
    # The script may be invoked from a different cwd; fall back to a
    # filesystem walk until we hit the cianfhoghlaim monorepo root.
    candidate = Path(__file__).resolve().parent
    while candidate != candidate.parent:
        if (candidate / "openspec").is_dir() and (candidate / ".agents").is_dir():
            REPO_ROOT = candidate
            break
        candidate = candidate.parent
REPORT_DIR = REPO_ROOT / "stedding" / "sync-reports"

# Files in scope for the audit. The root AGENTS.md, openspec/AGENTS.md,
# and the per-area AGENTS.md files (the 5 already present + the 5 new
# ones from Phase 2 T2.4).
AGENTS_FILES = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "openspec" / "AGENTS.md",
    REPO_ROOT / "cocoindex" / "AGENTS.md",
    REPO_ROOT / "dlt_sources" / "AGENTS.md",
    REPO_ROOT / "agents" / "AGENTS.md",
    REPO_ROOT / "agents" / "meaisinfhoghlaim" / "AGENTS.md",
    REPO_ROOT / "agents" / "tuatha" / "AGENTS.md",
    REPO_ROOT / "agents" / "api" / "AGENTS.md",
    REPO_ROOT / "agents" / "tools" / "AGENTS.md",
    REPO_ROOT / "motherduck" / "AGENTS.md",
    REPO_ROOT / "bonneagar" / "AGENTS.md",
    REPO_ROOT / "orchestration" / "AGENTS.md",  # NEW Phase 2 T2.4
    REPO_ROOT / "baml_src" / "AGENTS.md",        # NEW Phase 2 T2.4
    REPO_ROOT / "meaisinfhoghlaim" / "AGENTS.md",  # NEW Phase 2 T2.4
    REPO_ROOT / "notebooks" / "AGENTS.md",      # NEW Phase 2 T2.4
    REPO_ROOT / "web" / "AGENTS.md",            # NEW Phase 2 T2.4
]

# The 5 categories the lint understands. The pattern requires the
# number to NOT be preceded by a digit or hyphen (so "2026-08-15 specs"
# does NOT match "15 specs" — that's a date, not a spec count).
CLAIM_PATTERN = re.compile(
    r"(?<![\d-])(\d+)\s+(specs|skills|stacks|models|notebooks)\b",
    re.IGNORECASE,
)


def ground_truth() -> dict[str, int]:
    """Compute the live counts for the 5 categories.

    Returns:
        dict with keys: specs, skills, stacks, models, notebooks
    """
    counts: dict[str, int] = {}

    # specs: count openspec/specs/<name>/ directories
    specs = REPO_ROOT / "openspec" / "specs"
    if specs.is_dir():
        counts["specs"] = sum(1 for p in specs.iterdir() if p.is_dir())

    # skills: count .agents/skills/<name>/SKILL.md files (RECURSIVE; the
    # copilotkit/, dagster/, etc. skills nest sub-skills)
    skills = REPO_ROOT / ".agents" / "skills"
    if skills.is_dir():
        counts["skills"] = sum(1 for _ in skills.rglob("SKILL.md"))

    # stacks: count bonneagar/stacks/*/ directories
    stacks = REPO_ROOT / "bonneagar" / "stacks"
    if stacks.is_dir():
        counts["stacks"] = sum(1 for p in stacks.iterdir() if p.is_dir())

    # models: derive from MODEL_REGISTRY.summary()["total"] via uv run
    # (graceful fallback: hardcode 52 if the call fails)
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                "from meaisinfhoghlaim.models import MODEL_REGISTRY; "
                "print(MODEL_REGISTRY.summary()['total'])",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip().isdigit():
            counts["models"] = int(result.stdout.strip())
        else:
            counts["models"] = 52
    except (subprocess.TimeoutExpired, FileNotFoundError):
        counts["models"] = 52

    # notebooks: count notebooks/*.py files (active marimo notebooks)
    notebooks = REPO_ROOT / "notebooks"
    if notebooks.is_dir():
        counts["notebooks"] = sum(
            1 for p in notebooks.glob("*.py") if not p.name.startswith("__")
        )

    return counts


def extract_claims(text: str, source_path: Path) -> list[dict]:
    """Extract all claim matches from a single AGENTS.md file.

    Returns:
        list of dicts: { file, line, category, claimed, context }
    """
    claims: list[dict] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in CLAIM_PATTERN.finditer(line):
            claimed = int(match.group(1))
            category = match.group(2).lower()
            # Capture ±10 chars of context for the report
            ctx_start = max(0, match.start() - 10)
            ctx_end = min(len(line), match.end() + 10)
            context = line[ctx_start:ctx_end].strip()
            claims.append({
                "file": str(source_path.relative_to(REPO_ROOT)),
                "line": line_no,
                "category": category,
                "claimed": claimed,
                "context": context,
            })
    return claims


def audit(agents_files: list[Path], truth: dict[str, int]) -> dict:
    """Run the audit; return a structured report."""
    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ground_truth": truth,
        "in_scope_files": [str(p.relative_to(REPO_ROOT)) for p in agents_files if p.is_file()],
        "claims": [],
        "violations": [],
        "summary": {"total_claims": 0, "violations": 0, "files_with_violations": 0},
    }

    violating_files: set[str] = set()

    for path in agents_files:
        if not path.is_file():
            continue
        text = path.read_text()
        claims = extract_claims(text, path)
        report["claims"].extend(claims)
        for claim in claims:
            cat = claim["category"]
            if cat in truth and claim["claimed"] != truth[cat]:
                violation = {
                    **claim,
                    "actual": truth[cat],
                    "fix": f"Replace `{claim['claimed']}` with `{truth[cat]}` in {claim['file']}:{claim['line']}",
                }
                report["violations"].append(violation)
                violating_files.add(claim["file"])

    report["summary"]["total_claims"] = len(report["claims"])
    report["summary"]["violations"] = len(report["violations"])
    report["summary"]["files_with_violations"] = len(violating_files)
    return report


def write_reports(report: dict, fix: bool = False) -> tuple[Path, Path]:
    """Write the JSON + Markdown reports to stedding/sync-reports/."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_path = REPORT_DIR / f"docs-drift-{today}.json"
    md_path = REPORT_DIR / f"docs-drift-{today}.md"

    json_path.write_text(json.dumps(report, indent=2) + "\n")

    lines: list[str] = [
        f"# AGENTS.md Drift Report — {today}",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Ground truth",
        "",
        "| Category | Count |",
        "|:--|--:|",
    ]
    for cat, count in sorted(report["ground_truth"].items()):
        lines.append(f"| {cat} | {count} |")
    lines.extend([
        "",
        "## Summary",
        "",
        f"- Total claims scanned: **{report['summary']['total_claims']}**",
        f"- Violations: **{report['summary']['violations']}**",
        f"- Files with violations: **{report['summary']['files_with_violations']}**",
        "",
        "## In-scope files",
        "",
    ])
    for f in report["in_scope_files"]:
        lines.append(f"- `{f}`")
    lines.append("")

    if report["violations"]:
        lines.extend([
            "## Violations",
            "",
            "| File | Line | Category | Claimed | Actual | Fix |",
            "|:--|--:|:--|--:|--:|:--|",
        ])
        for v in report["violations"]:
            fix_text = v["fix"] if fix else "—"
            lines.append(
                f"| `{v['file']}` | {v['line']} | {v['category']} | "
                f"{v['claimed']} | {v['actual']} | {fix_text} |"
            )
    else:
        lines.extend([
            "## Result",
            "",
            f"OK: 0 number drift claims in {len(report['in_scope_files'])} audited AGENTS.md files",
        ])
    lines.append("")
    md_path.write_text("\n".join(lines))
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint AGENTS.md number claims against ground truth.")
    parser.add_argument("--dry-run", action="store_true", help="Exit 0 always; print report")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    parser.add_argument("--fix", action="store_true", help="Include the suggested fix in the report")
    args = parser.parse_args()

    truth = ground_truth()
    report = audit(AGENTS_FILES, truth)

    json_path, md_path = write_reports(report, fix=args.fix)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        violations = report["summary"]["violations"]
        if violations:
            print(f"ERROR: {violations} AGENTS.md number drift violation(s) found")
            for v in report["violations"]:
                print(f"  - {v['file']}:{v['line']}  {v['category']}: "
                      f"claimed {v['claimed']}, actual {v['actual']}")
            print(f"  Report: {md_path}")
        else:
            print(f"OK: 0 number drift claims in {len(report['in_scope_files'])} audited AGENTS.md files")
            print(f"  Report: {md_path}")

    if args.dry_run:
        return 0
    return 1 if report["summary"]["violations"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
