# 2026-07-13-eu-nations-full-depth-expansion-v1

## Why

The
[`2026-07-11-european-nations-ukraine-pipeline-v1`](../2026-07-11-european-nations-ukraine-pipeline-v1/)
change ships a thin scaffold for 6 EU pilot countries (UKR / FRA / DEU /
POL / ESP / ITA) — 1 DLT source per domain = 5 sources × 6 countries.
That's not Ireland-level depth.

The British Isles parity change
([`2026-07-12-british-isles-parity-pipeline-v1`](../2026-07-12-british-isles-parity-pipeline-v1/))
established the Ireland-level template:

- 6 per-subject DLT sources per country (mathematics / chemistry /
  biology / physics / language / computing) in
  `dlt/<region>/<nation>/education/subjects/`
- 3 BAML extraction files per country (education / law / medicine)
  with country-specific extraction functions
- 1 CocoIndex v1 App per nation (per the R1–R4 contract)
- 1 L3 Dagster defs + 6 L1 Dagster defs
- 1 MotherDuck Dive

This change brings the 6 EU pilot countries + the remaining 21 EU
member states + 3 EEA/EFTA members + 9 EU candidate states to that
Ireland-level depth, with a focus on each country's official
language(s) and the national education-system data surface.

## Pilot upgrade (6 countries)

For each of UKR, FRA, DEU, POL, ESP, ITA: add 6 per-subject DLT
sources under `dlt/european_nations/<iso3>/education/subjects/`
(matching the existing BIEP parity pattern). Update the
`european_nations_<iso3>_education_embedding.py` CocoIndex v1 App
to consume the per-subject rows.

## New countries (24)

```text
AUT (Austria)        — de
BEL (Belgium)        — nl, fr, de
BGR (Bulgaria)       — bg
HRV (Croatia)        — hr
CYP (Cyprus)         — el, tr
CZE (Czechia)        — cs
DNK (Denmark)        — da
EST (Estonia)        — et
FIN (Finland)        — fi, sv
GRC (Greece)          — el
HUN (Hungary)        — hu
LIE (Liechtenstein)  — de
LTU (Lithuania)      — lt
LUX (Luxembourg)     — lb, fr, de
LVA (Latvia)         — lv
MLT (Malta)          — mt, en
NLD (Netherlands)     — nl
PRT (Portugal)      — pt
ROU (Romania)       — ro
SVK (Slovakia)      — sk
SVN (Slovenia)      — sl
SWE (Sweden)        — sv
NOR (Norway)        — nb, nn, se
CHE (Switzerland)   — de, fr, it, rm
ISL (Iceland)       — is
```

Plus 9 EU candidate / accession / neighbour states:

```text
TUR (Turkey)         — tr
SRB (Serbia)         — sr
MNE (Montenegro)     — sr
BIH (Bosnia)         — bs, hr, sr
ALB (Albania)        — sq
MKD (North Macedonia)— mk
XKX (Kosovo)         — sq, sr
MDA (Moldova)        — ro
GEO (Georgia)        — ka
```

## Per-country deliverables

For each of the 30 countries (6 pilot upgrade + 24 new):

1. **6 per-subject DLT sources** at
   `dlt/european_nations/<iso3>/education/subjects/<subject>.py`:
   - mathematics, chemistry, biology, physics, language,
     computing_science
   - Honours `USE_LOCAL_SCRAPES=true`
   - Per-country language partition (the country's official
     language(s) + EN where bilingual)
2. **Per-domain DLT source** (law / medicine / statistics /
   government) at `dlt/european_nations/<iso3>/<domain>/<source>.py`
3. **3 BAML files** at
   `baml/european_nations/<iso3>/{education,law,medicine}.baml` with
   per-country extraction functions
4. **1 CocoIndex v1 App** at
   `cocoindex/european_nations_<iso3>_education_embedding.py`
5. **6 L1 + 1 L3 Dagster defs**
6. **1 cache fixture per subject** (6 per country) under
   `stedding/ingest_queue/european_nations/<iso3>/education/subjects/<subject>/<lang>/`

## Dependencies

```yaml
Blocked by: 2026-07-11-global-region-source-contract-v1
Blocked by (soft):
  - 2026-07-11-european-nations-ukraine-pipeline-v1
  - 2026-07-12-british-isles-endpoint-recovery-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-13-eu-nations-full-depth-expansion-v1 --strict` passes
- 30 countries × 6 per-subject DLT = 180 per-subject DLT sources
  AST-parse cleanly
- 30 countries × 5 baseline DLT (law/medicine/statistics/government +
  the 1 per-subject-root) = 150 baseline DLT sources AST-parse
- 30 countries × 3 BAML = 90 BAML files AST-parse
- 30 countries × 1 CocoIndex v1 App = 30 CocoIndex v1 Apps conform to
  R1–R4
- 30 countries × (6 L1 + 1 L3) = 210 Dagster defs.yaml files
  YAML-parse
- 30 countries × 6 cache fixtures = 180 JSON fixtures
- `dg check yaml` passes
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the existing EU nations scaffold (Phase 2)
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the Ireland-level template (Phase 2 BIEP parity)
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
