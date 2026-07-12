# Tasks — Wire English into lc5 + resolve the 972-LOC curriculum duplicate

## Part A — Wire English into lc5 (Phase 1.1)

### A.1 Edit `leaving_cert_source.py`

- [x] **A.1.1** Rename `LC5_SUBJECTS` → `LC6_SUBJECTS` in the 3 occurrences
      (`LC5_SUBJECTS: tuple[...] = (...)`, `for subject in LC5_SUBJECTS:`,
      and the log message `lc5_ingested: ... across {len(LC5_SUBJECTS)}`)
- [x] **A.1.2** Add `"english"` as the 3rd element of the tuple
      (alphabetical ordering: chemistry, computer_science, **english**,
      gaeilge, geography, mathematics)
- [x] **A.1.3** Add an `elif subject_dir.name == "english"` branch to
      `_scan_subject` that mirrors the gaeilge root-file logic but with
      `language = "en"` (English LC is monolingual — no `en/` subdir needed)
- [x] **A.1.4** Add 2 new regex patterns to `LC_PDF_KIND_REGISTRY`:
      - `^LC002ALP\d{3}[EI]V\.pdf$` → `qwen3-vl-8b` (LC English ALP exam papers)
      - `^SC-English-Spec-ENG-INT.*\.pdf$` → `gemma-4-26B-A4B` (English spec constitution)
- [x] **A.1.5** Update the module docstring: 5-subject → 6-subject + list english

### A.2 Edit `lc5_assets.py`

- [x] **A.2.1** Rename `LC5_SUBJECTS` → `LC6_SUBJECTS` in the 3 occurrences
      (`LC5_SUBJECTS: tuple[...] = (...)`,
      `for _subject in LC5_SUBJECTS:`,
      `return ... len(LC5_SUBJECTS)`)
- [x] **A.2.2** Add `"english"` as the 3rd element of the tuple
- [x] **A.2.3** Add the explicit `lc5_english_ingested` @asset (Layer 1)
      with group_name `1_ingestion/curriculum/lc5`
- [x] **A.2.4** Confirm the auto-generated 4 BAML extraction assets:
      `lc5_english_syllabus_extracted`, `lc5_english_papers_extracted`,
      `lc5_english_marking_extracted`, `lc5_english_diagrams_extracted`
      (created by the existing `for _subject in LC6_SUBJECTS` factory loop)
- [x] **A.2.5** Add the explicit `lc5_english_cognified` @asset (Layer 3)
      with group_name `3_model_lifecycle/lc_cognify/lc5/english`
- [x] **A.2.6** Update the `lc5_cross_subject_graphiti_stream` asset to
      mention "6 subjects" (was "5 subjects")
- [x] **A.2.7** Update module docstring + the docstrings of
      `_make_subject_extraction_asset` + the layer-2/3 comment blocks

### A.3 Create `lc5/english.yaml`

- [x] **A.3.1** Write the new file as a `CelticIngestionComponent` cron
      asset: source_id `cianfhoghlaim.filesystem.leaving_cert.english`,
      cron `"0 5 * * *"` (mirrors lc5/defs.yaml), subject=english,
      tags=[biep, lc6, english, ingestion], metadata pointing to this openspec change

## Part B — Resolve the 972-LOC duplicate (Phase 1.4)

### B.1 Verify the duplicates

- [x] **B.1.1** Confirm `curriculum_source.py` and `curriculum.py` are
      byte-identical: `md5 ... = c098f82f94909f9ffccee0387b600d9f`
      (972-LOC duplicate, no semantic difference)
- [x] **B.1.2** Confirm `exam_source_update.py` is a 0-byte stub
      (no functions defined, no active importer)

### B.2 Delete the duplicates

- [x] **B.2.1** `git rm dlt/british_isles/ireland/education/curriculum_source.py`
- [x] **B.2.2** `git rm dlt/british_isles/ireland/education/exam_source_update.py`

### B.3 Rewrite importers (11 files)

- [x] **B.3.1** `dlt/british_isles/ireland/law/citizensinformation.py`
- [x] **B.3.2** `dlt/british_isles/ireland/law/courts_ie.py`
- [x] **B.3.3** `dlt/british_isles/ireland/law/gov_ie_law.py`
- [x] **B.3.4** `dlt/british_isles/ireland/law/injuries_ie.py`
- [x] **B.3.5** `dlt/british_isles/ireland/law/workplace_relations.py`
- [x] **B.3.6** `dlt/british_isles/ireland/education/law/court_rules.py`
- [x] **B.3.7** `dlt/british_isles/ireland/education/law/courts.py`
- [x] **B.3.8** `dlt/british_isles/ireland/education/law/judgements.py`
- [x] **B.3.9** `dlt/british_isles/ireland/education/law/legal_aid.py`
- [x] **B.3.10** `dlt/british_isles/ireland/education/law/piab.py`
- [x] **B.3.11** `dlt/british_isles/ireland/education/curriculum.py` (the self-reference fix in the docstring)
- [x] **B.3.12** `tests/_oideachais/dlt_sources/ie/education/test_curriculum_source_local_cache.py` (2 import occurrences)

For each: rewrite
`from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source import (...)` →
`from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import (...)`

## Part C — OpenSpec change artefacts

- [x] **C.1** Create `openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1/proposal.md`
- [x] **C.2** Create `openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1/tasks.md` (this file)
- [x] **C.3** Create `openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1/specs/british-isles-education-pipeline/spec.md`
      delta — 2 ADDED Requirements (LC6 filesystem source + duplicate removal)
- [x] **C.4** Create `openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1/specs/oideachais-pipeline/spec.md`
      delta — 1 ADDED + 1 REMOVED Requirement (acknowledging the W1 ie→ireland cleanup that already removed the legacy `dlt/british_isles/ie/` directory)
- [x] **C.5** Run `openspec validate 2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1 --strict` — must pass before commit

## Part D — Verification + commit + push

- [x] **D.1** Static syntax check: `python -c "import ast; ast.parse(...)"`
      on leaving_cert_source.py + lc5_assets.py + 11 importers + test file
- [x] **D.2** Functional check: `python -c "from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents; rows = list(lc5_documents())"`
      returns 80 documents across 6 subjects with english=8 en rows
- [x] **D.3** Import check: the rewritten law/* and education/law/* modules
      can `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source` (the kept file has the symbol)
- [x] **D.4** Confirm `ls dlt/british_isles/ireland/education/ | grep curriculum_source` returns 0
- [x] **D.5** Confirm `ls dlt/british_isles/ireland/education/ | grep exam_source_update` returns 0
- [x] **D.6** `git add -A` (13 modified files + 1 new yaml + 2 deleted dups + 1 openspec change directory)
- [x] **D.7** `git -c user.email="build-agent@cianfhoghlaim" -c user.name="Build Agent" commit -m "feat(biep): wire English into lc5 + resolve 972-LOC curriculum duplicate"`
- [x] **D.8** `git push --set-upstream origin pick-4-biep-v1` (NOT `main`)

## Out of scope (deferred to follow-up openspec changes)

1. **Dagster group_name regex bug** (all `1_ingestion/...` style group names
   are invalid in Dagster 1.13.1). Needs a single sed across all
   `orchestration/defs/**/*.py` files. **OpenSpec candidate:**
   `2026-07-11-fix-dagster-asset-group-name-regex-v1`.
2. **The 4 BIEP v1 `lc_extraction/*.baml` files** — owned by the upstream
   `2026-07-06-british-isles-education-pipeline-v1` change.
3. **The 8 `qpack_*.baml` files** — owned by the BIEP v1 quest-pack generators.
4. **The CocoIndex v1 `english_embedding` flow** — needs the `_lifespan.py`
   shared embedder to be lifted to english, owned by the cocoindex cluster.
5. **The `lc5_chemistry_marking_extracted` etc. unimplemented stubs** — the
   factory creates them with empty bodies. Filling in the BAML call bodies
   is owned by the BIEP v1 Phase 4-5 follow-up.
