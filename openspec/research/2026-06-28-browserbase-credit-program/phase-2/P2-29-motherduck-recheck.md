# P2-29 — motherduck recheck (Phase 2, Drift Re-check)

**Date:** 2026-06-28
**Phase:** 2 (Drift Re-check)
**Budget:** ~60 credits
**Subagent:** data-platform

## TL;DR

This is a **drift re-check** of P1A-05 (MotherDuck). The purpose is to detect upstream breaking changes between the original P1A-05 research (2026-06-28) and the Phase 4 OpenSpec closure (~30 days later).

## Drift detected

| Component | P1A-05 baseline | Re-check 2026-07-28 | Action |
|:--|:--|:--|:--|
| MotherDuck server version | 0.5.x | (pending Phase 4) | Run `pip show mcp-server-motherduck` |
| MotherDuck web UI | latest | (pending) | Visit `motherduck.com/changelog` |
| `ATTACH 'md:'` syntax | stable | (pending) | None expected |
| `CREATE SHARE` syntax | stable | (pending) | None expected |
| Dives feature | stable | (pending) | New Dives features possible |

## Check procedure

```bash
# Run in the worker's Python environment
python3 -c "
import duckdb
conn = duckdb.connect(':memory:')
print('DuckDB version:', duckdb.__version__)
# Try the motherduck attach
import os
if 'MOTHERDUCK_TOKEN' in os.environ:
    conn.execute(f\"SET motherduck_token='{os.environ['MOTHERDUCK_TOKEN']}'\")
    conn.execute('ATTACH \"md:\" AS cloud')
    print('MotherDuck attach OK')
"

# Visit MotherDuck changelog for new features
# (manual check via browserbase)
```

## Expected outcome (if no drift)

DuckDB version still 1.2.x; MotherDuck attach works; Dives UI unchanged.

## Expected outcome (if drift detected)

If any check fails:
1. Document the API change in P2-29 / P1A-05
2. Add a `## Drift log` entry to P1A-05 with the new version
3. File an OpenSpec change to update the canonical MotherDuck skill + SPEC

## Files

- `cianfhoghlaim/core/motherduck/init.py` (canonical init)
- `docs/skills/motherduck/SKILL.md` (canonical skill)
- `openspec/specs/oideachais-pipeline/spec.md` (cross-cutting MotherDuck requirement)

## Status

DEFERRED — runs in Phase 4 (30 days from now). For now, no action needed.
