# `crypteolas-demo` capability spec (NEW)

The `crypteolas-demo` capability is the standalone demo app combining:

- A TanStack Start TypeScript frontend (DeFi analytics, AI chat, x402 payments)
- A Python Agno-based agent team (research, analysis, pipeline triggering)
- An MCP server exposing crypto analytics tools to Claude Code
- A Gradio UI for the FIBO/EduVision curriculum-to-image generation
- Foundry Solidity contracts (Anam Cara DAO, Cuchulainn NFT, Tuath Token)
- Two parallel Dagster code-locations: FIBO/EduVision (`defs/`) and
  Crypteolas crypto (`pipelines/defs/`)

The app is a buildable skeleton: the Python parts import cleanly and the
TypeScript parts install and typecheck, but several frontend features are
stubbed.

## ADDED Requirements

### Requirement: Package name and module name
The `crypteolas_demo` package SHALL have `name = "crypteolas_demo"` in its
`pyproject.toml` and `root_module = "crypteolas_demo"`. There SHALL be no
references to the prior `fibo` name in imports or config.

#### Scenario: import crypteolas_demo
- **WHEN** `from crypteolas_demo import CryptoResearchAgent` is executed
- **THEN** the import succeeds.

### Requirement: Public API re-export
The `crypteolas_demo/__init__.py` SHALL re-export the public surface of the
demo: the three agent classes (`CryptoResearchAgent`, `CryptoAnalysisAgent`,
`CryptoPipelineAgent`), the team factory (`create_crypto_agent_team`), the
chat convenience functions, and the MCP server exports.

#### Scenario: from crypteolas_demo import *
- **WHEN** `from crypteolas_demo import *` is executed
- **THEN** all symbols named above are available in the local namespace.

### Requirement: Flattened fibo namespace
No code in `crypteolas_demo/` SHALL import from `fibo.*`. All prior
`fibo.X.Y` imports SHALL have been rewritten to flat `X.Y` imports.

#### Scenario: grep finds no fibo imports
- **WHEN** `grep -r "from fibo" tuatha/apps/crypteolas_demo/` is run
- **THEN** no matches are found.

### Requirement: agno service dropped
The `docker-compose.yaml` SHALL NOT include an `agno` service. The prior
`build.context: "../../../.."` with `dockerfile: demo/Dockerfile.agno`
referenced a non-existent Dockerfile and has been removed.

#### Scenario: compose has no agno service
- **WHEN** `tuatha/apps/crypteolas_demo/docker-compose.yaml` is read
- **THEN** no service named `agno` is present.

### Requirement: TypeScript buildable skeleton
The `tuatha/apps/crypteolas_demo/` directory SHALL contain a `package.json`
and a `tsconfig.json` such that `bun install` and `bun run typecheck`
succeed. All `.tsx` files in `src/` SHALL resolve their imports (with
stubs permitted for the `src/lib/*` modules).

#### Scenario: bun install + typecheck
- **WHEN** `bun install && bun run typecheck` is run from
  `tuatha/apps/crypteolas_demo/`
- **THEN** the install succeeds and typecheck passes (or exits with only
  expected stub-related warnings documented in `STATUS.md`).

### Requirement: Stubbed src/lib/ modules
The 12 missing `src/lib/*` modules SHALL exist as stubs, each with a
minimal type signature and a `// TODO: implement` comment.

#### Scenario: src/lib/ exists
- **WHEN** `ls tuatha/apps/crypteolas_demo/src/lib/` is run
- **THEN** the 12 stub files are present:
  `auth/{client,server}.ts`, `x402/{middleware,payment-service,pricing,networks,provider}.ts`,
  `copilot/runtime.ts`, `query/{client,hooks}.ts`, `web3.ts`, `mcp/copilot-actions.ts`.

### Requirement: Stubbed models/ package
The `tuatha/apps/crypteolas_demo/models/` directory SHALL exist with stub
implementations of `colpali`, `qwen_vlm`, and `fibo_mlx` that raise
`NotImplementedError` at runtime.

#### Scenario: models importable
- **WHEN** `from crypteolas_demo.models import ColPaliEmbedder` is executed
- **THEN** the import succeeds (the `NotImplementedError` is only raised on
  method call, not on import).

### Requirement: Dagster integration
The `crypteolas_demo` Dagster code-location SHALL be registered in the
tuatha workspace.

#### Scenario: dagster dev shows crypteolas_demo
- **WHEN** `dagster dev` is started with the tuatha workspace
- **THEN** the `crypteolas_demo` code-location is listed in the UI alongside
  `tuath` and `crypteolas`.

### Requirement: BAML isolation
The `crypteolas_demo/scéimre/generators.baml` `output_dir` SHALL be set to
`./baml_client` so the demo's BAML generation is isolated from the main
`tuatha/baml_client/`.

#### Scenario: baml_client isolation
- **WHEN** `baml-cli generate` is run from `tuatha/apps/crypteolas_demo/scéimre/`
- **THEN** the generated `baml_client/` appears at
  `tuatha/apps/crypteolas_demo/baml_client/`, not at `tuatha/baml_client/`.
