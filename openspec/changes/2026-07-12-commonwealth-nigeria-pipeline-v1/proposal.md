# 2026-07-12-commonwealth-nigeria-pipeline-v1

## Why

The
[`2026-07-11-commonwealth-pipeline-v1`](../2026-07-11-commonwealth-pipeline-v1/)
change ships 5 pilot Commonwealth nations (AUS / CAN / NZL / IND /
ZAF). The user explicitly asked to **add Nigeria** to the
Commonwealth pipeline ("add nigeria").

Nigeria is a federation of **36 states + 1 Federal Capital Territory
(FCT, Abuja) = 37 sub-units**. The federal government + most state
ministries publish substantial education / law / medicine /
statistics / government data, but many state-government sites 403
or time-out (live probe results: only Lagos / Kano / Oyo return 200,
the rest need Firecrawl `stealth` or Wayback Machine fallback).

This change ships:

- **Federal tier** — 10 federal DLT sources (Ministry of Education,
  NUC, JAMB, NABTEB, NBC, NASS, FMHDS, NCDC, NPHCDA, Nigeria
  Customs).
- **State tier** — 185 state DLT sources (37 states × 5 domains).
  Per-state language partitioning (EN + the state's majority
  language + Pidgin for the federal tier).
- **Nigerian Legal Information Institute (`nigerialii.org`)** — the
  replacement for the now-offline `nigeria-law.org`.
- **BAML cluster** — 2 BAML files (federal + state).
- **CocoIndex v1 App + L3 defs**.
- **MotherDuck Dive + daily Flight**.

Blocked by the same Phase 0 contract + the Phase 1 endpoint
recovery change (the `nigeria-law.org` → `nigerialii.org` switch
is a Phase 1-style URL fix; many state sites need the Wayback
fallback).

## What changes

### 1. Federal tier (10 DLT sources)

```text
dlt/commonwealth/nga/education/federal_ministry_of_education.py
dlt/commonwealth/nga/education/nuc.py        # National Universities Commission
dlt/commonwealth/nga/education/jamb.py       # Joint Admissions & Matriculation Board
dlt/commonwealth/nga/education/nabteb.py     # NABTEB (technical exams)
dlt/commonwealth/nga/education/nbc.py        # National Business & Technical Examinations Board
dlt/commonwealth/nga/medicine/fmhds.py       # Federal Ministry of Health
dlt/commonwealth/nga/medicine/ncdc.py        # Nigeria Centre for Disease Control
dlt/commonwealth/nga/medicine/nphcda.py      # National Primary Health Care Dev Agency
dlt/commonwealth/nga/law/nass.py             # National Assembly + nigerialii.org
dlt/commonwealth/nga/government/customs.py   # Nigeria Customs Service
```

### 2. State tier (37 sub-units × 5 domains = 185 DLT sources)

Per-state DLT scaffold under
`dlt/commonwealth/nga/states/<state_slug>/<domain>/<ministry>.py`:

- 37 sub-units: Abia, Adamawa, Akwa Ibom, Anambra, Bauchi, Bayelsa,
  Benue, Borno, Cross River, Delta, Ebonyi, Edo, Ekiti, Enugu,
  FCT (Abuja), Gombe, Imo, Jigawa, Kaduna, Kano, Katsina, Kebbi,
  Kogi, Kwara, Lagos, Nasarawa, Niger, Ogun, Ondo, Osun, Oyo, Plateau,
  Rivers, Sokoto, Taraba, Yobe, Zamfara.
- Per-state language: `("en", <state_majority_language>)` where the
  majority language is one of `ha`, `yo`, `ig`, `pcm` (Pidgin) based
  on the state's primary ethnic group.

### 3. BAML extensions

- `baml/commonwealth/nga/federal.baml` —
  `ExtractNigerianFederalCurriculumSpec(federal_institution, language, text)`
- `baml/commonwealth/nga/state.baml` —
  `ExtractNigerianStateCurriculumSpec(state_code, language, text)`

### 4. CocoIndex v1 App

`dlt/commonwealth/nga/` CocoIndex v1 App (`nigeria_education_embedding.py`)
that embeds every Nigerian federal + state education row into a
shared LanceDB table partitioned by `state_code + language`.

### 5. MotherDuck Dive + Flight

- `nigeria_state_curriculum_matrix` — 37-state × 5-language matrix
- `nigeria_daily_sync_flight` — daily BAML backfill

### 6. Dagster defs

- 10 federal Dagster L1 defs
- 37 state Dagster L1 defs (1 per state)
- 1 L3 defs for the CocoIndex v1 App

## Dependencies

```yaml
Blocked by:
  - 2026-07-11-global-region-source-contract-v1
  - 2026-07-12-british-isles-endpoint-recovery-v1
Blocked by (soft): 2026-07-11-commonwealth-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-12-commonwealth-nigeria-pipeline-v1 --strict` passes
- 195 DLT sources (10 federal + 185 state) exist + AST-parse
- 2 BAML files exist + AST-parse
- 1 CocoIndex v1 App conforms to R1–R4
- 1 MotherDuck Dive + 1 daily Flight exist + YAML-parse
- 47+ Dagster L1 defs.yaml files YAML-parse
- `dg check yaml` passes
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`commonwealth-pipeline`](../commonwealth-pipeline/spec.md) —
  the parent pipeline
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the per-jurisdiction partition pattern reference
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `docs/agents/british_isles_endpoint_health_audit.md` —
  the Phase 1 endpoint snapshot
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
