# Infrastructure Stacks Documentation Capability

## Purpose

`infrastructure-stacks-documentation` is a capability of the
Cianfhoghlaim platform. It defines the contract for the
per-stack documentation that lives in `cianfhoghlaim/` (the
code repo) but documents the ops at `bonneagar/` (the
infra repo).

The corresponding source code lives at:

- `cianfhoghlaim/docs/stacks/README.md` (the index)
- `cianfhoghlaim/docs/stacks/<name>.md` (the 88 per-stack
  docs, one per stack in `bonneagar/stacks/`)
- `scripts/stack-doctor.sh` (the CI gate that fails if a
  stack is missing its doc)
- `.agents/skills/infrastructure-stacks-documentation/SKILL.md`
  (the agent entry point)

## Background

The Cianfhoghlaim monorepo has a clean separation:

- **`cianfhoghlaim/`** = the code (Python package, agents,
  web apps, BAML schemas, DLT sources, etc.)
- **`bonneagar/`** = the ops (Docker compose, Pangolin
  routing, Infisical secrets, Komodo orchestration, Backrest
  backups, IaC TypeScript client)

The 88 stacks at `bonneagar/stacks/` need documentation
that lives in `cianfhoghlaim/` because:

1. The **purpose for the cianfhoghlaim project** is a code
   concern (which stack is used by which Python module, BAML
   schema, Dagster asset, ADK agent, etc.)
2. The **why-GitOps** rationale is an operational concern
   (which stacks can be removed, which can be combined,
   which need separate Komodo Peripheries)
3. The **cross-references** need to point at both repos

The contract: every stack in `bonneagar/stacks/<name>/` MUST
have a corresponding `cianfhoghlaim/docs/stacks/<name>.md`
doc with a 4-section template.

## Requirements

The full Requirements + Scenarios are in the change-side
delta file
`openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/specs/infrastructure-stacks-documentation/spec.md`.

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 6-file GOLD_STANDARD + 88-stack inventory
- [`data-engineering-pipeline-documentation`](../data-engineering-pipeline-documentation/spec.md) —
  the 4 canonical ops dirs
- [`indexing-and-cognition`](../indexing-and-cognition/spec.md) —
  the IaC at `bonneagar/iac/komodo/`
- [`author-archive-pipeline`](../author-archive-pipeline/spec.md) —
  the hf-watchdog stack + the VISION_MODELS registry
