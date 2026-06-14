---
truth: partial
---

# Cianfhoghlaim Project Conventions

## Project Overview

Celtic language education platform with AI-powered tools for Irish curriculum processing.

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
| `dagger-ci` | Polyglot CI orchestration (Python, TypeScript, Rust) | Active |
| `dagger-gitops` | 8-step GitOps pipeline (Forgejo + Komodo) | Active |
| `dagger-forgejo` | Forgejo API automation | Active |
| `dagger-komodo` | Komodo SDK wrapper | Active |
| `dagger-cloudflare` | Pages and Worker deployment | Active |
| `dagger-blockchain` | SpacetimeDB, Solana, Ethereum CI | Active |

### Developer Tooling

| Capability | Description | Status |
|------------|-------------|--------|
| `beads-issue-tracking` | Distributed issue tracker for AI agents | Active |
| `chunkhound-code-search` | Semantic code search with MVCC | Active |

### Infrastructure

| Capability | Description | Status |
|------------|-------------|--------|
| `infrastructure-stacks` | 25+ storage and utility Docker stacks | Active |

## Naming Conventions

### Capabilities
- Use kebab-case: `curriculum-ingestion`, `bilingual-content`
- Single purpose per capability
- Use verb-noun pattern where applicable

### Changes
- Prefix with action: `add-`, `update-`, `remove-`, `refactor-`
- Example: `add-prerequisite-mapping`, `update-marking-scheme-extraction`

## Technology Constraints

All specs MUST respect constraints from `.claude/CONSTRAINTS.md`:

1. **Database:** Single-threaded DuckDB, MVCC LanceDB
2. **Embeddings:** Batch minimum 100 texts
3. **Irish language:** Use specialized models (UCCIX, GaBERT)
4. **BAML:** Schema validation required for LLM extraction

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

## Review Process

1. Create proposal in `changes/<change-id>/`
2. Validate with `openspec validate <change-id> --strict`
3. Request review
4. Implement after approval
5. Archive after deployment
