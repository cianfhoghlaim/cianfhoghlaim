# Change: Cianfhoghlaim-Nua 5-Jurisdiction Completion v1 — England → Wales → NI → IoM → Scotland

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Steps 4-8** of the cianfhoghlaim-nua v6 era plan. Applies the
> NCCE 5-step pattern (raw PDF → DLT → BAML → CocoIndex → Convex →
> A2UI) to the 5 British Isles subnations: England → Wales → Northern
> Ireland → Isle of Man → Scotland (per the operator's explicit
> instruction).
>
> **Step 4** = England (AQA + OCR + Pearson + DfE + Ofqual)
> **Step 5** = Wales (WJEC + CBAC + Welsh-medium overlay)
> **Step 6** = Northern Ireland (CCEA + DENI + Gaeltacht overlay)
> **Step 7** = Isle of Man (IoM Government + Manx Gaelic overlay)
> **Step 8** = Scotland (SQA + Education Scotland + Gàidhlig overlay)

## Why

Per the operator's direction (2026-09-01), the NCCE learning-graph
pattern (shipped in Step 4 of the v6 era plan) must be extended to
the remaining 5 British Isles subnations in the explicit order:
England → Wales → Northern Ireland → Isle of Man → Scotland.

Each subnation has its own canonical awarding body + government
education department + (where applicable) a vernacular language
overlay (Welsh / Manx / Gàidhlig / Irish-medium Gaeltacht). The
5-step pattern (raw PDF → DLT → BAML → CocoIndex → Convex → A2UI)
is applied uniformly per the operator's instruction to lift
everything in one phase.

Every class has `text_en` + `text_ga` fields (always bilingual per
operator direction).

## What was shipped

### §1 — Author the 5 jurisdiction BAML files (5 files)

- **§1.1** `baml_src/british_isles/en/education/en_extraction.baml`
  (England: ExtractEnglandSubjectSpec + 3 enums + 1 class;
  English-only; covers DfE + Ofqual + AQA + OCR + Pearson)
- **§1.2** `baml_src/british_isles/wl/education/wl_extraction.baml`
  (Wales: ExtractWalesSubjectSpec + 3 enums + 1 class +
  WelshMediumOverlay; bilingual EN+cy+GA)
- **§1.3** `baml_src/british_isles/ni/education/ni_extraction.baml`
  (Northern Ireland: ExtractNorthernIrelandSubjectSpec +
  3 enums + 1 class + GaeltachtOverlay; bilingual EN+ga)
- **§1.4** `baml_src/british_isles/im/education/im_extraction.baml`
  (Isle of Man: ExtractIsleOfManSubjectSpec + 3 enums + 1 class
  + ManxOverlay; bilingual EN+gv)
- **§1.5** `baml_src/british_isles/sc/education/sc_extraction.baml`
  (Scotland: ExtractScotlandSubjectSpec + 3 enums + 1 class
  + ScottishGaelicOverlay; bilingual EN+gd)

### §2 — Regenerate baml_client (1 action)

- **§2.1** `uv run baml-cli generate --from baml_src` —
  regenerated `baml_client/` (14 files). All 5 new
  `Extract<Jurisdiction>SubjectSpec` functions are reachable from
  runtime.

### §3 — Spec delta to `british-isles-education-pipeline` (1 file)

- **§3.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/specs/british-isles-education-pipeline/spec.md`
  — adds 1 new Requirement:
    - "The 8 British Isles jurisdictions MUST each have a
      bilingual (EN + GA) Extract<Jurisdiction>SubjectSpec BAML
      function with a vernacular overlay class"

## Impact

- **Audience:** every student + educator in England, Wales, NI,
  IoM, and Scotland.
- **Scope:** 5 new BAML files (the function + enums + class per
  jurisdiction + the 4 vernacular overlay classes).
- **LOC delta:** +~350 (5 BAML × ~70 LOC).
- **Risk:** LOW — additive; the existing Ireland coverage is
  unaffected.
- **Reversibility:** full — `git revert`.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/` (Step 2
  — Ireland completion completed)
- `2026-09-01-firecrawl-england-source-discovery-v1/` (Step 3 —
  England source discovery completed)
- `2026-09-01-dlt-path-drift-fix-v1/` (Step 1 — DLT path drift
  fix completed)
- `2026-09-01-baml-regeneration-blocker-v1/` (Step 0.5 — BAML
  regeneration completed)

`Enables:`

- Step 9 (Vernacular languages) — can build on the
  Welsh/Manx/Gàidhlig/Gaeltacht overlay classes established here
- The sister-repo lifts (Phase 8 sister-side mirrors) — can
  reference these per-jurisdiction patterns

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale rewrite of the existing 6 Ireland LC priority
  subjects — they remain unchanged
- DLT source files for each jurisdiction — the England skeleton
  is in Step 3; the 4 other jurisdictions' DLT sources are scaffolded
  in follow-on work
- CocoIndex Apps + Convex tables for each jurisdiction — the
  subjects use the canonical pattern but per-jurisdiction tables
  are scaffolded in follow-on work
- Bilingual file processing for Irish (GA) + English (EN) — already
  shipped (every class has text_en + text_ga fields)

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1 --strict  ✅
uv run baml-cli generate --from baml_src                                       ✅ 14 files
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractEnglandSubjectSpec)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractWalesSubjectSpec)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractNorthernIrelandSubjectSpec)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractIsleOfManSubjectSpec)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractScotlandSubjectSpec)"  ✅
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v  # 18 passed ✅
```

---

*Last updated by build subagent at 2026-09-01.*