---
truth: partial
---

# Browser Automation Platform Reference

## Merged From
- `browserbase/README.md`
- `browserbase/node/README.md`
- `smolagents/firecrawl-deepresearch/README.md` + `docs/blog-post.md`
- `AGENT_IMPLEMENTATIONS_SUMMARY.md`
- `Agent UI Ecosystem - A2UI.md`

---

## Part I: Browserbase — Cloud Browser Infrastructure

Browserbase provides cloud browser infrastructure for reliable web automation with stealth and anti-bot features.

### Features
- Cloud browser automation
- Stealth and anti-bot detection avoidance
- Session management and contexts
- Downloads, uploads, screenshots
- Proxy and captcha solving configuration

### Setup

```bash
git clone https://github.com/browserbase/playbook.git
cd playbook
npm install  # for TypeScript
python -m venv venv && pip install -r requirements.txt  # for Python
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
    # CDP high-performance screenshot
    client = browser.contexts[0].new_cdp_session(page)
    res = client.send("Page.captureScreenshot", {
        "format": "png", "fullpage": True, "captureBeyondViewport": True
    })
```

---

## Part II: Smolagents + Firecrawl Deep Research

An agentic deep research system combining HuggingFace Smolagents with Firecrawl for autonomous web research.

```python
from smolagents import CodeAgent, LiteLLMModel
model = LiteLLMModel(model_id="openai/gpt-4o")
agent = CodeAgent(tools=[firecrawl_tool], model=model)
result = agent.run("Research the latest developments in AI education")
```

The agent autonomously plans searches, extracts data, and synthesizes findings into structured reports.

---

## Part III: CopilotKit Framework

CopilotKit is a monorepo-based framework for building AI copilots with React/Next.js integration.

### Package Structure
```
CopilotKit/packages/
├── react-core/          # Core React hooks and context
├── react-textarea/      # Textarea component integration
├── react-ui/            # Pre-built UI components
├── runtime/             # Backend runtime
├── runtime-client-gql/  # GraphQL client
├── sdk-js/              # JavaScript SDK
└── shared/              # Shared types
```

### Core Context (CopilotContext)
- `actions`: Frontend actions registry
- `coAgentStateRenders`: Co-agent state rendering
- `chatComponentsCache`: Cached action components
- `coagentStates`: Agent state tracking
- `threadId/runId`: Session management
- `extensions`: MCP server extensions
- `langGraphInterruptAction`: LangGraph user input interrupts

### Action System
```typescript
export type FrontendAction<T extends Parameter[] | [] = []> = Action<T> & {
  name: string;
  available?: "disabled" | "enabled" | "remote" | "frontend";
  pairedAction?: string;
  render?: string | ((props: ActionRenderProps<T>) => React.ReactElement);
  renderAndWaitForResponse?: (props: ActionRenderPropsWait<T>) => React.ReactElement;
};
```

---

## Part IV: A2UI — Agent UI Ecosystem

A2UI is a streaming protocol for Agent-Driven User Interfaces — JSON messages sent to the client, rendered into native UI components by a renderer. Makes UIs "secure like data, expressive like code."

**Host Application Frameworks:**
- AG UI / CopilotKit
- Vercel AI SDK
- GenUI SDK for Flutter (already uses A2UI)
- Pydantic AI AG-UI integration

**Platform-Specific Ecosystems:**
- OpenAI ChatKit
- Google ADK AG-UI
- CopilotKit AG-UI

---

## Part V: AgentOS (Agno Platform Integration)

Modern chat interface for AgentOS instances with Agno platform integration. Provides:
- REST API for agent execution
- SSE streaming for real-time responses
- Multimodal input support
- Team coordination interfaces
