## Why

The 2026-09-02 skills-refresh audit (recorded in this change's
`design.md`) found 7 defects in the `.agents/skills/` surface:
oversized skill descriptions that the agent-platform splits on,
unclosed YAML frontmatter blocks (silently swallowing the rest of the
file), missing routers for nested-skill packs (`copilotkit/skills/`,
`pydantic/`), unescaped `: ` colons in description fields breaking
YAML parse, and the `openspec` skill still describing openspec 1.4
instead of the now-installed 1.11. None block runtime, but they make
the skill surface noisier for agents and break the
`mise run lint:skills` gate on a non-trivial subset.

## What Changes

- Rewrite `.agents/skills/openspec/SKILL.md` for openspec 1.11 with
  corrected schema/profile framing and verified counts.
- Fix YAML frontmatter defects in skills whose descriptions contain
  unescaped `: ` or have no closing `---`.
- Add the 2 missing routers (or upgrade placeholder content to a real
  router) for the `copilotkit` and `pydantic` skill packs.
- Trim oversized skill descriptions to fit the 200-char agent-platform
  recommendation.
- Add a `mise run lint:skills-frontmatter` gate that validates every
  skill's frontmatter round-trips through a YAML parser (catches the
  unescaped-colon class of defect automatically).

## Capabilities

### New Capabilities
(none — pure skill/docs refactor)

### Modified Capabilities
(none)

## Dependencies

`Blocked by: none`
`Blocked by (soft): openspec-1-11-migration` (so the openspec 1.11
setup is in place before this change's `openspec/SKILL.md` rewrite)
`Affected repos: cianfhoghlaim`