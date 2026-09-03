# Spec Delta — Agno Stage Teams (6 teams + 4 shared sub-agents)

## MODIFIED Requirements

### Requirement: Multi-Stage Agno Teams

The system SHALL provide **5 Agno `Team` instances** keyed on the 5 educational stages, each with stage-specific sub-agents, plus 4 shared sub-agents.

#### Scenario: Aistear Team
- **GIVEN** `sruth/oideachais/data_platform/agents/agno/stage_teams/aistear_team.py`
- **WHEN** `ask_aistear_team(query, language="ga")` is invoked
- **THEN** the team routes to `ThemeNavigator` for theme-discovery queries
- **AND** to `PrincipleMapper` for parent-facing principle questions
- **AND** to `NaionraFinder` (geo) for "find naíonra near me" queries
- **AND** to `ParentTipGenerator` for at-home parenting advice
- **AND** the response is bilingual (EN/GA) when language="ga"

#### Scenario: Senior Cycle Team
- **GIVEN** `sruth/oideachais/data_platform/agents/agno/stage_teams/senior_cycle_team.py`
- **WHEN** `ask_senior_cycle_team(query, subject="mathematics", year=2024)` is invoked
- **THEN** the team routes to `PaperAnalyst` for "show me the structure of 2024 Higher Maths Paper 1"
- **AND** to `MarkingSchemeDecoder` for "what are the marking criteria for Q3?"
- **AND** to `ExaminerInsights` for "what did the Chief Examiner say about Q3?"
- **AND** to `RubricJudge` for "score my essay against the rubric"
- **AND** to `ComparisonAgent` for "compare 2023 vs 2024 marking scheme"
- **AND** to `PracticeCoach` for "generate a practice question on differentiation"
- **AND** to `PointsCalculator` for "what's my CAO points for these 6 subjects"
- **AND** to `MatriculationAuditor` for "do my grades meet UCD medicine matriculation?"

#### Scenario: Tertiary Team
- **GIVEN** `sruth/oideachais/data_platform/agents/agno/stage_teams/tertiary_team.py`
- **WHEN** `ask_tertiary_team(query, pathway="cao")` is invoked
- **THEN** the team routes to `CAOCourseFinder` for "what courses can I do with my LC subjects?"
- **AND** to `QQIFETLadder` for "what PLC award ladders into Level 8?"
- **AND** to `ApprenticeshipAdvisor` for "what apprenticeships are available in software?"
- **AND** to `MatriculationCheck` for "do I meet NUI matriculation?"
- **AND** to `ApplicationTimelineGuide` for "when does CAO close?"
- **AND** to `HEIComparer` for "compare UCD vs UCC Medicine"

#### Scenario: Shared Sub-Agents
- **GIVEN** `sruth/oideachais/data_platform/agents/agno/stage_teams/_shared/`
- **WHEN** the 4 shared sub-agents are imported
- **THEN** `CurriculumScout` queries the 5 stage LanceDB tables and Cognee datasets
- **AND** `TranslationAgent` calls `litellm:4000/v1/chat/completions` with `model=irish` for EN↔GA translation
- **AND** `CogneeGraphQuery` exposes `cognee.search(query, dataset_name)` as an Agno tool
- **AND** `SourceCiter` always returns a NCCA/SEC/CAO/HEI source URL alongside every fact

#### Scenario: Compatibility Shim
- **GIVEN** the existing `agents/agno/education_team.py` (the 6-agent `Celtic Education Team`)
- **WHEN** the new stage teams are introduced
- **THEN** the existing `education_team` is replaced by a thin compatibility shim that dispatches to the 5 stage teams based on the query's detected stage
- **AND** the public API `ask_education_team(query)` still works
- **AND** `sruth/oideachais/data_platform/agent_os/config.yaml` is updated to register the 5 stage teams under the `agents:` block

## REMOVED Requirements

### Requirement: Single 6-Agent Celtic Education Team

**Reason**: The single 6-agent team is replaced by 5 stage-specific teams with stage-specific sub-agents. The single team was too coarse-grained to handle the Aistear, Primary, Junior Cycle, Senior Cycle, and Tertiary domains with the right sub-agent specialization.

**Migration**: The 6 original agents (Curriculum, Research, Translation, Corpus, Geospatial, Statistics) are re-distributed:
- `Curriculum Agent` → split into `CurriculumScout` (shared) + stage-specific `*_team.py` instances
- `Research Agent` → kept as `Research Agent` inside each stage team (or removed if not needed)
- `Translation Agent` → moved to `_shared/TranslationAgent`
- `Corpus Agent` → kept as a corpus sub-agent inside the relevant stage team (Senior Cycle for SEC examiner reports; Aistear for folklore)
- `Geospatial Agent` → moved to `_shared/CurriculumScout` and to `NaionraFinder` in the Aistear team
- `Statistics Agent` → kept as a sub-agent inside the Senior Cycle team (for grade distribution analysis)
