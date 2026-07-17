# 2026-07-25-flatten-notebooks-v1

## Why

The user explicitly requested **flatten and merge the notebook sprawl** —
no subdirectories, just bigger more grouped marimo notebooks at the top
level. Current state:

- 177 marimo notebooks sprawl across 20 subdirectories (~49,260 LOC)
- 6 per-subject LC notebooks at `notebooks/leaving_cert/<subject>.py`
  (chem/cs/eng/ga/geo/math, 2,331 LOC) are 90% identical scaffolding
- 7 `leaving_cert/*.py` files in total (including `06_en_vs_ga_comparison.py`)
  could be a single grouped marimo with 7 tabs

The audit identified that the existing pattern
(`marimo_dashboards/06_per_subject_analytics.py` parameterised by subject)
is the canonical template for the merge. The new grouped panel adopts
`mo.ui.tabs` for the 6 subjects + EN/GA comparison.

## What changes

### 1. Merge 7 LC notebooks → 1 grouped marimo

DELETE the 7 files:
- `notebooks/leaving_cert/chemistry.py` (450 LOC)
- `notebooks/leaving_cert/computer_science.py` (387 LOC)
- `notebooks/leaving_cert/english.py` (351 LOC)
- `notebooks/leaving_cert/gaeilge.py` (396 LOC)
- `notebooks/leaving_cert/geography.py` (396 LOC)
- `notebooks/leaving_cert/mathematics.py` (351 LOC)
- `notebooks/leaving_cert/06_en_vs_ga_comparison.py` (326 LOC)

CREATE `notebooks/40_leaving_cert_subject_panel.py` (~650 LOC) with 7 marimo `mo.ui.tabs`:
1. Mathematics
2. Chemistry
3. Geography
4. Gaeilge (bilingual EN/GA)
5. English (bilingual EN/GA)
6. Computer Science
7. EN/GA Comparison

### 2. Flatten all other notebooks to top-level

Per the audit, the canonical layout:

```
notebooks/
├── __init__.py
├── cli.py
├── nb_utils.py
├── ie_law_explorer.py             # (already flat)
├── README.md                      # rewritten
├── LEGACY_ALIASES.md              # updated
├── 00_overview_setup.py           # DELETE (merged into 02)
├── 02_education_overview.py       # NEW (merges 01 + BIEP corpus + BIEP v2 overview)
├── 03_irish_primary_jc.py         # NEW (merges aistear + primary + JC stages)
├── 04_irish_senior_cycle.py       # NEW (merges senior_cycle + 6 LC subjects via 40)
├── 05_england_aqa_ocr_edexcel.py  # NEW (merges England + cross_domain + QQI ladder)
├── 06_celtic_languages.py         # NEW (merges 7 celtic_language panels)
├── 07_junior_cycle_ireland.py     # = BIEP v2 01_junior_cycle_explorer.py
├── 08_ocr_ensemble_audit.py       # = BIEP v2 03_ocr_ensemble_audit.py
├── 09_leabharlann_corpus.py       # NEW
├── 10_biep_pipeline_lakehouse.py  # NEW
├── 11_irish_law.py                # NEW
├── 12_corpus_overview.py          # NEW
├── 13_official_media.py           # NEW
├── 14_dev_env_tools.py            # NEW
├── 15_observability.py            # NEW
├── 40_leaving_cert_subject_panel.py  # the 7-tab grouped LC panel
├── _shared/                       # KEEP (from Change 1)
└── legacy/                        # KEEP (for 5 cleanup in Change 5)
```

168 notebooks get renamed + flattened to top-level.

### 3. Update docs

- UPDATE `notebooks/README.md` — rewrite the area table for the flat layout
- UPDATE `notebooks/LEGACY_ALIASES.md` — add the v8-flatten entry with
  all 168 old-path → new-path aliases

## Dependencies

```yaml
Blocked by: 2026-07-25-nb-utils-ibis-first-v1
            2026-07-25-cocoindex-per-subject-dedup-v1
            2026-07-25-baml-archive-orphaned-and-superseded-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-25-flatten-notebooks-v1 --strict` passes
- 7 LC notebooks merged into 1 grouped `40_leaving_cert_subject_panel.py`
- 168 notebooks renamed + flattened
- `notebooks/` has only `_shared/` and `legacy/` as subdirectories
  (verified by `find notebooks -mindepth 1 -maxdepth 1 -type d`)
- `notebooks/40_leaving_cert_subject_panel.py` renders all 7 tabs
- Every renamed notebook preserves its `## KCG patterns used` docstring
- Every renamed notebook uses `nb_utils.connect_md()` (not raw `duckdb.connect`)
- `LEGACY_ALIASES.md` documents the 168 old-path → new-path aliases
- `mise run lint:skills` — must remain 53/53
- Push target: `origin/main`

## Cross-references

- [`oideachais-marimo-dashboards`](../../specs/oideachais-marimo-dashboards/spec.md) —
  the parent marimo dashboard spec that gets a new "notebooks/ is flat" requirement
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1 LC spec (the 6 subjects now live in the grouped panel)
- `openspec/changes/2026-07-25-nb-utils-ibis-first-v1/` — the prerequisite
  `nb_utils.connect_md()` helper
- `openspec/changes/2026-07-25-purge-stale-notebooks-and-archive-v1/` —
  the next change that deletes the 23 stale `03_leaving_cert/` files
- `.agents/skills/marimo/SKILL.md` — the marimo conventions
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract