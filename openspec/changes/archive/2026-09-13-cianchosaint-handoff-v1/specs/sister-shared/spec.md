## ADDED Requirements

### Requirement: Shared-1 — 4-tier ModelProviderRouter pattern is the shared BAML contract
Every sister repo's `baml_src/clients.baml` MUST declare exactly 3 named clients (`Primary`, `Fallback`, `Emergency`) routed through a `baml_src/_shared/provider_router.py` module (or a sister-local equivalent) that implements the 4-tier fallback chain (Unsloth Studio primary → LiteLLM → MiniMax Token Plan → Gemini API) per the `centralized-model-registry` spec.

#### Scenario: Cianchosaint satisfies Shared-1
- **WHEN** an agent inspects `/Users/cianmacandeisigh/dev/cianchosaint/baml_src/clients.baml`
- **THEN** the system SHALL find 3 named clients (`Primary` = Unsloth Studio, `Fallback` = LiteLLM, `Emergency` = MiniMax Token Plan)
- **AND** the system SHALL find `/Users/cianmacandeisigh/dev/cianchosaint/baml_src/_shared/provider_router.py` + `provider_router_config.yaml` as the routing module

#### Scenario: Cianfhoghlaim currently lacks `_shared/provider_router.py`
- **WHEN** an agent inspects `/Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src/_shared/`
- **THEN** the system SHALL find only `templates/` (the cianfhoghlaim `_shared/` is sparse)
- **AND** the system SHALL record this as a **gap** to close before archive (follow-up openspec change `2026-09-XX-shared-provider-router-bridge-v1`)

#### Scenario: The 4-tier fallback chain is documented in clients.baml
- **WHEN** an agent grep's `baml_src/clients.baml` for `provider "openai-generic"`
- **THEN** the system SHALL find exactly 3 declarations (Primary, Fallback, Emergency)
- **AND** the system SHALL find no legacy named clients like `Default`, `LocalVisionGemma4`, etc. (those are cianfhoghlaim-specific to the OCR/VLM ensemble and stay in cianfhoghlaim only)

### Requirement: Shared-2 — `jurisdiction_pipeline_base.py` is the shared DLT scaffold
Every sister repo MUST carry a wholesale copy of `jurisdiction_pipeline_base.py` from cianfhoghlaim's canonical location `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py`, with sister-local cohort extensions appended (one per jurisdiction the sister owns).

#### Scenario: Cianfhoghlaim is the canonical source
- **WHEN** an agent inspects `/Users/cianmacandeisigh/dev/cianfhoghlaim/dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py`
- **THEN** the system SHALL find the canonical 34-line `JurisdictionPipelineBase` class
- **AND** the system SHALL record that cianfhoghlaim's `dlt_sources/british_isles/_cross/` is the source-of-truth (NOT `dlt_sources/_cross/` which does not exist)

#### Scenario: Cianchosaint carries the wholesale copy with cohort extensions
- **WHEN** an agent diffs `cianfhoghlaim/dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py` against `cianchosaint/dlt_sources/_cross/jurisdiction_pipeline_base.py`
- **THEN** the system SHALL find a non-empty diff (the cianchosaint version is 60 lines vs cianfhoghlaim's 34 — the 26 extra lines are cohort extensions)
- **AND** the system SHALL find 8 `_factory.py` files under `cianchosaint/dlt_sources/law_enforcement/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland}` importing `JurisdictionPipelineBase`

#### Scenario: Ciancheiltis carries the wholesale copy
- **WHEN** an agent lists `~/dev/ciancheiltis/dlt_sources/_cross/`
- **THEN** the system SHALL find `jurisdiction_pipeline_base.py`
- **AND** the system SHALL record that ciancheiltis adds `_shared/` + `cultural_heritage/` + `language/` + `lexicographic/` cohorts

#### Scenario: Ciandlithe carries the wholesale copy
- **WHEN** an agent lists `ciandlithe/dlt_sources/_cross/`
- **THEN** the system SHALL find `jurisdiction_pipeline_base.py` + `5_stage_registry.py` + `5_stage_runner.py` + `connection.py` + `legal_registry.py` + `registry_api.py` + `registry_loader.py`
- **AND** the system SHALL record that ciandlithe adds `_cross/registry_*` cohort extensions

### Requirement: Shared-3 — `cocoindex_flows/_shared/` carries the canonical 7 modules
Every sister repo's `cocoindex_flows/_shared/` MUST carry a wholesale copy of the 7 canonical cianfhoghlaim modules (`_lifespan.py`, `cli.py`, `cocoindex_query_api.py`, `languages.py`, `repo_embedding.py`, `repo_type_detector.py`, `reranker.py`). A sister repo MAY add Celtic-language extras (`caighdean_standardize.py`) ONLY if it ingests Celtic-language content.

#### Scenario: Cianfhoghlaim carries all 7 + the Celtic extra
- **WHEN** an agent lists `cianfhoghlaim/cocoindex_flows/_shared/`
- **THEN** the system SHALL find 7 canonical modules + `caighdean_standardize.py` (8 total)

#### Scenario: Cianchosaint carries the 6 canonical modules (correctly omits caighdean)
- **WHEN** an agent lists `cianchosaint/cocoindex_flows/_shared/`
- **THEN** the system SHALL find exactly 6 canonical modules (`_lifespan.py`, `cli.py`, `cocoindex_query_api.py`, `languages.py`, `repo_embedding.py`, `repo_type_detector.py`, `reranker.py` — note `__init__.py` is also present so that's 7 files but 6 canonical + __init__)
- **AND** the system SHALL NOT find `caighdean_standardize.py` (cianchosaint does not ingest Celtic-language content)

#### Scenario: Ciancheiltis and ciandlithe inherit via the wholesale-copy pattern
- **WHEN** an agent lists `ciandlithe/cocoindex_flows/_shared/` or `~/dev/ciancheiltis/cocoindex_flows/_shared/`
- **THEN** the system SHALL find the 7 canonical modules in ciandlithe (per the verified inventory)
- **AND** the system SHALL record that ciancheiltis does not ship its own `cocoindex_flows/` directory at all (verified: `ls ~/dev/ciancheiltis/cocoindex_flows` returns `No such file or directory`); ciancheiltis inherits the canonical flows from cianfhoghlaim's `cocoindex_flows/british_isles/uk/ciancheiltis_*` per Canonical-2

### Requirement: Shared-4 — OpenSpec 6-file change bundle convention is the shared documentation contract
Every sister repo MUST have `openspec/AGENTS.md` + `openspec/changes/` + `openspec/specs/` matching the cianfhoghlaim convention (proposal.md + tasks.md + spec deltas + cross-repo-sync.md when ≥2 repos affected + per-spec AGENTS.md for new specs).

#### Scenario: Cianfhoghlaim is the canonical openspec surface
- **WHEN** an agent lists `openspec/{changes,changes/archive,specs}/`
- **THEN** the system SHALL expose 38 pending changes + 346 archived changes + 102 specs
- **AND** the system SHALL keep the 336-line `openspec/AGENTS.md` as the canonical convention

#### Scenario: Cianchosaint has its own openspec
- **WHEN** an agent lists `cianchosaint/openspec/{changes,changes/archive,specs}/`
- **THEN** the system SHALL find 13 changes + 24 archived + 33 specs
- **AND** the system SHALL find `cianchosaint/openspec/AGENTS.md` + a TRL compliance section (per the HMGCC reference)

#### Scenario: Each sister repo's openspec matches the 6-file change-bundle convention
- **WHEN** an agent enumerates any `openspec/changes/<id>/` in any sister repo
- **THEN** the system SHALL find at minimum `proposal.md` + `tasks.md`
- **AND** for cross-repo changes the system SHALL find `cross-repo-sync.md`
- **AND** for spec-introducing changes the system SHALL find `specs/<spec-name>/spec.md` with `## ADDED Requirements` (or `MODIFIED`/`REMOVED`)

### Requirement: Shared-5 — Bonneagar 6-file GOLD_STANDARD pattern is the shared IaC contract
Every sister repo that ships its own IaC MUST carry the canonical 6-file GOLD_STANDARD pattern (`compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`) per the `infrastructure-stacks` spec.

#### Scenario: Cianfhoghlaim `bonneagar/stacks/litellm/` carries all 6
- **WHEN** an agent lists `cianfhoghlaim/bonneagar/stacks/litellm/`
- **THEN** the system SHALL find `README.md` + `blueprint.yaml` + `compose.dev.yaml` + `compose.yaml` + `pangolin.yaml` + `secrets.env` + `sidecar.yaml` + `config/`

#### Scenario: Cianchosaint `bonneagar/stacks/litellm/` carries all 6 (wholesale-copied)
- **WHEN** an agent lists `cianchosaint/bonneagar/stacks/litellm/`
- **THEN** the system SHALL find all 6 GOLD_STANDARD files
- **AND** the system SHALL find a `# CIANCHOSAINT wholesale-copy of cianfhoghlaim/cianfhoghlaim @ main branch. Migrated to cianchosaint: 2026-08-23` header in `config/config.yaml`

#### Scenario: Ciandlithe `bonneagar/stacks/` carries a subset of the 95 stacks
- **WHEN** an agent lists `ciandlithe/bonneagar/stacks/`
- **THEN** the system SHALL find a subset of the canonical 95 stacks (only the ones ciandlithe actually uses — visual/digital-art + coroner/health/legal slice)
- **AND** the system SHALL NOT duplicate stacks that exist only in cianfhoghlaim (no `oideachais` stack, no `dagster` stack, no `lakehouse` stack in ciandlithe)