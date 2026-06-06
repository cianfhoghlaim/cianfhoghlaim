# Spec Delta — Stage-Specific Marimo Notebooks (5 new + 9 existing kept)

## ADDED Requirements

### Requirement: 5 Stage-Specific Notebooks
The system SHALL provide 5 new marimo notebooks in `oideachais/notebooks/dashboards/`, one per educational stage, generated from `analysis_plan.md` files via the `explore-data` + `build-notebook` skill flow.

#### Scenario: Aistear Notebook
- **GIVEN** `oideachais/notebooks/analysis_plan/aistear.md`
- **WHEN** the `build-notebook` skill is invoked against the plan
- **THEN** the notebook `oideachais/notebooks/dashboards/aistear.py` is generated
- **AND** it answers questions like:
  - "What is the distribution of Aistear learning goals across the 4 themes?"
  - "How many naíonra exist per county?"
  - "What percentage of Aistear learning goals have been bridged to Primary Stage 1 outcomes?"

#### Scenario: Primary Notebook
- **GIVEN** `oideachais/notebooks/analysis_plan/primary.md`
- **WHEN** the `build-notebook` skill is invoked
- **THEN** the notebook `oideachais/notebooks/dashboards/primary.py` is generated
- **AND** it answers questions about Primary strand distribution, Stage 1→4 progression, language-medium uptake, etc.

#### Scenario: Junior Cycle Notebook
- **GIVEN** `oideachais/notebooks/analysis_plan/junior_cycle.md`
- **WHEN** the `build-notebook` skill is invoked
- **THEN** the notebook `oideachais/notebooks/dashboards/junior_cycle.py` is generated
- **AND** it answers questions about JC grade distribution, CBA completion, short course uptake

#### Scenario: Senior Cycle Notebook
- **GIVEN** `oideachais/notebooks/analysis_plan/senior_cycle.md`
- **WHEN** the `build-notebook` skill is invoked
- **THEN** the notebook `oideachais/notebooks/dashboards/senior_cycle.py` is generated
- **AND** it answers questions about LC grade distribution, marking scheme drift, subject difficulty trends

#### Scenario: Tertiary Notebook
- **GIVEN** `oideachais/notebooks/analysis_plan/tertiary.md`
- **WHEN** the `build-notebook` skill is invoked
- **THEN** the notebook `oideachais/notebooks/dashboards/tertiary.py` is generated
- **AND** it answers questions about CAO points trends, NUI matriculation, QQI laddering, Apprenticeship uptake

### Requirement: Existing Notebooks Preserved
The system SHALL preserve all 9 existing marimo notebooks.

#### Scenario: 9 Existing Notebooks Unchanged
- **GIVEN** the existing 9 marimo notebooks in `oideachais/notebooks/`
- **WHEN** the implementation of this change is complete
- **THEN** the 9 notebooks continue to work:
  - `mission_control.py`
  - `lakehouse_inspector.py`
  - `pdf_download_dashboard.py`
  - `pipeline_e2e_test.py`
  - `ducklake_explorer.py`
  - `curriculum_educator.py`
  - `exam_papers_explorer.py`
  - `marking_scheme_analyzer.py`
  - `syllabus_visualizer.py`
- **AND** the 5 new notebooks are added alongside, not replacing

### Requirement: Notebook Mounting
The system SHALL mount each notebook at `/dashboards/$stage` (file-based routes in both EN and GA).

#### Scenario: Dashboard Route per Stage
- **GIVEN** a user navigates to `/en/dashboards/senior_cycle`
- **WHEN** the page loads
- **THEN** the SPA renders the marimo notebook for the Senior Cycle dashboard
- **AND** the `/ga/dashboards/scoil-daraigh` mirror is the Irish-language equivalent
