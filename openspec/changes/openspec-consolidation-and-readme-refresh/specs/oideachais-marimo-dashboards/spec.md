## ADDED Requirements

The `oideachais-marimo-dashboards` capability is consolidated from the
old `leabharlann-full-stack-demo` spec. The full Requirements +
Scenarios are in the canonical spec at
`openspec/specs/oideachais-marimo-dashboards/spec.md`.

### Requirement: 11 Marimo notebooks

The system SHALL provide 11 Marimo notebooks at
`oideachais/notebooks/` covering the 5 educational stages
(Aistear, Primary, JC, SC, Tertiary), the cross-domain analysis, the
ducklake explorer, the lakehouse inspector, the leabharlann
full-stack demo, and the syllabus visualiser.

#### Scenario: Notebooks render

- **WHEN** the FastAPI app starts with the Marimo mount
- **THEN** the 11 notebooks are accessible at `/dashboards/*`

### Requirement: Leabharlann full-stack demo

The system SHALL provide a Marimo notebook that visualises the
end-to-end leabharlann pipeline.

#### Scenario: Demo renders

- **WHEN** the user navigates to `/dashboards/leabharlann-full-stack-demo`
- **THEN** the notebook renders with the 5-step pipeline + DuckDB
  result table
