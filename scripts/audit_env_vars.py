"""
Audit every environment variable referenced in code against
`.env.example`, and emit a generated manifest grouped by owning
subsystem.

Unlike `scripts/validate_env.py` (a narrow 7-row smoke test for the
CIANFHOGHLAIM_* observability matrix), this script is a broad,
reproducible SCAN: it walks the Python + TypeScript source tree,
extracts every `os.environ[...]` / `os.getenv(...)` / `process.env.X`
reference, and reports which ones are undocumented in `.env.example`.

Why this exists: a 2026-08-26 repo audit found `.env.example` had 11
variables while the working `.env` had 139 and code referenced ~460
distinct names — meaning a fresh clone had no way to discover what it
needed to set. This script makes that gap auditable and re-checkable,
instead of a one-off manual count.

Run via:
    uv run python3 scripts/audit_env_vars.py                # human report
    uv run python3 scripts/audit_env_vars.py --json          # machine report
    uv run python3 scripts/audit_env_vars.py --write-example # append undocumented vars to .env.example (grouped, placeholder values)

This does NOT read or write real secret values — it only extracts
variable NAMES from source code and cross-references them against
`.env` / `.env.example` key names. It never inspects `.env` values.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories to scan for env-var references, mapped to a short
# subsystem tag used to group the generated .env.example output.
SCAN_DIRS: dict[str, str] = {
    "dlt_sources": "DATA — dlt sources",
    "orchestration": "DATA — dagster orchestration",
    "cocoindex_flows": "DATA — cocoindex flows",
    "agents": "AGENTS — agent runtime",
    "meaisinfhoghlaim": "AGENTS — meaisinfhoghlaim platform",
    "observability": "OBSERVABILITY",
    "scripts": "TOOLING — scripts",
    "bonneagar/iac": "INFRA — bonneagar IaC",
    "web": "WEB",
    "notebooks": "NOTEBOOKS — marimo",
}

# Excluded from the "real gap" count — generic process/OS env vars
# every language runtime reads, not app-specific config.
NOISE_VARS: frozenset[str] = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "SHELL",
        "PWD",
        "LANG",
        "LC_ALL",
        "TERM",
        "TMPDIR",
        "TMP",
        "TEMP",
        "CI",
        "DEBUG",
        "NODE_ENV",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "PORT",
        "HOST",
        "HOSTNAME",
        "COLUMNS",
        "LINES",
        "EDITOR",
        "PAGER",
    }
)

PY_ENV_PATTERN = re.compile(
    r"os\.(?:environ(?:\.get)?|getenv)\(\s*[\"']([A-Z][A-Z0-9_]+)[\"']"
)
TS_ENV_PATTERN = re.compile(r"process\.env(?:\.([A-Z][A-Z0-9_]+)|\[[\"']([A-Z][A-Z0-9_]+)[\"'])")

SKIP_DIR_NAMES = {"node_modules", "__pycache__", ".venv", ".turbo", "dist", ".git"}


def _iter_files(base: Path, suffixes: tuple[str, ...]) -> list[Path]:
    if not base.exists():
        return []
    out: list[Path] = []
    for p in base.rglob("*"):
        if p.suffix not in suffixes:
            continue
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        out.append(p)
    return out


def scan() -> dict[str, set[str]]:
    """Return {subsystem_tag: {VAR_NAME, ...}}."""
    found: dict[str, set[str]] = {tag: set() for tag in SCAN_DIRS.values()}
    for rel_dir, tag in SCAN_DIRS.items():
        base = REPO_ROOT / rel_dir
        for f in _iter_files(base, (".py",)):
            try:
                text = f.read_text(errors="ignore")
            except OSError:
                continue
            for m in PY_ENV_PATTERN.finditer(text):
                found[tag].add(m.group(1))
        for f in _iter_files(base, (".ts", ".tsx")):
            try:
                text = f.read_text(errors="ignore")
            except OSError:
                continue
            for m in TS_ENV_PATTERN.finditer(text):
                found[tag].add(m.group(1) or m.group(2))
    return found


def read_env_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys: set[str] = set()
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]*)=", line)
        if m:
            keys.add(m.group(1))
    return keys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument(
        "--write-example",
        action="store_true",
        help="append undocumented vars to .env.example, grouped by subsystem, with placeholder values",
    )
    ap.add_argument(
        "--fail-on-gap",
        action="store_true",
        help="exit 1 if any code-referenced var is undocumented in .env.example (CI gate mode)",
    )
    args = ap.parse_args()

    by_subsystem = scan()
    all_vars: set[str] = set()
    for names in by_subsystem.values():
        all_vars |= names
    all_vars -= NOISE_VARS

    example_keys = read_env_keys(REPO_ROOT / ".env.example")
    dotenv_keys = read_env_keys(REPO_ROOT / ".env")

    undocumented = sorted(all_vars - example_keys)
    dead_in_example = sorted(example_keys - all_vars)

    if args.json:
        print(
            json.dumps(
                {
                    "total_referenced": len(all_vars),
                    "documented_in_example": len(all_vars & example_keys),
                    "undocumented_in_example": undocumented,
                    "dead_in_example": dead_in_example,
                    "missing_from_dotenv": sorted(all_vars - dotenv_keys),
                    "by_subsystem": {k: sorted(v) for k, v in by_subsystem.items()},
                },
                indent=2,
            )
        )
    else:
        print("=" * 72)
        print("Environment variable audit")
        print("=" * 72)
        print(f"Referenced in code (excluding {len(NOISE_VARS)} noise vars): {len(all_vars)}")
        print(f"Documented in .env.example:                                 {len(all_vars & example_keys)}")
        print(f"UNDOCUMENTED in .env.example:                               {len(undocumented)}")
        print(f"Dead entries in .env.example (not referenced anywhere):     {len(dead_in_example)}")
        print()
        if dead_in_example:
            print("Dead .env.example entries (review — may be indirect / mise-injected):")
            for v in dead_in_example:
                print(f"  - {v}")
            print()
        print("Undocumented vars by subsystem:")
        for tag in sorted(SCAN_DIRS.values()):
            names = sorted((by_subsystem.get(tag, set()) - NOISE_VARS) - example_keys)
            if names:
                print(f"\n  [{tag}]  ({len(names)})")
                for v in names:
                    print(f"    {v}")

    if args.write_example:
        _write_example(by_subsystem, example_keys)

    if args.fail_on_gap and undocumented:
        print(f"\nFAIL — {len(undocumented)} undocumented env var(s). Run with --write-example to fix.")
        return 1
    return 0


def _write_example(by_subsystem: dict[str, set[str]], existing: set[str]) -> None:
    path = REPO_ROOT / ".env.example"
    existing_text = path.read_text() if path.exists() else ""
    additions: list[str] = []
    additions.append("")
    additions.append("# " + "=" * 76)
    additions.append("# Auto-discovered vars (scripts/audit_env_vars.py --write-example)")
    additions.append("# Grouped by owning subsystem. Values are PLACEHOLDERS — fill in via")
    additions.append("# Infisical / `bun run secrets:env`, do not commit real secrets here.")
    additions.append("# " + "=" * 76)
    for tag in sorted(SCAN_DIRS.values()):
        names = sorted((by_subsystem.get(tag, set()) - NOISE_VARS) - existing)
        if not names:
            continue
        additions.append(f"\n# --- {tag} ---")
        for v in names:
            additions.append(f"{v}=")
    with path.open("a") as fh:
        fh.write("\n".join(additions) + "\n")
    print(f"\nAppended {sum(1 for line in additions if '=' in line and not line.startswith('#'))} vars to {path}")


if __name__ == "__main__":
    sys.exit(main())
