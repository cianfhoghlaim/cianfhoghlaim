---
title: "Monorepo Strategy — Polyglot Toolchain & Workspace Topology"
domain: architecture
status: stable
description: "Complete bun + uv + turbo polyglot monorepo strategy covering workspace topology, mise toolchain, Dagger CI/CD, and monorepo task orchestration"
supersedes:
  - docs/bonneagar/monorepo-best-practices-2025.md
  - docs/bonneagar/Monorepo Toolchain_ Mise, Dagger, Taskipy.md
  - docs/bonneagar/Enhancing Monorepo Ansible Workflow.md
  - docs/bonneagar/.!31103!monorepo-best-practices-2025.md
  - docs/bonneagar/integrating-dagger-polyglot-monorepo-ci-cd-workflow.md
  - docs/bonneagar/DAGGER_GUIDE_INDEX.md
  - docs/bonneagar/DAGGER_PATTERNS_ANALYSIS.md
  - docs/bonneagar/DAGGER_QUICK_REFERENCE.md
  - docs/bonneagar/dagger-docker-compose-workflow-komodo-periphery-pangolin-newt-olm.md
  - docs/bonneagar/dagger-implementation-checklist.md
  - docs/bonneagar/dagger-pipeline-orchestration-komodo-pangolin-fullstack-deployment.md
  - docs/bonneagar/dagger-unified-pipeline-architecture.md
  - docs/bonneagar/development-tools.md
  - docs/bonneagar/infrastructure-tools.md
  - docs/bonneagar/Enhancing Monorepo Ansible Workflow.md
entities:
  - Monorepo
  - MiseEnPlace
  - Dagger
  - BunWorkspaces
  - UvWorkspaces
  - Turbo
related_skills:
  - .agents/skills/dagger/SKILL.md
  - .agents/skills/ccc/SKILL.md
ccc_query_hints:
  - "monorepo workspace topology"
  - "bun uv turbo polyglot"
  - "mise toolchain configuration"
  - "dagger ci/cd pipeline"
  - "how to run tasks across monorepo"
  - "polyglot build system"
last_reviewed: 2026-06-06
truth: partial

---

# Monorepo Strategy — Polyglot Toolchain & Workspace Topology

Cianfhoghlaim is a **bun + uv + turbo polyglot monorepo**. Two language graphs live side by side, orchestrated by `turbo.json` and a single `mise.toml` toolchain.

## Workspace Topology

### TypeScript Graph (bun workspaces)

The root `package.json` declares these `workspaces`:

| Workspace | Path | Purpose |
|:--|:--|:--|
| `oideachais-web` | `oideachais/web/` | TanStack Start + React front-end (the public web app) |
| `oideachais-mcp-filesystem` | `oideachais/mcp/filesystem/` | Filesystem MCP server for the data platform |
| `tuatha-ui` | `tuatha/ui/` | Túatha educational MMO front-end |

The root `package.json` only orchestrates: setup, turbo passthroughs, secret management, dagster, komodo/pangolin/locket glue, ccc indexing, and OpenSpec.

### Python Graph (uv workspaces)

The root `pyproject.toml` is a uv-workspace **shell** (no dependencies, no console scripts):

| Member | Path | Purpose |
|:--|:--|:--|
| `oideachais` | `oideachais/` | Celtic education data platform (Dagster, DLT, LanceDB) |
| `tuath` | `tuatha/` | Educational MMO + crypto platform (Babylon.js, siwe, x402) |
| `códeolas` | `códeolas/` | Code intelligence library (publishable) |
| `sruth-browser` | `infrastructure/browser/` | Browser automation client (Stagehand, MCP) |
| `mcpo` | `oideachais/mcp/mcpo/` | MCPO bridge (optional) |

Members import each other via `[tool.uv.sources]`.

## The mise Toolchain

`mise.toml` defines the polyglot toolchain and developer task aliases:

```toml
[tools]
python = "3.12"
uv = "latest"
bun = "latest"
dagger = "latest"

[settings]
experimental_monorepo_root = true
python.uv_venv_auto = true

[env]
MISE_ENV = "development"

[tasks.dev]
description = "Run local dev servers in parallel"
run = "mise run //...:dev"

[tasks.test]
description = "Run tests locally"
run = "mise run //...:test"

[tasks.ci]
description = "Run hermetic CI pipeline via Dagger"
run = "dagger call test"
```

### Why mise over Taskipy

| Feature | Mise-en-place | Taskipy |
|---------|--------------|---------|
| **Scope** | Environment & Task Runner | Command Alias (Python) |
| **Language Support** | Universal / Polyglot | Python-Centric |
| **Execution Context** | Host Machine | Subprocess |
| **Dependency Graph** | Yes (DAG in TOML) | Limited (Chaining) |
| **Caching** | File Modification Time | None |
| **Monorepo Awareness** | High (Wildcards, Root Trust) | Low (Directory-bound) |
| **CI Parity** | Low | Low |

### Monorepo Task Features

- **Wildcard Execution**: `mise run //...:test` traverses all sub-projects
- **Unified Namespace**: `//packages/ui:build`
- **Context Awareness**: Sub-project's environment loaded before execution
- **Parallel Execution**: Mise analyzes DAG and runs independent tasks in parallel

### Sub-Project Configuration

**Backend (`backend/mise.toml`):**

```toml
[tools]
# uv and python inherited from root

[tasks.install]
run = "uv sync"

[tasks.dev]
run = "uv run fastapi dev app.py"

[tasks.lint]
depends = ["lint:ruff", "lint:ty"]

[tasks."lint:ruff"]
run = "uv run ruff check ."

[tasks.test]
run = "uv run pytest"
```

**Frontend (`frontend/mise.toml`):**

```toml
[tools]
# bun inherited from root

[tasks.install]
run = "bun install"

[tasks.dev]
run = "bun run dev"

[tasks.test]
run = "bun test"
```

## Dagger — Programmable CI/CD

Dagger shifts the paradigm from "running commands on a shell" to "defining pipelines as code."

### Architecture

Dagger operates via a client-server model. The Dagger SDK (TypeScript, Python, Go) sends GraphQL queries to the Dagger Engine (a containerized BuildKit daemon).

### Why Dagger Over YAML CI

| Limitation of YAML | Dagger Solution |
|--------------------|-----------------|
| Different locally vs CI | Same code everywhere |
| No real programming | TypeScript/Python/Go |
| Hard to test | Unit tests on pipelines |
| Copy-paste reuse | Module imports |

### Module Structure

```
.dagger/
├── src/
│   ├── index.ts              # Main entry point
│   ├── build.ts              # Build functions
│   ├── test.ts               # Test functions
│   ├── deploy.ts             # Deploy functions
│   └── secrets.ts            # 1Password/Infisical integration
├── dagger.json               # Module configuration
└── package.json
```

### Pipeline Implementation

```typescript
import { dag, Container, Directory } from "@dagger.io/dagger"

export async function build(src: Directory): Promise<Container> {
  return dag
    .container()
    .from("node:20-alpine")
    .withDirectory("/app", src)
    .withWorkdir("/app")
    .withExec(["npm", "install"])
    .withExec(["npm", "run", "build"])
}

export async function test(src: Directory): Promise<string> {
  const container = await build(src)
  return container.withExec(["npm", "test"]).stdout()
}

export async function publish(container: Container, registry: string): Promise<string> {
  return container.publish(`${registry}/my-app:latest`)
}
```

### Polyglot Pipeline Example

```python
# dagger/main.py
import dagger
from dagger import dag, function, object_type

@object_type
class Monorepo:
    @function
    async def test(self) -> str:
        """Run all tests in the monorepo hermetically."""
        src = dag.host().directory(".")

        # Backend (Python)
        backend_test = (
            dag.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "uv"])
            .with_directory("/app", src.directory("oideachais"))
            .with_workdir("/app")
            .with_exec(["uv", "sync"])
            .with_exec(["uv", "run", "pytest"])
        )

        # Frontend (TypeScript)
        frontend_test = (
            dag.container()
            .from_("oven/bun:latest")
            .with_directory("/app", src.directory("oideachais/web"))
            .with_workdir("/app")
            .with_exec(["bun", "install"])
            .with_exec(["bun", "test"])
        )

        await backend_test.sync()
        await frontend_test.sync()
        return "All tests passed successfully."
```

### Dagger + Infisical Secrets

```typescript
import { dag, Secret } from "@dagger.io/dagger"

export function getSecret(ref: string): Secret {
  // Resolve at runtime from Infisical
  const value = process.env[ref] || ""
  return dag.setSecret(ref, value)
}

export async function withSecrets(container: Container): Promise<Container> {
  const dbUrl = getSecret("DATABASE_URL")
  return container.withSecretVariable("DATABASE_URL", dbUrl)
}
```

## turbo.json — Cross-Language Task Graph

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "typecheck": {},
    "lint": {},
    "format": {},
    "test": {},
    "clean": {
      "cache": false
    },
    "dagster": {},
    "ccc:index": {},
    "spec:validate": {}
  }
}
```

## Developer Onboarding (One Command)

```bash
bun run setup
# expands to: mise install && bun install && uv sync && bun run secrets:env && bun run secrets:init
```

### Developer Workflow

```
1. Clone repo → mise install (installs python, uv, bun, dagger)
2. cd into project → mise hook hydrates .env from Infisical
3. mise run dev → starts all sub-project dev servers in parallel
4. mise run test → runs all tests (fast, non-hermetic)
5. mise run ci → runs hermetic Dagger pipeline (exact CI parity)
```

## Secrets Bootstrap

Secrets follow the strict three-way contract:

1. **Source of truth** — `dev-baile` environment in the self-hosted Infisical vault
2. **Template** — `.infisical.env` (committed) — every value is an `infisical://dev-baile/...` reference
3. **Hydrated runtime** — `.env` (gitignored) — written by `mise`/`locket`/`bun run secrets:init`

```bash
bun run scripts/create-env.ts   # Create dev-baile environment
bun run scripts/init-vault.ts   # Sync .env + .infisical.env to vault
mise run secrets:init           # Alias for above
mise run locket:exec -- <cmd>   # Wrap command with Locket secret injection
```

## Codebase Indexing (ccc)

```bash
bun run ccc:init     # First time only
bun run ccc:index    # (Re)build the semantic index
bun run ccc:search "Dagster asset partition definition"
```

## OpenSpec — Spec-Driven Changes

```bash
bun run spec:list
bun run spec:validate my-change-id --strict
bun run spec:archive my-change-id
```

## Pipeline Orchestration

`turbo.json` defines the cross-language task graph:
- `build`, `dev`, `typecheck`, `lint`, `format`, `test`, `clean`
- `dagster`, `ccc:index`, `spec:validate`

`mise.toml` defines developer task aliases:
- `mise turbo dev`
- `mise ccc:search …`
- `mise secrets:init`
- `mise dagster:oideachais`

`dg.toml` loads `oideachais` and `tuatha` code-locations into a single Dagster deployment UI.

## The "Mise + Dagger" Architecture

This combination covers both the "Inner Loop" and "Outer Loop":

- **Mise** handles the developer's machine: ensuring uv and bun are installed, environment variables are set, and providing a unified CLI (`mise run`)
- **Dagger** handles build integrity: ensuring tests execute in a pristine environment that mirrors production

```bash
# Inner loop (fast, local)
mise run dev
mise run test

# Outer loop (hermetic, CI parity)
mise run ci  # → dagger call test
```

### Debugging CI Failures Locally

```bash
# Standard CI: "works on my machine" problem
# Mise + Dagger: exact parity
dagger call test              # Run same pipeline locally
dagger call --interactive     # Shell into container state before failure
```

## Caching Strategy

| Layer | Mechanism | Speed | Correctness |
|-------|-----------|-------|-------------|
| **Mise (local)** | File mtime | Fast | May drift |
| **Dagger (container)** | Content-addressable | Slower | Guaranteed correct |
| **uv (Python)** | Global cache + copy-on-write venv | Very fast | Lockfile-enforced |
| **bun (TypeScript)** | Global package cache | Very fast | Lockfile-enforced |

## The "Astral Stack" & "Bun Stack" Synergy

The tool selection represents a coherent theme: **The Shift to Native Code Tooling**.

| Tool | Language | Performance vs Legacy |
|------|----------|-----------------------|
| **uv** | Rust | 10-100x faster than pip |
| **ruff** | Rust | Orders of magnitude faster than pylint |
| **mise** | Rust | Instantly activates environments |
| **bun** | Zig | Starts faster than Node.js |
| **dagger** | Go | Container-native with BuildKit caching |

The task runner must not become the bottleneck. Mise (Rust) aligns with this performance profile perfectly.

## Integration with Other Tools

### GitHub Actions / Forgejo CI

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Dagger
        run: |
          curl -fsSL https://dl.dagger.io/dagger/install.sh | sh
          sudo mv bin/dagger /usr/local/bin/

      - name: Run Pipeline
        run: |
          dagger call build --src=.
          dagger call test --src=.
          dagger call publish
          dagger call deploy
        env:
          INFISICAL_CLIENT_ID: ${{ secrets.INFISICAL_CLIENT_ID }}
          INFISICAL_CLIENT_SECRET: ${{ secrets.INFISICAL_CLIENT_SECRET }}
```
