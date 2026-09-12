## Context

The `.agents/skills/` surface grew from 18 entries (2026-06) to 72
entries (2026-09-02) across 8 months of additions. Several defects
became visible during a 2026-09-02 round-trip of every SKILL.md
through a YAML parser (the audit method, not eye-balling):

1. **`openspec/SKILL.md` describes 1.4, not 1.11** — the CLI was
   upgraded mid-session but the skill description field still says
   "OpenSpec 1.4 (Fission AI)" with the legacy "OPSX schema not
   adopted" framing that conflated schema choice with command-delivery
   profile.
2. **Unclosed frontmatter in `dagster/SKILL.md`** — the body
   horizontal-rule (`---`) was masquerading as the frontmatter closer,
   silently swallowing the "What's new" section into YAML. The file
   parsed as YAML but the post-rule section never reached the agent.
3. **Unescaped `: ` in `cianfhoghlaim-nua-v6-era`'s description** —
   YAML treats `key: value` pairs at the top level; the description
   field's `5-pillar pattern (BAML → Convex → A2UI → Hono → React)`
   broke the parse.
4. **2 router-only placeholders** for nested-skill packs —
   `.agents/skills/copilotkit/SKILL.md` and `.agents/skills/pydantic/SKILL.md`
   exist but their content is a single line, while the nested packs
   (`copilotkit/skills/*` and `pydantic/building-pydantic-ai-agents/`,
   `pydantic/logfire-*`, `pydantic/pydantic-ai-harness`) are real
   content. Agents see the stub and don't know to load the nested
   pack.
5. **3 oversized skill descriptions** (>200 chars, the
   agent-platform recommendation) — agents split on long descriptions
   and miss the trigger phrase.
6. **`openspec/SKILL.md` quoted counts are stale** (78/97/96 vs
   verified 36/102/344).
7. **No lint gate for skill frontmatter round-trip** — every defect
   above was found by hand, not by `mise run lint:*`.

## Goals / Non-Goals

**Goals:**
- Fix all 7 defects above in a single sweep.
- Add a lint gate so the same class of defect doesn't reappear.

**Non-Goals:**
- This change does NOT restructure `.agents/skills/` into a
  different directory shape.
- This change does NOT remove any skill — even the 2 router-only
  ones are upgraded to real routers, not deleted.

## Decisions

**Skills-refresh is `skip_specs: true`** because the SKILL.md files
are documentation; they describe how agents use existing
capabilities, they don't change capability behaviour. No capability's
requirements change as a result.

**Frontmatter round-trip lint gate** parses every `SKILL.md` with
`yaml.safe_load` on the frontmatter block; if `safe_load` throws, the
lint fails. This catches the unescaped-colon and unclosed-block
classes of defect automatically going forward.

## Risks / Trade-offs

- [Risk] Trimming oversized skill descriptions may drop trigger
  phrases agents rely on → Mitigation: trim only descriptions whose
  length is genuinely >200 chars AND whose first 100 chars contain
  the canonical trigger phrase; defer the longer tail to the skill
  body.
- [Trade-off] Adding the lint gate may break the CI green path until
  every existing skill's frontmatter is fixed → Accepted: this
  change fixes all 7 existing defects in the same sweep, so the gate
  goes green after this change archives.

## Migration Plan

1. Each defect fix is a per-file edit, no migration of callers needed.
2. The new `lint:skills-frontmatter` task is added to `mise.toml` in
   the same change so the gate goes live alongside the fixes.