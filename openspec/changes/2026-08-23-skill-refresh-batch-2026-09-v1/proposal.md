# 2026-08-23 — Skill refresh batch 2026-09 (8-10 skills + new frontmatter convention)

## Why

The `.agents/skills/` tree has 65 skills, many of which are dated 2026-07
or earlier. Per the mega plan, the omnibus skill refresh should:

1. **Update the dated 2026-07 skills** with a "What's new in 2026-08/09"
   section (8-10 skills)
2. **Introduce a unified frontmatter convention** (the canonical 5-field
   schema: name + description + when_to_use + argument-hint + tags)
3. **Fold the 4 dignified-python-310/311/312/313 variants** into the
   canonical `dignified-python` skill (which already has version
   detection)

## What changes

### 1. Refresh 8-10 skills (add "What's new in 2026-08/09" sections)

Per the plan:
- `apple-photos-ingestion` — bump to 2026-09 patterns (the 5th leabharlann
  corpus via osxphotos; 3 v1 CocoIndex Apps)
- `huggingface` — add v3 Spaces MCP server + ZeroGPU patterns
- `mlflow` — v3.15+ patterns (MLflow Server 2.22+)
- `langfuse` — v4 patterns (the Phase 3C.2 + commit a6d408a54 work)
- `cognee` — v1.1.2 patterns (Cypher injection patch)
- `graphiti` — v0.29.2 patterns (FalkorDB Lite + summarize_saga)
- `dagster` — 1.13+ patterns (the `dg` CLI; Phase 3B.1)
- `dlt` — 1.30+ patterns (Phase 3B.2)
- `litellm` — v1.97+ patterns (Phase 3C.2)

### 2. Fold 4 dignified-python-310/311/312/313 variants

The canonical `dignified-python` skill has version detection (3.10 → 3.13).
The 4 variant skills (`dignified-python-310`, `dignified-python-311`,
`dignified-python-312`, `dignified-python-313`) are now DEPRECATED
redirects to the canonical skill.

### 3. New frontmatter convention

Add the `when_to_use` field (already present in most skills) as the
canonical dispatch trigger. Skills without it get a lint warning.

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the 2026-08-13 skill-consolidation-and-extension-v1 change
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. 8-10 skills have new "What's new in 2026-08/09" sections
2. The 4 dignified-python-310/311/312/313 variants are DEPRECATED redirects
3. `mise run lint:skills` exits 0 (no frontmatter drift)
4. The canonical skills (graphiti, dagster, dlt, litellm, etc.) remain unchanged in their core content
5. `openspec validate 2026-08-23-skill-refresh-batch-2026-09-v1 --strict` exits 0

## Rollback plan

- `git checkout` the 8-10 skill files
- Restore the 4 dignified-python-310/311/312/313 skills to their pre-change versions
- No code changes; no API changes; no migration