# Spec Delta: centralized-model-registry

## ADDED Requirements

### Requirement: Bilingual GA↔EN cross-stage BAML extraction SHALL be added

`baml_src/british_isles/ireland/education/_cross/cross_linguistic.baml` SHALL add `ExtractBilingualLearningOutcome(en_text, ga_text) -> BilingualLearningOutcome` and `ExtractCrossLinguisticGA(ga_text) -> CrossLinguisticConcept` functions with real prompts.

**WHEN** `b.ExtractBilingualLearningOutcome(en_text=..., ga_text=...)` is called with paired LC English + Irish syllabus text
**THEN** it SHALL return `{en_lo_id, ga_lo_id, confidence, source_pairs: [(en_segment, ga_segment)]}`

#### Scenario: Bilingual pair extracted from LC English + Irish chemistry syllabus

- **WHEN** the operator runs `b.ExtractBilingualLearningOutcome(en_text=english_chem_syllabus, ga_text=irish_chem_syllabus)`
- **THEN** the function returns `{en_lo_id: "LC-CHEM-LO-023", ga_lo_id: "LC-CEM-LO-023", confidence: 0.92, source_pairs: [...]}`
- **AND** the result lands in `md:cianfhoghlaim.bilingual_los` table for downstream Graphiti episodes

### Requirement: Cross-stage cognify SHALL create 8 cross-stage edges

The `cross_stage_cognify` asset SHALL execute the 8 hand-coded `EDGE_DEFINITIONS`:
- `AistearPrinciple-BRIDGES_TO->PrimaryLearningOutcome`
- `PrimaryLearningOutcome-PREPARES_FOR->JCLearningOutcome`
- `JCLearningOutcome-PROGRESSES_TO->SCLearningOutcome`
- `SCLearningOutcome-ASSESSED_BY->ExamQuestion`
- `LCSubject-REQUIRED_FOR->CAOCourse`
- `CAOCourse-DELIVERS->Programme`
- `QQIFetAward-LADDERS_INTO->CAOCourse`
- `Apprenticeship-ALTERNATIVE_TO->CAOCourse`

**WHEN** all 5 stage cognify assets complete successfully
**THEN** cross-stage cognify SHALL iterate the 8 EDGE_DEFINITIONS and call BAML `ExtractCrossStageLink(a, b)` to score each pair
**AND** write edges to Cognee dataset `cianfhoghlaim.education.cross_stage` where the BAML score >= 0.5

#### Scenario: AistearPrinciple bridges to PrimaryLearningOutcome via BAML scoring

- **WHEN** the cross-stage cognify runs after `aistear_cognify` + `primary_cognify` complete
- **THEN** for each pair (AistearPrinciple, PrimaryLearningOutcome), `ExtractCrossStageLink(principle, lo)` returns a score
- **AND** if score >= 0.5, a `BRIDGES_TO` edge is written to the cross_stage dataset

### Requirement: Cross-qualification map SHALL be backed by Cognee

The 30 hard-coded equivalences in `meaisinfhoghlaim/alignment/cross_qualification_subject_map.py:81-120` SHALL be migrated to a Cognee dataset `british_isles_equivalences` with provenance from `baml_src/british_isles/_cross/isles_education.baml`. New equivalences SHALL be added for: Scotland Nat 5/Higher/Adv Higher (3), Wales WJEC (1), Northern Ireland CCEA (1), Jersey/Guernsey/Isle of Man (3) — total 38 equivalences.

**WHEN** `CrossJurisdictionDiffer.diff(qual_a, jur_a, qual_b, jur_b)` is called
**THEN** it SHALL query Cognee for the matching equivalence edge
**AND** return the alignment percentage + provenance link to the source BAML extraction

#### Scenario: Ireland chemistry ↔ England chemistry returns 0.80 alignment

- **WHEN** `CrossJurisdictionDiffer.diff("lc", "ireland", "gcse", "england", subject="chemistry")` is called
- **THEN** it queries the Cognee `british_isles_equivalences` dataset for the matching edge
- **AND** returns `{alignment_pct: 0.80, equivalence_id: "lc_chem_gcse_chem_01", notes: "LC is broader"}`

### Requirement: 9 cognee_ingest scripts SHALL be wired as Dagster sensors

Each of `cognee_ingest_{docs,dlt_sources,baml_schemas,skills,agent_definitions,openspec,stacks_catalog,notebooks}.py` SHALL be wrapped as a `@sensor` in `orchestration/defs/3_model_lifecycle/cognify/sensors/` watching the relevant root directory.

**WHEN** any file in `baml_src/*.baml` changes
**THEN** the `cognee_ingest_baml_schemas` sensor SHALL trigger a re-cognify into the `baml_schemas` Cognee dataset

#### Scenario: New BAML function triggers re-cognify

- **WHEN** an operator adds a new `@function` to `baml_src/british_isles/ireland/education/stages/aistear.baml`
- **THEN** the `baml_schemas_sensor` fires within 60s
- **AND** `cognee_ingest_baml_schemas.py` runs against the new schema
- **AND** the `baml_schemas` Cognee dataset is updated
