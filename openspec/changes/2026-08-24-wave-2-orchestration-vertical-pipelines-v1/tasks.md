# Tasks: 2026-08-24-wave-2-orchestration-vertical-pipelines-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-2-orchestration-vertical-pipelines-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-2-orchestration-vertical-pipelines-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-2-orchestration-vertical-pipelines-v1/specs/orchestration-vertical-pipelines/spec.md`

## Phase 2: PipelineFactoryComponent (3 tasks)

- [ ] **T2.1**: Build `orchestration/components/pipeline_factory.py` (NEW)
  - Implements `PipelineFactoryComponent(dg.Component, dg.Resolvable)`
  - Reads `dlt_source` attribute (Python import path)
  - Reads `pipeline_kind` attribute (one of: syllabus, exam_papers,
    personal_archive, official_docs, comics, crypto, pdf, media)
  - Reads `processing`, `destinations`, `schedules`, `sensors` lists
  - Auto-derives the asset graph via the appropriate
    `pipeline_kind_handlers/<kind>_handler.py` class
  - Uses BOTH (a) decorator metadata introspection AND (c)
    `pipeline.dataset()` schema introspection

- [ ] **T2.2**: Re-export from `orchestration/components/__init__.py`
  - Add `PipelineFactoryComponent` to the import list

- [ ] **T2.3**: Verify `dg list components` includes the new Component

## Phase 3: pipeline_kind_handlers (3 tasks)

- [ ] **T3.1**: Build `orchestration/components/pipeline_kind_handlers/__init__.py`
  - Re-exports the 8 handler classes

- [ ] **T3.2**: Implement the 8 handler classes
  - `syllabus_handler.py` (chemistry_syllabus → experiments → artifacts)
  - `exam_papers_handler.py` (UoG exam papers + LC + GCSE VLM extraction)
  - `personal_archive_handler.py` (notes + assignments + transcripts)
  - `official_docs_handler.py` (university module pages + student union)
  - `comics_handler.py` (VLM via cognee)
  - `crypto_handler.py` (chain indexer for crypteolas)
  - `pdf_handler.py` (OCR + BAML)
  - `media_handler.py` (codec probe + thumbnail + embeddings)

- [ ] **T3.3**: Verify each handler imports cleanly

## Phase 4: orchestration/pipelines/ skeleton (2 tasks)

- [ ] **T4.1**: Create `orchestration/pipelines/` directory structure
  - Mirrors the Wave 1 `dlt_sources/` domain-first layout
  - Starts with `education/tertiary/uog/`, `education/tertiary/nui_federation/`,
    `education/tertiary/british_isles/`, `law/`, `medicine/`,
    `media_comics/`, `media_games/`

- [ ] **T4.2**: Add `pipelines/__init__.py` package marker

## Phase 5: UoG flat-file conversion (3 tasks)

- [ ] **T5.1**: Convert `orchestration/defs/uog_exam.py` →
  `orchestration/pipelines/education/tertiary/uog/exam_papers/defs.yaml`
  - Use `PipelineFactoryComponent`
  - `pipeline_kind: exam_papers`
  - Preserve the VLM extraction logic

- [ ] **T5.2**: Convert `orchestration/defs/uog_personal_archive.py` +
  `uog_personal_archive_figures.py` →
  `orchestration/pipelines/education/tertiary/uog/personal_archive/defs.yaml`

- [ ] **T5.3**: Convert `orchestration/defs/uog_official_docs.py` →
  `orchestration/pipelines/education/tertiary/uog/official_docs/defs.yaml`
  + `uog_students_union.py` →
  `orchestration/pipelines/education/tertiary/uog/students_union/defs.yaml`

- [ ] **T5.4**: Convert `orchestration/defs/nui_federation.py` →
  `orchestration/pipelines/education/tertiary/nui_federation/defs.yaml`

## Phase 6: definitions.py update (2 tasks)

- [ ] **T6.1**: Update `orchestration/definitions.py` to also walk
  `orchestration/pipelines/` (in addition to `orchestration/defs/`)

- [ ] **T6.2**: Verify `dg list defs` includes the new pipelines

## Phase 7: Verification (3 tasks)

- [ ] **T7.1**: `mise run sync:dagster` passes
- [ ] **T7.2**: `mise run lint:drift-docs` passes
- [ ] **T7.3**: Sample new pipeline imports:
  - `from orchestration.components.pipeline_factory import PipelineFactoryComponent`
  - `from orchestration.components.pipeline_kind_handlers.exam_papers_handler import ExamPapersHandler`
  - `from orchestration.pipelines.education.tertiary.uog.exam_papers import defs`

## Phase 8: Commit + push (2 tasks)

- [ ] **T8.1**: Stage only Wave 2 files (NOT unrelated work)
- [ ] **T8.2**: Commit + push

## Total: 21 tasks across 8 phases

Estimated effort: ~15 days (per the master plan's Wave 2 estimate).
This PR delivers the framework + UoG conversion (~3 days). Subsequent
PRs migrate the rest of the defs/ tree.
