# Change: pipeline-ciancheiltis-celtic-bilingual — Celtic bilingual umbrella

> **Status:** umbrella change that subsumes `2026-09-06-ciancheiltis-v1`.
> This umbrella provides the cross-batch contract + the consolidated
> task list for the 6-phase staging rollout.

## Why

Existing `dlt_sources/british_isles/**` DLT sources for Celtic-language
jurisdictions were authored against the pre-v7 Firecrawl tool surface
and ship with almost no real bilingual content:

- `en-cy` (Welsh): 0 rows
- `en-gd` (Scottish Gaelic): 1 EN sample
- `en-ga NI` (Irish in Northern Ireland): 1 EN sample
- `en-gv` (Manx): 0 rows
- `en-ga EU` (Irish at EU institutions): 18 placeholders

The CIANCHEILTIS umbrella extends materialised coverage to the 4
other Celtic pairs (Welsh + Scottish Gaelic + Irish in NI + Manx)
plus the EU-level `en-ga` dimension and re-platforms onto the v1
Firecrawl MCP tool surface (firecrawl_agent, firecrawl_monitor_*,
firecrawl_interact, firecrawl_parse, firecrawl_map).

Without this umbrella, every Celtic-language jurisdiction needs its
own bespoke DLT source. With it, every Celtic jurisdiction reuses the
same 6-phase staging template + the same canonical file layout.

## What Changes

- Adds the cross-batch CIANCHEILTIS contract: the 6-phase staging
  (sources → classification → extraction → embed → surface → integration)
  applies uniformly to all 5 Celtic pairs.
- Consolidates all tasks from `2026-09-06-ciancheiltis-v1` (0/56) into
  one tasks.md below.
- Records the canonical file layout `dlt_sources/ciancheiltis/` (sibling
  to `dlt_sources/british_isles/`) in this change's `design.md`.

## Capabilities

### New Capabilities

- `ciancheiltis` — the umbrella spec for Celtic bilingual coverage
  beyond the Republic-of-Ireland `en-ga` pair. Captures the 13
  Requirements: 6-phase staging, 10-theme taxonomy, canonical file
  layout, content-based language detection, opaque-URL scanner,
  gov.wales WAF bypass, CLARIN-UK integration, BAML extraction,
  CocoIndex R1–R4, Dagster 5-layer, MotherDuck Dive + Flight,
  cross-pipeline integration, DO NOT section.

## Impact

- **Affected changes**: 1 bundled + this umbrella
- **Affected repos**: cianfhoghlaim + ciancheiltis
- **Affected code** (once executed):
  - NEW `dlt_sources/ciancheiltis/` canonical file layout
  - 5 NEW DLT sources per jurisdiction (Wales + Scotland + NI + IoM +
    EU-IE)
  - 5 NEW CocoIndex flows (one per Celtic pair)
  - NEW BAML extraction for 10 themes across 6 jurisdictions
  - NEW MotherDuck Dive + Flight for the Celtic bilingual surface

## Out of scope (follow-up changes)

- `ciancheiltis-bilingual-corpus-extension-v1` — extend the existing
  `leabharlann/` corpus with the 5 Celtic pairs (after the initial
  scaffolding is in place)
- `ciancheiltis-marimo-dashboards-v1` — surface the Celtic bilingual
  data via marimo dashboards (analogous to the BIEP dashboards)
- `ciancheiltis-copa-cogadh-v1` — surface via the A2UI surface
  (analogous to the BIEP A2UI surface)

## Dependencies

`Blocked by:` none (this is the foundational Celtic bilingual umbrella).
`Affected repos:` cianfhoghlaim + ciancheiltis.

## Cross-repo sync

This change ships the cianfhoghlaim-side scaffolding + the
ciancheiltis-side adoption. The sister-shared contract (per the
`pipeline-sister-repo-handoff` umbrella) governs the handoff.

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianfhoghlaim
openspec validate pipeline-ciancheiltis-celtic-bilingual --strict
# Expected: pass
```
