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
5. Request approval before implementing

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

### Developer Tooling

| Capability | Purpose |
|------------|---------|
| `beads-issue-tracking` | Distributed issue tracker for AI agents |
| `chunkhound-code-search` | Semantic code search with MVCC |

### Infrastructure

| Capability | Purpose |
|------------|---------|
| `infrastructure-stacks` | 25+ storage and utility Docker stacks |

## Critical Rules

1. **NEVER skip validation** - Always run `openspec validate --strict`
2. **ALWAYS include scenarios** - Every requirement needs at least one
3. **Use correct headers** - `#### Scenario:` (4 hashtags)
4. **Respect constraints** - Check `.claude/CONSTRAINTS.md`
