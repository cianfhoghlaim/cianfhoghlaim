## ADDED Requirements

### Requirement: 8 active Spaces + 1 archived Space + 1 canonical exception

The `spaces/` directory SHALL expose 8 active HuggingFace
Spaces (4 production + 4 new demos), 1 archived Space, and
1 canonical exception. The 4 production Spaces are the
Celtic AI demo suite:

1. `an_scrudu/` (An Scrúdú) — gradio 5.x, oideachais (Earth),
   past-paper heatmap + PCLM-XML/PDF download
2. `meaisin_cliste/` (Meaisín Cliste) — gradio 5.x,
   meaisinfhoghlaim (Water + Air), 3 Celtic AI tools
3. `cianfhoghlaim/` (RPG) — gradio 5.x, tuatha (Air + Spirit),
   Hades-style dialogue with 6 Celtic NPCs
4. `anam_sruth/tuatha/` (Anam) — gradio 5.x, croilar (5 elements),
   5 elements + 2 cross-cutting features = 7 panels

The 4 new demo Spaces (the 2026-06-24 batch):

5. `croilar_portfolio_demo/` — gradio 5.x, croilar, demo
   of the 3-persona portfolio site
6. `oideachais_mission_control/` — gradio 5.x, oideachais,
   mission-control dashboard for the lakehouse
7. `crypteolas_defi_monitor/` — gradio 5.x, crypteolas,
   DeFi monitor
8. `tuatha_mmo_demo/` — gradio 5.x, tuatha, demo of the
   British Isles formative assessment MMO

The 1 archived Space:

- `anti-phish/` — archived to `archive/anti-phish-2022-academic/`
  (2022 personal academic project)

The 1 canonical exception:

- `data-engineering/` — the only non-gradio Space (dagster
  + dbt + evidence); consumes `sruth/oideachais/agents/adk/` +
  `sruth/oideachais/baml_src/` directly, not the LiteLLM gateway

Each active Space SHALL have the canonical 4-file structure:

- `app.py` — the Gradio app
- `requirements.txt` — the Gradio + BAML dependencies
- `README.md` — the HF Space README
- `AGENTS.md` — the developer quick reference

#### Scenario: A new Space follows the canonical 4-file structure

- **WHEN** a developer adds a new Space to `spaces/`
- **THEN** the 4 required files SHALL be present
  (`app.py` + `requirements.txt` + `README.md` + `AGENTS.md`)
- **AND** the `app.py` SHALL import from the canonical
  `_common/` bundle (`from spaces._common import ...`)
- **AND** the Space SHALL be added to the `spaces/AGENTS.md`
  active Spaces table

### Requirement: data-engineering quarantine

The `spaces/data-engineering/` Space SHALL be the canonical
exception to the "all Spaces are gradio 5.x" rule. It uses
the dagster + dbt + evidence stack (not gradio) and lives
in `spaces/` for historical reasons (it was the first
Space-like artefact in the monorepo, before the Celtic AI
demo suite was built).

The `data-engineering/` Space SHALL consume
`sruth/oideachais/agents/adk/` + `sruth/oideachais/baml_src/` directly
(not the LiteLLM gateway) because it is a data plane (not
a user-facing demo). The `_common/` bundle SHALL NOT be
imported by the `data-engineering/` Space (the 5-element
palette + the i18n toggle + the Anam Bonneagar footer are
not applicable to a data plane).

#### Scenario: The data-engineering Space does not import _common

- **WHEN** the `data-engineering/` Space boots
- **THEN** no `from spaces._common import ...` import SHALL
  be present in `data-engineering/app.py` (or the equivalent
  entry point)
- **AND** the Space SHALL consume `sruth/oideachais/agents/adk/`
  + `sruth/oideachais/baml_src/` directly via the canonical
  Dagster + BAML patterns
- **AND** the Space SHALL be documented as the canonical
  exception in `spaces/AGENTS.md`
