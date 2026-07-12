# `infrastructure/dagger/` — Cianfhoghlaim Dagger module

The Dagger module that drives the entire Cianfhoghlaim polyglot monorepo's
CI/CD. The Python root exposes **8 callable functions** that compose
across the **3 pipelines** (infrastructure / web / data). The prior
TypeScript `bonneagar/dagger/` implementation is preserved as a
submodule at `ts_submodules/bonneagar/` and is called via cross-module
composition for the control-plane glue (Komodo, Pangolin, Forgejo,
Cloudflare).

See [`openspec/changes/dagger-monorepo-integration/`](../../../openspec/changes/dagger-monorepo-integration/)
for the full change spec, the spec deltas for the 6 existing dagger-*
capabilities, and the deferred `dagger-blockchain` followup.

## Quickstart

```bash
# 0. One-time: install the toolchain (per the monorepo root mise.toml)
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise install    # installs Python 3.12, uv, bun, dagger, pulumi

# 1. Sync the workspace (resolves the 8 dagger deps + the prior ts_submodules deps)
cd infrastructure/dagger
uv sync

# 2. Run the full test pipeline (lint + typecheck + unit across all 3 pipelines)
dagger call test-all --source ../..

# 3. Build + publish the 3 pipeline images to ghcr.io/cianfhoghlaim
dagger call build-images --source ../.. \
  --registry=ghcr.io/cianfhoghlaim \
  --tag=$(git rev-parse --short HEAD)

# 4. Deploy to staging (or production with --approved=true)
dagger call deploy --source ../.. --environment=staging

# 5. Roll back if something went wrong
dagger call rollback --source ../.. \
  --environment=production \
  --previous-version=v1.2.2 \
  --approved=true
```

Or via the monorepo-root `mise.toml` task aliases:

```bash
# These are defined at the repo root and previously pointed at
# the non-existent path. They now resolve to the live module.
mise run dagger:ci                  # dagger call test-all
mise run dagger:test-python         # scoped to Python
mise run dagger:test-typescript     # scoped to bun
mise run dagger:build-images        # dagger call build-images
mise run dagger:deploy-cloudflare   # dagger call deploy (staging)
```

## The 8 callable functions

### Top-level orchestrators (in `UnifiedPipeline`)

| Function | Args | Purpose |
|:--|:--|:--|
| `test_all` | `--source` | Lint + typecheck + unit across all 3 pipelines in parallel via `asyncio.gather` |
| `build_images` | `--source`, `--registry`, `--tag` | Build + push the 3 pipeline images to the registry with multi-arch `linux/amd64,linux/arm64` |
| `deploy` | `--source`, `--environment`, `--approved` | End-to-end deploy for an environment. `production` requires `--approved=true` |
| `rollback` | `--source`, `--environment`, `--previous-version`, `--approved` | Revert to a previous image tag. `production` requires `--approved=true` |

### Per-pipeline functions

| Pipeline | Function | Args | Purpose |
|:--|:--|:--|:--|
| `InfrastructurePipeline` | `test` | `--source` | ruff + mypy + pulumi validate + ansible --syntax-check |
| `InfrastructurePipeline` | `build_api` | `--source` | Build the `oideachais-api` image |
| `InfrastructurePipeline` | `deploy` | `--source`, `--environment` | Pulumi up → Locket template → Komodo redeploy → Pangolin label verify |
| `InfrastructurePipeline` | `rollback` | `--environment`, `--previous_version` | Komodo rollback |
| `WebPipeline` | `test` | `--source` | turbo lint + typecheck + test across 4 bun workspaces |
| `WebPipeline` | `build_ui` | `--source` | `bunx turbo run build` |
| `WebPipeline` | `deploy` | `--source`, `--environment` | turbo build → Locket template → Cloudflare Pages → Komodo redeploy |
| `WebPipeline` | `rollback` | `--environment`, `--previous_version` | Komodo rollback |
| `DataPipeline` | `test` | `--source` | ruff + mypy + pytest across the Python uv workspace |
| `DataPipeline` | `build_dagster` | `--source` | Build the unified `dagster-unified` image (3 code-locations) |
| `DataPipeline` | `deploy` | `--source`, `--environment` | Locket template → Dagster materialise → Komodo redeploy → LiteLLM smoke test |
| `DataPipeline` | `rollback` | `--environment`, `--previous_version` | Komodo rollback |

## Architecture

```
infrastructure/dagger/
├── dagger.json                              # engine v0.19.2, Python SDK, TS submodule dep
├── pyproject.toml                           # entry point: cianchoghlaim:UnifiedPipeline
├── README.md                                # this file
│
├── src/
│   ├── __init__.py                          # UnifiedPipeline (top-level orchestrator)
│   ├── infrastructure/__init__.py            # InfrastructurePipeline (Pulumi + Komodo + Pangolin)
│   ├── web/__init__.py                      # WebPipeline (bun + Cloudflare)
│   ├── data/__init__.py                     # DataPipeline (Dagster + DLT + CocoIndex)
│   └── shared/
│       ├── __init__.py                      # public surface re-exports
│       ├── containers.py                    # python/bun/rust container builders
│       ├── caching.py                       # uv/bun/cargo cache volume helpers
│       ├── secrets.py                       # Locket template generator + 3 registries
│       └── testing.py                       # polyglot test runners
│
├── ts_submodules/
│   └── bonneagar/                           # preserved TypeScript implementation
│       ├── dagger.json                      # SDK = typescript
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/                             # 31 .ts files (~12.6k LOC)
│       │   ├── index.ts                      # @object() classes
│       │   ├── komodo.ts
│       │   ├── pangolin.ts
│       │   ├── forgejo.ts
│       │   ├── cloudflare.ts
│       │   ├── ci.ts
│       │   ├── gitops.ts
│       │   └── … (all 31 files)
│       ├── src/sdk/                         # vendored Dagger TS SDK (4.4 MB)
│       └── README.md                        # submodule docs
│
├── templates/
│   ├── secrets.env.template                 # {{ infisical://dev-baile/... }} for infra
│   ├── secrets.web.env.template             # same, for web
│   ├── secrets.data.env.template            # same, for data
│   └── sidecar.yaml.template                # Locket sidecar snippet
│
├── .forgejo/
│   └── workflows/
│       ├── ci.yaml                          # dagger call test-all on PR + main
│       └── deploy.yaml                      # dagger call deploy to staging + production
│
└── openspec/                               # (symlink at the monorepo root)
    └── changes/
        └── dagger-monorepo-integration/    # the change spec
            ├── proposal.md
            ├── tasks.md
            └── specs/dagger-monorepo-integration.md
```

## The 3 sub-package hierarchy

```
                        ┌───────────────────────────────────┐
                        │  UnifiedPipeline (top-level)      │
                        │  test_all, build_images, deploy,  │
                        │  rollback                          │
                        └─────────────┬─────────────────────┘
                                      │  asyncio.gather
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
  │ Infrastructure    │   │ Web               │   │ Data              │
  │ Pipeline          │   │ Pipeline          │   │ Pipeline          │
  │                   │   │                   │   │                   │
  │ - Pulumi IaC      │   │ - bun / turbo     │   │ - Dagster assets  │
  │ - Locket          │   │ - TanStack Start  │   │ - DLT + CocoIndex │
  │ - Komodo          │   │ - Cloudflare       │   │ - LiteLLM smoke  │
  │ - Pangolin        │   │   Pages/Workers   │   │   test            │
  │ - Forgejo         │   │ - 4 bun workspaces│   │ - Dagster + KGs   │
  └────────┬──────────┘   └────────┬──────────┘   └────────┬──────────┘
           │                       │                       │
           └────────────┬──────────┴───────────────┬───────┘
                        │  calls into              │
                        ▼                          ▼
              ┌─────────────────────────────────────────────┐
              │  ts_submodules/bonneagar/ (TypeScript)     │
              │  31 files, ~12.6k LOC, 4.4 MB vendored SDK │
              │  Komodo + Pangolin + Forgejo + Cloudflare  │
              │  + 1Password Connect REST wrappers         │
              └─────────────────────────────────────────────┘
```

## Secret model

**Dagger NEVER directly resolves Infisical secrets.** Instead, it produces
`secrets.env` templates that contain `{{ infisical://dev-baile/<folder>/<key> }}`
placeholders. The Locket sidecar (deployed per
[`infrastructure/stacks/GOLD_STANDARD.md`](../stacks/GOLD_STANDARD.md))
resolves these placeholders at container runtime.

The 3 canonical registries in `src/shared/secrets.py` enumerate every
secret each pipeline needs. The `locket_secrets_env()` renderer emits
the Locket template format:

```bash
# service: infrastructure
# vault: dev-baile
# rendered-by: cianchoghlaim-dagger v0.1.0
# Locket will substitute the {{ infisical://... }} refs at container runtime

INFISICAL_TOKEN={{ infisical://dev-baile/infisical_cianfhoghlaim/service-token }}
KOMODO_API_KEY={{ infisical://dev-baile/komodo/api-key }}
KOMODO_API_SECRET={{ infisical://dev-baile/komodo/api-secret }}
KOMODO_PASSKEY={{ infisical://dev-baile/komodo/passkey }}
PANGOLIN_TOKEN={{ infisical://dev-baile/pangolin/admin-token }}
FORGEJO_TOKEN={{ infisical://dev-baile/forgejo/admin-token }}
POCKET_ID_CLIENT_SECRET={{ infisical://dev-baile/pocket-id/client-secret }}
CROWDSEC_BOUNCER_KEY={{ infisical://dev-baile/crowdsec/bouncer-key }}
PULUMI_ACCESS_TOKEN={{ infisical://dev-baile/pulumi/access-token }}
...
```

Rendered templates are written to `infrastructure/dagger/templates/` as
the canonical reference. When the pipeline runs, the same renderer in
`src/shared/secrets.py` is called and the rendered stdout is passed
through to the TS submodule's `komodo_redeploy` function.

This is a **deliberate divergence from the 8 design docs** in
`docs/old/taighde_old/archive/infrastructure-skills/dagger/`, which
assumed 1Password. The 1Password pattern is replaced by Infisical +
Locket per the project's `AGENTS.md` "Strict Secret Hydration" rule.

## Container image policy

Every base image is **pinned to a `sha256:` digest, never `:latest`**.
The digests in `src/shared/containers.py` are the latest stable as of
the `dagger-monorepo-integration` change (2026-Q2) and should be
re-pinned when a new release is verified.

| Image | Pinned digest (short) | Use |
|:--|:--|:--|
| `ghcr.io/astral-sh/uv:python3.12-bookworm` | `0b6f4e2a…` | Python tooling (uv sync, ruff, mypy, pytest, Pulumi, Dagster) |
| `oven/bun:1.1.42` | `f1c5d2b7…` | bun + turbo (TanStack, Vinxi, Babylon.js) |
| `rust:1.83-slim-bookworm` | `7c5b8e2a…` | Rust (infrastructure/locket, tuatha/crates/) |
| `pulumi/pulumi-python:3.83.0` | `5c8e2a4f…` | InfrastructurePipeline Pulumi runs |
| `ghcr.io/cianfhoghlaim/dagster-unified:latest` | *replaced at build* | DataPipeline Dagster materialise |
| `curlimages/curl:8.11.1` | `6c8e2a4f…` | DataPipeline LiteLLM smoke test |
| `ghcr.io/bpbradley/locket:infisical` | `1d2e3f4a…` | Locket sidecar (template) |

`Ignore` patterns applied to every `with_directory(/src, source, …)`:

```python
[
    ".venv", "node_modules", "__pycache__", ".git", ".turbo", "dist",
    ".ruff_cache", ".pytest_cache", ".mypy_cache", "*.lock",
    "data/", "stedding/", ".cocoindex_code/", "dlthub/",
    "instagram_output/", "docs/", "oideachais/data_platform/datasets/",
]
```

## Forgejo Actions integration

The `.forgejo/workflows/` directory has 2 workflows:

- **`ci.yaml`** — runs on every PR + main push. Installs mise + Dagger, runs
  `dagger call test-all`. On main, additionally runs
  `dagger call build-images --tag=${{ github.sha }}` to publish the
  pipeline images.
- **`deploy.yaml`** — runs on main push. Two jobs:
  1. `deploy-staging` (no manual gate) runs
     `dagger call deploy --environment=staging`.
  2. `deploy-production` (gated by `environment: production` manual
     approval) runs
     `dagger call deploy --environment=production --approved=true`.

The `approved: bool = False` default in `UnifiedPipeline.deploy` is a
belt-and-braces safety check — even if the Forgejo gate is bypassed,
the Dagger function itself refuses to deploy to production without
explicit opt-in.

## OpenSpec capabilities touched

This change touches 7 capabilities:

| Capability | Change |
|:--|:--|
| `dagger-ci` | Path refs updated to `infrastructure/dagger/src/`; new Locket secret model |
| `dagger-gitops` | Path refs updated; 8-step pipeline now calls Python root + TS submodule |
| `dagger-forgejo` | Path refs updated; REST wrappers integrated with Python root |
| `dagger-komodo` | Path refs updated; SDK wrapper integrated with Python root |
| `dagger-cloudflare` | Path refs updated; Pages/Worker deploys |
| `dagger-blockchain` | DEFERRED to followup (requires Rust toolchain in Python root + GPU support) |
| `dagger-monorepo-integration` | NEW — the wrapper + 3 pipelines + 8 functions |

## Integration points

| Tool | How this module integrates |
|:--|:--|
| **mise** | 5 `dagger:*` task aliases at the repo root (`mise.toml`) call `cd infrastructure/dagger && dagger call …` |
| **uv** | `uv sync` from the monorepo root; this module consumes the workspace via the entry point |
| **bun + turbo** | The Python root's `WebPipeline.test/build_ui` invokes `bunx turbo run lint typecheck test build` |
| **Pulumi** | `InfrastructurePipeline.deploy` runs `pulumi/pulumi-python:3.83.0` against `infrastructure/pulumi/<env>/` |
| **Komodo** | The TS submodule's `komodo.ts` makes the REST API calls (redeploy, rollback, listStacks) |
| **Pangolin** | The TS submodule's `pangolin-api.ts` makes the Integration API calls (resources, blueprints) |
| **Forgejo** | The TS submodule's `forgejo.ts` makes the REST API calls (users, tokens, webhooks, runners) |
| **Cloudflare** | The TS submodule's `cloudflare.ts` makes the Pages / Workers deploy calls |
| **Infisical** | The Dagger Python root **does not** call Infisical — it produces `{{ infisical://... }}` templates; Locket consumes them |
| **Locket** | The Dagger Python root does **not** deploy Locket; it produces `secrets.env` files that Locket sidecars (deployed by Komodo) consume |
| **Forgejo Actions** | The 2 `.forgejo/workflows/*.yaml` files install Dagger + mise + run `dagger call …` |

## Out of scope (filed as followup OpenSpec changes)

- **`dagger-blockchain`** — SpacetimeDB + Solana + Ethereum CI. Requires a Rust
  toolchain in the Python root + GPU support. Filed as a separate change.
- **Komodo SDK vs raw `curl`** — The prior TS implementation uses raw `curl`
  calls. If `@komodo/sdk` is published on npm, the TS submodule can be
  rewritten to use it; otherwise the `curl` approach is fine.
- **Multi-runner Dagger cache** — For now, the Forgejo runners each build
  their own cache volume. A shared S3/MinIO-backed cache is a followup.
- **GPU support** — Dagster AI / LiteLLM may need CUDA. The DinD pattern
  with `--gpus all` is unproven in Dagger.
- **Cross-pipeline Service bindings** — Web pipeline calling Data
  pipeline's Dagster REST API. Not needed at the CI/test scope.

## Validation

```bash
# 1. Regenerate the Dagger client bindings
cd infrastructure/dagger
dagger develop

# 2. Smoke-test the unified test pipeline
dagger call test-all --source ../..

# 3. Smoke-test the image build (does not push, just verifies the chain)
dagger call build-images --source ../.. --tag=test-smoke

# 4. Validate the OpenSpec change
cd ../../openspec
openspec validate dagger-monorepo-integration --strict
```

## Related docs

- [`openspec/changes/dagger-monorepo-integration/`](../../../openspec/changes/dagger-monorepo-integration/) — the change proposal
- [`openspec/specs/dagger-ci/`](../../../openspec/specs/dagger-ci/) — polyglot CI spec
- [`openspec/specs/dagger-gitops/`](../../../openspec/specs/dagger-gitops/) — GitOps spec
- [`openspec/specs/dagger-forgejo/`](../../../openspec/specs/dagger-forgejo/) — Forgejo spec
- [`openspec/specs/dagger-komodo/`](../../../openspec/specs/dagger-komodo/) — Komodo spec
- [`openspec/specs/dagger-cloudflare/`](../../../openspec/specs/dagger-cloudflare/) — Cloudflare spec
- [`AGENTS.md`](../../../AGENTS.md) — agent protocols (Strict Secret Hydration, Landing the Plane)
- [`infrastructure/AGENTS.md`](../AGENTS.md) — infra-agent protocols (Gold-Standard stack pattern)
- [`infrastructure/stacks/GOLD_STANDARD.md`](../stacks/GOLD_STANDARD.md) — 5-file stack pattern
- [`ts_submodules/bonneagar/README.md`](ts_submodules/bonneagar/README.md) — the preserved TS submodule
- [`docs/bonneagar/dagger/dagger.md`](../../docs/bonneagar/dagger/dagger.md) — the original v0.18 design doc
- [`mise.toml`](../../mise.toml) — the 5 `dagger:*` task aliases

## License

BUSL-1.1 — non-commercial, cultural preservation, and academic research
use permitted within Ireland, UK, EU, Commonwealth, and aligned
jurisdictions. Transitions to AGPL-3.0 after 4 years.
See [`LICENSE.md`](../../../LICENSE.md).
