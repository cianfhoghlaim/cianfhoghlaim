## MODIFIED Requirements

### Requirement: Canonical Directory Layout

The `docs/` tree SHALL be organised into numbered domain directories,
each focused on one capability area. The `00_index.md` file at the
root SHALL be the single master routing table.

In addition, every README in the Cianfhoghlaim monorepo SHALL
follow the canonical 6-section structure:

1. **What lives here** — the quadrant/area overview (1-2 paragraphs)
2. **Quick start** — the dev quick-start (5-10 commands)
3. **Key commands** — the canonical commands (build / dev / test /
   lint / deploy)
4. **Common workflows** — the add-a-new-X workflows (3-5 patterns)
5. **How to deploy** — the deploy playbook (the per-area steps)
6. **How to debug** — the troubleshooting guide (5-10 common
   failure modes + fixes)

The 7 READMEs in the monorepo are:

- `README.md` (root) — the monorepo overview + the 8-phase
  end-to-end deploy playbook
- `infrastructure/README.md` — the 94-stack inventory
- `sruth/oideachais/README.md` — the lakehouse quadrant
- `sruth/meaisinfhoghlaim/README.md` — the AI/ML quadrant
- `sruth/tuatha/README.md` — the MMO + crypto quadrant
- `sruth/croilar/README.md` — the portfolio quadrant
- `spaces/README.md` — the HuggingFace Spaces

A standalone `DEPLOY.md` at the repo root SHALL contain the
end-to-end deploy playbook (the 8 phases + the 9th phase rollback).

#### Scenario: New canonical document is added to a domain

- **GIVEN** a contributor wants to add a new canonical document covering
  a topic in the `data_platform` domain
- **WHEN** the document is created
- **THEN** it is placed in `docs/02-data-platform/` with a kebab-case
  filename that matches the topic
- **AND** the document carries the standard frontmatter schema
- **AND** the `00_index.md` routing table is updated to include the new
  document in the "I want to..." table and the per-domain document list

#### Scenario: A README follows the 6-section structure

- **GIVEN** a new quadrant is added to the monorepo
- **WHEN** the quadrant's `README.md` is created
- **THEN** it SHALL have the 6 canonical sections
  (What lives here / Quick start / Key commands / Common workflows /
  How to deploy / How to debug)
- **AND** the section ordering SHALL be consistent with the other
  7 READMEs

## ADDED Requirements

### Requirement: End-to-end deploy playbook

The root `README.md` SHALL contain an 8-phase end-to-end deploy
playbook. The 8 phases are:

1. **Phase 0: Pre-flight** — verify the toolchain (`mise install`),
   the secrets (`bun run secrets:env` + `bun run secrets:init`),
   and the 2 hosts (`arm1-oci` + `bunchloch`)
2. **Phase 1: Infrastructure** — bootstrap the Infisical vault
   (the `dev-baile` environment) + the Komodo control plane
   + the Pangolin mesh + the Locket sidecar + the 4 quadrant
   stacks (infra → oideachais → meaisinfhoghlaim → tuatha →
   croilar)
3. **Phase 2: Oideachais** — deploy the lakehouse (Dagster +
   FastAPI + TanStack Start + Agno AgentOS + Google ADK)
4. **Phase 3: Meaisínfhoghlaim** — deploy the AI/ML services
   (llama-swap + mlx-omni + invokeai + the 12 agents)
5. **Phase 4: Tuatha** — deploy the MMO + the crypteolas
   achievement ledger
6. **Phase 5: Croílár** — deploy the 3-persona portfolio
   + the DevTools Hub
7. **Phase 6: Spaces** — deploy the 4 active HuggingFace
   Spaces (sync via the reusable workflow)
8. **Phase 7: Verify** — run the 4 audit scripts (the
   `infrastructure/audit/scripts/` quartet) + the `stack-doctor`
   CI gate
9. **Phase 8: Rollback** — the canonical rollback procedure
   (the Locket sidecar auto-rollback + the Infisical version
   restore + the Komodo stack disable)

The playbook SHALL also be duplicated as a standalone `DEPLOY.md`
at the repo root (for users who want the playbook without the
monorepo overview).

#### Scenario: A developer follows the 8-phase playbook

- **GIVEN** a developer wants to deploy the entire Cianfhoghlaim
  monorepo to a fresh `bunchloch` + `arm1-oci` cluster
- **WHEN** they follow the 8-phase playbook in `README.md`
  (or the standalone `DEPLOY.md`)
- **THEN** the 5 quadrants (infrastructure + oideachais +
  meaisinfhoghlaim + tuatha + croilar) + the 4 Spaces deploy
  in dependency order
- **AND** the 4 audit scripts return 0 (clean)
- **AND** the `stack-doctor` CI gate passes
- **AND** the developer can roll back via Phase 8 if any phase
  fails
