## Why

`.agents/skills/` had **20 browser / scraping / agent-on-the-web
skills** (8 browser-* + 1 stagehand + 11 firecrawl-*). The 8 browser
skills (`browser`, `browser-to-api`, `browser-trace`, `browserbase-cli`,
`cookie-sync`, `autobrowse`, `safe-browser`, `ui-test`, `stagehand`)
all overlap with Firecrawl / Stagehand / Playwright / Browserbase,
but with no single routing skill an agent has to read all 8 to
figure out which is the right one.

The 11 `firecrawl-*` sub-skills (agent, crawl, download, interact,
map, monitor, parse, scrape, search, plus the canonical `firecrawl`
+ `firecrawl-cli`) are the upstream Firecrawl skill tree, useful
in isolation but polluting the discoverability of the canonical
`firecrawl` and `firecrawl-cli` (the 2 entry points KCG actually uses).

This change consolidates 20 → 3:

- `browser-tools` (NEW) — the router. Picks the right tool for
  the task (Stagehand / Firecrawl / crawl4ai / safe-browser / Playwright).
- `firecrawl` (KEEP, update) — the MCP variant. Cross-link to
  `browser-tools`.
- `firecrawl-cli` (KEEP, update) — the Bash CLI variant. Cross-link
  to `browser-tools`.

The 17 deleted skills:

- `browser`, `browser-to-api`, `browser-trace` — raw Playwright/CDP
  trace skills, content absorbed into `browser-tools`.
- `browserbase-cli` — CLI wrapper for Browserbase; absorbed into
  `stagehand` (which is also deleted — see below).
- `cookie-sync` — Browserbase cookie sync; absorbed into
  `browser-tools` §"KCG safety rules".
- `autobrowse` — autonomous browser loop; absorbed into
  `browser-tools` decision tree.
- `safe-browser` — constrained-agent pattern; absorbed into
  `browser-tools` §"KCG safety rules".
- `ui-test` — AI adversarial UI testing; absorbed into
  `browser-tools` (use Stagehand for adversarial).
- `stagehand` — Stagehand v3 docs; the content is small enough
  to live as a section in `browser-tools` §"When to use Stagehand
  v3 agent mode".
- `firecrawl-agent`, `firecrawl-crawl`, `firecrawl-download`,
  `firecrawl-interact`, `firecrawl-map`, `firecrawl-monitor`,
  `firecrawl-parse`, `firecrawl-scrape`, `firecrawl-search` —
  the 9 upstream Firecrawl endpoint-specific skills; their
  content is summarised in `browser-tools` decision tree and the
  `firecrawl` / `firecrawl-cli` skills.

## What changes

- `.agents/skills/browser-tools/SKILL.md` — NEW (the router)
- `.agents/skills/firecrawl/SKILL.md` — update frontmatter to
  cross-link to `browser-tools` + `firecrawl-cli`
- `.agents/skills/firecrawl-cli/SKILL.md` — update frontmatter to
  cross-link to `browser-tools` + `firecrawl`
- 17 sub-skill directories deleted
