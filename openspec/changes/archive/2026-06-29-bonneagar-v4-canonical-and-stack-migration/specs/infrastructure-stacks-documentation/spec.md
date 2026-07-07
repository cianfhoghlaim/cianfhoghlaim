# `infrastructure-stacks-documentation` capability spec — leabharlann-email-inbox-pipeline delta

`infrastructure-stacks-documentation` is a NEW capability of
the Cianfhoghlaim platform. This document is the change-side
delta file; the canonical home for the capability spec is
`openspec/specs/infrastructure-stacks-documentation/spec.md`.

The corresponding source code lives at:

- `cianfhoghlaim/docs/stacks/README.md` (the index)
- `cianfhoghlaim/docs/stacks/<name>.md` (the 88 per-stack
  docs, one per stack in `bonneagar/stacks/`)
- `scripts/stack-doctor.sh` (the CI gate that fails if a
  stack is missing its doc)
- `.agents/skills/infrastructure-stacks-documentation/SKILL.md`
  (the agent entry point)

The contract: every stack in `bonneagar/stacks/<name>/`
MUST have a corresponding
`cianfhoghlaim/docs/stacks/<name>.md` doc with a 4-section
template.

## ADDED Requirements

### Requirement: Per-stack doc at `cianfhoghlaim/docs/stacks/<name>.md`

The system SHALL ship a per-stack doc at
`cianfhoghlaim/docs/stacks/<name>.md` for every stack in
`bonneagar/stacks/`. The doc SHALL contain 4 sections:

1. **Purpose for the Cianfhoghlaim project** — what this
   stack does for the platform (2-3 sentences)
2. **Why it stays in komodo/pangolin/infisical GitOps** —
   the operational requirement (2-3 sentences)
3. **Cross-references** — to the ops dir at
   `bonneagar/stacks/<name>/`, to the code (if any), to
   the IaC entry, to the Pangolin domain (if exposed)
4. **Tags** — the IaC tags (`host:bunchloch` /
   `host:arm1-oci` / `tier:infrastructure` /
   `tier:data-plane` / `tier:ci` / `tier:agent-platform` /
   `tier:user-facing-web` / `project:cianfhoghlaim`)

#### Scenario: All 88 stacks have a doc

- **WHEN** the developer lists `cianfhoghlaim/docs/stacks/`
- **THEN** the directory SHALL contain at least 88 .md
  files (one per stack in `bonneagar/stacks/`)
- **AND** a `README.md` index that lists all 88 docs
- **AND** each .md file SHALL follow the 4-section
  template

#### Scenario: `stack-doctor` fails if a doc is missing

- **WHEN** `bun run validate-stacks` runs
- **THEN** the CI gate SHALL fail with exit code 1 if any
  stack in `bonneagar/stacks/` is missing its
  corresponding `cianfhoghlaim/docs/stacks/<name>.md`
- **AND** the developer SHALL add the missing doc before
  the PR merges

#### Scenario: `hf-watchdog` doc is the canonical example

- **WHEN** the developer reads
  `cianfhoghlaim/docs/stacks/ci/hf-watchdog.md`
- **THEN** the doc SHALL contain:
  1. **Purpose**: "Daily HF Hub liveness check for the v4
     OCR/VLM registry. Verifies every model_id in
     `cianfhoghlaim.ocr.models.VISION_MODELS` against the
     HF Hub API. Posts a Slack alert on any 404."
  2. **Why GitOps**: "Runs as a daily container with zero
     side effects; the Slack webhook is optional; the
     watchdog sleeps 86400 seconds between checks."
  3. **Cross-references**: ops at
     `bonneagar/stacks/ci/hf-watchdog/`; code at
     `cianfhoghlaim/ci/hf_watchdog.py`; IaC entry in
     `bonneagar/iac/komodo/deploy-stacks.ts` (tag
     `host:bunchloch` + `tier:ci` + `project:cianfhoghlaim`)
  4. **Tags**: `host:bunchloch`, `tier:ci`,
     `project:cianfhoghlaim`, `v4:consolidated`

### Requirement: `infrastructure-stacks-documentation` SKILL.md

The system SHALL ship a SKILL.md at
`.agents/skills/infrastructure-stacks-documentation/SKILL.md`
with the 4-metadata-rule frontmatter (name, description,
when_to_load, location).

#### Scenario: SKILL.md is discoverable

- **WHEN** a developer runs `mise run lint:skills`
- **THEN** the new SKILL.md SHALL pass the 4 metadata rules
  (name matches dir, description ≥ 40 chars, valid
  frontmatter, under 2000 lines)

## MODIFIED Requirements

*(None — the change only ADDs the new capability.)*

## REMOVED Requirements

*(None.)*
