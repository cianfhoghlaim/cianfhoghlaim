## ADDED Requirements

### Requirement: Per-subject marimo notebooks invoke BAML quest functions

The system SHALL ensure all 12 per-subject interactive marimo notebooks (6 study tools in `cianfhoghlaim/notebooks/12_subject_study_tools/` plus 6 dashboards in `cianfhoghlaim/notebooks/leaving_cert/`) invoke the generated per-subject BAML client functions instead of recording dead-code dictionaries or stale placeholder state.

The six study-tool notebooks SHALL invoke the corresponding `Generate<Subject>FormativeItem(lo_code, difficulty, level, topic)` function and surface either the generated item or the caught BAML error in the marimo output. The six `leaving_cert` dashboards SHALL invoke the canonical `Generate<Subject>QuestPack(syllabus, past_papers, marking_schemes, level)` function for their subject, using the exact generated qpack function names (`GenerateMathQuestPack`, `GenerateChemQuestPack`, `GenerateCompQuestPack`, `GenerateEnglQuestPack`, `GenerateGaelQuestPack`, `GenerateGeogQuestPack`).

#### Scenario: Study-tool notebooks call real formative-item functions

- **GIVEN** the six study-tool notebooks exist under `cianfhoghlaim/notebooks/12_subject_study_tools/`
- **WHEN** the per-subject BAML cell is inspected
- **THEN** each notebook calls its generated `b.Generate<Subject>FormativeItem(...)` function with `lo_code`, `difficulty`, `level`, and `topic`
- **AND** none of the six notebooks records a `{"function": "Generate<Subject>FormativeItem", "status": "invoked"}` dictionary placeholder
- **AND** the marimo output includes the generated result or the caught error state.

#### Scenario: Leaving-cert dashboards use canonical quest-pack signatures

- **GIVEN** the six `leaving_cert/<subject>.py` dashboards exist
- **WHEN** their quest-pack BAML cells are inspected
- **THEN** each dashboard calls its generated `Generate<Subject>QuestPack` function with `syllabus`, `past_papers`, `marking_schemes`, and `level`
- **AND** none of the six dashboards calls the stale `(topic, level, language, n_items)` signature
- **AND** Computer Science, English, Gaeilge, and Geography use the generated abbreviated qpack names (`Comp`, `Engl`, `Gael`, `Geog`) rather than non-existent long-form function names.

#### Scenario: All 12 notebooks remain syntactically valid

- **WHEN** the user runs `ast.parse` over the 6 study-tool notebooks and 6 `leaving_cert` dashboards
- **THEN** all 12 notebooks parse successfully.
