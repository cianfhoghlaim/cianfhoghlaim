## Why

After the spaces cleanup (A1 + A2 + A3 — the BAML canonical
promotion, the LiteLLM gateway rewrite, and the anti-phish
archive), the 5 active Spaces + the 1 archived Space have no
AGENTS.md files. Each Space has a `README.md` (the HF Space
README) but no developer-quick-reference routing table.

The 7 main monorepo AGENTS.md files (root + 4 quadrants + openspec +
infrastructure) all have a "Priority quick reference" section at
the top per the `agents-md-priority-quick-reference` change. The
Spaces are out of step with this convention.

This change adds 8 AGENTS.md files (1 per Space + 1 per shared
bundle + 1 parent), each starting with a "Priority quick
reference" section that prominently surfaces the canonical
skills, the ccc + openspec commands, and the openspec specs most
relevant to that Space.

The 6 new files (per the agents-md-priority-quick-reference
"Priority quick reference section in every AGENTS.md" Requirement):

1. `spaces/AGENTS.md` — the 4 active Spaces + 1 archived + 5 priority skills
2. `spaces/_common/AGENTS.md` — the 5 shared modules + 3 priority skills
3. `spaces/an_scrudu/AGENTS.md` — the past-paper heatmap + `ExtractCircularMeta` BAML
4. `spaces/meaisin_cliste/AGENTS.md` — the 3 Celtic AI tools + `CompareCelticNations` BAML
5. `spaces/cianfhoghlaim/AGENTS.md` — the Hades-style RPG + `GenerateNpcDialogue` BAML
6. `spaces/anam_tuatha/AGENTS.md` — the integration Space + `GenerateExitCardQuestions` BAML
7. `spaces/data-engineering/AGENTS.md` — the PyPI analytics dashboard (Dagster + dbt + Evidence)

Plus an 8th file (1 parent + 1 shared + 5 per-Space = 7 actually; I had an off-by-one). The `spaces/AGENTS.md` is the parent.

## What changes

- 7 new AGENTS.md files (each <= 60 lines, table-heavy, top of file)
- 1 ADDED Requirement to the `infrastructure-stacks` spec
  ("Priority quick reference section in every Spaces AGENTS.md")

## Out of scope

- Per-Space modernization (C1-C4) — separate changes
- The Spaces README.md (the HF Space README) is left untouched
- The data-engineering Space modernization (E1-E2) — separate changes
