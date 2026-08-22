#!/usr/bin/env bash
# scripts/tool-versions-report.sh
#
# Per the 2026-08-23-dev-tooling-version-pinning-v1 change: emit a
# structured table of all installed mise tools + their resolved
# versions. Active versions are marked with *.
set -uo pipefail

# Capture mise output, strip warnings, parse JSON
RAW=$(mise ls --installed --json 2>&1 | grep -v "^mise WARN" || true)

# Parse with python (use a heredoc to avoid quoting hell)
python3 <<PYEOF
import json, sys
raw = """$RAW"""
data = json.loads(raw)
print(f"{len(data)} toolchain entries installed:")
print()
rows = []
seen = set()
for name, versions in data.items():
    for v in versions:
        if v.get("active"):
            rows.append((name, v["version"], "*"))
            seen.add(name)
for name, versions in data.items():
    if name in seen: continue
    for v in versions:
        rows.append((name, v["version"], " "))
        seen.add(name)
        break
for n, v, marker in sorted(rows):
    print(f"  {n:18s} {v:20s} {marker}")
print()
print("(* = active)")
PYEOF
