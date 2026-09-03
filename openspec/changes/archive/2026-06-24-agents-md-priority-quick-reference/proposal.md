## Why

After the q3-2026-oideachais-consolidation work (Sections A–D),
the `.agents/skills/` tree is 108 skills (consolidated from 158)
and the openspec archive has 11 new changes (skills governance
+ tooling). But the **AGENTS.md files** (root + 4 quadrants +
`infrastructure/` + `openspec/`) still reference the old state:

- The root `AGENTS.md` lists 14 skills in its "Agent Capabilities"
  table, but does not surface the 4 most-used skills
  (`motherduck`, `ccc`, `browser-tools`, `agent-observability`)
  at the top.
- The root `AGENTS.md` mentions the ccc + openspec commands in
  middle paragraphs, not at the top.
- The 4 quadrant `AGENTS.md` files have a "Related skills" section
  but it is buried below the overview.
- `infrastructure/AGENTS.md` lists 94 stacks in an inventory
  table but does not surface the 4 priority stacks (oideachais,
  litellm, langfuse, lakehouse) at the top.
- `openspec/AGENTS.md` lists 32 capability specs in a table but
  does not surface the 4 priority specs (`oideachais-pipeline`,
  `infrastructure-stacks`, `agent-memory-systems`,
  `dagger-pipelines`) at the top.

The user asked: "make sure that our skills and ccc and openspec
and priority packages and compose stacks and associated
commands are prominently outlined in our relevant agents.md
of our root and subdirectories."

This change adds a **Priority quick reference** section to the
TOP of each AGENTS.md (root + 4 quadrants + `infrastructure/` +
`openspec/`) that prominently surfaces:

1. The 5-10 priority skills for that file's audience
2. The ccc code search command
3. The 4 priority openspec commands
4. The 4-5 priority mise tasks
5. The 4-8 priority compose stacks (for `infrastructure/AGENTS.md`
   only — the root lists 4 priority stacks)
6. The 4-8 priority openspec specs (for `openspec/AGENTS.md`
   only)

The 6 new requirements (1 per file family) capture the rule:
"Every AGENTS.md MUST start with a 'Priority quick reference'
section that prominently surfaces the canonical skills, ccc,
openspec commands, and priority tools for that file's audience."

## What changes

- 6 new sections appended at the TOP of:
  - `/AGENTS.md` (root) — 1 section
  - `/sruth/oideachais/AGENTS.md` — 1 section
  - `/sruth/meaisinfhoghlaim/AGENTS.md` — 1 section
  - `/sruth/tuatha/AGENTS.md` — 1 section
  - `/sruth/croilar/AGENTS.md` — 1 section
  - `/infrastructure/AGENTS.md` — 1 section
  - `/openspec/AGENTS.md` — 1 section

Each section is a 1-page (≤ 50 lines) table-heavy quick reference
that an agent can read in 10 seconds.

## Out of scope

- Restructuring the existing "Agent Capabilities" /
  "Quick routing" / "Stack Inventory" sections in each
  file. Those are kept; the new "Priority" section is
  added at the top.
- Adding new skills (already covered by the consolidation
  work).
