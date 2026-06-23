---
name: stagehand
description: AI browser operator (Browserbase) — natural-language act/extract/observe, CUA computer-use agent, hybrid mode, DeepLocator XPath targeting, multi-page workflows. Use when scraping authenticated or JS-heavy government sites (SEC, NCCA, Dept. of Ed), building multi-step browser workflows, or when firecrawl/crawl4ai can't get the data.
---

# Stagehand V3

## When to use this skill

Use when you need to:

- "Scrape a site that requires login (NCCN portal, SEC EDGAR)"
- "Fill a multi-step government form (e.g. Department of Ed)
  with an LLM"
- "Extract structured data from a page that has no schema"
  (DeepLocator, Zod-typed extract)
- "Run an autonomous browser agent (CUA mode) when
  Crawl4AI / Firecrawl can't"
- "Build a multi-page workflow that branches on what's
  on each page"

## Overview

[Stagehand](https://stagehand.dev/) is the AI browser
operator from Browserbase. V3 (current) provides 4 main
primitives:

- **act** — atomic natural-language browser action ("click
  the 'Sign In' button")
- **observe** — return all possible actions + their element
  descriptors, with optional deepLocator XPath targeting
- **extract** — typed extraction (with or without a Zod
  schema), with optional target element + URL
- **agent** — autonomous multi-step execution with branching
  ("sign in, then navigate to /orders, then extract the
  table for customer X")

V3 adds:

- **CUA (computer-use agent)** mode — full Claude/Gemini
  computer-use for sites that fight the structured model
- **Hybrid mode** — DOM-targeted (fast, cheap) + computer-use
  (slow, accurate) on the same step
- **DeepLocator** — XPath-aware targeting for dynamic / shadow
  DOM elements that the DOM model can't see

## Package layout

The V3 SDK is published as 4 separate npm packages (per
`@browserbasehq/stagehand` README):

| Package | Purpose |
|:--|:--|
| `@browserbasehq/stagehand` | Core SDK (TypeScript) |
| `@browserbasehq/stagehand-core` | Lower-level driver (no LLM) |
| `@browserbasehq/stagehand-evals` | Eval suite for the SDK |
| `@browserbasehq/stagehand-server` | Server-side (Next.js / Workers) |
| `@browserbasehq/stagehand-docs` | Source for `stagehand.dev` |

For the KCG stack, the canonical install is via the
`infrastructure/stacks/stagehand` Compose stack
(which pins `@browserbasehq/stagehand@^3.0.0`).

## Initialize

```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
  env: "BROWSERBASE",  // or "LOCAL" for local Chromium
  model: {
    modelName: "gpt-4o",
    modelClientOptions: { apiKey: process.env.OPENAI_API_KEY },
  },
  verbose: 1,  // 0=silent, 1=info, 2=debug
});

await stagehand.init();
const page = await stagehand.context.newPage();
```

`env: "LOCAL"` runs a local Chromium (via `patchright-core` for
anti-bot). `env: "BROWSERBASE"` runs in Browserbase's cloud
(residential proxies, CAPTCHA solving, 150+ geolocations).

## Act — atomic natural-language actions

```typescript
await page.act("Click the 'Sign In' button");
await page.act("Type 'cianmac' into the username field");
await page.act("Type '...' into the password field and press Enter");
await page.act("Wait for the dashboard to load");
await page.act("Click the 'Curriculum' link in the main nav");
```

The LLM picks the right DOM element. The action is observed
visually, then executed.

## Observe + Act pattern (recommended)

```typescript
// First, see what's on the page
const observations = await page.observe();
for (const obs of observations) {
  console.log(`[${obs.method}] ${obs.description} (selector: ${obs.selector})`);
}

// Then act on a specific observation
const login = observations.find(o => o.description.includes("Sign In"));
if (login) {
  await page.act(login);  // use the observation directly
}
```

This pattern is more reliable than `act("Click Sign In")`
because you're not re-asking the LLM to find the same element.

## Extract — with / without Zod schema

```typescript
import { z } from "zod";

const curriculum = await page.extract({
  instruction: "Extract the curriculum area, strands, and learning outcomes",
  schema: z.object({
    area: z.string(),
    strands: z.array(z.string()),
    learning_outcomes: z.array(z.string()),
  }),
});
// curriculum.area, curriculum.strands, ...
```

Without a schema, the extraction is free-text and returned as
a string. **Always pass a Zod schema in production.**

## Agent — autonomous multi-step execution

```typescript
const agent = stagehand.agent({
  model: "gpt-4o",
  mode: "dom",  // or "hybrid" or "cua"
  integrations: [
    /* MCP servers, custom tools */
  ],
});

const result = await agent.execute({
  instruction: `
    Sign in with these credentials.
    Navigate to /orders.
    Extract the order history for customer cianmac.
    If the page requires a CAPTCHA, raise an error.
  `,
  maxSteps: 20,
});
```

### Agent modes

| Mode | Models | Use case |
|:--|:--|:--|
| `dom` (default) | Any | Most pages; uses DOM + accessibility tree |
| `hybrid` | `gemini-3-flash`, `claude-sonnet-4` | Mixes DOM targeting with computer-use for tricky elements |
| `cua` | `claude-sonnet-4`, `gemini-2.5-computer-use` | Full computer-use; slow + expensive; fallback for sites that fight DOM |

**Recommendation:** start with `dom`. Escalate to `hybrid`
when the DOM model fails (e.g. shadow DOM, custom widgets).
Escalate to `cua` only as a last resort.

## DeepLocator (XPath targeting)

For elements that the DOM model can't see (shadow DOM, dynamic
content, custom widgets), use the DeepLocator to specify the
exact element:

```typescript
await page.act({
  action: "Click the Submit button",
  deepLocator: [
    { role: "form" },
    { name: "submit" },
    { xpath: "/html/body/div[1]/form/button[2]" },
  ],
});
```

The DeepLocator walks the tree from the root, trying each
descriptor in order. The first match wins.

## Multi-page workflows

The agent handles branching naturally:

```typescript
const result = await agent.execute(`
  1. Sign in with username 'cianmac' and password '...'
  2. On the dashboard, click 'Curriculum'
  3. If the page shows a 'Year' dropdown, select '2024'
  4. Extract the table as a list of {subject, strands, outcomes}
  5. If no data is found, return an empty list (do not error)
`);
```

The agent reasons about each step, decides what to do next,
and returns the structured result.

## Next.js server route

For server-side use (e.g. a Dagster asset that calls Stagehand
via HTTP), expose a Next.js route:

```typescript
// app/api/scrape/route.ts
import { Stagehand } from "@browserbasehq/stagehand";

export async function POST(req: Request) {
  const { url, instruction } = await req.json();
  const stagehand = new Stagehand({ env: "BROWSERBASE", model: "gpt-4o" });
  await stagehand.init();
  const page = await stagehand.context.newPage();
  await page.goto(url);
  const result = await page.extract({ instruction, schema: /* ... */ });
  await stagehand.close();
  return Response.json(result);
}
```

## KCG integration

The KCG browser-automation stack is a fallback ladder:

```
   ┌──────────────┐
   │  firecrawl   │  ← primary (cheap, fast, no JS)
   │  -mcp        │
   └──────┬───────┘
          │ fails (login, JS-heavy, anti-bot)
          ▼
   ┌──────────────┐
   │  sruth-browser│  ← secondary (Playwright via patchright)
   │  + patchright │
   └──────┬───────┘
          │ fails (CAPTCHA, advanced anti-bot)
          ▼
   ┌──────────────┐
   │  stagehand   │  ← tertiary (LLM-driven; CUA mode)
   │  + browserbase│
   └──────┬───────┘
          │ fails (worst case)
          ▼
   ┌──────────────┐
   │   skyvern    │  ← quaternary (different AI; last resort)
   └──────────────┘
```

The Stagehand step in the ladder kicks in for authenticated
sites (e.g. UoG student portal, SEC EDGAR), JS-heavy
single-page apps (e.g. an internal admin tool), and sites
with aggressive bot detection.

## Chrome DevTools MCP (round-9 reference)

The `chrome-devtools-mcp` server (459-line GitHub README
preserved as a clipping) is a related-but-distinct
browser-automation tool to Stagehand. The differences:

| Tool | When to use |
|:--|:--|
| **chrome-devtools-mcp** | A coding agent (Claude, Aider, etc.) needs to debug a running app — take screenshots, read console logs, inspect DOM, profile performance. MCP server, lives in the agent's tool surface. |
| **Stagehand** | The agent (or a human) needs to *navigate*, *act*, or *extract* from a third-party site autonomously. V3 SDK with `act` / `observe` / `extract` / `agent` primitives. |

**KCG use of chrome-devtools-mcp:** the
`sruth-browser` skill + the `sruth-browser` MCP server
expose the same primitives for **debugging KCG frontends
in dev**. An agent can `mcp.call("chrome-devtools",
"take_screenshot", { url: "http://localhost:3000/curriculum" })`
and read the resulting PNG to verify a UI change. This
is the canonical "verify the agent's work" loop.

**KCG use of Stagehand:** for the browser-automation
fallback in the scraping ladder
(`firecrawl → sruth-browser → stagehand → skyvern`).
The Stagehand step kicks in for authenticated sites
(UoG student portal, SEC EDGAR), JS-heavy SPAs, and
aggressive bot detection — see §"KCG integration" for
the full ladder.

The two are **complementary, not competing**: Chrome
DevTools MCP for "look at this app", Stagehand for
"navigate that app".

See `references/clippings/chrome-devtools-mcp.md` for
the full upstream README and the complete slim-tool
reference.

## Resources

- Stagehand docs: <https://stagehand.dev/>
- V3 API reference: <https://stagehand.dev/v3/api>
- `@browserbasehq/stagehand` on npm
- Browserbase cloud: <https://www.browserbase.com/>
- KCG stack: `infrastructure/stacks/stagehand/`
- Related skills: `.agents/skills/browser/`,
  `.agents/skills/crawl4ai/SKILL.md`, `.agents/skills/firecrawl/`,
  `.agents/skills/cookie-sync/`
