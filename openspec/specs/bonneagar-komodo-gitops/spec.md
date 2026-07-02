# Bonneagar Komodo GitOps Capability

## Purpose

`bonneagar-komodo-gitops` is a capability of the Cianfhoghlaim
platform. It defines the canonical Komodo GitOps pattern for
the `bonneagar/` fleet: 3 resource-syncs (one per host + one
cross-cutting) that auto-pull from the repo on every commit.

The corresponding source code lives at:

- `bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml`
- `bonneagar/iac/commands/health.ts` (registers the
  resource-syncs with Komodo via `listResourceSyncs()`)
- `bonneagar/komodo/procedures/*.toml` (the procedures the
  resource-syncs import)
- `bonneagar/komodo/stacks/*.toml` (the stack registrations
  the resource-syncs import)

## Background

Pre-v5, the IaC pushed procedures via `iac:sync:procedures`
— a state mutation, not a sync. The canonical Komodo GitOps
pattern is resource-syncs: declare the resource (stack,
procedure, monitor, action-recipient, variable, schedule)
in TOML, register it with Komodo via `POST /sync`, and let
Komodo auto-pull from the repo on every commit. This change
converts the 84 procedures (minus the 38 deleted + 4 phantom
in Phases 6.7-6.9) to 3 resource-syncs and slims the IaC to
the orchestration layer that ensures resource-syncs are
configured + secrets are synced.

The full Requirements + Scenarios are in the change-side
delta file
`openspec/changes/2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops/specs/bonneagar-komodo-gitops/spec.md`.

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 88 stacks at `bonneagar/stacks/`
- [`bonneagar-iac-merge`](../bonneagar-iac-merge/spec.md) —
  the IaC capability (slimmed to orchestration layer)
- [`dagger-pipelines`](../dagger-pipelines/spec.md) —
  the Dagger module that wires `iac:bootstrap` into CI
- [`secrets-management`](../../../.agents/skills/secrets-management/SKILL.md) —
  the Infisical + Locket + mise 3-way contract
