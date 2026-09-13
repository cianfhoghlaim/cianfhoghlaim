# Change: Tier 3 grouped dashboards consolidation (marimo v14)

## Why

The 36+ notebooks in Tier 3 currently fragment the cianfhoghlaim
notebook surface into per-domain sub-notebooks:

- **5 meaisin ops dashboards** (`60_meaisin_ireland_ops.py` +
  `61_meaisin_england_ops.py` + `62_meaisin_extraction_progress.py`
  + `63_meaisin_eval_dashboard.py` + `64_meaisin_bilingual_curriculum.py`)
- **7 Celtic languages dashboards** (`06_celtic_languages_01..07_*.py`
  + `06_celtic_languages__shared.py`)
- **8 corpus overview dashboards** (`12_corpus_overview_01..04_*.py`
  × 2 domains + `12_corpus_overview__shared.py`)
- **8 speedrun MMO dashboards** (`16_speedrun_mmo_00..08_*.py` +
  `16_speedrun_mmo__shared.py`)
- **8 academic history dashboards** (`17_academic_history_01..08_*.py`
  + `17_academic_history__common.py`)
- **6 Irish law dashboards** (`11_irish_law_01..06_*.py`)

This fragmentation makes it hard for operators to find the right
notebook, hard to keep the per-domain UI consistent, and hard to apply
the marimo v14 features (tabs, LLM chat, dual-mode CLI, RAGAS gauge)
across the entire domain.

Following the same pattern as the BIEP v3 jurisdiction dashboards
(notebooks 19, 20, 26, 27) which already use the canonical 8-cell
operator console + `mo.ui.tabs`, this change consolidates the 36+
Tier 3 sub-notebooks into 6 grouped dashboards (one per domain).

The consolidation pattern:

1. The sub-notebook's content (its cells + its data model) becomes
   the tab content of the grouped dashboard.
2. The grouped dashboard uses `mo.ui.tabs` to surface all the tabs.
3. Each grouped dashboard keeps the dual-mode (marimo + CLI)
   pattern per https://docs.marimo.io/guides/scripts/.
4. Each grouped dashboard uses `setup_biep_registry_header()` (R1)
   + `build_biep_v3_dashboard()` (R2) per the helper modules from
   the `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`
   change.

## What changes

- **6 new grouped marimo dashboards**:
  - `notebooks/meaisin_ops_console.py` — consolidates
    `60_meaisin_ireland_ops.py` + `61_meaisin_england_ops.py` +
    `62_meaisin_extraction_progress.py` + `63_meaisin_eval_dashboard.py`
    + `64_meaisin_bilingual_curriculum.py` (5 sub-notebooks → 6 tabs:
    Overview / Ireland / England / Extraction Progress / Eval /
    Bilingual Coverage).
  - `notebooks/celtic_languages.py` — consolidates
    `06_celtic_languages_01..07_*.py` + `06_celtic_languages__shared.py`
    (7 sub-notebooks → 7 tabs: Gaois / Dúchas / Heritage Sites /
    Canúint / UD Treebank / Local Documents / Celtic Curriculum).
  - `notebooks/corpus_overview.py` — consolidates
    `12_corpus_overview_01..04_*.py` × 2 domains +
    `12_corpus_overview__shared.py` (8 sub-notebooks → 4 tabs:
    BIEP Corpus / Leabharlann Corpus / Cognee Knowledge Graph /
    Embedding Coverage).
  - `notebooks/speedrun_mmo.py` — consolidates
    `16_speedrun_mmo_00..08_*.py` + `16_speedrun_mmo__shared.py`
    (8 sub-notebooks → 5 tabs: Celtic NFT / Mission Control /
    Language Staking / Token Shop / Exam Predictions).
  - `notebooks/academic_history.py` — consolidates
    `17_academic_history_01..08_*.py` + `17_academic_history__common.py`
    (8 sub-notebooks → 6 tabs: UoG Maths / Module Map / Statistics /
    Numerical Analysis / Formulas / Worked Solutions).
  - `notebooks/irish_law.py` — consolidates `11_irish_law_01..06_*.py`
    (6 sub-notebooks → 6 tabs: Personal Injury / Courts Index / WRC
    Decisions / Citizens Info / Gov.ie Law / Unified Search).
- **40+ old sub-notebooks deprecated** — moved to
  `notebooks/legacy/v7_consolidation/` with a `DEPRECATED.md`
  redirect note pointing to the new grouped dashboard.
- **6 new area_shim modules**:
  - `notebooks/_shared/area_shims/meaisin.py`
  - `notebooks/_shared/area_shims/celtic_languages.py`
  - `notebooks/_shared/area_shims/corpus_overview.py`
  - `notebooks/_shared/area_shims/speedrun_mmo.py`
  - `notebooks/_shared/area_shims/academic_history.py`
  - `notebooks/_shared/area_shims/irish_law.py`
- **6 new `mise.toml` tasks** — `biep:v3:marimo:<domain>:dev` per
  grouped dashboard.
- **1 ADDED Requirement** to
  `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`
  (consolidation pattern for the per-domain grouped dashboards).

## Out of scope

- The 17 Tier 1+2 BIEP v3 dashboards (already in
  `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`).
- The 10 sync layer dashboards (tracked by the follow-up change
  `2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1`).
- The 4 Tier 4 legacy notebooks (`notebooks/legacy/*` +
  `ie_law_explorer.py`) — only R1 applied (header hoist); no other
  refactor.
- Cross-repo changes (`leabharlann/` is a read-only consumer).

## Dependencies

```markdown
## Dependencies

`Blocked by (soft): 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`
(the 3 helper modules — `marimo_patterns.py`,
`area_shims/biiep_v3_dashboard.py`, `ragas_gauge.py` — are required
inputs for the 6 grouped dashboards).

`Affected repos: cianfhoghlaim`
```

## Impact

- **Affected specs**: `cianfhoghlaim-marimo-dashboards` (1 ADDED
  Requirement).
- **Affected code/config**:
  - 6 new grouped dashboards (~2,400 LOC total)
  - 6 new area_shim modules (~480 LOC total)
  - 40+ old sub-notebooks moved to `notebooks/legacy/v7_consolidation/`
  - `mise.toml` adds 6 `biep:v3:marimo:<domain>:dev` tasks
- **LOC saved**: ~2,000+ LOC (consolidation of the 40+ sub-notebooks).
- **No secret values written to disk**: all `infisical://dev-baile/...`
  refs hydrated by mise + Locket.

## Cross-references

- `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md` — the
  capability this change extends (1 ADDED Requirement)
- `openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/`
  — the 3 helper modules this change depends on
- `openspec/specs/agent-platform-cluster/spec.md` — the meaisin
  agent fleet (the `meaisin_ops_console.py` dashboard surfaces this)
- `openspec/specs/celtic-language-pipeline/spec.md` — the Celtic
  language DLT sources (the `celtic_languages.py` dashboard
  surfaces this)
- `openspec/specs/cianfhoghlaim-leabharlann/spec.md` — the Leabharlann
  corpus (the `corpus_overview.py` dashboard surfaces this)
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the
  Túatha educational MMO (the `speedrun_mmo.py` dashboard surfaces
  this)
- `notebooks/_shared/area_shims/leaving_cert.py` — the BIEP v3
  overview helper (the area_shim modules mirror this pattern)
- `.agents/skills/marimo/SKILL.md` — the marimo skill (the
  consolidation pattern follows P1-P6)