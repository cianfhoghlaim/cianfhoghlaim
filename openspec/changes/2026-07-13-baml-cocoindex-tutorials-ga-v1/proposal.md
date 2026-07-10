# BAML+CocoIndex 5-notebook Gaeilge (Irish-language) counterpart tutorial track v1

## Why

The English-language BAML+CocoIndex tutorial track (5 marimo notebooks at
`cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/`) shipped at
commit `78f2938ac` via the openspec change
`2026-07-12-baml-cocoindex-tutorials-v1`. The English tutorial track is
explicitly acknowledged as the "English-language counterpart" in its own
README + its own proposal.md ("the Irish-language (Gaeilge) counterpart of
the 5-tutorial track — planned as a separate follow-up change
`2026-07-12-baml-cocoindex-tutorials-v1-ga/`").

This change ships the **5 Gaeilge (Irish-language) companion
tutorials** — one per English tutorial — that demonstrate the
bilingual EN+GA extraction path through the same BAML 0.223.0 +
CocoIndex v1 + vision-model stack.

The bilingual EN+GA mandate is project-wide: the agent fleet + marimo
notebooks + BAML extraction functions all carry both languages.
Extending the bilingual mandate to the BAML+CocoIndex tutorial track
is the natural next step.

## What changes

| File | Action | LOC delta |
|:--|:--|--:|
| `cianfhoghlaim/baml/education/_shared/content_types.baml` | MODIFY (add `enum GaeilgeLanguage` + 2 functions: `ExtractBilingualText`, `ExtractStrandGaStatement`) | +~30 |
| `cianfhoghlaim/baml/education/subjects/qpack_gaeilge.baml` | MODIFY (add `ExtractGaelGaStatement`) | +~25 |
| `cianfhoghlaim/baml/education/subjects/qpack_mathematics.baml` | MODIFY (add `ExtractMathGaStatement`) | +~20 |
| `cianfhoghlaim/baml/education/subjects/qpack_history.baml` | MODIFY (add `ExtractHistGaStatement`) | +~20 |
| `cianfhoghlaim/baml/education/subjects/qpack_geography.baml` | MODIFY (add `ExtractGeogGaStatement`) | +~20 |
| `cianfhoghlaim/baml/education/subjects/qpack_chemistry.baml` | MODIFY (add `ExtractChemGaStatement`) | +~20 |
| `cianfhoghlaim/baml/education/subjects/qpack_applied_mathematics.baml` | MODIFY (add `ExtractAppmGaStatement`) | +~20 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/01_baml_post_v4_syntax_ga.py` | NEW | +~316 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough_ga.py` | NEW | +~382 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline_ga.py` | NEW | +~318 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/04_cocoindex_baml_integration_ga.py` | NEW | +~294 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration_ga.py` | NEW | +~289 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/README.md` | MODIFY (add 5 _ga companion entries) | +~30 |
| `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` | NEW (proposal.md + tasks.md + 1 spec delta) | +~250 |
| `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` | NEW (1 MODIFIED delta adding 1 ADDED requirement) | +~30 |

## The 5 _ga tutorials (summary)

| # | File | LOC | What it teaches |
|:--|:--|--:|:--|
| 1 | `01_baml_post_v4_syntax_ga.py` | 316 | Bilingual EN+GA syntax additions (`enum GaeilgeLanguage`, `class BilingualText`, `function ExtractBilingualText`, `function ExtractStrandGaStatement`) + a `bilingual(en, ga)` rendering helper |
| 2 | `02_qpack_8_subject_walkthrough_ga.py` | 382 | The 6 GA-LC-subject qpack variants (gaeilge + mathematics + history + geography + chemistry + applied_mathematics) with the `Extract<Subject>GaStatement` functions |
| 3 | `03_education_pdf_vision_pipeline_ga.py` | 318 | Side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison on Gaeilge NCCA PDFs (síneadh fada + dual-column Irish+English layout) |
| 4 | `04_cocoindex_baml_integration_ga.py` | 294 | The 3 CocoIndex+BAML integration patterns (`upstream_api_surface`, `upstream_blog_monitor`, `docs_skills_consolidation`) applied to GA content with `language: "ga"` discriminator |
| 5 | `05_post_v4_duplicate_audit_and_migration_ga.py` | 289 | Bilingual audit of the 10 BAML additions (4 in `_shared/` + 6 GA-qpack variants), 0 new duplicates, 0 new residual errors |
| **TOTAL** | | **1,599** | |

## The 10 BAML additions (4 + 6)

### 4 additions in `_shared/content_types.baml`

```baml
enum GaeilgeLanguage {
  GA @description("Gaeilge (Irish) — the canonical first-language form for Gaeilge-medium content")
  EN @description("Béarla (English) — the canonical first-language form for English-medium content")
}

function ExtractBilingualText(content: string) -> BilingualText {
  client default
  prompt #"Extract the structured bilingual text from: {{ content }}.
    Return the English text (text_en) and the Irish (Gaeilge) text
    (text_ga) where present..."#
}

function ExtractStrandGaStatement(paragraph: string) -> string[] {
  client default
  prompt #"Extract the NCCA strand/outcome statements in Irish (Gaeilge)
    from: {{ paragraph }}. Return them as a list of full Irish statements..."#
}
```

### 6 GA-qpack variants (one per GA-LC-subject)

| Subject | Function |
|:--|:--|
| Gaeilge | `ExtractGaelGaStatement(paragraph) -> string[]` |
| Mathematics | `ExtractMathGaStatement(paragraph) -> string[]` |
| History | `ExtractHistGaStatement(paragraph) -> string[]` |
| Geography | `ExtractGeogGaStatement(paragraph) -> string[]` |
| Chemistry | `ExtractChemGaStatement(paragraph) -> string[]` |
| Applied Mathematics | `ExtractAppmGaStatement(paragraph) -> string[]` |

All 6 GA variants share the same `string[]` return shape and use
`client default` (not `client ExtractEn`) so the GA path is
benchmarkable against the EN path. For LOs the NCCA did not
translate (most LC Mathematics + Chemistry + Applied Mathematics
LOs), the GA function returns the EN statements verbatim with a
leading `[EN-only]` marker.

## How

### Approach

Single coordinated commit per the AGENTS.md "Commit + push" template,
targeting `origin/pick-4-biep-v1` (NOT main). Each step is auditable
via a single `ls` / `openspec validate` / `python -c "import ast; ..."`
check.

1. Add `enum GaeilgeLanguage` + `function ExtractBilingualText` +
   `function ExtractStrandGaStatement` to
   `cianfhoghlaim/baml/education/_shared/content_types.baml`.
2. Add `Extract<Subject>GaStatement(paragraph) -> string[]` to each of
   the 6 GA-LC-subject qpack files
   (`qpack_gaeilge.baml`, `qpack_mathematics.baml`, `qpack_history.baml`,
   `qpack_geography.baml`, `qpack_chemistry.baml`,
   `qpack_applied_mathematics.baml`).
3. Create the 5 _ga companion tutorials at
   `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/*_ga.py`. Each
   is ~50-70% the size of its English counterpart (~150-380 LOC).
4. Update the `README.md` in the tutorial directory to add the 5 _ga
   companion entries + the bilingual EN+GA mandate explanation.
5. Verify each _ga tutorial AST-parses under Python 3.13
   (`python -c "import ast; ast.parse(open(f).read())"`).
6. Verify `mise run baml:generate` does NOT introduce new errors
   beyond the 47 documented pre-existing residual errors
   (per `2026-07-13-baml-final-cleanup-v1/SCOPE_DECISION.md`).
7. Write the openspec change artefacts (proposal.md + tasks.md +
   1 spec delta).
8. `openspec validate 2026-07-13-baml-cocoindex-tutorials-ga-v1
   --strict` must pass before commit.
9. Single commit + push to `origin/pick-4-biep-v1`.

### Why single-commit

The 5 _ga tutorials + the 4 BAML additions + the 6 GA-qpack variants
+ the spec delta + the README update form a single logical unit: the
5 _ga tutorials only make sense in the context of the BAML additions
+ the GA-qpack variants. A single commit is the smallest rebase-safe
unit.

## Dependencies

`Blocked by: 2026-07-12-baml-cocoindex-tutorials-v1` (commit
`78f2938ac`; the English tutorial track must land first so the 5 _ga
companions have a stable English-language base to mirror).

`Blocked by (soft): 2026-07-11-baml-cocoindex-modernization-v1` (the
parent mega-change that created the BAML 0.223.0 + CocoIndex v1 base).

`Blocked by (soft): 2026-07-12-baml-rename-42-duplicates-v1` (commit
`49e0259a0`; the 42-renames commit hoisted `BilingualText` to
`_shared/content_types.baml`, which this change builds on).

`Blocked by (soft): 2026-07-13-baml-final-cleanup-v1` (the
50-residual-errors scope decision; this change does NOT add any new
BAML errors beyond the documented 47 file-level diagnostic groups).

`Affected repos: cianfhoghlaim` (single-repo; no `bonneagar/` or
`leabharlann/` cross-repo sync needed).

## Out of scope (acknowledged)

- The 7 `baml/education/lc_extraction/*.baml` files (owned by the
  BIEP v1 openspec change; the 4 vision extraction functions
  referenced by Tutorial 3 live here but are documented, not modified)
- The 50+ archived openspec changes under `openspec/changes/archive/*`
  — preserved unchanged
- The 47 documented pre-existing residual `baml-cli` validation
  errors in the `_shared/` / `pdfs/` / `celtic/` /
  `lc_extraction/` / `processing/` clusters — owned by separate
  openspec changes; this change adds 0 new errors to the residual
  count
- The leabharlann/ worktree — not touched (NCCA corpus data lives
  there, not in the baml/ tree)
- The baml-py / baml_client version skew — out of scope
- The Computer Science + English qpack `Extract<Subject>GaStatement`
  variants — these subjects are predominantly EN-only at NCCA level;
  the GA path returns the EN statements verbatim with a `[EN-only]`
  marker, so they would be 1-line near-duplicates of the existing
  `Extract<Subject>LOStatement` and are deliberately omitted

## Acceptance gates

- [x] `openspec validate 2026-07-13-baml-cocoindex-tutorials-ga-v1
      --strict` passes
- [x] `baml/education/_shared/content_types.baml` has the
      `GaeilgeLanguage` enum + the `BilingualText` class (hoisted by
      the 42-renames commit) + the `ExtractBilingualText` function +
      the `ExtractStrandGaStatement` function
- [x] All 6 GA-qpack variants expose
      `Extract<Subject>GaStatement(paragraph) -> string[]`
- [x] 5 _ga companion notebooks at
      `notebooks/13_baml_cocoindex_tutorial/*_ga.py` exist + AST-parse
      cleanly
- [x] `notebooks/13_baml_cocoindex_tutorial/README.md` is updated
      with the 5 new entries
- [x] `mise run baml:generate` exit code matches the documented
      pre-change baseline (the 47 residual errors are unchanged after
      this change; 0 new errors introduced)
- [x] `mise run baml:test` exit code matches the documented
      pre-change baseline (same 47 residual errors block both
      `baml:generate` and `baml:test`)
- [x] Pushed to `origin/pick-4-biep-v1` (NOT `main`)