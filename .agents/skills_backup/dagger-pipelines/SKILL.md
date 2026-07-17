---
name: dagger-pipelines
description: Router for the Dagger CI/CD pipeline capability. The Dagger module at `infrastructure/dagger/` is the 8-step GitOps pipeline that builds, tests, and ships every KCG workspace image. Use when adding a new pipeline step, modifying an existing function, wiring a new caller (Komodo, Forgejo Actions, or a local `dagger call`), or debugging a pipeline failure. Covers the Python root + TypeScript submodule, the 8 callable functions, the 4 build pipelines, the BuildKit caching, the multi-language SDK pattern (Go/Python/TypeScript), and the LLM-secrets injection pattern. Triggers: 'dagger call', 'dagger module', 'dagger pipeline', 'dagger function', 'buildkite', 'buildkit cache', 'dagger-python', 'dagger-typescript', 'gitops pipeline', 'komodo deploy'.
---

# Dagger Pipelines — Router

The Cianfhoghlaim platform has a Dagger module that runs every
CI/CD pipeline. This skill is the router — pick the right entry
point for the task.

## The Dagger module

Located at `infrastructure/dagger/`. Two submodules:

- **Python root** (`infrastructure/dagger/python/`) — the
  primary build pipeline (Bun, Python, Docker, Pulumi).
- **TypeScript submodule** (`infrastructure/dagger/typescript/`)
  — the BAML extraction + DLT validation pipeline.

## The 4 build pipelines

| Pipeline | What it does | When to use |
|:--|:--|:--|
| **`build-image`** | Build a single OCI image from a `Dockerfile` | `dagger call build-image --source ./path` |
| **`build-monorepo`** | Build all workspace images (oideachais, tuatha, meaisínfhoghlaim, croilar, cianfhoghlaim-web) | `dagger call build-monorepo` |
| **`deploy-stack`** | Deploy a single Docker Compose stack to a target host via Komodo | `dagger call deploy-stack --stack oideachais --host bunchloch` |
| **`validate-infra`** | Run `stack-doctor` + `komodo-validate` + `pulumi-preview` against the current infra | `dagger call validate-infra` |

## The 8 callable functions

| Function | Purpose |
|:--|:--|
| `test-python` | Run pytest across all uv workspaces |
| `test-typescript` | Run bun test across all bun workspaces |
| `lint-monorepo` | Run `ruff` + `eslint` + `biome` + `actionlint` |
| `format-monorepo` | Run `ruff format` + `biome format` + `prettier --write` |
| `build-image` | Build a single OCI image |
| `build-monorepo` | Build all workspace images |
| `deploy-stack` | Deploy a single stack to a target host |
| `validate-infra` | Validate the entire infrastructure tree |

## KCG conventions

1. **Dagger 0.13+** is the minimum (the multi-language SDK
   pattern requires it).
2. **BuildKit cache** is persistent in `~/.cache/dagger`
   on the runner host. Use `--cache-from` and `--cache-to`
   for cross-pipeline reuse.
3. **Secrets** come from the Infisical `dev-baile` vault.
   `dagger call` reads them via the Locket sidecar (do
   NOT inline secrets in the Dagger function).
4. **Multi-arch builds** are `linux/amd64,linux/arm64`
   (the 3 host tiers: arm1-oci ARM, bunchloch M4 ARM64,
   cax41-hetzner x86_64).

## Adding a new pipeline step

1. Edit `infrastructure/dagger/python/<file>.py` (or
   `typescript/<file>.ts` for the TS submodule).
2. Add a `@function` with the canonical signature.
3. Run `dagger call <file>.<function>` locally to test.
4. Wire the caller: Komodo (production), Forgejo Actions
   (CI), or `mise run dagger:<function>` (dev).
5. Add an entry to `mise.toml` `[tasks]` block.
6. Update `infrastructure/AGENTS.md` with the new function.

## Pair this skill with

- `dagger/SKILL.md` — the Dagger detail (Python SDK + Functions
  + caching + BuildKit)
- `monorepo/SKILL.md` — the Inner/Outer loop pattern (mise is
  inner, Dagger is outer)
- `infrastructure-stacks/SKILL.md` — the 6-file GOLD_STANDARD
  that Dagger validates
- `komodo/SKILL.md` — the production deployment target

## Cross-references

- [Dagger docs](https://docs.dagger.io)
- [Dagger Python SDK](https://docs.dagger.io/sdk/python)
- [Dagger TypeScript SDK](https://docs.dagger.io/sdk/typescript)
- [Cianfhoghlaim Dagger module](../infrastructure/dagger/)
