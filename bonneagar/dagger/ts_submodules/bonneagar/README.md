# `ts_submodules/bonneagar/` — preserved TypeScript submodule

This directory is a **read-only copy** of the prior `bonneagar/dagger/`
TypeScript implementation that lived in
`stedding/dev/cianfhoghlaim copy/bonneagar/dagger/`. The original is a
~12.6k LOC Dagger module (31 hand-written `.ts` files + 4.4 MB
auto-generated `src/sdk/` client bindings) that drives 30+ service
wrappers for Komodo, Pangolin, Forgejo, PocketID, 1Password Connect,
and Cloudflare.

## Why preserve it

The Python root at `infrastructure/dagger/src/` is the **orchestrator**
(3 pipelines × test/build/deploy/rollback, plus a top-level
`UnifiedPipeline`). The TypeScript implementation here is the
**integration glue** — every actual REST/curl call against the
control-plane services.

Cross-module composition: the Python root calls into this submodule
via `await Module("bonneagar", source=...)`. See
`src/infrastructure/__init__.py:deploy`, `src/web/__init__.py:deploy`,
`src/data/__init__.py:deploy` for the call sites.

## Functions consumed by the Python root

The Python root invokes these submodule functions:

| Submodule function | Called from |
|:--|:--|
| `komodo_redeploy(stack, environment, secrets_env)` | InfrastructurePipeline.deploy, WebPipeline.deploy, DataPipeline.deploy |
| `komodo_rollback(stack, environment, version)` | InfrastructurePipeline.rollback, WebPipeline.rollback, DataPipeline.rollback |
| `pangolin_verify_labels(stack)` | InfrastructurePipeline.deploy |
| `cloudflare_deploy_pages(environment, secrets_env)` | WebPipeline.deploy |

## Status of the submodule

This is preserved **verbatim** from the prior commit. It still uses the
`@object`/`@func`/`@field` decorator API (the API was removed in
Dagger v0.16+; the submodule is pinned to engine v0.19.2 but the
package.json `@dagger.io/dagger ^0.15.1` still works via the
`dagger develop` codegen). It uses 1Password Connect (the prior
implementation's secret model); the Python root translates the new
Infisical refs to the Locket template before passing them in.

For the open issues with the submodule (hard-coded domain, vendored SDK,
two `index.ts` files, no tests, dead `publish()` code path), see the
prior `bonneagar/dagger/` analysis in the explore-agent report.

## Updating the submodule

Edit the source files in this directory as needed. To regenerate the
auto-generated `src/sdk/client.gen.ts`:

```bash
cd infrastructure/dagger/ts_submodules/bonneagar
bun install
dagger develop    # regenerates client.gen.ts
```

Do NOT remove this directory. It is the source of truth for the
control-plane glue.
