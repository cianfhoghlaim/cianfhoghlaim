# Spec Delta: tuatha-british-isles-mmo

## Purpose

`tuatha-british-isles-mmo` is the canonical capability for the
**Tuatha** project — the British Isles Formative Assessment MMO
sub-project that lives at
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
(soon to be the independent GitHub repo at
`github.com/cianmacandeisigh/tuatha.git`).

The capability is the implementation surface for the
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md` spec.
The Tuatha project implements the British Isles Formative
Assessment MMO theming (the 8 NCCA Leaving Certificate subjects
+ the 4 BIEP hackathon features + the 3 educational agents + the
1 media_intel pipeline).

This capability was created by the
`2026-08-25-tuatha-british-isles-mmo-consolidation-v1` change,
which consolidates the prior scattered `agents/tuatha/` state +
the prior top-level `tuatha/` skeleton + the
`agents/meaisinfhoghlaim/media_intel/` module into the new
single coherent Tuatha project.

## ADDED Requirements

### Requirement: 8 NCCA Leaving Certificate subject agents

The system SHALL provide end-to-end per-subject agents for the 8
NCCA Leaving Certificate subjects: mathematics,
applied_mathematics, chemistry, geography, history, english,
gaeilge, computer_science. Each subject SHALL have a
`<subject>_agent.py` ADK agent in the new `tuatha/subjects/`
directory + 5 per-subject tools (syllabus_lookup +
past_paper_lookup + marking_scheme_lookup +
formative_item_generate + response_score) in the new
`tuatha/tools/` directory.

#### Scenario: A student asks the Mathematics agent a syllabus question

- **GIVEN** the user is authenticated in the new `tuatha/`
  project
- **AND** the `tuatha/subjects/mathematics.py` agent is
  available via the `tuatha.agents.media_intel.media_descriptor_agent`
  re-routing (or directly)
- **WHEN** the user asks "what is the NCCA LC Mathematics Higher
  Level syllabus on complex numbers"
- **THEN** the agent calls the `tuatha/tools/mathematics_syllabus_lookup`
  tool
- **AND** returns the BAML-extracted syllabus topic with the
  `ncca_code` + `excerpt_en` + `source_page` from the
  `qpack_mathematics.baml` extractor
- **AND** the response carries a citation linking back to the
  `leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf`
  PDF (the canonical NCCA Mathematics syllabus)

### Requirement: 3 educational agents (academic + Celtic grammar + Celtic morphology)

The system SHALL provide 3 educational agents under
`tuatha/agents/educational/` for the academic + Celtic-language
specialty layer:

1. `academic_history_agent.py` — the cross-subject +
   cross-jurisdiction history research agent (routes to the
   Wikipedia + CELT + Dúchas / Gaois corpora)
2. `celtic_grammar_agent.py` — the Irish grammar specialist
   (gaelicisation + dialectical forms + corpus reference)
3. `celtic_morphology_agent.py` — the Celtic morphology
   specialist (prefix + suffix + infix patterns + calque
   identification)

These are the 3 educational agents from
`agents/meaisinfhoghlaim/educational/`, refactored into the new
`tuatha/agents/educational/` location.

#### Scenario: A Gaeilge teacher asks the Celtic grammar agent about dialectical forms

- **GIVEN** the user is authenticated in the new `tuatha/`
  project
- **WHEN** the user asks "what is the difference between the
  Connacht and Ulster dialectical forms of the verb 'bí'"
- **THEN** the `celtic_grammar_agent` routes to the
  `qpack_gaeilge.baml` extractor's grammar sub-function
- **AND** returns the 2 dialectical forms side-by-side with the
  relevant excerpts from the CELT corpus
- **AND** the response carries a citation linking back to the
  CELT text source (per the `dúchas.ie` / Gaeltacht data sources
  in the `agents/tuatha/gaeilge.md` research doc)

### Requirement: 4 BIEP hackathon features

The system SHALL provide 4 BIEP hackathon features under
`tuatha/agents/hackathon/` (per the
`2026-08-21-biiep-hackathon-agentic-educational-system-v1/`
change):

1. `marking_grader.py` — the Adaptive Marking Grader (student
   uploads answer + marking scheme → instant grade + feedback)
2. `adaptive_tutor.py` — the Adaptive Tutor Chat (stateful
   6-jurisdiction syllabus tutor with persistent memory)
3. `equivalency_generator.py` — the Cross-Jurisdiction
   Equivalency Generator (compare LC ↔ A-Level ↔ GCSE topics
   side-by-side)
4. `curriculum_change_sensor.py` — the Curriculum Change
   Detection Sensor (Dagster sensor that watches NCCA + AQA +
   SQA + WJEC + CCEA + IoM websites)

#### Scenario: A teacher uses the Adaptive Marking Grader

- **GIVEN** the teacher uploads a student's PDF answer + the
  official NCCA marking scheme
- **WHEN** the `marking_grader` workflow runs
- **THEN** the `tuatha/baml/marking_grader.baml` extractor
  matches the answer against the marking scheme
- **AND** returns a grade + personalised feedback in plain
  English
- **AND** the grade + feedback is persisted to the
  `oideachais_lc_<subject>` Cognee dataset for the next session
  (the future student-teacher longitudinal study)

### Requirement: 1 media_intel pipeline (the 10-tool agent)

The system SHALL provide the media_intel pipeline (moved from
`agents/meaisinfhoghlaim/media_intel/`) under
`tuatha/agents/media_intel/`. The 10-tool ADK
`media_descriptor_agent` orchestrates the 5 per-medium BAML
extractor functions (comic / prose / animation / gameplay /
official_document) + the 5 corpus introspection tools
(list_sources / list_descriptors_by_class / summarise_corpus /
compare_class_consistency / search_descriptors).

#### Scenario: A research user asks the media_descriptor_agent for cross-medium consistency

- **GIVEN** the media_intel corpus has 100+ rows per class
- **WHEN** the user calls `compare_class_consistency("fire")`
- **THEN** the agent returns the per-medium cosine similarity
  scores + the consistency score (inverse of variance)
- **AND** the response identifies the most consistently
  described source class for the `fire` element
- **AND** the response is logged to Langfuse with the
  `agent.media_descriptor.extract` trace

### Requirement: The British Isles Formative Assessment MMO theme

The system SHALL adopt the British Isles Formative Assessment MMO
theme per the canonical `cianfhoghlaim-educational-mmo` spec.
The 8 NCCA Leaving Certificate subjects are the canonical
content surface.

**The 3 deprecated themes are HARD-ARCHIVED** (per the
`CONSOLIDATION_PLAN.md`):

- ~~Pent-Elemental Cosmology~~ (5 realms: Spirit / Water / Fire
  / Earth / Air) — archived
- ~~Babylon.js 3D~~ game front-end — replaced with the TanStack
  Start 2D client
- ~~SpacetimeDB v2~~ game engine backend — replaced with Convex +
  Hono + Dagster + DuckLake
- ~~Crypteolas financial token~~ — replaced with the
  educational-credential badge system
- ~~Anam Cara~~ soul friend mechanic — replaced with the 4 BIEP
  hackathon features
- ~~Brown Ajah theming~~ (the 8 NCCA subject ↔ Tuatha Dé deity
  mapping is preserved as `tuatha/subjects/character.py` but the
  "Brown Ajah" name is dropped)

The technological choices that ARE preserved:
- The 8 NCCA subject agents (refactored into `tuatha/subjects/`)
- The 40 subject-specific tools (refactored into `tuatha/tools/`)
- The 12-agent fleet pattern (root_agent + curriculum_agent + ...)
- The 3 educational agents (refactored into
  `tuatha/agents/educational/`)
- The 4 BIEP hackathon features (refactored into
  `tuatha/agents/hackathon/`)
- The media_intel pipeline (moved to `tuatha/agents/media_intel/`)
- The BAML extraction + DLT + Dagster + CocoIndex + marimo pipeline
  stack
- The Hono + Convex + TanStack Start + CopilotKit web stack
- The LiteLLM + Cognee + Graphiti + LanceDB + Letta memory stack
- The educational-credential badge system (the previous
  `crypteolas/` financial-token system is archived)

#### Scenario: A user opens the new `tuatha/` project for the first time

- **WHEN** the user runs `tuatha --version`
- **THEN** the project reports version `0.1.0` (the initial
  build) + the British Isles Formative Assessment MMO theme
  description
- **AND** the project does NOT contain the 3 deprecated themes
  (verified by `tuatha --audit`)
- **AND** the project references the `leabharlann` + `bonneagar`
  sibling repos via the standard cross-repo sync contract
