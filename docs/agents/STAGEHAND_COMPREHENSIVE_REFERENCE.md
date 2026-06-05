# Stagehand Comprehensive Reference: Browser Automation with AI

## Merged From
- `stagehand/README.md` + `stagehand/claude.md`
- `stagehand/core/README.md` + `stagehand/core/CHANGELOG.md`
- `stagehand/packages/core/README.md` + `stagehand/packages/core/CHANGELOG.md`
- `stagehand/packages/evals/README.md` + `stagehand/packages/evals/CHANGELOG.md`
- `stagehand/packages/docs/README.md`
- `stagehand/packages/server/README.md` + `stagehand/packages/server/CHANGELOG.md`
- `stagehand/packages/README.md`
- `stagehand/evals/README.md` + `stagehand/evals/CHANGELOG.md`
- `stagehand/docs/README.md`
- `stagehand/CHANGELOG.md` + `stagehand/core/examples/CHANGELOG.md`

---

## Stagehand V3: AI-Powered Browser Automation

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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
