## ADDED Requirements

### Requirement: LC5 + Gemini consumers of the 3 memory backends

The 3 memory backends (Cognee + Graphiti + FalkorDB) SHALL have
**11 Cognee datasets + 11 Graphiti streams + 2 FalkorDB labels** as
a result of the LC5 + Gemini pipelines introduced in
2026-07-03.

#### Scenario: The 5 LC Cognee datasets exist after LC5 pipeline materialises

- **WHEN** `dagster asset materialize --select 'lc5_*_cognified'`
- **THEN** `oideachais_chemistry`, `oideachais_computer_science`, `oideachais_gaeilge`, `oideachais_geography`, `oideachais_mathematics` SHALL all exist

#### Scenario: The 6 Gemini Cognee datasets exist after Gemini pipeline materialises

- **WHEN** `dagster asset materialize --select 'gemini_*_cognified'`
- **THEN** 6 datasets SHALL exist: `gemini_law_research, gemini_medical_research, gemini_politics_research, gemini_culture_research, gemini_technology_research, gemini_other_research`

#### Scenario: The Gemini Graphiti episodes have event_time from PDF prose, NOT mtime

- **GIVEN** a Gemini law PDF with a section `// the incident occurred on 2023-05-15`
- **WHEN** `gemini_cross_corpus_graphiti_stream` adds an episode
- **THEN** the episode's `event_time` SHALL be `2023-05-15` (from BAML TimelineEvent extraction)
- **AND** the file mtime SHALL NOT influence `event_time`

#### Scenario: The 2 FalkorDB labels connect 11 datasets

- **WHEN** the LC5 + Gemini cognify runs to completion
- **THEN** `falkordb_label="lc5_knowledge_graph"` SHALL be queryable with Subject → Topic → LO → Year → Q edges
- **AND** `falkordb_label="gemini_6_corpus_kg"` SHALL be queryable with Corpus → CaseProfile → Party → Jurisdiction edges
