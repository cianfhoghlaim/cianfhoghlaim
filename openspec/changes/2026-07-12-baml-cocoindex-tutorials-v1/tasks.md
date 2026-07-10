# Tasks — BAML+CocoIndex 5-notebook tutorial track v1

## 1. Create the `end-to-end-llm-zoomcamp-style-tutorial` capability spec

- [x] **1.1** Verify the spec doesn't already exist at
      `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`
      (it does NOT — the original spec at commit `1d94711c1` was
      pruned by the ie → ireland namespace migration)
- [x] **1.2** Create the spec at
      `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`
      with 8 requirements (the 6 original requirements from the
      `1d94711c1` blob `280c0aabe` + 2 ADDED requirements for the
      5-notebook tutorial track + the `01_overview_setup.py` Step 0.5
      pointer)
- [x] **1.3** Confirm `openspec list --specs | grep llm-zoomcamp`
      returns the spec

## 2. Create the 5 marimo tutorial notebooks

- [x] **2.1** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/01_baml_post_v4_syntax.py`
      (~600 lines; covers `generator` + `field Type` + `@@stream.*` +
      `image` + `?` optionality + `enum` + `function`)
- [x] **2.2** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough.py`
      (~500 lines; covers the 8 `qpack_<subject>.baml` files + the
      `paragraph → LO[] → FormativeItem → Score → Validate` pattern)
- [x] **2.3** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline.py`
      (~500 lines; covers the 4 vision extraction functions + the
      side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison
      cell + the `match_confidence` Jaccard similarity)
- [x] **2.4** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/04_cocoindex_baml_integration.py`
      (~400 lines; covers the 3 real CocoIndex+BAML integration
      patterns + the lazy-import + `ContextKey` + `use_context` +
      fallback-stub patterns)
- [x] **2.5** Create
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration.py`
      (~500 lines; covers the 42-renames commit audit + the 3
      unavoidable dups + the 1 missed dup + the 50 residual errors)
- [x] **2.6** Confirm all 5 notebooks AST-parse under
      `python -c "import ast; ast.parse(open(f).read())"`

## 3. Add the Step 0.5 pointer in `01_overview_setup.py`

- [x] **3.1** Create
      `cianfhoghlaim/notebooks/01_overview_setup.py` (a new
      welcome + architecture diagram + Step 0.5 BAML+CocoIndex
      tutorial pointer + Steps 1-4 + nb_utils tour; ~250 lines)
- [x] **3.2** Add the "Step 0.5: the BAML+CocoIndex tutorial track"
      Markdown cell that links to the 5 tutorials in
      `notebooks/13_baml_cocoindex_tutorial/`
- [x] **3.3** Confirm the file AST-parses

## 4. Update the `README.md` placeholder in the tutorial dir

- [x] **4.1** Replace the placeholder README at
      `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/README.md`
      with the canonical 5-notebook README (per the snippet in the
      parent change proposal)
- [x] **4.2** Add cross-references to the openspec spec + the parent
      mega-change + the 5-tangent change
- [x] **4.3** Add the `cianfhoghlaim-marimo` CLI usage examples

## 5. Update the `cli.py` to discover the new group

- [x] **5.1** Add `13_baml_cocoindex_tutorial` to the `GROUPS` tuple
      in `cianfhoghlaim/notebooks/cli.py`
- [x] **5.2** Confirm `uv run cianfhoghlaim-marimo list
      13_baml_cocoindex_tutorial` discovers the 5 entries
- [x] **5.3** Confirm `uv run cianfhoghlaim-marimo list` shows the
      5 entries under the new group

## 6. Verify each tutorial renders

- [x] **6.1** AST-parse all 5 tutorial notebooks + the
      `01_overview_setup.py` file
- [x] **6.2** Confirm `uv run cianfhoghlaim-marimo list
      13_baml_cocoindex_tutorial` returns 5 entries
- [x] **6.3** Confirm Tutorial 3 has the side-by-side
      `gemma-4-26B-A4B` + `qwen3-vl-8b` comparison cell
- [x] **6.4** Confirm the Step 0.5 pointer in `01_overview_setup.py`
      links to the 5 tutorials

## 7. Write the openspec change artefacts

- [x] **7.1** Create
      `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/`
- [x] **7.2** Write `proposal.md` (this change)
- [x] **7.3** Write `tasks.md` (this file)
- [x] **7.4** Write
      `specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` (1
      MODIFIED delta adding 2 ADDED requirements)
- [x] **7.5** Write
      `specs/oideachais-marimo-dashboards/spec.md` (1 ADDED
      requirement for the 5 tutorial notebooks)

## 8. Validate

- [x] **8.1** Run
      `openspec validate 2026-07-12-baml-cocoindex-tutorials-v1
      --strict` — must pass before commit

## 9. Commit + push

- [x] **9.1** `git add -A` (5 new + 1 modified + 2 new spec files)
- [x] **9.2** Commit with `feat(tutorials):` prefix
- [x] **9.3** Push to `origin/pick-4-biep-v1` (NOT `main`)

## Out of scope (deferred to follow-up openspec changes)

- The 7 `baml/education/lc_extraction/*.baml` files (owned by the
  BIEP v1 openspec change)
- The 50+ archived openspec changes under `openspec/changes/archive/*`
  — preserved unchanged
- The 50+ residual `baml-cli` validation errors in the `_shared/` /
  `pdfs/` / `celtic/` clusters — owned by separate openspec changes
- The leabharlann/ worktree — not touched
- The baml-py / baml_client version skew — out of scope
- The Irish-language (Gaeilge) counterpart of the 5-tutorial track —
  planned as a separate follow-up change
  (`2026-07-12-baml-cocoindex-tutorials-v1-ga/`)