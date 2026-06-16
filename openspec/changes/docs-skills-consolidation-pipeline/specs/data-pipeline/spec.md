## ADDED Requirements

### Requirement: Docs-Skills Consolidation Asset Group
The system SHALL expose a `docs_skills` asset group in the Dagster UI that wraps the `docs_skills_consolidation` CocoIndex v1 App and its child targets.

#### Scenario: Asset group registration
- **GIVEN** the `oideachais/dagster_defs/assets/docs_skills_assets.py` module
- **WHEN** the Dagster definitions are loaded
- **THEN** the following assets SHALL be registered in the `docs_skills` group:

| Asset | Type | Wraps |
|---|---|---|
| `docs_skills_manifest` | `@asset` | SHA256 of every file under `docs/` and `.agents/skills/` |
| `docs_skills_chunk_and_tag` | `@asset` | `cocoindex update oideachais/cocoindex_flows/docs_skills_consolidation.py` (batch) |
| `docs_skills_graph_publish` | `@asset` (with `asset_check`) | Verifies FalkorDB node/edge counts ≥ 1 and reports the number of files that failed BAML extraction |
| `docs_skills_live` | `@asset` (sensor-launched) | `cocoindex update -L` — long-running |
| `codebase_chunk_and_embed` | `@asset` | `cocoindex update oideachais/cocoindex_flows/codebase_indexing.py` (batch) |
| `codebase_live` | `@asset` (sensor-launched) | `cocoindex update -L` for the codebase index |

- **AND** all six assets SHALL be added to `oideachais/dagster_defs/definitions.py`'s `combined_assets` list

#### Scenario: Asset check enforces downstream readiness
- **GIVEN** the `docs_skills_graph_publish` asset check
- **WHEN** it runs after a materialisation
- **THEN** it SHALL pass only if (a) the FalkorDB graph has ≥ 1 `DocSkill` node per materialised file, AND (b) the failed-BAML count is 0
- **AND** it SHALL surface a `WARNING`-severity check result (not a hard `FAIL`) when the failed-BAML count is > 0, so downstream assets can still proceed

#### Scenario: Live-mode sensor
- **GIVEN** the `docs_skills_live` asset is registered
- **WHEN** the Dagster sensor observes a change in `docs_skills_manifest`
- **THEN** it SHALL launch `docs_skills_live` as a long-running job
- **AND** the sensor SHALL poll the manifest hash at most once per 30 seconds
