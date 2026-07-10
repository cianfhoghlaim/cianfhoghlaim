# Tasks — BAML+CocoIndex 5-notebook Gaeilge counterpart tutorial track v1

## 1. Inventory the existing bilingual patterns

- [x] **1.1** Verify the existing `BilingualText` class is hoisted to
      `baml/education/_shared/content_types.baml` (per the 42-renames
      commit `49e0259a0`)
- [x] **1.2** Confirm the 8 qpack files all expose
      `Extract<Subject>LOStatement(paragraph) -> string[]`
- [x] **1.3** Confirm `Extract<Subject>GaStatement` does NOT yet exist
      in any of the 8 qpack files
- [x] **1.4** Confirm `enum GaeilgeLanguage` does NOT yet exist in any
      `.baml` file

## 2. Add `GaeilgeLanguage` enum + bilingual functions to `_shared/content_types.baml`

- [x] **2.1** Add the `enum GaeilgeLanguage` enum (GA / EN values, no
      quotes per BAML enum syntax)
- [x] **2.2** Add the `function ExtractBilingualText(content) ->
      BilingualText` function
- [x] **2.3** Add the `function ExtractStrandGaStatement(paragraph) ->
      string[]` function
- [x] **2.4** Verify the 3 additions do NOT introduce any new BAML
      errors (the pre-existing 47 documented residual errors remain
      unchanged)

## 3. Add `Extract<Subject>GaStatement` to the 6 GA-LC-subject qpack files

- [x] **3.1** Add `ExtractGaelGaStatement(paragraph) -> string[]` to
      `qpack_gaeilge.baml`
- [x] **3.2** Add `ExtractMathGaStatement(paragraph) -> string[]` to
      `qpack_mathematics.baml`
- [x] **3.3** Add `ExtractHistGaStatement(paragraph) -> string[]` to
      `qpack_history.baml`
- [x] **3.4** Add `ExtractGeogGaStatement(paragraph) -> string[]` to
      `qpack_geography.baml`
- [x] **3.5** Add `ExtractChemGaStatement(paragraph) -> string[]` to
      `qpack_chemistry.baml`
- [x] **3.6** Add `ExtractAppmGaStatement(paragraph) -> string[]` to
      `qpack_applied_mathematics.baml`
- [x] **3.7** Verify all 6 additions do NOT introduce any new BAML
      errors (the pre-existing 47 documented residual errors remain
      unchanged)

## 4. Create the 5 _ga companion marimo notebooks

- [x] **4.1** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/01_baml_post_v4_syntax_ga.py`
      (~316 LOC; covers the bilingual EN+GA syntax additions +
      a `bilingual(en, ga)` rendering helper)
- [x] **4.2** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough_ga.py`
      (~382 LOC; covers the 6 GA-LC-subject qpack variants with the
      `Extract<Subject>GaStatement` functions)
- [x] **4.3** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline_ga.py`
      (~318 LOC; covers the vision+PDF pipeline on Gaeilge NCCA PDFs +
      the side-by-side `gemma-4` vs `qwen3-vl` comparison)
- [x] **4.4** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/04_cocoindex_baml_integration_ga.py`
      (~294 LOC; covers the 3 CocoIndex+BAML integration patterns on
      GA content)
- [x] **4.5** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration_ga.py`
      (~289 LOC; covers the bilingual audit of the 10 BAML additions)
- [x] **4.6** Confirm all 5 _ga notebooks AST-parse under
      `python -c "import ast; ast.parse(open(f).read())"`

## 5. Update the `README.md` in the tutorial directory

- [x] **5.1** Add the 5 _ga companion entries to the README.md table
- [x] **5.2** Add the bilingual EN+GA mandate explanation
- [x] **5.3** Add the `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/`
      cross-reference

## 6. Verify the 5 _ga companions AST-parse

- [x] **6.1** Run the `for nb in ...; do echo "=== $nb ==="; uv run
      python3 -c "import ast; ast.parse(open('$nb').read()); print('OK:
      AST-parse passed')" 2>&1; done` loop
- [x] **6.2** Confirm all 5 print "OK: AST-parse passed"

## 7. Verify BAML generate + test

- [x] **7.1** Run `cd cianfhoghlaim && uv run baml-cli generate
      --from baml_src 2>&1 | tail -30` — confirm the error stream does
      NOT mention any of the 4 new BAML additions or any of the 6
      new GA-qpack functions
- [x] **7.2** Run `cd cianfhoghlaim && uv run baml-cli test
      --from baml_src 2>&1 | tail -15` — confirm same
- [x] **7.3** Document that `baml:generate` + `baml:test` exit
      non-zero on the documented pre-existing 47 residual errors
      (per `2026-07-13-baml-final-cleanup-v1/SCOPE_DECISION.md`); 0
      new errors introduced

## 8. Write the openspec change artefacts

- [x] **8.1** Create
      `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/`
- [x] **8.2** Write `proposal.md`
- [x] **8.3** Write `tasks.md` (this file)
- [x] **8.4** Write
      `specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` (1
      MODIFIED delta adding 1 ADDED requirement for the 5 _ga
      companion tutorials)

## 9. Validate

- [x] **9.1** Run
      `openspec validate 2026-07-13-baml-cocoindex-tutorials-ga-v1
      --strict` — must pass before commit
  - **Result:** `Change '2026-07-13-baml-cocoindex-tutorials-ga-v1' is valid`

## 10. Commit + push

- [x] **10.1** `git add -A` (5 new _ga notebooks + 1 modified
      `content_types.baml` + 6 modified qpack files + 1 modified
      README.md + 1 new openspec change directory)
- [x] **10.2** Commit with `feat(tutorials):` prefix
- [x] **10.3** Push to `origin/pick-4-biep-v1` (NOT `main`)

## Out of scope (deferred to follow-up openspec changes)

- The 7 `baml/education/lc_extraction/*.baml` files (owned by the
  BIEP v1 openspec change)
- The 50+ archived openspec changes under `openspec/changes/archive/*`
  — preserved unchanged
- The 47 documented pre-existing residual `baml-cli` validation
  errors in the `_shared/` / `pdfs/` / `celtic/` /
  `lc_extraction/` / `processing/` clusters — owned by separate
  openspec changes
- The leabharlann/ worktree — not touched
- The baml-py / baml_client version skew — out of scope
- The Computer Science + English qpack `Extract<Subject>GaStatement`
  variants — these subjects are predominantly EN-only at NCCA level
- Translating the BAML function prompts themselves to Irish — the
  prompts remain in English (the canonical LLM language) with the
  output structured for Irish extraction