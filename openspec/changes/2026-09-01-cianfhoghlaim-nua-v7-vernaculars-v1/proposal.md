# Change: Cianfhoghlaim-Nua V7 Vernaculars v1 — 7 vernacular language extraction pipelines

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Step 9** of the cianfhoghlaim-nua v6 era plan. Adds BAML
> extraction support for the 7 vernacular languages of the British
> Isles beyond the canonical EN + GA pair.

## Why

Per the v6 era plan + the operator's direction (2026-09-01), the
BAML extraction pipeline must support the 7 vernacular languages
of the British Isles (beyond the canonical EN + GA pair):

1. **Welsh (cy)** — Wales
2. **Scottish Gaelic (gd)** — Scotland
3. **Breton (br)** — sister-repo lift target
4. **Cornish (kw)** — sister-repo lift target
5. **Manx (gv)** — Isle of Man
6. **Channel Islands French (fr-je + fr-gg)** — Jersey + Guernsey
7. **Ulster Scots (sco)** — Northern Ireland

The current `TranslationRequest.source_language` enum (in
`baml_src/british_isles/_cross/multi_nation_curriculum.baml`) only
supports 5 languages (en, ga, cy, gd, gv). This change adds the
missing 7 (br, kw, fr-je, fr-gg, sco + the explicit fr-je/fr-gg
variants) + the per-vernacular extraction BAML functions.

Every class is always bilingual (EN + GA + vernacular).

## What was shipped

### §1 — Author the 7-vernacular BAML file (1 file)

- **§1.1** `baml_src/british_isles/_cross/vernacular_languages.baml`:
  - `VernacularLanguage` enum (CY + GD + BR + KW + GV + FR_JE + FR_GG + SCO)
  - `VernacularSubjectSpec` class (bilingual EN + GA + vernacular)
  - 8 extraction functions: `ExtractWelshSubjectSpec` +
    `ExtractScottishGaelicSubjectSpec` + `ExtractBretonSubjectSpec`
    + `ExtractCornishSubjectSpec` + `ExtractManxSubjectSpec` +
    `ExtractJerseyFrenchSubjectSpec` + `ExtractGuernseyFrenchSubjectSpec`
    + `ExtractUlsterScotsSubjectSpec`
  - 2 BAML test blocks (Welsh + Scottish Gaelic)

### §2 — Update the `TranslationRequest.source_language` description (1 file)

- **§2.1** `baml_src/british_isles/_cross/multi_nation_curriculum.baml`:
  - Updated `source_language` description to include all 11
    language codes: "en, ga, cy, gd, gv, br, kw, gv-IM, fr-je,
    fr-gg, sco"

### §3 — Regenerate baml_client (1 action)

- **§3.1** `uv run baml-cli generate --from baml_src` —
  regenerated `baml_client/` (14 files). All 8 new
  `Extract<Vernacular>SubjectSpec` functions are reachable from
  runtime.

### §4 — Spec delta to `british-isles-education-pipeline` (1 file)

- **§4.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/specs/british-isles-education-pipeline/spec.md`
  — adds 1 new Requirement:
    - "The 7 British Isles vernacular languages (Welsh + Scottish
      Gaelic + Breton + Cornish + Manx + Channel Islands French +
      Ulster Scots) MUST each have a BAML Extract<Vernacular>SubjectSpec
      function"

## Impact

- **Audience:** every sister repo maintainer (the 8 extraction
  functions are designed to be lifted to `ciancheiltis/`,
  `gemini_hackathon/`, etc.).
- **Scope:** 2 files (1 new + 1 modified).
- **LOC delta:** +~250.
- **Risk:** LOW — additive; the existing 5 languages are
  unaffected.
- **Reversibility:** full.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/`
  (Steps 4-8 — the per-jurisdiction vernacular overlay classes
  established the pattern)
- `2026-09-01-baml-regeneration-blocker-v1/` (Step 0.5)

`Enables:`

- Step 10 (Final docs + skills) — the per-vernacular coverage
  matrix is now complete (all 8 British Isles subnations + the 7
  vernacular languages)
- Sister-repo lifts (Phase 8 sister-side mirrors) — the
  `ciancheiltis/` sister repo can lift the Breton + Cornish +
  Welsh + Manx functions; the `gemini_hackathon/` sister repo can
  lift the Scottish Gaelic function

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale rewrite of the existing 5 language support (en + ga +
  cy + gd + gv) — they remain unchanged
- DLT sources for each vernacular — follow-on work
- CocoIndex Apps for each vernacular — follow-on work
- Convex tables for each vernacular — follow-on work

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1 --strict  ✅
uv run baml-cli generate --from baml_src                                              ✅ 14 files
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractWelshSubjectSpec)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractScottishGaelicSubjectSpec)"  ✅
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractManxSubjectSpec)"  ✅
```

---

*Last updated by build subagent at 2026-09-01.*