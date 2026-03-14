# Archived Research Materials

This directory contains superseded research documents and deprecated examples that have been consolidated into the main `taighde/patterns/` files.

## Contents

### research_docs/

Original research documents whose patterns have been extracted into the consolidated `PATTERNS_*.md` files:

| Document | Extracted To |
|----------|--------------|
| AI Agents for Irish Language Resources.md | PATTERNS_AGENTS.md |
| Building a Hybrid Self-Hosted Agent Stack.md | PATTERNS_AGENTS.md, PATTERNS_WEB.md |
| Data Lake Stack Integration Research.md | PATTERNS_STORAGE.md |
| Hybrid GPU Resource Orchestration Plan.md | PATTERNS_STORAGE.md |
| Self-Hosted Data Platform MCP Integration.md | PATTERNS_DATA_PIPELINE.md, PATTERNS_OBSERVABILITY.md |

### deprecated_examples/

Example projects that have been superseded by canonical implementations:

#### cocoindex/
- `patient_intake_extraction_baml/` → merged into `structured_extraction/`
- `patient_intake_extraction_dspy/` → merged into `structured_extraction/`
- `pdf_elements_embedding/` → consolidated with `pdf_embedding/`

#### tanstack/
- `orcish-saas/` → superseded by `tanstack-start-better-auth-starter/`
- `orcish-tanstack-dashboard/` → superseded by `mcp-auth/`

## When to Reference

These documents may still be useful for:
- Historical context on project decisions
- Detailed implementation notes not captured in patterns
- Full code examples with dependencies

For current best practices, always refer to the `taighde/patterns/` files.

---

*Archived: 2025-12-29*
