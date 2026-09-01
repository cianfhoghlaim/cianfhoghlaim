# Change: Cianfhoghlaim-Nua Ireland LC Completion v1 — 8 NCCA-adjacent + Physics + aistear/primary embeddings

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Step 2** of the cianfhoghlaim-nua v6 era plan. Closes the
> Ireland LC gap by adding the 6 NCCA-adjacent subjects (accounting,
> business, french, history, art, music) + physics + applied_mathematics
> + the aistear + primary CocoIndex embeddings.

## Why

Ireland has 8 NCCA LC priority subjects (chemistry, mathematics,
geography, gaeilge, english, computer_science) with full BAML +
CocoIndex + Convex + Dagster coverage. The 6 NCCA-adjacent
subjects (accounting, business, french, history, art, music) +
physics + applied_mathematics had only PDFs but no BAML extraction
functions, no CocoIndex Apps, and no Convex tables.

Additionally, the aistear (early years, ages 0-6) and primary
(ages 5-12) stages only had notebook dashboards — no CocoIndex
embeddings of the ~70 + ~137 source PDFs.

This change ships the 8 BAML marking files + 16 Convex subject
tables + the 2 missing CocoIndex Apps to complete Ireland coverage.

## What was shipped

### §1 — Author the 8 NCCA-adjacent + physics BAML files (8 files)

- **§1.1** `baml_src/british_isles/ireland/education/marking/accounting_marking.baml`
  (AccountingQuestionType + AccountingCommonMistake +
  AccountingMarkingScheme + ExtractAccountingMarkingScheme)
- **§1.2** `baml_src/british_isles/ireland/education/marking/business_marking.baml`
- **§1.3** `baml_src/british_isles/ireland/education/marking/french_marking.baml`
- **§1.4** `baml_src/british_isles/ireland/education/marking/history_marking.baml`
- **§1.5** `baml_src/british_isles/ireland/education/marking/art_marking.baml`
- **§1.6** `baml_src/british_isles/ireland/education/marking/music_marking.baml`
- **§1.7** `baml_src/british_isles/ireland/education/marking/applied_mathematics_marking.baml`
- **§1.8** `baml_src/british_isles/ireland/education/marking/physics_marking.baml`

### §2 — Extend the CocoIndex LC factory to include 8 more subjects (1 file modified)

- **§2.1** `cocoindex_flows/biep_parity/ireland_lc_factory.py`:
  - Added 8 `LCSubjectConfig` entries (accounting + business + french
    + history + art + music + applied_mathematics + physics)
  - French uses `("fr", "ga")` for the French-medium + Irish-medium
    bilingual surface
  - The factory auto-generates 16 new Apps (8 subjects × 2 langs
    minus 1 for French which has both `fr` + `ga`)

### §3 — Create the 16 Convex subject tables (16 files)

- **§3.1** `web/apps/cianfhoghlaim-nua/convex/lc/{accounting,business,french,history,art,music,physics}.{ts,types.ts}`
  (lifted from `web/apps/_archive/oideachais-dashboard-pre-v6/convex/lc/`)
- **§3.2** `web/apps/cianfhoghlaim-nua/convex/lc/applied_mathematics.{ts,types.ts}`
  (created from mathematics template — was missing from the archive)
- **§3.3** `web/apps/cianfhoghlaim-nua/convex/lc/index.ts`
  (re-exports the 8 new subject tables)
- **§3.4** `web/apps/cianfhoghlaim-nua/convex/schema.ts`
  (defines the 8 new tables + the 7 existing tables; the default
  schema includes all 8 new subjects)

### §4 — Create the 2 missing CocoIndex early-years Apps (2 files)

- **§4.1** `cocoindex_flows/british_isles/ireland/education/aistear_embedding.py`
  (consumes ~70 Aistear PDFs from
  `stedding/site_scrape_samples/aistear/`)
- **§4.2** `cocoindex_flows/british_isles/ireland/education/primary_embedding.py`
  (consumes ~137 Primary PDFs from
  `stedding/site_scrape_samples/primary/`)
- **§4.3** Both flows write to LanceDB with bilingual EN/GA fields
  (always bilingual per operator direction)

### §5 — Regenerate baml_client (1 action)

- **§5.1** `uv run baml-cli generate --from baml_src` —
  regenerated `baml_client/` (14 files). The 8 new
  `Extract<Subject>MarkingScheme` functions are reachable from
  runtime.

### §6 — Spec delta to `british-isles-education-pipeline` (1 file)

- **§6.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/specs/british-isles-education-pipeline/spec.md`
  — adds 2 new Requirements:
    - "All 14 NCCA LC subjects MUST have a BAML marking scheme extractor"
    - "The aistear + primary stages MUST have CocoIndex embeddings"

## Impact

- **Audience:** every Irish secondary + primary student (the
  full 14-subject LC curriculum + the 2 missing early-years stages
  are now covered).
- **Scope:** 8 new BAML + 2 new CocoIndex + 16 new Convex + 1
  schema modification.
- **LOC delta:** +~250 (8 BAML × ~20 LOC + 2 CocoIndex × ~50 LOC
  + 16 Convex × ~5 LOC + schema ~30 LOC).
- **Risk:** LOW — additive; the existing 6 subjects are unaffected.
- **Reversibility:** full — `git revert` restores the 6-subject
  baseline.

## Dependencies

`Blocked by (hard):` none.

`Blocked by (soft):`

- `2026-09-01-baml-regeneration-blocker-v1/` (Step 0.5 — BAML
  regeneration completed)
- `2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/`
  (Step 0 — Phase 3 completion completed)
- `2026-09-01-dlt-path-drift-fix-v1/` (Step 1 — DLT path drift fix
  completed)

`Enables:`

- Step 4-8 (England → Wales → NI → IoM → Scotland) — the canonical
  Ireland + the 6 NCCA-adjacent pattern is now available to be
  cloned for the 7 other jurisdictions
- Step 9 (Vernaculars) — can reference the bilingual EN/GA pattern
  established here

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale rewrite of the existing 6 priority subjects — they
  remain unchanged
- England / Wales / NI / IoM / Scotland / Jersey / Guernsey
  coverage — handled in Step 4-8
- Bilingual vernacular languages (Welsh + Breton + Cornish + Manx
  + Channel Islands French + Ulster Scots + Scottish Gaelic) —
  handled in Step 9

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1 --strict  ✅
uv run baml-cli generate --from baml_src                                       ✅ 14 files
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractAccountingMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractBusinessMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractFrenchMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractHistoryMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractArtMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractMusicMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractAppliedMathsMarkingScheme)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractPhysicsMarkingScheme)"  ✅
```

---

*Last updated by build subagent at 2026-09-01.*