---
title: "MCP Servers & Protocol Reference"
domain: agents
status: stable
description: "Consolidated reference for the Model Context Protocol (MCP): specification, Python/TypeScript SDKs, server implementations, Claude Code integration, authentication (OAuth, x402, SIWE), MCP-UI, and security best practices."
supersedes:
  - docs/agents/MCP_COMPREHENSIVE_RESEARCH.md
  - docs/agents/MCP Toolbox.md
  - docs/agents/MCP-UI.md
  - docs/agents/MCP_RESEARCH.md
  - docs/agents/MCP _ Better Auth.md
  - docs/agents/MCP Server with x402.md
  - docs/agents/MCP Server.md
  - docs/agents/mcp-ui-gradio-evidence-integration-analysis.md
  - docs/agents/mcp-research-report.md
  - docs/agents/Agent _ Firecrawl.md
  - docs/agents/Sign In With Ethereum (SIWE) _ Better Auth.md
  - docs/agents/x402_examples_typescript_servers_hono at main · coinbase_x402.md
entities:
  - MCPHost
  - MCPClient
  - MCPServer
  - FastMCP
  - MCPTool
  - MCPResource
  - MCPPrompt
  - MCPUIResource
  - x402Payment
  - BetterAuthPlugin
related_skills:
  - .agents/skills/mcp-builder/SKILL.md
  - .agents/skills/browser/SKILL.md
  - .agents/skills/firecrawl/SKILL.md
ccc_query_hints:
  - "MCP server Python FastMCP example"
  - "MCP Claude Code integration HTTP transport"
  - "MCP-UI Gradio Evidence integration"
  - "x402 MCP payment protocol"
  - "MCP OAuth authentication best practices"
  - "how to build an MCP server"
last_reviewed: 2026-06-06
truth: partial

---

# MCP Servers & Protocol Reference

## Part I: MCP Fundamentals

### What is MCP?

The Model Context Protocol (MCP) is an **open-source standard** developed by Anthropic for connecting AI applications to external systems. It provides a universal interface for AI models to interact with data sources, tools, and services — functioning as "USB-C for AI."

**Key Characteristics:**
- **Open Standard:** Developed by Anthropic, supported by OpenAI, DeepMind, Microsoft
- **Protocol Foundation:** Built on JSON-RPC 2.0
- **Universal Connector:** Single interface for multiple integrations
- **Bidirectional Communication:** Requests, responses, notifications
- **Transport Agnostic:** Works over stdio, HTTP, SSE, WebSockets

### Three-Component Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   MCP Host  │ ◄─────► │ MCP Client  │ ◄─────► │ MCP Server  │
│  (Claude)   │         │             │         │  (Tools)    │
└─────────────┘         └─────────────┘         └─────────────┘
```

1. **MCP Hosts** — AI applications (Claude Desktop, Claude Code, Cursor, VS Code)
2. **MCP Clients** — Intermediaries maintaining 1:1 connections with servers
3. **MCP Servers** — Expose functionality through standardized interfaces

### Core Capabilities (Primitives)

| Primitive | Type | Description |
|---|---|---|
| **Resources** | Read-only data | Files, database records, API responses, computed values. URI-like: `@github:issue://123` |
| **Tools** | Executable functions | Perform actions or computations. Can modify state. Return via `tools/call`. |
| **Prompts** | Instruction templates | Predefined templates for common tasks. Discoverable via `prompts/list`. |
| **Sampling** | LLM requests | Servers can request LLM completions — enables agentic behaviors. |

**When combined:** Prompts + Sampling + Tools = True Agent Behavior

### Protocol Layers

| Layer | Purpose | Required |
|---|---|---|
| Base Protocol | JSON-RPC 2.0 message framework | Yes |
| Lifecycle Management | Connection setup, capability negotiation | Yes |
| Authorization | Authentication for HTTP transports | Optional |
| Server Features | Resources, prompts, tools | Optional |
| Client Features | Sampling, directory listings | Optional |
| Utilities | Logging, argument completion | Optional |

### Connection Lifecycle

```
Transport Connection → Capability Negotiation → Feature Discovery → Active Session → Shutdown
```

### Transport Layers

| Transport | Use Case | Recommendation |
|---|---|---|
| **stdio** | Local processes | Desktop apps, CLI tools |
| **HTTP** | Remote cloud services | **RECOMMENDED** for production |
| **SSE** | Streaming (DEPRECATED) | Migrate to HTTP |
| **WebSocket** | Bidirectional real-time | Interactive applications |
| **In-Memory** | Testing | Development, unit tests |

---

## Part II: Claude Code Integration

### HTTP Servers (Recommended)

```bash
claude mcp add --transport http github https://mcp.github.com
claude mcp add --transport http --auth-token "$GITHUB_TOKEN" github-api https://api.github.com/mcp
```

### Stdio Servers (Local)

```bash
claude mcp add --transport stdio filesystem -- npx -y @modelcontextprotocol/server-filesystem /path
```

### Configuration Scopes

| Scope | File | Use Case | Sharing |
|---|---|---|---|
| Local | Project user settings | Personal experiments | Private |
| Project | `.mcp.json` in project root | Team collaboration | Version controlled |
| User | User settings directory | Cross-project utilities | Private |

### `.mcp.json` Example

```json
{
  "mcpServers": {
    "github": {
      "transport": "http",
      "url": "https://mcp.github.com",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    },
    "postgres": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "${DATABASE_URL:-postgresql://localhost/mydb}" }
    }
  }
}
```

---

## Part III: Server Implementations

### Python — Low-Level SDK

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("my-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(
        name="calculate_sum",
        description="Add two numbers",
        inputSchema={
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"]
        }
    )]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "calculate_sum":
        return [TextContent(type="text", text=str(arguments["a"] + arguments["b"]))]

if __name__ == "__main__":
    stdio_server(app)
```

### Python — FastMCP (High-Level)

```python
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.resource("config://app")
def get_config():
    return {"version": "1.0.0", "environment": "production"}

@mcp.prompt()
def greeting(name: str) -> str:
    return f"Hello, {name}! How can I assist you today?"

if __name__ == "__main__":
    mcp.run()
```

### TypeScript SDK

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
  { name: 'my-mcp-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler('tools/list', async () => ({
  tools: [{
    name: 'calculate_sum',
    description: 'Add two numbers',
    inputSchema: {
      type: 'object',
      properties: { a: { type: 'number' }, b: { type: 'number' } },
      required: ['a', 'b']
    }
  }]
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

### TypeScript MCP Manager Pattern

```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';

export class MCPManager {
  private clients: Map<string, Client> = new Map();
  private toolMap: Map<string, string> = new Map();

  async initialize() {
    const transport = new SSEClientTransport(new URL('https://mcp.example.com/sse'));
    const client = new Client(
      { name: 'my-app', version: '1.0.0' },
      { capabilities: {} }
    );
    await client.connect(transport);
    this.clients.set('server-name', client);

    const toolsResult = await client.listTools();
    for (const tool of toolsResult.tools) {
      this.toolMap.set(tool.name, 'server-name');
    }
  }

  async executeTool(toolName: string, args: Record<string, unknown>): Promise<string> {
    const client = this.clients.get(this.toolMap.get(toolName));
    const result = await client.callTool({ name: toolName, arguments: args });
    return result.content.filter(c => c.type === 'text').map(c => c.text).join('\n');
  }
}
```

---

## Part IV: Framework Integrations

### Agno Python

```python
from agno.tools.mcp import MCPTools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        mcp_tools = MCPTools(session=session)
        await mcp_tools.initialize()
        agent = Agent(tools=[mcp_tools])
        await agent.aprint_response("What files are in the current directory?", stream=True)
```

**HTTP Transport with Anthropic Claude:**
```python
from agno.models.anthropic import Claude
from agno.utils.models.claude import MCPServerConfiguration

agent = Agent(
    model=Claude(
        id="claude-sonnet-4-20250514",
        default_headers={"anthropic-beta": "mcp-client-2025-04-04"},
        mcp_servers=[
            MCPServerConfiguration(type="url", name="deepwiki", url="https://mcp.deepwiki.com/sse")
        ]
    )
)
```

**AgentOS with MCP:**
```python
from agno.os import AgentOS
mcp_tools = MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")
agent = Agent(id="support-agent", tools=[mcp_tools])
agent_os = AgentOS(agents=[agent])
agent_os.serve(app="app:app")  # Available at http://localhost:7777/docs
```

### Dagger MCP

Any Dagger module can be exposed as an MCP server:

```bash
dagger -m <module> mcp
dagger -m github.com/kpenfound/dag/puzzmo mcp
dagger -m ./my-local-module mcp
```

### Convex MCP Server

```bash
npx -y convex@latest mcp start
```

Exposes tools for deployment status, table inspection, data queries, function execution, and environment variable management.

### Shadcn MCP Server

```bash
npx shadcn mcp
```

Allows AI assistants to browse, search, and install components from registries.

### Z.ai MCP Servers

| Server | Tools |
|---|---|
| Vision MCP Server | `ui_to_artifact`, `extract_text_from_screenshot`, `Web Reader` |
| Web Search MCP Server | Web search capabilities |
| Web Reader MCP Server | DOM text extraction and crawling |
| Zread MCP Server | Document reading and parsing |

### Agno MCP Toolbox

```python
from agno.tools.mcp import MCPTools

mcp_tools = MCPTools(
    transport="streamable-http",
    url="http://localhost:8080/mcp"
)
agent = Agent(tools=[mcp_tools])
```

### Pydantic Logfire MCP Instrumentation

```python
import logfire
logfire.configure(service_name='server')
logfire.instrument_mcp()

# Client side
logfire.configure(service_name='agent')
logfire.instrument_pydantic_ai()
logfire.instrument_mcp()
```

---

## Part V: Authentication & Authorization

### Five-Layer Authentication Model

1. **Agent Identity** — Each agent has traceable identity
2. **Delegator Authentication** — User must authenticate and consent
3. **Consent from Delegator** — Define what agent can do
4. **Access to MCP Server** — Agent authenticates to server
5. **Upstream Service Access** — Honor both agent and user permissions

### OAuth 2.1 with PKCE

```json
{
  "authorization": {
    "type": "oauth2",
    "authorizationUrl": "https://example.com/oauth/authorize",
    "tokenUrl": "https://example.com/oauth/token",
    "scopes": ["read:data", "write:data"]
  }
}
```

### Better Auth MCP Plugin

Expose your app as an OAuth provider for MCP clients:

```typescript
import { betterAuth } from "better-auth";
import { mcp } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [mcp({ loginPagePath: "/mcp/login" })]
});
```

### SIWE (Sign In With Ethereum) with Better Auth

```typescript
import { betterAuth } from "better-auth";
import { siwe } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [siwe()]  // ERC-4361 Ethereum wallet authentication
});
```

### x402 Payment Protocol with MCP

The x402 payment protocol enables paid API requests through MCP servers. The MCP server bridges between Claude (or any MCP client) and a paid API.

**Hono Server with x402 Middleware:**
```typescript
import { Hono } from 'hono';
import { x402 } from '@x402/hono';

const app = new Hono();
app.use('/api/*', x402({ network: 'base', receiver: '0x...' }));
```

**Setup:**
```bash
git clone https://github.com/coinbase/x402
cd x402/examples/typescript/mcp-server
pnpm install
cp .env-local .env  # Configure wallet and RPC URLs
pnpm dev
```

**Transaction Flow:**
1. Agent requests a premium resource
2. Server responds with `402 Payment Required` containing cost, accepted currency, destination address
3. Agent (with Coinbase AgentKit wallet) signs and resends with Payment-Authorization header
4. Server verifies payment and releases content

---

## Part VI: MCP-UI — Interactive Agent Interfaces

### Overview

MCP-UI is an open protocol (now standardized into **MCP Apps**) for building rich, dynamic interfaces for agentic apps.

### Content Delivery Methods

| Content Type | MIME Type | Delivery | Use Case |
|---|---|---|---|
| Inline HTML | `text/html` | `srcDoc` in iframe | Self-contained components |
| Remote URL | `text/uri-list` | `src` in iframe | External hosted resources |
| Remote DOM | `application/vnd.mcp-ui.remote-dom` | JS in Worker | Lightweight rendering |

**Security Model:** All content executes in sandboxed iframes. Remote DOM scripts run in Web Workers. UI changes communicated via JSON.

### MCP Apps vs A2UI

| Aspect | MCP Apps | A2UI |
|---|---|---|
| Approach | Resource-fetching (opaque payload in iframe) | Native component blueprints |
| Styling | Sandboxed — inherits nothing | Inherits host app styling |
| Orchestrator visibility | Cannot inspect opaque payloads | Can understand lightweight A2UI messages |
| Best for | Pre-built HTML content | Cross-platform generative UI |

### Gradio MCP Integration

```python
import gradio as gr

def classify_and_visualize(image):
    predictions = classifier(image)
    return fig  # Plotly figure

demo = gr.Interface(
    fn=classify_and_visualize,
    inputs=gr.Image(type="pil"),
    outputs=gr.Plot(),
    mcp_server=True
)

@demo.mcp_resource("classifier_ui")
def classifier_ui():
    return html_resource(
        html="<div id='classifier-container'>...</div>",
        title="Image Classifier Interface"
    )

demo.launch()
```

Gradio exposes MCP primitives:
- **Tools** (default): Every Gradio function becomes an MCP tool
- **Resources**: Expose data via `@gr.mcp_resource`
- **Prompts**: Reusable templates via `@gr.mcp_prompt`

### Evidence.dev MCP Integration

```python
from mcp_ui_server import url_resource

@app.list_resources()
async def list_resources():
    return [types.Resource(
        uri="evidence://sales-dashboard",
        name="Sales Dashboard",
        mimeType="text/uri-list"
    )]

@app.read_resource()
async def read_resource(uri: str):
    if uri == "evidence://sales-dashboard":
        return url_resource(
            url="https://my-evidence-app.netlify.app/dashboard",
            title="Sales Dashboard"
        )
```

### Unified MCP-UI Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (MCP-UI)                  │
│           React/Vue + @mcp-ui/client                │
└────────────────────┬────────────────────────────────┘
                     │ MCP Protocol (JSON-RPC)
┌────────────────────▼────────────────────────────────┐
│              MCP Orchestrator Server                │
│  Auth | Resource routing | Event coordination      │
└───────┬─────────────────────────┬───────────────────┘
        │                         │
┌───────▼──────────┐      ┌──────▼──────────┐
│  Gradio Service  │      │ Evidence Static │
│  (MCP Server)    │      │ (Hosted)        │
│  ML Models       │      │ BI Dashboards   │
└──────────────────┘      └─────────────────┘
```

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + @mcp-ui/client | Render MCP-UI resources |
| Orchestrator | Python FastAPI + MCP SDK | Route requests, coordinate services |
| ML Service | Gradio + mcp_server=True | Interactive ML inference |
| Analytics | Evidence.dev (static build) | BI dashboards |
| Database | PostgreSQL / DuckDB | Shared data |
| Cache | Redis | Performance optimization |

---

## Part VII: Security Best Practices

### Key Principles

**DO:**
- Design single-purpose, well-defined servers
- Validate all inputs strictly
- Implement idempotent operations
- Use TLS 1.2+ for all remote connections
- Implement enterprise allowlists
- Monitor token usage and output sizes

**DON'T:**
- Map every API endpoint to a tool (avoid over-fragmentation)
- Use session IDs for authentication
- Skip input validation
- Ignore OWASP guidelines
- Expose sensitive data without encryption

### Attack Vectors

| Vector | Mitigation |
|---|---|
| **Prompt Injection** | Sanitize all tool inputs, validate against schema |
| **Confused Deputy** | Use delegated user credentials, not server credentials |
| **Data Exfiltration** | Implement domain allowlists for fetch operations |

### Agent-Ready Services Pattern

Design tools around user intentions, not implementation details.

| Anti-Pattern | Best Practice |
|---|---|
| `createUser()`, `updateUser()`, `deleteUser()`, `getUserById()` | `manageUser({action, userId?, data?})`, `searchUsers({filters, pagination})` |

---

## Part VIII: MCP Ecosystem

### Official Reference Servers (Anthropic)

| Server | Purpose |
|---|---|
| Everything | Reference/test server |
| Fetch | Web content retrieval |
| Filesystem | Secure file I/O |
| Git | Version control |
| Memory | Knowledge graph-based memory |
| Sequential Thinking | Complex reasoning |
| Time | Timezone conversions |

### Key Categories (6,480+ servers as of 2025)

| Category | Examples |
|---|---|
| **Development** | GitHub, GitLab, Sentry, Socket |
| **Project Management** | Linear, Jira, Asana, Monday, Notion |
| **Databases** | PostgreSQL, MongoDB, BigQuery, Airtable |
| **Cloud** | Vercel, Netlify, Cloudflare, AWS |
| **Design** | Figma, Canva, Cloudinary |
| **Payments** | Stripe, PayPal, Square |
| **Communication** | Slack, Google Drive, Google Calendar, Gmail |
| **AI/LLM** | Puppeteer, Graphiti, AWS KB Retrieval |
| **Automation** | Zapier (8,000+ apps), Workato, Make |

### Server Discovery

| Directory | URL |
|---|---|
| PulseMCP | `www.pulsemcp.com/servers` |
| MCP Server Finder | `www.mcpserverfinder.com` |
| MCP Market | `mcpmarket.com` |
| Claude Partners | `claude.com/partners/mcp` |

---

## Resources

### Official Documentation
- MCP Homepage: https://modelcontextprotocol.io
- Specification: https://modelcontextprotocol.io/specification/2025-06-18/basic
- Claude Code MCP docs: https://code.claude.com/docs/en/mcp

### SDKs
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- FastMCP (Python): `pip install fastmcp`
- FastMCP (TypeScript): `npm install fastmcp`

### Tools
- MCP Inspector: `npx @modelcontextprotocol/inspector`
- Reference Servers: https://github.com/modelcontextprotocol/servers

### Learning
- Anthropic Course: https://anthropic.skilljar.com/model-context-protocol-advanced-topics
- Hugging Face Course: https://huggingface.co/learn/mcp-course

**MCP Version Referenced:** 2025-06-18 Specification
**Ecosystem Stats:** 6,480+ servers, supported by Anthropic, OpenAI, DeepMind, Microsoft
