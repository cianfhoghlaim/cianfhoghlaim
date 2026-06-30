# Bonneagar IaC Merge Capability

## Purpose

`bonneagar-iac-merge` is a capability of the Cianfhoghlaim
platform. It defines the unified TypeScript IaC at
`bonnegar/iac/` that orchestrates the 3 systems (Komodo +
Pangolin + Infisical) into a single codebase.

The corresponding source code lives at:

- `bonnegar/iac/clients/{komodo,pangolin,infisical}-client.ts`
- `bonnegar/iac/models/{komodo,pangolin,infisical}.ts`
- `bonnegar/iac/sources/{discover-stacks,discover-resources,discover-secrets,key-stacks}.ts`
- `bonnegar/iac/commands/{plan,deploy,bootstrap,teardown,health}.ts`
- `bonnegar/iac/commands/sync-{secrets,resources,procedures,resource-syncs,monitors,alerts,variables,schedules,action-recipients,olm}.ts`
- `bonnegar/iac/{config,cli,diff,auth,README}.ts/.md`

## Background

The v0 IaC was split across 3 disconnected sub-circuits:
the 5 TypeScript files at `iac/komodo/`, the 3 bash scripts
at `scripts/`, and the 2 vault scripts at the repo root. The
3 systems (Komodo + Pangolin + Infisical) were not
synchronised.

This change merges them into a single TypeScript codebase
with 15 CLI commands + 3 typed clients + 4 source-discoverers
+ 5 top-level commands.

The 3 typed clients use the official API surfaces:
- **Pangolin** — the Enterprise Edition **Integrations API**
  at `${PANGOLIN_URL}/v1` + `/api/v1/integration/...`
  (verified by `PANGOLIN_LICENCE=PER-...`)
- **Infisical** — the official `@infisical/sdk` npm package
- **Komodo** — raw `fetch()` against the Komodo RPC API
  (the `komodo_client` npm package has a `localStorage`
  browser-only bug)

## Requirements

The full Requirements + Scenarios are in the change-side
delta file
`openspec/changes/2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical/specs/bonneagar-iac-merge/spec.md`.

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 88 stacks at `bonnegar/stacks/` + the 6-file
  GOLD_STANDARD pattern
- [`indexing-and-cognition`](../indexing-and-cognition/spec.md) —
  the cognify + indexing layers
- [`data-engineering-pipeline-documentation`](../data-engineering-pipeline-documentation/spec.md) —
  the 4 canonical ops dirs
