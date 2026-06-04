# OpenSpec Instructions for Cianfhoghlaim

## Quick Reference

```bash
# List specs and changes
openspec list --specs
openspec list

# Validate before implementation
openspec validate <change-id> --strict

# Archive after deployment
openspec archive <change-id> --yes
```

## Workflow

### Creating Changes

1. Check existing specs: `openspec list --specs`
2. Create change directory: `openspec/changes/<change-id>/`
3. Write `proposal.md`, `tasks.md`, and spec deltas
4. Validate: `openspec validate <change-id> --strict`
5. Request review before implementing
6. Implement after approval
7. Archive after deployment: `openspec archive <change-id> --yes`

### Spec Delta Format

```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide...

#### Scenario: Success case
- **WHEN** user performs action
- **THEN** expected result

## MODIFIED Requirements
### Requirement: Existing Feature
[Complete modified requirement with all scenarios]

## REMOVED Requirements
### Requirement: Old Feature
**Reason**: [Why removing]
**Migration**: [How to handle]
```

## Capability Specs

### Education Platform

| Capability | Purpose |
|------------|---------|
| `curriculum-ingestion` | NCCA/SEC document processing |
| `bilingual-content` | English/Irish content management |
| `knowledge-graph` | Prerequisites and relationships |
| `semantic-search` | Vector-based search |
| `assessment-extraction` | Exam papers and marking schemes |
| `oideachais-pipeline` | Celtic education curriculum pipeline |

### Dagger Modules

| Capability | Purpose |
|------------|---------|
| `dagger-ci` | Polyglot CI orchestration (Python, TypeScript, Rust) |
| `dagger-gitops` | 8-step GitOps pipeline (Forgejo + Komodo) |
| `dagger-forgejo` | Forgejo API automation |
| `dagger-komodo` | Komodo SDK wrapper |
| `dagger-cloudflare` | Pages and Worker deployment |
| `dagger-blockchain` | SpacetimeDB, Solana, Ethereum CI |

### Team Workflow

| Capability | Purpose |
|------------|---------|
| `workflow-automation` | n8n + LLM pipelines (OpenCode Go API) |
| `task-management` | Vikunja kanban + Gantt + list + team sharing |
| `scheduling` | cal-diy team + per-member booking pages |

### Stack Operations

| Capability | Purpose |
|------------|---------|
| `infrastructure-stacks` | 70+ Docker Compose stacks under `infrastructure/stacks/*/*/` |
| `stack-audit` | `scripts/stack-doctor.sh` auditor + turbo validate-stacks task |

### Monitoring & Observability

| Capability | Purpose |
|------------|---------|
| `infrastructure/monitoring` | Prometheus + Grafana + Loki + Alertmanager + Promtail |

### Developer Tooling

| Capability | Purpose |
|------------|---------|
| `chunkhound-code-search` | Semantic code search with MVCC |

### Personal Portfolio (croilar)

| Capability | Purpose |
|------------|---------|
| `croilar-portfolio` | Public TanStack Start site — 9 subprojects |
| `croilar-data-engineering` | Dagster + DLT + CocoIndex + BAML pipelines |
| `croilar-cv-extraction` | BAML extraction of the author's CV/achievements/teaching PDFs |

### Infrastructure

| Capability | Purpose |
|------------|---------|
| `infrastructure` | Pangolin convergence, secrets, Komodo GitOps |

## Adding a New Capability

When a change introduces a new capability (not a MODIFIED of an existing one), follow this recipe:

1. **Add the capability** to the relevant section in [`project.md`](./project.md)
2. **Create a capability spec** at `openspec/specs/<capability>/spec.md` with at least 1 Requirement and 1 Scenario
3. **In the change's `specs/<capability>/spec.md`** (the delta file), use `## ADDED Requirements` header and a `### Requirement:` block with `#### Scenario:` children
4. **Validate with `openspec validate --strict`** — every Requirement needs at least one Scenario
5. **Cross-reference** related skills at `.agents/skills/<relevant-skill>/SKILL.md`

## Adding a New Docker Compose Stack

1. Create the directory: `infrastructure/stacks/<category>/<name>/`
2. Add the 6 GOLD_STANDARD files: `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`
3. Use `pangolin.private-resources.<name>.*` (6-label pattern) — see `.agents/skills/stack-ops/SKILL.md`
4. Add a Komodo procedure: `infrastructure/komodo/procedures/<name>-*.toml`
5. Add Infisical items: `bun run scripts/init-vault.ts` after appending to root `.infisical.env`
6. Validate: `bun run validate-stacks` (the new `stack-doctor` turbo task)

## Critical Rules

1. **NEVER skip validation** - Always run `openspec validate --strict`
2. **ALWAYS include scenarios** - Every requirement needs at least one
3. **Use correct headers** - `#### Scenario:` (4 hashtags)
4. **Respect constraints** - Architecture standardizes on **Infisical**, **Dagster**, **DuckLake**, **MCP** servers, and the 6-file GOLD_STANDARD stack pattern.
5. **Historical research lives in `docs/openspec/`** - never modify the 3 research files there; they're point-in-time artifacts.

## Cross-references

- [`project.md`](./project.md) — project conventions, capability list
- [`../docs/openspec/README.md`](../docs/openspec/README.md) — historical research material index
- [`../.agents/skills/stack-ops/SKILL.md`](../.agents/skills/stack-ops/SKILL.md) — operational skill for adding/fixing stacks
- [`../.agents/skills/ccc/SKILL.md`](../.agents/skills/ccc/SKILL.md) — semantic code search
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
