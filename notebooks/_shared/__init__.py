"""Cross-notebook shared helpers for the Cianfhoghlaim platform.

This is the canonical ibis-first helper package per the 2026-07-25
refactor batch. Every notebook that needs a lakehouse connection
SHALL import from here rather than calling raw `ibis.duckdb.connect(uri)`.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — `ibis.duckdb.connect`
  for analytics + `ibis.lancedb.connect` for vector (NO raw `duckdb.connect`).
- marimo (per `.agents/skills/marimo/SKILL.md`) — the helper is
  marimo-agnostic (pure function) so it works in both marimo and CLI modes.

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
"""