---
name: infrastructure-stacks-documentation
description: |
  This skill should be used when working on per-stack
  documentation at `cianfhoghlaim/docs/stacks/<name>.md`.
  Covers the 4-section template (Purpose + Why-GitOps +
  Cross-references + Tags), the cianfhoghlaim/bonneagar code-ops
  split, the per-stack-doc CI gate, the 5-group model
  (infrastructure / data-engineering / agent-platform /
  language-model / user-facing-web), and the canonical
  `infrastructure-stacks-documentation` capability spec.
  Trigger phrases include 'stack doc', 'per-stack
  documentation', 'why-gitops', 'purpose for the
  cianfhoghlaim project', 'stack tags', 'group model',
  'infrastructure-stacks-documentation', 'docs/stacks'.
when_to_load: |
  Load when creating/modifying a per-stack doc at
  `cianfhoghlaim/docs/stacks/<name>.md`, when auditing
  the 88 docs for completeness, when running
  `bun run validate-stacks` and the gate fails due to a
  missing doc, when designing the cianfhoghlaim/bonneagar
  code-ops split, or when adding a new stack to
  `bonneagar/stacks/`.
location: .agents/skills/infrastructure-stacks-documentation/SKILL.md
---

# Infrastructure Stacks Documentation

## Overview

The `infrastructure-stacks-documentation` capability defines
the contract for the 88 per-stack docs at
`cianfhoghlaim/docs/stacks/<name>.md`. Each doc follows a
4-section template:

1. **Purpose for the Cianfhoghlaim project** — what this
   stack does for the platform (2-3 sentences)
2. **Why it stays in komodo/pangolin/infisical GitOps** —
   the operational requirement (2-3 sentences)
3. **Cross-references** — to the ops dir at
   `bonneagar/stacks/<name>/`, to the code (if any), to
   the IaC entry, to the Pangolin domain
4. **Tags** — the IaC tags (`host:bunchloch` /
   `host:arm1-oci` / `tier:infrastructure` / `tier:data-plane`
   / `tier:ci` / `tier:agent-platform` /
   `tier:user-facing-web` / `project:cianfhoghlaim`)

## The 5-Group Model

The 88 stacks are organised into 5 logical groups
(informational only, not a deploy-time constraint):

| Group | Count | Host | Examples |
|:--|--:|:--|:--|
| **infrastructure** | 9 | arm1-oci | Pangolin, Pocket ID, TinyAuth, Traefik, Infisical, Locket, Komodo Core + Periphery, Backrest |
| **data-engineering** | 12 | bunchloch | Dagster, Lakehouse, Marimo, CocoIndex, Cognify, Litellm, Langfuse, Llama-swap |
| **agent-platform** | 7 | bunchloch | Agno AgentOS, Google ADK, OpenClaw, OpenChamber, Cognee, Graphiti, Letta |
| **language-model** | 6 | bunchloch | LiteLLM, llama-swap, MLX-Omni, Logfire, Langfuse, mlflow |
| **user-facing-web** | 6 | bunchloch | cianfhoghlaim-web, cianfhoghlaim-api, cianfhoghlaim-dagster, cianfhoghlaim-agent-os, cianfhoghlaim-adk-agents, openclaw |
| **ci** | 1 | bunchloch | hf-watchdog |

## The 4-Section Template

```markdown
# <Stack Display Name>

## Purpose for the Cianfhoghlaim project

<2-3 sentences explaining what this stack does for the
platform. Reference the Python module / BAML schema /
Dagster asset / ADK agent that uses it.>

## Why it stays in komodo/pangolin/infisical GitOps

<2-3 sentences explaining the operational requirement.
Why is this stack self-hosted instead of cloud-managed?
What is the Komodo / Pangolin / Infisical surface that
makes it deployable + secure + reproducible?>

## Cross-references

- **Ops**: `bonneagar/stacks/<name>/` (the 6-file
  GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any)
- **IaC**: registered in
  `bonneagar/iac/komodo/deploy-stacks.ts` with tags
  `<tag1>` + `<tag2>` + ...
- **Pangolin**: `https://<name>.cianfhoghlaim.ie` (if
  exposed)

## Tags

- `host:<bunchloch|arm1-oci>`
- `tier:<infrastructure|data-plane|ci|agent-platform|user-facing-web>`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
```

## The CI Gate

`scripts/stack-doctor.sh` (run via `bun run validate-stacks`)
fails if any stack in `bonneagar/stacks/` is missing its
`cianfhoghlaim/docs/stacks/<name>.md` doc. The gate is
necessary because:

1. The 88 docs are the discoverability layer — without them,
   the cianfhoghlaim project loses track of which stack
   does what
2. The cross-references in the docs are the single source
   of truth for which ops file maps to which Python module
3. The 5-group model is documented in the index README at
   `cianfhoghlaim/docs/stacks/README.md`

## Cross-references

- [`.agents/skills/infrastructure-stacks/SKILL.md`](../infrastructure-stacks/SKILL.md) —
  the 6-file GOLD_STANDARD + 88-stack inventory
- [`.agents/skills/indexing-and-cognition/SKILL.md`](../indexing-and-cognition/SKILL.md) —
  the IaC at `bonneagar/iac/komodo/`
- [`.agents/skills/data-engineering-pipeline-documentation/SKILL.md`](../data-engineering-pipeline-documentation/SKILL.md) —
  the 4 canonical ops dirs
- [`openspec/specs/infrastructure-stacks-documentation/spec.md`](../../openspec/specs/infrastructure-stacks-documentation/spec.md) —
  the canonical capability spec
- [`openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/`](../../openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/) —
  the openspec change artifacts
