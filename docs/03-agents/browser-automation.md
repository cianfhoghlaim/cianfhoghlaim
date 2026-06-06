---
title: "Browser Automation & Web Scraping"
domain: agents
status: stable
description: "Consolidated reference for browser automation: Browserbase cloud infrastructure, Stagehand V3 AI-powered agents, Firecrawl APIs, and multi-agent deep research with Smolagents."
supersedes:
  - docs/agents/browser-automation.md
  - docs/agents/BROWSER_AUTOMATION_PLATFORM.md
  - docs/agents/STAGEHAND_COMPREHENSIVE_REFERENCE.md
  - docs/agents/Agentic Web Scraping Pipeline.md
entities:
  - Browserbase
  - Stagehand
  - StagehandAgent
  - FirecrawlAgent
  - SmolagentsCoordinator
  - CDPScreenshot
related_skills:
  - .agents/skills/browser/SKILL.md
  - .agents/skills/firecrawl/SKILL.md
  - .agents/skills/firecrawl-agent/SKILL.md
  - .agents/skills/firecrawl-scrape/SKILL.md
  - .agents/skills/firecrawl-crawl/SKILL.md
  - .agents/skills/firecrawl-search/SKILL.md
ccc_query_hints:
  - "Stagehand act extract observe agent API"
  - "Browserbase CDP screenshot capture"
  - "Firecrawl agent autonomous web research"
  - "multi-agent deep research smolagents firecrawl"
  - "how to run browser automation in the cloud"
last_reviewed: 2026-06-06
---

# Browser Automation & Web Scraping

## Part I: Browserbase — Cloud Browser Infrastructure

### Overview

Browserbase provides cloud browser infrastructure for reliable web automation with stealth and anti-bot features. Supports TypeScript (Node.js) and Python.

### Core Features

| Feature | Description |
|---|---|
| Cloud Browsers | Run automation in the cloud — no local browser needed |
| Stealth Mode | Anti-bot detection avoidance |
| Session Management | Persistent browser sessions and contexts |
| CAPTCHA Solving | Automatic CAPTCHA resolution via `waitForCaptchaSolves` |
| Proxies | Residential and datacenter proxy configuration |
| Screenshots | CDP-based and Playwright-based capture |
| Downloads/Uploads | File transfer within browser sessions |

### Setup

```bash
git clone https://github.com/browserbase/playbook.git
cd playbook
npm install          # TypeScript
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt  # Python
```

**Environment:**
```
BROWSERBASE_PROJECT_ID=your_project_id
BROWSERBASE_API_KEY=your_api_key
```

### CDP Screenshot Capture (Python)

```python
from playwright.sync_api import sync_playwright
from browserbase import Browserbase

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(bb.sessions.connect_url(session.id))
    page = browser.contexts[0].pages[0]
    page.goto(url, timeout=60000)
    page.wait_for_load_state("networkidle")
    # High-performance CDP screenshot
    client = browser.contexts[0].new_cdp_session(page)
    res = client.send("Page.captureScreenshot", {
        "format": "png", "fullpage": True, "captureBeyondViewport": True
    })
```

### Cookie Sync

Sync cookies from local Chrome to a Browserbase persistent context to access authenticated sites. See `.agents/skills/cookie-sync/SKILL.md`.

### Project Structure (Node Playbook)

```
playbook/node/
├── stagehand/       # Stagehand-based automation
│   ├── _tools/      # Shared utilities
│   ├── research/    # Research agents
│   ├── complete_task/ # Task completion
│   └── authenticate/  # Authentication flows
├── playwright/      # Playwright-based automation
│   ├── _tools/
│   ├── research/
│   ├── complete_task/
│   └── authenticate/
└── useful_browserbase_functions.ts  # Shared utilities
```

---

## Part II: Stagehand V3 — AI-Powered Browser Automation

### Overview

Stagehand is a browser automation framework from Browserbase with AI-powered `act`, `extract`, `observe`, and `agent` methods. V3 removes internal Playwright dependency, adds 20-40% speed increases, bun compatibility, and simplified extract schemas.

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

### Core Methods

#### `act` — Atomic Actions

Use atomic, specific instructions. Recommended pattern: Observe + Act.

```typescript
await stagehand.act("click the sign in button");
await stagehand.act("click the sign in button", { page: page2 });

// Recommend: Observe + Act
const actions = await stagehand.observe("Click the sign in button");
await stagehand.act(actions[0]);

// Good: "Click the sign in button", "Type 'hello' into the search input"
// Bad:  "Order me pizza", "Type in the search bar and hit enter"
```

#### `extract` — Data Extraction

```typescript
import { z } from "zod/v3";

// With schema
const data = await stagehand.extract(
  "extract all apartment listings with prices and addresses",
  z.object({
    listings: z.array(z.object({ price: z.string(), address: z.string() })),
  }),
);

// Simple (no schema)
const { extraction } = await stagehand.extract("extract the sign in button text");

// Targeted element via xpath
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

#### `agent` — Autonomous Execution

Three agent modes:

| Mode | Description | Models Required |
|---|---|---|
| `"dom"` (default) | DOM-based tools (act, fillForm) | Any model |
| `"hybrid"` | DOM + coordinate-based (act, click, type, dragAndDrop) | gemini-3-flash-preview, claude-sonnet-4 |
| `"cua"` | Computer Use Agent providers | claude-sonnet-4, gemini-2.5-computer-use |

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

// Hybrid mode (requires experimental: true)
const stagehand = new Stagehand({ env: "LOCAL", experimental: true });
const hybridAgent = stagehand.agent({
  mode: "hybrid",
  model: "google/gemini-3-flash-preview",
});
```

### Advanced Features

**DeepLocator (XPath Targeting):**
```typescript
await page
  .deepLocator("/html/body/div[2]/div[3]/iframe/html/body/p")
  .highlight({ durationMs: 5000, contentColor: { r: 255, g: 0, b: 0 } });
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

**Next.js Integration:**
```typescript
// app/api/browse/route.ts
export async function POST(req: Request) {
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
├── evals/         # Evals CLI for benchmarking
├── docs/          # Documentation site
├── server/        # Server-side utilities
└── packages/      # Published packages
    ├── core/      # @browserbasehq/stagehand
    ├── evals/     # @browserbasehq/evals
    ├── docs/      # @browserbasehq/docs
    └── server/    # @browserbasehq/stagehand-server
```

---

## Part III: Smolagents + Firecrawl Deep Research

### Architecture

A multi-agent deep research system combining HuggingFace Smolagents with Firecrawl MCP tools:

| Component | File | Role |
|---|---|---|
| Planner | `planner.py` | Drafts research strategy using open model |
| Task Splitter | `task_splitter.py` | Decomposes plan into JSON-schema-validated subtasks |
| Coordinator | `coordinator.py` | Orchestrates sub-agents, synthesizes final report |
| Sub-Agents | (spawned dynamically) | Each researches one subtask using Firecrawl MCP tools |

### Core Pattern

```python
from smolagents import CodeAgent, LiteLLMModel

model = LiteLLMModel(model_id="openai/gpt-4o")
agent = CodeAgent(tools=[firecrawl_tool], model=model)
result = agent.run("Research the latest developments in AI education")
```

### Firecrawl MCP Integration

```python
FIRECRAWL_API_KEY = os.environ["FIRECRAWL_API_KEY"]
MCP_URL = f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp"

with MCPClient({"url": MCP_URL, "transport": "streamable-http"}) as mcp_tools:
    @tool
    def initialize_subagent(subtask_id, subtask_title, subtask_description):
        subagent = ToolCallingAgent(tools=mcp_tools, model=subagent_model)
        return subagent.run(subagent_prompt)
```

### Pipeline Flow

```
User Query → Planner (research strategy)
           → Task Splitter (3-8 non-overlapping subtasks)
           → Coordinator (spawns one sub-agent per subtask)
           → Sub-Agents (search + scrape via Firecrawl MCP)
           → Coordinator (synthesizes into markdown report)
           → research_result.md
```

### Setup

```bash
export HF_TOKEN=...
export FIRECRAWL_API_KEY=...
uv sync
uv run main.py
```

### Centralized Prompt Architecture

All prompts live in `prompts.py`: PLANNER, TASK_SPLITTER, SUBAGENT, COORDINATOR. Tweak one file to affect all agents — enables A/B testing by toggling templates.

---

## Part IV: Firecrawl Agent API

### Autonomous Web Research

Firecrawl `/agent` is an autonomous web research endpoint — no URL required, just describe what you need:

```json
{
  "prompt": "Find the top 5 AI startups founded in 2024 and their funding amounts",
  "schema": {
    "type": "object",
    "properties": {
      "startups": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "funding": { "type": "string" },
            "founded": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### Firecrawl Tool Matrix

| API | Purpose | Best For |
|---|---|---|
| `/scrape` | Single-page extraction | Known URL |
| `/crawl` | Multi-page extraction | Site sections |
| `/map` | URL discovery | Finding pages |
| `/search` | Web search + scrape | Open-ended research |
| `/agent` | Autonomous research | Complex multi-source tasks |
| MCP Server | Tools for agents | Smolagents, ADK, Agno integration |

---

## Scraping Pattern Decision Matrix

| Scenario | Recommended Tool |
|---|---|
| Known URL, need specific data | Stagehand `extract` with zod schema |
| Known URL, need interaction | Stagehand `agent` (dom mode) |
| Multi-step form, protected site | Stagehand CUA (claude-sonnet-4) |
| Unknown sources, open research | Smolagents + Firecrawl MCP |
| Bulk site crawl | Firecrawl `/crawl` |
| CDP-level control | Browserbase direct CDP |
| Authenticated browsing | Cookie sync → Browserbase context |
| CAPTCHA-protected sites | Browserbase `waitForCaptchaSolves` |

## Resources

- Browserbase: https://docs.browserbase.com
- Stagehand: https://docs.stagehand.dev | https://github.com/browserbase/stagehand
- Firecrawl: https://docs.firecrawl.dev
- Smolagents: https://github.com/huggingface/smolagents
