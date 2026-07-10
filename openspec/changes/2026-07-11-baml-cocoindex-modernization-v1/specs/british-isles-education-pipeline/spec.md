## ADDED Requirements

### Requirement: `ExtractDocSkillTag` + `ExtractTriples` BAML re-creation (dangling-import fix)

The system SHALL provide a BAML source file at `cianfhoghlaim/baml/processing/docs_skills_extraction.baml` that defines the 2 functions + 2 classes referenced from `cianfhoghlaim/cocoindex/docs_skills_consolidation.py`.

#### Scenario: dangling imports resolve

- **GIVEN** the new file at `cianfhoghlaim/baml/processing/docs_skills_extraction.baml` (created in step 5 of `tasks.md`)
- **WHEN** `baml-cli generate` is run
- **THEN** the BAML-generated `baml_client.types.DocSkillTag` + `baml_client.types.Triple` classes are reachable
- **AND** the BAML-generated `b.ExtractDocSkillTag(content: string, path: string) -> DocSkillTag` and `b.ExtractTriples(content: string, path: string) -> Triple[]` functions are reachable
- **AND** the call sites at `cocoindex/docs_skills_consolidation.py:247,273,293` no longer raise `AttributeError`

#### Scenario: 1 test block added

- **GIVEN** the `test ExtractDocSkillTagTest { ... }` block in the new file
- **WHEN** `mise run baml:test` is run
- **THEN** the test block is discovered by `baml-cli test`
- **AND** the test passes (the BAML-codegen'd fixture input matches the BAML-codegen'd fixture output)

### Requirement: side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` vision pipeline (deferred)

The system SHALL provide a side-by-side vision pipeline that runs the same PDF extraction (`ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` + `ExtractSyllabusDiagram` + `ExtractMarkingSchemeGuideline`) against both `gemma-4-26B-A4B` and `qwen3-vl-8b` for comparison.

#### Scenario: vision generators wired but comparison deferred

- **GIVEN** the 2 new generators `local_vision_gemma4` + `local_vision_qwen3vl` are added in `clients.baml` (via the `meaisinfhoghlaim-agent-frameworks` delta)
- **WHEN** the BIEP `ExtractSyllabusDiagram` function is invoked
- **THEN** the function calls either `local_vision_gemma4` or `local_vision_qwen3vl` per the `pointing_model` parameter
- **AND** the side-by-side notebook tutorial that produces a comparison table is created under `notebooks/13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline.py` — but **this tutorial notebook is deferred** to the `2026-07-12-baml-cocoindex-tutorials-v1` follow-up openspec change
- **AND** the BIEP canonical contract (the 7 `baml/education/lc_extraction/*.baml` files) is **not modified** by either this change or the follow-up
