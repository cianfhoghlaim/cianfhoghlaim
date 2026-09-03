# spaces-cicd-pipeline Specification

## Purpose

`spaces-cicd-pipeline` is a capability of the Cianfhoghlaim platform.
It is the **reusable Hugging Face Space sync workflow** — a single GitHub
Actions workflow at `infrastructure/ci/spaces-sync.yml` that any Space
under `spaces/<name>/` can call via `uses: ./infrastructure/ci/spaces-sync.yml`
to publish the Space to Hugging Face.

The workflow supports all 3 Space SDKs (gradio + docker + static) and
handles auth via the `HF_TOKEN` + `SPACE_TOKEN` secrets. The reusable
workflow is the canonical alternative to per-Space YAMLs (~15 spaces ×
~50 LOC each → 1 shared workflow).

The corresponding source code lives at `infrastructure/ci/spaces-sync.yml`.
## Requirements
### Requirement: Reusable Spaces sync workflow
The system SHALL provide a reusable GitHub Actions workflow at
`infrastructure/ci/spaces-sync.yml` that any Space can call via a single
`uses: ./infrastructure/ci/spaces-sync.yml` reference to publish a directory
to a Hugging Face Space.

#### Scenario: Gradio Space sync
- **GIVEN** a Space at `spaces/my_space/` with `sdk: gradio` in its `README.md` frontmatter
- **AND** `HF_TOKEN` and `HF_USERNAME` are configured as repo secrets/vars
- **WHEN** a push to `main` modifies any file under `spaces/my_space/`
- **THEN** the workflow SHALL install dependencies from
  `spaces/my_space/requirements.txt`
- **AND** SHALL upload the directory to
  `huggingface.co/spaces/$HF_USERNAME/my_space` via the `huggingface_hub` Python API
- **AND** the HF Space SHALL rebuild and become live within 90 seconds

#### Scenario: Static dashboard sync (subtree push)
- **GIVEN** a Space at `spaces/my_space/` with a `dashboard/` subdir
- **AND** the `static_space` input is set to a HF Space slug
- **WHEN** a push to `main` modifies any file under `spaces/my_space/dashboard/`
- **THEN** the workflow SHALL run
  `git subtree split --prefix spaces/my_space/dashboard main`
- **AND** SHALL force-push the resulting commit to
  `huggingface.co/spaces/$HF_USERNAME/$static_space`

#### Scenario: Workflow is path-filtered
- **GIVEN** the workflow is configured for `spaces/an_scrudu/`
- **WHEN** a commit touches only `spaces/anam_cianfhoghlaim/`
- **THEN** the workflow SHALL NOT trigger for the an_scrudu Space

#### Scenario: Failure surfaces a readable error
- **GIVEN** the HF token is missing or expired
- **WHEN** the workflow runs
- **THEN** the workflow SHALL fail with exit code 1
- **AND** the error message SHALL include the resolved `HF_USERNAME` and the
  target Space slug

#### Scenario: Docker SDK support (deferred to follow-up)
- **GIVEN** a Space at `spaces/my_space/` with a `Dockerfile`
- **WHEN** a push to `main` modifies any file under `spaces/my_space/`
- **THEN** the workflow SHALL `docker build` the Space
- **AND** SHALL push the image to `huggingface.co/spaces/$HF_USERNAME/my_space`
  via the HF Docker registry
- **NOTE** This scenario is documented but the implementation is deferred to
  the follow-up commit that adds `infrastructure/ci/test_spaces_sync.py`.

### Requirement: an_scrudu Pydantic schema validation

The `an_scrudu` Space MUST validate every LLM response against the Pydantic schema (PCircularExtraction) before returning the extraction to the UI. The validation MUST accept both the nested BAML shape (post-A1) and the flat legacy shape (pre-A1) for backward compatibility. The Space MUST add `pydantic>=2.5` to `spaces/an_scrudu/requirements.txt`.

#### Scenario: Schema validation fails

- **WHEN** the LLM response does not match the Pydantic schema
- **THEN** the Space logs a warning and falls back to the flat schema
- **AND** the heatmap still renders (the UI is never broken)

### Requirement: cianfhoghlaim Pydantic schema validation

The `cianfhoghlaim` Space MUST validate every LLM response against the Pydantic schema (PNpcDialogue) before returning the dialogue to the UI. The Space MUST add `pydantic>=2.5` to `spaces/cianfhoghlaim/requirements.txt`.

#### Scenario: Pydantic validation fails

- **WHEN** the LLM response does not match the Pydantic schema
- **THEN** the Space logs a warning and falls back to the flat schema
- **AND** the dialogue still renders (the UI is never broken)

### Requirement: anam_tuatha Pydantic schema validation

The `anam_tuatha` Space MUST validate every LLM response against the Pydantic schema (PExitCardSet) before returning the exit card to the UI. The Space MUST add `pydantic>=2.5` to `spaces/anam_cianfhoghlaim/requirements.txt`.

#### Scenario: Pydantic validation fails

- **WHEN** the LLM response does not match the Pydantic schema
- **THEN** the Space logs a warning and falls back to the template bank
- **AND** the exit card still renders (the UI is never broken)

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
4. `anam_cianfhoghlaim/` (Anam) — gradio 5.x, croilar (5 elements),
   5 elements + 2 cross-cutting features = 7 panels

The 4 new demo Spaces (the 2026-06-24 batch):

5. `croilar_portfolio_demo/` — gradio 5.x, croilar, demo
   of the 3-persona portfolio site
6. `cianfhoghlaim_mission_control/` — gradio 5.x, oideachais,
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
  + dbt + evidence); consumes `cianfhoghlaim/agents/adk/` +
  `cianfhoghlaim/baml_src/` directly, not the LiteLLM gateway

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
`cianfhoghlaim/agents/adk/` + `cianfhoghlaim/baml_src/` directly
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
- **AND** the Space SHALL consume `cianfhoghlaim/agents/adk/`
  + `cianfhoghlaim/baml_src/` directly via the canonical
  Dagster + BAML patterns
- **AND** the Space SHALL be documented as the canonical
  exception in `spaces/AGENTS.md`

