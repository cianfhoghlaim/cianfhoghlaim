# Tasks: 2026-07-13-eu-nations-full-depth-expansion-v1

## 1. OpenSpec scaffolding (myself)

- [ ] 1.1 Create `openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/`
- [ ] 1.2 Create the proposal.md + tasks.md + spec deltas (this file)
- [ ] 1.3 `openspec validate 2026-07-13-eu-nations-full-depth-expansion-v1 --strict` passes

## 2. Subagent dispatch

Dispatch 3 parallel data-platform subagents:

### Subagent 1 (Group A — Western + Northern EU + EEA/EFTA)

For each of the 11 countries AUT, BEL, CHE, DNK, FIN, ISL, LIE,
LUX, NLD, NOR, SWE:
- 6 per-subject DLT sources
- 5 baseline DLT sources (1 per domain)
- 3 BAML files
- 1 CocoIndex v1 App + L3 def
- 6 L1 + 1 L3 Dagster defs
- 6 cache fixtures

### Subagent 2 (Group B — Central + Eastern EU + Iberia + Baltics)

For each of the 13 countries BGR, CYP, CZE, EST, GRC, HRV, HUN,
LTU, LVA, MLT, PRT, ROU, SVK, SVN:
- 6 per-subject DLT sources
- 5 baseline DLT sources
- 3 BAML files
- 1 CocoIndex v1 App + L3 def
- 6 L1 + 1 L3 Dagster defs
- 6 cache fixtures

### Subagent 3 (Group C — Balkans + Caucasus + Turkey + Moldova)

For each of the 9 countries ALB, BIH, GEO, MDA, MKD, MNE, SRB,
TUR, XKX:
- 6 per-subject DLT sources
- 5 baseline DLT sources
- 3 BAML files
- 1 CocoIndex v1 App + L3 def
- 6 L1 + 1 L3 Dagster defs
- 6 cache fixtures

### Subagent 0 (Pilot upgrade — 6 countries)

For each of the 6 pilot countries UKR, FRA, DEU, POL, ESP, ITA
(already scaffolded at the basic 5-DLT-per-domain level): add 6
per-subject DLT sources + update the existing CocoIndex v1 App to
consume the per-subject rows + 6 L1 + 1 L3 Dagster defs + 6 cache
fixtures. Do NOT replace the existing 5 baseline DLT sources.

## 3. Spec deltas

- [ ] 3.1 ADDED Requirements on `european-nations-ukraine-pipeline/spec.md`
  for the 30-country full-depth layer
- [ ] 3.2 MODIFIED delta on `cross-region-pipeline/spec.md` adding a
  cross-reference
- [ ] 3.3 MODIFIED delta on `cianfhoghlaim-pipeline/spec.md` adding a
  cross-reference

## 4. Validate

- [ ] 4.1 `openspec validate 2026-07-13-eu-nations-full-depth-expansion-v1 --strict` passes
- [ ] 4.2 All 180+ per-subject DLT sources AST-parse
- [ ] 4.3 All 90 BAML files AST-parse
- [ ] 4.4 All 210 Dagster defs.yaml files YAML-parse
- [ ] 4.5 `dg check yaml` passes
- [ ] 4.6 `mise run lint:skills` still passes (53/53)

## 5. Commit + push

- [ ] 5.1 Stage the 3 subagent deliverables + the openspec change
- [ ] 5.2 Single commit with message
  `feat(eu): full-depth expansion for 30 EU nations (6 pilot upgrade + 24 new) — per-subject DLT + BAML + CocoIndex + Dagster + Dive`
- [ ] 5.3 `git push origin main`
