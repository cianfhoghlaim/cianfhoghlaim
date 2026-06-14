---
title: 'Stagehand — AI Browser Operator: Reference & Skill Card'
domain: 'agents'
status: 'stable'
description: 'Stagehand is an open-source AI-powered browser automation framework by Browserbase. Uses natural language instructions to control a web browser — navigating pages, clicking elements, filling forms, extracting data — powered by LLM reasoning and computer vision. Full V3 reference (act, extract, observe, agent, DeepLocator, hybrid mode) + skill card with KCG context.'
read_when:
  - looking for documentation on this topic
updated: 2026-06-13
supersedes:
  - docs/agents/STAGEHAND_COMPREHENSIVE_REFERENCE.md
  - docs/agents/stagehand.md
truth: sole
ccc_query_hints:
  - stagehand ai browser operator
  - stagehand act extract observe agent
  - stagehand v3 browserbase
  - stagehand cua computer use agent
  - stagehand hybrid mode
---

# Stagehand — AI Browser Operator: Reference & Skill Card

> **Merged from 2 canonical sources**:
> - `STAGEHAND_COMPREHENSIVE_REFERENCE.md` (237 lines) — V3 reference
> - `stagehand.md` (53 lines) — skill card with KCG context

---

## Skill Card

### Overview

Stagehand is an open-source AI-powered browser automation framework by Browserbase. It uses natural language instructions to control a web browser — navigating pages, clicking elements, filling forms, and extracting data — powered by LLM reasoning and computer vision. The Python SDK provides `@browserbasehq/stagehand` for building AI-driven web agents.

### Why This Matters for Kings' College Galway

The curriculum ingestion pipeline's most fragile step is scraping Irish government education websites. The SEC (State Examinations Commission), NCCA (National Council for Curriculum and Assessment), and Department of Education websites have inconsistent structures, JavaScript-rendered content, and CAPTCHA protections. Stagehand replaces brittle CSS-selector-based scrapers with AI-driven navigation — it "sees" the page like a human, finds the "Download Exam Paper" button by visual understanding, and handles multi-step login/download flows that traditional scrapers fail on.

### Key Features

- **Natural language control** — `page.act("click the download button for 2024 exam papers")`
- **Computer vision** — Understands page layout visually, not via selectors
- **Self-healing** — Adapts to website changes without code updates
- **Structured extraction** — `page.extract("list all exam papers with years and subjects")`
- **Browserbase integration** — Cloud browsers with residential proxies and CAPTCHA solving

### Installation

```bash
uv add stagehand-py
```

### Integration with Our Stack

Stagehand is the "Operator" in the browser automation stack (Stagehand → Crawl4AI → Skyvern). It handles complex interactive scraping for curriculum sources. DLT sources use Stagehand for authenticated and JavaScript-heavy government websites. Browserbase provides the cloud browser infrastructure.

### Upstream

- **Repository**: <https://github.com/browserbase/stagehand>
- **Documentation**: <https://docs.stagehand.dev>
- **Latest**: Active development — natural language `act`/`extract`/`observe` methods, improved vision models, Browserbase integration

### Screenshot

Stagehand is a programmatic SDK. The `stagehand.dev` docs show code examples with the `act()`, `extract()`, and `observe()` APIs. The Browserbase session replay shows the browser in action as Stagehand navigates and interacts. DLT pipeline logs show Stagehand extraction results as structured JSON output.

---

## Stagehand V3: AI-Powered Browser Automation Reference

### Overview

Stagehand is a browser automation framework from Browserbase with AI-powered `act`, `extract`, `observe`, and `agent` methods. It is a monorepo containing:

- **core** - Main Stagehand package
- **evals** - Evals CLI for testing
- **docs** - Documentation at docs.stagehand.dev

The main class is imported as `Stagehand` from `@browserbasehq/stagehand`.

**Key Classes:**
- `Stagehand`: Main orchestrator providing `act`, `extract`, `observe`, and `agent`
- `context`: `V3Context` object managing browser contexts and pages
- `page`: Individual page objects via `stagehand.context.pages()[i]` or `stagehand.context.newPage()`

### Initialize

```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
  env: "LOCAL",       // or "BROWSERBASE"
  verbose: 2,         // 0, 1, or 2
  model: "openai/gpt-4.1-mini",
});

await stagehand.init();
const page = stagehand.context.pages()[0];
const page2 = await stagehand.context.newPage();
```

### Act — Atomic Actions

Actions are called on the `stagehand` instance. Use atomic, specific instructions.

```typescript
await stagehand.act("click the sign in button");
await stagehand.act("click the sign in button", { page: page2 });

// ✅ Good: "Click the sign in button", "Type 'hello' into the search input"
// ❌ Bad: "Order me pizza", "Type in the search bar and hit enter"
```

**Observe + Act Pattern (Recommended):**
```typescript
const actions = await stagehand.observe("Click the sign in button");
await stagehand.act(actions[0]);
```

### Extract — Data Extraction

```typescript
import { z } from "zod/v3";

// With schema
const data = await stagehand.extract(
  "extract all apartment listings with prices and addresses",
  z.object({
    listings: z.array(z.object({
      price: z.string(),
      address: z.string(),
    })),
  }),
);

// Simple (no schema)
const { extraction } = await stagehand.extract("extract the sign in button text");

// Targeted element
const reason = await stagehand.extract(
  "extract the reason why script injection fails",
  z.string(),
  { selector: "/html/body/div[2]/div[3]/iframe/html/body/p[2]" },
);

// URL extraction
const { links } = await stagehand.extract(
  "extract all navigation links",
  z.object({ links: z.array(z.string().url()) }),
);
```

### Agent — Autonomous Execution

```typescript
// Basic agent
const agent = stagehand.agent({
  model: "google/gemini-2.0-flash",
});
const result = await agent.execute({
  instruction: "Search for the stock price of NVDA",
  maxSteps: 20,
});

// Computer Use Agent (CUA)
const cuaAgent = stagehand.agent({
  cua: true,
  model: "anthropic/claude-sonnet-4-20250514",
});
await cuaAgent.execute({
  instruction: "Apply for a library card at the San Francisco Public Library",
  maxSteps: 30,
});

// Agent with MCP integrations
const mcpAgent = stagehand.agent({
  integrations: [`https://mcp.exa.ai/mcp?exaApiKey=${process.env.EXA_API_KEY}`],
});
```

### Agent Modes

| Mode | Description | Models Required |
|------|-------------|-----------------|
| `"dom"` (default) | DOM-based tools (act, fillForm) | Any model |
| `"hybrid"` | DOM + coordinate-based (act, click, type, dragAndDrop) | gemini-3-flash-preview, claude-sonnet-4 |
| `"cua"` | Computer Use Agent providers | claude-sonnet-4, gemini-2.5-computer-use |

**Hybrid Mode:**
```typescript
const stagehand = new Stagehand({
  env: "LOCAL",
  experimental: true,  // Required for hybrid mode
});
await stagehand.init();

const agent = stagehand.agent({
  mode: "hybrid",
  model: "google/gemini-3-flash-preview",
});
await agent.execute({
  instruction: "Click the submit button and fill the form",
  maxSteps: 20,
  highlightCursor: true,
});
```

### Advanced Features

**DeepLocator (XPath Targeting):**
```typescript
await page
  .deepLocator("/html/body/div[2]/div[3]/iframe/html/body/p")
  .highlight({
    durationMs: 5000,
    contentColor: { r: 255, g: 0, b: 0 },
  });
```

**Multi-Page Workflows:**
```typescript
const page1 = stagehand.context.pages()[0];
await page1.goto("https://example.com");
const page2 = await stagehand.context.newPage();
await page2.goto("https://example2.com");
await stagehand.act("click button", { page: page1 });
await stagehand.extract("get title", { page: page2 });
```

### Next.js Integration

Stagehand can run in Next.js server environments for server-side browser automation:

```typescript
// app/api/browse/route.ts
import { Stagehand } from "@browserbasehq/stagehand";

export async function POST(req: Request) {
  const { url } = await req.json();
  const stagehand = new Stagehand({ env: "BROWSERBASE" });
  await stagehand.init();
  const page = stagehand.context.pages()[0];
  await page.goto(url);
  const result = await stagehand.extract("extract the page title");
  await stagehand.close();
  return Response.json(result);
}
```

### Package Structure

```
stagehand/
├── core/          # Main Stagehand V3 package
│   └── examples/  # Example usage patterns
├── evals/         # Evals CLI for benchmarking
├── docs/          # Documentation site
├── server/        # Server-side utilities
└── packages/      # Published packages
    ├── core/      # @browserbasehq/stagehand
    ├── evals/     # @browserbasehq/evals
    ├── docs/      # @browserbasehq/docs
    └── server/    # @browserbasehq/stagehand-server
```

**Key Dependencies:**
- `@browserbasehq/stagehand` — main package
- `zod` — schema validation for extraction
- Playwright — browser automation backend

**Resources:** https://docs.stagehand.dev | https://github.com/browserbase/stagehand
