# Spec Delta — infrastructure-stacks

## ADDED Requirements

### Requirement: 33 User-Selected Selfhosted Stacks (v4)

The system SHALL expose the 33 user-selected selfhosted stacks at `cianfhoghlaim/stacks/{backrest,browser,cognee,dagster,docling-serve,dots-ocr,dragonfly,falkordb,garage,graphiti,infisical,invokeai,komodo,lakehouse,lancedb,langfuse,litellm,logfire,marimo,memgraph,mlflow,mlx-omni,motherduck,nimtable,olake,olmocr,openchamber,openclaw,paddleocr,pangolin,planetscale,r2,risingwave}/`. The remaining 57 stacks remain at `infrastructure/stacks/` for archival.

#### Scenario: Stack discoverability

- **WHEN** a developer asks "where is the dagster stack?"
- **THEN** `ls cianfhoghlaim/stacks/dagster/` returns the 6-file GOLD_STANDARD pattern (`compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `README.md`)
- **AND** the stack file path is documented in `cianfhoghlaim/stacks/STACKS_INDEX.md` (NEW)

### Requirement: No Workspace Stack Re-addition (v4)

The system SHALL NOT re-add any of the previously deleted stacks (`blinko`, `croilar-convex`, `croilar-dagster`, `croilar-hono-api`, `croilar-marimo`, `croilar-postgres`, `croilar-web`, `DevDocs`, `DnsServer`, `mathesar`, `MCPJungle`, `monitoring`, `networking-toolbox`, `Perplexica`, `presenton`, `Termix`) to `cianfhoghlaim/stacks/` unless explicitly approved via a new openspec change.

#### Scenario: Validation

- **WHEN** `bun run validate-stacks` runs
- **THEN** the 33 user-selected stacks validate
- **AND** the 57 archived stacks at `infrastructure/stacks/` are skipped (marked `archived: true` in `STACKS_INDEX.md`)