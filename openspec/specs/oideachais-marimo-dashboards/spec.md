# Oideachais Marimo Dashboards Capability

## Purpose

`oideachais-marimo-dashboards` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`oideachais/notebooks/` and `oideachais/notebooks/dashboards/`. See
`docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for
the project identity.

This spec was consolidated from the 51-line
`leabharlann-full-stack-demo` spec and now covers the full Marimo
notebook surface.

## Background

Marimo reactive Python notebooks for the oideachais lakehouse. The
notebooks are served as dashboards (mounted at `/dashboards/*` on the
FastAPI app) and cover the 5 educational stages (Aistear, Primary,
Junior Cycle, Senior Cycle, Tertiary), the cross-domain analysis, the
ducklake explorer, the lakehouse inspector, and the leabharlann
full-stack demo.

## Requirements

### Requirement: 5-stage education dashboards

The system SHALL provide Marimo notebooks for each of the 5 educational
stages (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary).

#### Scenario: Aistear dashboard renders

- **GIVEN** the `oideachais/notebooks/dashboards/aistear.py` notebook
- **WHEN** the user navigates to `/dashboards/aistear`
- **THEN** the notebook renders with the Aistear theme data from
  DuckLake

### Requirement: Leabharlann full-stack demo

The system SHALL provide a Marimo notebook that visualises the
end-to-end leabharlann pipeline (1 UoG + 1 Zotero sample PDF →
BAML extraction → CocoIndex update → LanceDB insert → Cognee add →
DuckDB metadata write).

#### Scenario: Full-stack demo renders

- **GIVEN** the `oideachais/notebooks/dashboards/leabharlann_full_stack_demo.py`
  notebook
- **WHEN** the user navigates to `/dashboards/leabharlann-full-stack-demo`
- **THEN** the notebook renders with the 5-step pipeline visualisation
  + the DuckDB result table for the last demo run

### Requirement: Cross-domain + lakehouse + ducklake dashboards

The system SHALL provide cross-domain, lakehouse, and ducklake
explorer notebooks.

#### Scenario: DuckLake explorer renders

- **GIVEN** the `oideachais/notebooks/ducklake_explorer.py` notebook
- **WHEN** the user navigates to `/dashboards/ducklake`
- **THEN** the notebook renders with the table list from DuckLake
  and an interactive SQL query interface

## Cross-references

- [`oideachais/notebooks/`](../../oideachais/notebooks/) (the 11 Marimo notebooks)
- [`oideachais/notebooks/dashboards/`](../../oideachais/notebooks/dashboards/) (the dashboard subdir)
- [`.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md)
- [`.agents/skills/build-notebook/SKILL.md`](../../.agents/skills/build-notebook/SKILL.md)
- [`openspec/specs/oideachais-leabharlann/spec.md`](oideachais-leabharlann/spec.md) (the upstream pipeline)
