# Tasks: archive-celtic-baml-orphans

## Phase 1: Audit confirm zero callers

- [x] `grep -r "b\.IdentifyCognates\|b\.ExtractMorphology\|b\.ExtractVerbConjugation\|b\.ExtractProfileFromCV\|b\.ExtractProfileFromGitHubReadme\|b\.ExtractMusicProfile\|b\.ExtractGameProject\|b\.ExtractCelticEntities\|b\.ExtractHiddenHeritagesTale" /Users/cianmacandeisigh/dev/kings_college_galway/` returns 0 hits

## Phase 2: Add ARCHIVED header to each of the 6 files

- [ ] Add ARCHIVED header to `baml_src/cognates.baml` (5 functions)
- [ ] Add ARCHIVED header to `baml_src/celtic_linguistics.baml` (3 functions)
- [ ] Add ARCHIVED header to `baml_src/morphology.baml` (4 functions)
- [ ] Add ARCHIVED header to `baml_src/grammar_patterns.baml` (6 functions)
- [ ] Add ARCHIVED header to `baml_src/named_entities.baml` (5 functions)
- [ ] Add ARCHIVED header to `baml_src/portfolio_extraction.baml` (6 functions)

## Phase 3: Move the 6 files to baml_src/_archive/

- [ ] `git mv sruth/oideachais/baml_src/cognates.baml sruth/oideachais/baml_src/_archive/cognates.baml`
- [ ] `git mv sruth/oideachais/baml_src/celtic_linguistics.baml sruth/oideachais/baml_src/_archive/celtic_linguistics.baml`
- [ ] `git mv sruth/oideachais/baml_src/morphology.baml sruth/oideachais/baml_src/_archive/morphology.baml`
- [ ] `git mv sruth/oideachais/baml_src/grammar_patterns.baml sruth/oideachais/baml_src/_archive/grammar_patterns.baml`
- [ ] `git mv sruth/oideachais/baml_src/named_entities.baml sruth/oideachais/baml_src/_archive/named_entities.baml`
- [ ] `git mv sruth/oideachais/baml_src/portfolio_extraction.baml sruth/oideachais/baml_src/_archive/portfolio_extraction.baml`

## Phase 4: Create the archive README

- [ ] Create `sruth/oideachais/baml_src/_archive/README.md` with:
  - Rationale: 29 BAML functions in 6 files have no current consumer
  - Re-activation procedure: implement the consumer, remove the
    ARCHIVED marker, update STATUS.md
  - Reference to openspec/changes/archive-celtic-baml-orphans

## Phase 5: Update STATUS.md and REFACTORING.md

- [ ] In `sruth/oideachais/STATUS.md`: add a section "Archived BAML
  functions" that lists the 6 files + 29 functions with a
  pointer to the archive directory
- [ ] In `sruth/oideachais/REFACTORING.md`: add an entry for the archive
  with the re-activation procedure

## Phase 6: Validation

- [ ] `ls sruth/oideachais/baml_src/_archive/` shows 6 .baml files + README.md
- [ ] `grep -r "ARCHIVED 2026-06-24" sruth/oideachais/baml_src/_archive/` returns 6 hits
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
- [ ] `openspec validate archive-celtic-baml-orphans --strict` passes

## Phase 7: Land the plane

- [ ] Stage the moves + new files + modified docs
- [ ] Commit: `git commit -m "archive-celtic-baml-orphans: move 6 files to _archive/ (29 orphan functions)"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
