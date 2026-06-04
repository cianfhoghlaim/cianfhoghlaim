# Dagger Monorepo Integration

## Why

The Cianfhoghlaim monorepo has **six OpenSpec capability specs for Dagger** (`dagger-ci`, `dagger-gitops`, `dagger-forgejo`, `dagger-komodo`, `dagger-cloudflare`, `dagger-blockchain`) and a prior TypeScript implementation at `stedding/dev/cianfhoghlaim copy/bonneagar/dagger/`, but **no in-repo Dagger module exists**. The 4 `mise.toml` task aliases (`dagger:ci`, `dagger:test-python`, `dagger:test-typescript`, `dagger:deploy-cloudflare`) all point at the non-existent `infrastructure/dagger/` and fail at runtime. The `infrastructure/scripts/create-olm-clients.sh` script and 16 `infrastructure/komodo/procedures/*.toml` `RunAction` references (`deploy-pangolin-dagger`, `deploy-auth-stack-dagger`) are all dead code.

This change brings a real Dagger module online at `infrastructure/dagger/`, organised as a **Python root + TypeScript submodule** hybrid. The Python root carries the orchestration logic (test_all, build_images, deploy, rollback for the 3 pipelines). The prior TypeScript implementation (31 files, ~12.6k LOC) is consumed as a TypeScript submodule via `dagger.json` `dependencies` to preserve the prior work and avoid duplication. The Locket secret model replaces the 1Password pattern in the 8 design docs because the project uses Infisical + Locket (see `AGENTS.md` "Strict Secret Hydration"), not 1Password.

Scope is intentionally narrow: **6-8 callable functions** that unblock the broken mise task aliases and the 16 dead `RunAction` references. The 6 existing OpenSpec specs are updated to point at the new location. The `dagger-blockchain` spec is deferred to a followup because SpacetimeDB + Solana + Ethereum CI requires a Rust toolchain that the current module does not yet wire.

## What Changes

### Add: `infrastructure/dagger/` (new module)

- **`infrastructure/dagger/dagger.json`** — Dagger engine v0.19.2, Python SDK, declares a TypeScript dependency on the prior `bonneagar` impl.
- **`infrastructure/dagger/pyproject.toml`** — package name `cianchoghlaim-dagger`, `[project.entry-points."dagger.mod"] main_object = "cianchoghlaim:UnifiedPipeline"`.
- **`infrastructure/dagger/src/__init__.py`** — exports `UnifiedPipeline` (`@object_type`) with 4 top-level orchestrators: `test_all()`, `build_images()`, `deploy()`, `rollback()`.
- **`infrastructure/dagger/src/infrastructure/__init__.py`** — `InfrastructurePipeline` (`@object_type`) with `test()`, `build_api()`, `deploy()`, `rollback()`. Drives Pulumi → Locket template render → Komodo redeploy → Pangolin label verify.
- **`infrastructure/dagger/src/web/__init__.py`** — `WebPipeline` with `test()`, `build_ui()`, `deploy()`, `rollback()`. Drives `bunx turbo run build` → Cloudflare Pages (via TS submodule) → Komodo redeploy.
- **`infrastructure/dagger/src/data/__init__.py`** — `DataPipeline` with `test()`, `build_dagster()`, `deploy()`, `rollback()`. Drives Dagster materialise → Komodo redeploy → LiteLLM gateway smoke test.
- **`infrastructure/dagger/src/shared/containers.py`** — `python_container()`, `bun_container()`, `rust_container()` builders with pinned base images (`ghcr.io/astral-sh/uv:python3.12-bookworm@sha256:…`, `oven/bun:1.1.42@sha256:…`, `rust:1.83-slim@sha256:…`) and `Ignore` exclude list.
- **`infrastructure/dagger/src/shared/caching.py`** — `uv_cache()`, `bun_cache()`, `cargo_cache()` `CacheVolume` helpers.
- **`infrastructure/dagger/src/shared/secrets.py`** — `InfisicalSecret` dataclass, `locket_secrets_env()` template renderer, canonical secret registry for the 3 pipelines (INFRA_SECRETS, WEB_SECRETS, DATA_SECRETS).
- **`infrastructure/dagger/src/shared/testing.py`** — `test_python`, `lint_python`, `typecheck_python`, `test_bun`, `lint_bun`, `typecheck_bun`, `test_rust`, `clippy_rust` runners.
- **`infrastructure/dagger/ts_submodules/bonneagar/`** — copy of the prior `stedding/dev/cianfhoghlaim copy/bonneagar/dagger/` (read-only, consumed as TS submodule).
- **`infrastructure/dagger/templates/secrets.env.template`** — `{{ infisical://dev-baile/... }}` template per `GOLD_STANDARD.md`.
- **`infrastructure/dagger/templates/sidecar.yaml.template`** — Locket sidecar snippet.
- **`infrastructure/dagger/.forgejo/workflows/ci.yaml`** — installs Dagger + mise, runs `dagger call test-all` on PR, runs `dagger call build-images` on main.
- **`infrastructure/dagger/.forgejo/workflows/deploy.yaml`** — gated deploy (`environment: production` for manual approval) to staging and production.
- **`infrastructure/dagger/README.md`** — local docs.

### Modify: `mise.toml`

The 4 broken `dagger:*` task aliases (lines 147-161) are uncommented and rewritten to point at the new `infrastructure/dagger/`. A new `dagger:build-images` alias is added.

### Modify: 6 OpenSpec capability specs

The 6 existing `openspec/specs/dagger-{ci,gitops,forgejo,komodo,cloudflare,blockchain}/spec.md` files have their `bonneagar/dagger/src/*.ts` path references updated to `infrastructure/dagger/src/*.py` (or `*.ts` for the submodule).

### Modify: `openspec/project.md`

Add the new capability `dagger-monorepo-integration` to the capability table.

### Add: `openspec/changes/dagger-monorepo-integration/`

This change skeleton (`proposal.md` + `tasks.md` + 5 spec deltas).

## Impact

| Surface | Before | After |
|:--|:--|:--|
| `infrastructure/dagger/` | does not exist | 8 callable functions + 2 Forgejo Actions + 3 Locket templates + TS submodule preserved |
| `mise.toml` `dagger:*` tasks | 4 broken aliases | 5 working aliases |
| 6 OpenSpec dagger specs | reference dead `bonneagar/dagger/src/*.ts` paths | reference the new `infrastructure/dagger/src/*` |
| 16 Komodo `RunAction` references | dead code | wired into the Python root via TS submodule composition |
| `infrastructure/scripts/create-olm-clients.sh` | `DAGGER_DIR` not found | `infrastructure/dagger/ts_submodules/bonneagar/` exists |
| Forgejo Actions | no Dagger | 2 new workflows (ci.yaml + deploy.yaml) |
| OpenSpec capability count | 28 | 29 (add `dagger-monorepo-integration`) |
