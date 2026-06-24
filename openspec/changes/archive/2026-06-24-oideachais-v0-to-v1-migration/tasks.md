# Tasks: oideachais-v0-to-v1-migration

## 1. 3 new skills

- [x] Create `.agents/skills/oideachais-leabharlann/SKILL.md` (186 lines)
- [x] Create `.agents/skills/oideachais-baml-schemas/SKILL.md` (218 lines)
- [x] Create `.agents/skills/oideachais-cocoindex-v1/SKILL.md` (304 lines)

## 2. Openspec change

- [x] Create `openspec/changes/oideachais-v0-to-v1-migration/proposal.md`
- [x] Create `openspec/changes/oideachais-v0-to-v1-migration/tasks.md`
- [x] Create `openspec/changes/oideachais-v0-to-v1-migration/specs/oideachais-cocoindex-v1-migration/spec.md`
  (1 MODIFIED + 1 ADDED)
- [x] `openspec validate oideachais-v0-to-v1-migration --strict`
- [x] `openspec archive oideachais-v0-to-v1-migration --yes`

## 3. Refactor: 10 v0 modules → `_v0_archive/`

- [x] `mkdir oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/author_archive_embedding.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/curriculum_embedding.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/curriculum_translation.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/curriculum_specification_extraction.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/geospatial_indexing.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/learning_outcome_graph.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/ocr_embedding.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/pdf_embedding.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/research_embedding.py oideachais/cocoindex_flows/_v0_archive/`
- [x] `git mv oideachais/cocoindex_flows/site_analysis_embedding.py oideachais/cocoindex_flows/_v0_archive/`
- [x] Create `oideachais/cocoindex_flows/_v0_archive/__init__.py` (the deprecation note)

## 4. Refactor: doc updates

- [x] Update `oideachais/cocoindex_flows/README.md` v0/v1 status table
  (10 rows change from "Migrate to v1 (deferred)" to "DEPRECATED 2026-06-24, archived at _v0_archive/")
- [x] Update `oideachais/AGENTS.md` Quick routing table — add 3 new
  skill rows (oideachais-leabharlann, oideachais-baml-schemas,
  oideachais-cocoindex-v1)
- [x] Update `oideachais/STATUS.md` §3 — change the v0/v1 status
  description

## 5. Commit + push + archive

- [x] `git commit -m "refactor(oideachais): archive 10 v0 cocoindex modules + 3 new skills (round 9)"`
- [x] `git push origin q3-2026-oideachais-consolidation`
- [x] `openspec archive oideachais-v0-to-v1-migration --yes` (already done above)
- [x] `git commit -m "openspec(archive): 2026-06-24-oideachais-v0-to-v1-migration"`
- [x] `git push origin q3-2026-oideachais-consolidation`
