## ADDED Requirements

### Requirement: 8 NCCA ADK specialists as A2UI surface emitters

The system SHALL register the 8 NCCA ADK specialists at
`cianfhoghlaim/agents/tuatha/{math,chem,geog,gael,engl,comp,appm,hist}_agent.py`
as CopilotKit dispatch targets that emit A2UI operations
(`createSurface` / `updateComponents` / `updateDataModel`) when
responding to user queries. The 18 per-subject workflow handlers
(`_workflow_handlers.py::make_study_plan_handler` /
`discuss_exam_paper_handler` / `explain_marking_scheme_handler` × 6
subjects) SHALL be the dispatcher entry points.

This requirement is the canonical link between the agent fleet and
the A2UI surface generation described in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R18.

#### Scenario: A user opens a Mathematics page

- **GIVEN** the user is on `/en/subjects/mathematics/`
- **WHEN** they ask the CopilotKit sidebar for a study plan
- **THEN** `math_agent` is dispatched
- **AND** `make_study_plan_handler` invokes the BAML `WebStudyPlan`
- **AND** the agent emits an A2UI `createSurface` operation
- **AND** the client mounts the `<StudyPlanCard>` from the catalog

#### Scenario: A user asks Gaeilge agent for a past paper discussion (in Irish)

- **GIVEN** the user is on `/ga/subjects/gaeilge/`
- **WHEN** they type "déan plé ar Pháipéar 2 2024" (discuss Paper 2 2024)
- **THEN** `gael_agent` is dispatched
- **AND** `discuss_exam_paper_handler` invokes `b.WebExamPaperDiscussion(subject="gaeilge", paper_year=2024, paper_level="LC_HL", paper_language="ga", question_text="...")`
- **AND** the agent emits an A2UI `createSurface` with bilingual EN+GA labels
