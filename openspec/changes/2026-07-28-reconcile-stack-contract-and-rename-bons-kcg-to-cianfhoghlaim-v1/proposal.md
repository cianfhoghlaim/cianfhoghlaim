# Reconcile Stack Contract and Rename Bons/Kcg to Cianfhoghlaim

## Why

The repository has accumulated drift across the 6-file stack contract, the Locket/Bons shim image, the Hetzner host references, and the CLI/mise brand tokens. Three competing definitions of `blueprint.yaml`, two incompatible `secrets.env` grammars, and dozens of `ghcr.io/cianfhoghlaim/locket-shim` / `kcg` / `cax41-hetzner` references make deterministic, reproducible deployment impossible.

This change:

1. Reconciles the two GOLD_STANDARD documents into one canonical contract.
2. Adopts the Pangolin EE `private-resources:` / `public-resources:` root blueprint as the single `blueprint.yaml` shape.
3. Renames every `bons-*`, `bons:`, `kcg`, and `KCGu` brand token to `cianfhoghlaim` (lowercase).
4. Removes all active Hetzner / `security.hetzner` references and rewrites the 17 affected stack READMEs.
5. Rebuilds and pushes the Locket shim under `ghcr.io/cianfhoghlaim/locket-shim`. The push requires a GitHub PAT with `write:packages` scope; the build is reproducible locally. If the operator's `GH_TOKEN` lacks that scope, the build artifact is preserved locally and a follow-up push is queued.
6. Adds the new `cianfhoghlaim` CLI with Commander + Clack + Ink, plus a strict linter that fails on legacy patterns.

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-27-fix-locket-env-file-parse-time-on-63-stacks-v1` (this change builds on the shell-wrapper fix)

`Affected repos: cianfhoghlaim`

## Scope

In scope:

- `bonneagar/stacks/<name>/compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`
- `bonneagar/GOLD_STANDARD.md` and `bonneagar/stacks/GOLD_STANDARD.md` (reconcile into one)
- `bonneagar/iac/` TypeScript IaC + the new `cianfhoghlaim` CLI
- `bonneagar/dagger/ts_submodules/bonneagar/src/ci.ts` (`deployHetzner` removal)
- `mise.toml` (mise task renames)
- Stack READMEs for the 17 stacks that referenced `cax41-hetzner`
- `openspec/specs/infrastructure-stacks/spec.md` (contract update)

Out of scope:

- `bonneagar/iac/pulumi/hetzner/` — preserved as frozen historical record
- `.agents/skills_backup/` — retired-skill archive
- `stedding/` — non-canonical archive
- Republishing any Locket shim images outside this change's brand rename

## Plan order

1. Scaffold this change and validate `openspec validate --strict`.
2. Reconcile the two GOLD_STANDARD documents into `bonneagar/stacks/GOLD_STANDARD.md`.
3. Migrate the 5 important stacks (`litellm`, `cognee`, `openclaw`, `openchamber`, `langfuse`) to the new `blueprint.yaml` shape and shell-wrapper sidecar.
4. Rename the Locket shim image from `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` to `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` in every `sidecar.yaml` that uses the shim. Rebuild and push the image.
5. Remove `deployHetzner` and `security.hetzner` defaults from `bonneagar/dagger/ts_submodules/bonneagar/src/ci.ts`.
6. Rewrite the 17 stack READMEs to point at `arm1-oci` or `bunchloch`.
7. Rename all `bons:` and `kcg:` CLI/mise identifiers to `cianfhoghlaim:`.
8. Add the `cianfhoghlaim` CLI: `stack lint|plan|deploy|verify|rollback`, `secrets lint|verify|hydrate|seed`, `preflight`, `topology validate`.
9. Run `openspec validate --strict` and the quality gates.
10. Ask the user before committing and pushing.