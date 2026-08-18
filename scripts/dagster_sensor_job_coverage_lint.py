#!/usr/bin/env python3
"""Dagster sensor-job-coverage lint.

Per the 2026-08-17-hygiene-drift-cleanup-v1 change (P1.7): every
@sensor(job_name=...) in orchestration/sensors/ MUST have a matching
define_asset_job (with the same name=) somewhere in the orchestration/
tree. The canonical home is orchestration/sensors/jobs.py per the
2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1 change; the
garage_pdf_arrival_sensor.py keeps its define_asset_job locally per
the 2026-08-08-lakehouse-extensive-hydration-v1 change.

Without this lint, the BIEP v3 auto-refresh breaks silently at the
wire layer - Dagster emits RunRequest, fails to resolve the job, and
logs JobNotFoundError (the 8-of-8 silent failure that the
2026-08-08-lakehouse-extensive-hydration-v1 change documented).

This script uses line-based static analysis (not import-based) so it
runs in any environment, including the preflight CI gate.

Usage:
    mise run lint:dagster:sensor-job-coverage

Exit codes:
    0 = all sensor job_names have matching jobs
    1 = one or more dangling job_names
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SENSORS_DIR = REPO_ROOT / "orchestration" / "sensors"

# Match the first job_name= or define_asset_job(name=...) on a non-comment,
# non-doc-string line. Doc-strings are handled at the file level below.
JOB_NAME_RE = re.compile(r"""job_name\s*=\s*['"]([^'"]+)['"]""")
DEFINE_RE = re.compile(r"""define_asset_job\s*\(\s*name\s*=\s*['"]([^'"]+)['"]""")


def extract_code_lines(text: str) -> str:
    """Return text with all full-line comments stripped (no multiline
    docstring handling - we trust that Python source has docstrings
    at the top of the file only, and the regex below skips them by
    checking line position).

    For accuracy we strip leading docstrings via a simple state machine.
    """
    out_lines = []
    in_docstring = False
    for line in text.splitlines():
        # Skip full-line comments
        if line.lstrip().startswith("#"):
            continue
        # Track triple-quoted docstring state
        if not in_docstring:
            if '"""' in line:
                # Crude handling: if odd number of  on the line,
                # toggle state. Lines with exactly one triple-quote
                # mark the start of a docstring.
                count = line.count('"""')
                if count == 1:
                    in_docstring = True
                    # Output the part of the line AFTER the opening triple-quote
                    parts = line.split('"""', 1)
                    after = parts[1] if len(parts) > 1 else ""
                    if after.strip():
                        out_lines.append(after)
                    continue
                elif count >= 2:
                    # Both open and close on same line - skip the whole line
                    # if it's only docstring, else keep what's outside
                    parts = line.split('"""')
                    outside = parts[0] + (parts[2] if len(parts) > 2 else "")
                    if outside.strip():
                        out_lines.append(outside)
                    continue
                else:
                    out_lines.append(line)
            else:
                out_lines.append(line)
        else:
            # Inside a docstring - look for closing triple-quote
            if '"""' in line:
                in_docstring = False
                # Output the part BEFORE the closing triple-quote on
                # the same line, if any
                parts = line.split('"""', 1)
                if parts[0].strip():
                    out_lines.append(parts[0])
                continue
            # Otherwise skip this docstring line entirely
    return "\n".join(out_lines)


def scan_sensor_files() -> tuple[set[str], set[str]]:
    """Scan orchestration/sensors/*.py for both sensor job_names and
    define_asset_job(name=...) definitions. Returns (sensor_jobs, defined_jobs).
    """
    sensor_jobs: set[str] = set()
    defined_jobs: set[str] = set()

    for py_file in SENSORS_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        raw_text = py_file.read_text(encoding="utf-8")
        code_text = extract_code_lines(raw_text)

        for match in JOB_NAME_RE.finditer(code_text):
            sensor_jobs.add(match.group(1))
        for match in DEFINE_RE.finditer(code_text):
            defined_jobs.add(match.group(1))

    return sensor_jobs, defined_jobs


def main() -> int:
    sensor_jobs, defined_jobs = scan_sensor_files()

    missing = sensor_jobs - defined_jobs
    unused = defined_jobs - sensor_jobs

    print(f"Found {len(sensor_jobs)} sensor job_names: {sorted(sensor_jobs)}")
    print(f"Found {len(defined_jobs)} defined jobs:     {sorted(defined_jobs)}")

    if missing:
        print(
            f"\nFAIL: {len(missing)} sensor job_name(s) have no matching define_asset_job:",
            file=sys.stderr,
        )
        for name in sorted(missing):
            print(f"  - {name}", file=sys.stderr)
        return 1

    if unused:
        print(
            f"\nWARN: {len(unused)} defined job(s) are not referenced by any @sensor:",
        )
        for name in sorted(unused):
            print(f"  - {name}")

    print("\nOK: all sensor job_names have matching define_asset_job instances.")
    return 0


if __name__ == "__main__":
    sys.exit(main())