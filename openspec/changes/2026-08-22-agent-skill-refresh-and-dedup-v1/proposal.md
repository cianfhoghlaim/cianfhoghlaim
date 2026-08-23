# 2026-08-22 — Replace DEPRECATED skills with redirect-only stubs + add lint gate

## Why

The `.agents/skills/` tree currently has **3 DEPRECATED skills** (per the
`2026-07-06-2026-07-06-add-dev-env-demo-tools-to-adk-agents` change):

| DEPRECATED skill | File size | Canonical replacement |
|:--|:--|:--|
| `graphiti-core`        | 221 lines | `graphiti` (v0.29.2) |
| `dlthub-router`        | 54 lines  | `dlt` (the KCG dlt router) |
| `setup-secrets`        | 127 lines | `secrets-management` (Infisical + Locket + mise three-way contract) |

Each has a multi-line DEPRECATION NOTICE at the top but the **bulk of the file (50-220 lines) is stale content from the previous Graphiti/dlt/secrets versions**. New agents waste tokens parsing this stale content before they discover the redirect.

The fix: replace each DEPRECATED file with a **5-line redirect-only stub** that just points to the canonical replacement + the redirect reason. Same frontmatter (so `mise run lint:skills` still passes), no stale body content.

## What changes

### 1. Replace the 3 DEPRECATED skill files with 5-line stubs

For each of the 3 files, replace the body with:

```markdown
---
name: <skill-name>
description: "DEPRECATED — canonical replacement is <canonical-skill> (<reason>). This stub is redirect-only; use the canonical skill for all new work."
---

# <skill-name> — DEPRECATED (use <canonical-skill>)

This skill is **deprecated** as of 2026-07-06 and retained only for backward compatibility.

**Use the canonical replacement: `.agents/skills/<canonical-skill>/SKILL.md`**
```

The canonical skill is already present in the tree (verified: graphiti, dlt, secrets-management all exist).

### 2. Add a new `lint-skill:deprecated-cleanup` task

A CI gate that fails if any DEPRECATED skill has more than 50 lines:

```bash
# Find any DEPRECATED skill files over 50 lines
for f in $(grep -rl "^name:.*DEPRECATED\|^> \*\*DEPRECATION NOTICE" .agents/skills/*/SKILL.md); do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 50 ]; then
    echo "FAIL: $f has $lines lines (max 50 for redirect-only stubs)"
    exit 1
  fi
done
exit 0
```

This prevents future DEPRECATED skills from accumulating stale content.

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the 2026-07-06 deprecation changes (the canonical replacements are already in place)
- **Affected repos:** cianfhoghlaim only
- **Out of scope:**
  - The `mcp-builder` + `chatgpt-app-builder` files (these are vendored under `.agents/skills/copilotkit/examples/` — not part of the main skill tree)
  - The `dignified-python-310/311/312/313` 4-variant skill (folded into the canonical `dignified-python` per a separate change; tracked in `skill-refresh-batch-2026-09-v1`)

## Acceptance criteria

1. All 3 DEPRECATED skill files are ≤ 10 lines (5-line body + frontmatter)
2. The new `lint-skill:deprecated-cleanup` task exists in `mise.toml` and exits 0
3. `mise run lint:skills` still passes (frontmatter intact)
4. The canonical skills (`graphiti`, `dlt`, `secrets-management`) are unchanged
5. `openspec validate 2026-08-22-agent-skill-refresh-and-dedup-v1 --strict` exits 0

## Rollback plan

- `git checkout` the 3 skill files (revert to the long DEPRECATED versions)
- Remove the `lint-skill:deprecated-cleanup` task from `mise.toml`
- No data loss; no API changes; no migration
