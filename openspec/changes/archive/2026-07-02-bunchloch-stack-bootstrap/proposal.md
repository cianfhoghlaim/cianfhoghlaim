# Change: 2026-07-02-bunchloch-stack-bootstrap

## Why

After the 2026-06-28 cianfhoghlaim v4 consolidation and the
2026-06-29 v4-canonical + IaC merge, the `bunchloch` workload host
(MacBook M4 / M4 Max / Pro — `Cians-MacBook-Pro.local`) is a cold-boot.
As of 2026-07-02 zero Docker Compose stacks are running locally,
despite the 2026-06-15 HEALTH_REPORT showing 35 healthy containers
(per `bonneagar/stacks/HEALTH_REPORT.md`, last refreshed 2026-06-15).

The in-flight `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops`
change is healing the Komodo TOML path drift (TOL bundles reference
`infrastructure/stacks/<x>/` which no longer exists; canonical path is
`bonneagar/stacks/<x>/`). Until that lands, **the canonical IaC path
(`bun run iac:bootstrap`) cannot register the 86 stacks** because 4 of
8 bootstrap phases are still `logWarn` stubs and the TOML `file_paths`
entries fail to resolve.

This change provides a **bridge** that brings the 19 most-needed
bunchloch stacks up via `./scripts/stack.sh` (the dev-mode direct
CLI that reads compose.yaml off disk and bypasses Komodo entirely),
documented in a runbook that any cold-boot agent can follow.

It is **complemented** by 3 sibling changes:

- `2026-07-02-add-lancedb-and-logfire-stacks` — adds 2 observability
  + vector-viewer stacks + pins 5 unpinned `:latest` images
- `2026-07-02-add-marimo-stack` — adds the marimo notebook server
- `2026-07-02-add-agent-surface-stacks` — adds 3 agent UI surfaces
  (hermes + openclaw + openchamber)

After all 4 changes ship, the canonical `bun run iac:bootstrap`
GitOps path can take over (a separate follow-up change that
consumes the v5-drift merge).

## What changes

- 1 new file at `bonneagar/deploy-runbooks/bunchloch-bootstrap.md`
  (the cold-boot runbook)
- 1 new openspec change directory with `proposal.md`, `tasks.md`,
  and `specs/infrastructure-stacks/spec.md` (the ADDED Requirements
  delta)
- 0 compose.yaml edits in this change (mlflow port mapping was
  already correct on re-inspection; the earlier diagnostic that
  flagged `ports: ["0.0.0.0", "5000"]` was a false positive
  triggered by the `--host 0.0.0.0 --port 5000` command args being
  parsed as a ports list)

The 19 stacks remain unchanged; they retain their current image
versions and port mappings. The 5 unpinned `:latest` images
(`cognee`, `dots-ocr`, `olmocr`, `paddleocr`, `docling-serve`) are
**deferred to Change 2** (per `infrastructure-stacks` §"Image Pinning
Policy", stack-doctor reports WARNINGs that do not block dev mode).

## Impact

- **Affected spec:** `infrastructure-stacks` (shared)
- **Affected code:** 1 new runbook + openspec change metadata
- **Affected hosts:** `bunchloch` only (the workload host)
- **Risk:** low (dev mode, no Locket, no Infisical state writes,
  per-stack rolls back with `./scripts/stack.sh <name> down`)
- **Audit gates:** `bun run validate-stacks` (pre/post) +
  `mise run lint:skills` (regression gate) + `openspec validate
  --strict` (change gate)
- **Pre-existing pre-flight findings:**
  - Total cold-start: 0 containers running
  - Disk free: 322 GB / 926 GB
  - RAM: 51.5 GB total (estimated ~36-42 GB peak once all 19
    are up; phased bring-up reduces per-wave pressure to ~10 GB)
  - Local ports already bound (macOS native, no conflicts with
    target ports)

## Non-goals

- Not fixing the 17 known drift items in the v5-drift change —
  this change explicitly scopes around them and relies on
  `./scripts/stack.sh` which reads compose.yaml directly.
- Not bringing up the `browser` stack (missing 5/6 GOLD_STANDARD
  files: no secrets.env, no sidecar.yaml, no blueprint.yaml,
  no README). Folded into a separate
  `2026-07-XX-bring-browser-stack-to-gold-standard` change.
- Not adding the 6 deferred stacks (`mailcow-dockerized`,
  `mlx-omni`, `letta`, `memgraph`, `lancedb`, `logfire`,
  `marimo`, `hermes`, `openclaw`, `openchamber`); these are
  handled by Changes 2-4 or future changes.
- Not converting to full IaC GitOps (that is the v5-drift
  change's outcome, not this one).
- Not registering Komodo stacks (path drift means the TOMLs
  will break; once v5-drift lands, a follow-up registers them).
- Not pinning the 5 unpinned `:latest` images (deferred to
  Change 2).
- Not producing a production Locket/Infisical integration
  (the runbook uses dev-mode defaults from each stack's
  `secrets.env`).

## Spec delta

See `specs/infrastructure-stacks/spec.md` for the ADDED
Requirement + Scenarios that govern this change.

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Pin 5 `:latest` images | `2026-07-02-add-lancedb-and-logfire-stacks` |
| Bring browser stack to GOLD_STANDARD | `2026-07-XX-bring-browser-stack-to-gold-standard` (deferred) |
| Register stacks in Komodo after v5-drift lands | `2026-07-XX-komodo-register-bunchloch-stacks` (deferred) |
| Migrate lakehouse to cax41-hetzner (per convergence spec) | `2026-07-XX-migrate-lakehouse-to-hetzner` (deferred) |