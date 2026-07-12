# 2026-07-15-eu-pilot-upgrade-v1

## Why

The
[`2026-07-11-european-nations-ukraine-pipeline-v1`](../2026-07-11-european-nations-ukraine-pipeline-v1/)
change ships a thin baseline scaffold for 6 EU pilot countries
(UKR / FRA / DEU / POL / ESP / ITA) — 1 DLT source per domain = 5
sources × 6 countries. That is NOT the BIEP per-subject depth.

The
[`2026-07-12-british-isles-parity-pipeline-v1`](../2026-07-12-british-isles-parity-pipeline-v1/)
change established the BIEP per-subject template (6 subjects:
mathematics / chemistry / biology / physics / language /
computing_science, with bilingual language partition). Scotland
already shipped 6 subjects; Wales / England / Northern Ireland only
shipped 4 (missing physics + biology).

This change brings the 6 EU pilot countries (including Ukraine — the
user's explicit priority) AND the 3 BI nations (Wales / England /
Northern Ireland) up to full BIEP per-subject depth.

## What changes

### 1. Ukraine (UKR) full depth upgrade

Ukraine gets the per-subject depth with **7 subjects** (the BIEP 6
+ a 7th Ukrainian-language subject for the ZNO national curriculum):

```text
dlt/european_nations/ukr/education/subjects/
├── mathematics.py
├── chemistry.py
├── biology.py
├── physics.py
├── language.py         # English as a foreign language
├── computing_science.py
└── ukrainian_language.py  # NEW: native Ukrainian language + literature
```

Each subject DLT source honours `USE_LOCAL_SCRAPES=true` with the
canonical Ukraine partition (default `uk`, secondary `en`).

### 2. The other 5 EU pilot countries (FRA / DEU / POL / ESP / ITA)

Each gets the standard BIEP 6 subjects:

```text
dlt/european_nations/<iso3>/education/subjects/
├── mathematics.py
├── chemistry.py
├── biology.py
├── physics.py
├── language.py
└── computing_science.py
```

### 3. British Isles — Wales / England / Northern Ireland fill-in

Each gets the 2 missing subjects (physics + biology) added to its
existing `education/subjects/` directory.

### 4. Dagster L1 + L3 defs

Every country gets:
- 7 (Ukraine) or 6 (other EU pilots + BI) per-subject L1 defs at
  `orchestration/defs/1_ingestion/european_nations/<iso3>/education/subjects/<subject>/defs.yaml`
- 1 L3 def at
  `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_<iso3>_education/defs.yaml`

The 3 BI nations get 2 additional per-subject L1 defs each.

### 5. BAML extraction schema updates

Each country's 3 BAML files (education / law / medicine) gain
per-subject extraction functions matching the BIEP pattern. The
Ukraine education BAML additionally gets a per-subject language
discriminator (Ukrainian-language vs other subjects).

### 6. CocoIndex v1 Apps

Each country gets a per-subject CocoIndex v1 App that partitions on
`(subject, language)` and embeds with `BAAI/bge-m3` 1024-d.

### 7. Cache fixtures

Each per-subject DLT source gets a cache fixture under
`stedding/ingest_queue/european_nations/<iso3>/education/subjects/<subject>/<lang>/sample.json`.

## Dependencies

```yaml
Blocked by:
  - 2026-07-11-global-region-source-contract-v1
Blocked by (soft):
  - 2026-07-11-european-nations-ukraine-pipeline-v1
  - 2026-07-12-british-isles-parity-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-15-eu-pilot-upgrade-v1 --strict` passes
- Ukraine: 7 per-subject DLT + 6 BIEP per-subject + 7 Dagster L1 +
  1 L3 def + 1 CocoIndex v1 App + 7 cache fixtures = ~22 files
- 5 EU pilots: 6 per-subject DLT + 6 L1 defs + 1 L3 + 1 CocoIndex +
  6 cache fixtures = ~20 files × 5 = ~100 files
- 3 BI nations: 2 missing subjects × 3 nations = 6 per-subject
  files + 6 L1 defs + 6 cache fixtures = ~18 files
- All AST-parse + YAML-parse cleanly
- `dg check yaml` passes
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/pick-4-biep-v1`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the EU nations scaffold (parent of Ukraine)
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the BIEP parent spec (the per-subject template reference)
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
