# Cianfhoghlaim Project Conventions

## Project Overview

Celtic language education platform with AI-powered tools for Irish curriculum processing. The monorepo is a **bun + uv + turbo polyglot orchestration** of multiple subprojects and 70+ Docker Compose stacks.

## Subprojects

| Subproject | Path | Purpose |
|:--|:--|:--|
| `oideachais/` | top-level | Celtic education data platform (Dagster, DLT, LanceDB) |
| `meaisínfhoghlaim/` | top-level | AI/ML (OCR, alignment, RAG, ASR/TTS) |
| `tuatha/` | top-level | Educational MMO + crypto platform |
| `croilar/` | top-level | Personal portfolio + CV + data engineering subproject (Cian's core) |

## Capability Areas

### Education Platform

| Capability | Description | Status |
|------------|-------------|--------|
| `curriculum-ingestion` | NCCA/SEC document processing | Active |
| `bilingual-content` | English/Irish content management | Active |
| `knowledge-graph` | Prerequisite and topic relationships | Active |
| `semantic-search` | Vector-based curriculum search | Active |
| `assessment-extraction` | Exam papers and marking schemes | Active |
| `oideachais-pipeline` | Celtic education curriculum pipeline | Active |

### Dagger Modules

| Capability | Description | Status |
|------------|-------------|--------|
| `dagger-monorepo-integration` | Python root at `infrastructure/dagger/` with 3 pipelines (infra/web/data) × test/build/deploy/rollback + TS submodule + Locket secret model + 2 Forgejo Actions | Active |
| `dagger-ci` | Polyglot CI orchestration (Python, TypeScript, Rust) | Active |
| `dagger-gitops` | 8-step GitOps pipeline (Forgejo + Komodo) | Active |
| `dagger-forgejo` | Forgejo API automation | Active |
| `dagger-komodo` | Komodo SDK wrapper | Active |
| `dagger-cloudflare` | Pages and Worker deployment | Active |
| `dagger-blockchain` | SpacetimeDB, Solana, Ethereum CI | Deferred (requires Rust toolchain in Python root + GPU support) |

### Team Workflow

| Capability | Description | Status |
|------------|-------------|--------|
| `workflow-automation` | n8n + LLM pipelines (OpenCode Go API) | Active |
| `task-management` | Vikunja kanban + Gantt + list + team sharing | Active |
| `scheduling` | cal-diy team + per-member booking pages | Active |

### Stack Operations

| Capability | Description | Status |
|------------|-------------|--------|
| `infrastructure-stacks` | 70+ Docker Compose stacks under `infrastructure/stacks/*/*/` | Active |
| `stack-audit` | `scripts/stack-doctor.sh` auditor + turbo validate-stacks task | Active |

### Monitoring & Observability

| Capability | Description | Status |
|------------|-------------|--------|
| `infrastructure/monitoring` | Prometheus + Grafana + Loki + Alertmanager + Promtail | Active |
| `infrastructure` | Pangolin convergence, Infisical + Locket secrets, Komodo GitOps | Active |

### Developer Tooling

| Capability | Description | Status |
|------------|-------------|--------|
| `chunkhound-code-search` | Semantic code search with MVCC | Active |
| `ai-agent-skills` | Portable instruction directories (`.agents/skills/`) | Active |

### Personal Portfolio (croilar)

| Capability | Description | Status |
|------------|-------------|--------|
| `croilar-portfolio` | Public TanStack Start site — 9 subprojects (home/cv/music/code/research/teaching/data/identity/contact) | Active |
| `croilar-data-engineering` | Dagster + DLT + CocoIndex + BAML pipelines (read from DuckLake catalog) | Active |
| `croilar-cv-extraction` | BAML extraction of the author's CV/achievements/teaching PDFs | Active |

## AI Agent Toolchain & Conventions

The project embraces an AI-first development workflow utilizing **OpenCode CLI** with multi-model subagents.

1. **Agent Skills (`.agents/skills/`)**: We utilize the [Agent Skills standard](https://agentskills.io/). Specialized capabilities, workflows, and prompts must be documented as skills within the `.agents/skills/` directory. This ensures portability across all AI agents.
2. **Issue Tracking**: All AI agents should use standard GitHub/Forgejo issues. Follow the `AGENTS.md` handoff protocol upon session completion.
3. **Model Context Protocol (MCP)**: Agents access local and remote capabilities (like `browserbase`, `firecrawl`, `motherduck`, `infisical`, `chrome`, `cocoindex-code`) via the MCP servers defined in `opencode.json`.
4. **Subagent Architecture**: Specialized subagents (data-engineer, ai-engineer, frontend-dev, devops-architect, explorer) are defined in `opencode.json` with model-specific routing for cost optimization.

## Infrastructure

- **Toolchain**: mise (python 3.12, uv, bun, dagger, pulumi, duckdb, sops, opencode)
- **Orchestration**: turbo.json (cross-language task graph)
- **Secret management**: Infisical (source of truth) + Locket (runtime injection) + mise (auto-hydration)
- **Deploy**: Komodo (GitOps) + Pangolin (private routing) + Pocket ID (OIDC) + Cloudflare (edge)
- **Storage**: Garage S3 (object), DuckLake (lakehouse), LanceDB (vectors), FalkorDB (graph), Memgraph (graph)
- **Observability**: Prometheus + Grafana + Loki + Alertmanager + Promtail + Langfuse (LLM) + Logfire (Pydantic) + MLflow (ML)

## Naming Conventions

### Capabilities
- Use kebab-case: `curriculum-ingestion`, `bilingual-content`
- Single purpose per capability
- Use verb-noun pattern where applicable

### Changes
- Prefix with action: `add-`, `update-`, `remove-`, `refactor-`
- Example: `add-prerequisite-mapping`, `update-marking-scheme-extraction`

## Technology Constraints

All specs MUST respect constraints from `docs/context/00-core/CONSTRAINTS.md`:

1. **Database:** Single-threaded DuckDB, MVCC LanceDB
2. **Embeddings:** Batch minimum 100 texts
3. **Irish language:** Use specialized models (UCCIX, GaBERT)
4. **BAML:** Schema validation required for LLM extraction
5. **Secrets:** Infisical is the source of truth; Locket injects at runtime; never commit `.env`
6. **Image registry:** `ghcr.io/cianfhoghlaim/`, pinned to `<major>.<minor>.<patch>`, never `:latest`
7. **Multi-arch:** Every in-repo image built for `linux/amd64,linux/arm64`

## Requirement Language

- Use **SHALL** for normative requirements
- Use **SHOULD** for recommendations
- Use **MAY** for optional features

## Scenario Format

```markdown
#### Scenario: Descriptive name
- **GIVEN** initial context
- **WHEN** action occurs
- **THEN** expected result
```

## File Locations

- Specs: `openspec/specs/<capability>/spec.md`
- Changes: `openspec/changes/<change-id>/`
- Archives: `openspec/changes/archive/YYYY-MM-DD-<change-id>/`
- Historical research: `docs/openspec/` (point-in-time, do not edit)
- Agent skills: `.agents/skills/<skill-name>/SKILL.md`
- Docker stacks: `infrastructure/stacks/<category>/<name>/`

## Review Process

1. Create proposal in `changes/<change-id>/`
2. Validate with `openspec validate <change-id> --strict`
3. Request review
4. Implement after approval
5. Archive after deployment

## Current In-Flight Changes

(Updated as changes move through the workflow.)

| Change | Status |
|:--|:--|
| `consolidate-external-libs-into-tuatha` | implemented |
| `monorepo-restructure-v2` | implemented |
| `team-workflow-stack` | implemented |
| `fix-existing-stacks` | implemented |
| `croilar-portfolio` | in-flight |
