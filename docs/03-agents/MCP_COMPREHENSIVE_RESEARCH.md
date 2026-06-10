# MCP Comprehensive Research: Protocol, Integration, and Applications

## Merged From
- `mcp-research-report.md`
- `mcp-ui-gradio-evidence-integration-analysis.md`
- `MCP Server.md` (shadcn MCP)
- `MCP Server with x402.md` (Coinbase x402 MCP)
- `MCP _ Better Auth.md` (Better Auth MCP plugin)
- `MCP_RESEARCH.md` (Dagger MCP)
- `MCP-UI.md` (MCP-UI overview)
- `MCP Toolbox.md` (Agno MCP Toolbox)
- `Sign In With Ethereum (SIWE) _ Better Auth.md`
- `x402_examples_typescript_servers_hono at main · coinbase_x402.md`
- `Agent _ Firecrawl.md`

---

## Part I: MCP Fundamentals

### 1.1 What is MCP?

The Model Context Protocol (MCP) is an **open-source standard** developed by Anthropic for connecting AI applications to external systems. Released on November 18, 2024, MCP provides a universal interface for AI models to interact with data sources, tools, and services—functioning as "USB-C for AI."

**Key Characteristics:**
- **Open Standard**: Developed by Anthropic, supported by OpenAI, DeepMind, Microsoft
- **Protocol Foundation**: Built on JSON-RPC 2.0
- **Universal Connector**: Single interface for multiple integrations
- **Bidirectional Communication**: Requests, responses, notifications
- **Transport Agnostic**: Works over stdio, HTTP, SSE, WebSockets

### 1.2 Three-Component Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   MCP Host  │ ◄─────► │ MCP Client  │ ◄─────► │ MCP Server  │
│  (Claude)   │         │             │         │  (Tools)    │
└─────────────┘         └─────────────┘         └─────────────┘
```

1. **MCP Hosts** - AI applications (Claude Desktop, Claude Code, Cursor, VS Code)
2. **MCP Clients** - Intermediaries maintaining 1:1 connections with servers
3. **MCP Servers** - Expose functionality through standardized interfaces

### 1.3 Core Capabilities (Primitives)

**Resources:** Read-only data for AI context (files, database records, API responses, computed values). Referenced using URI-like syntax: `@github:issue://123`

**Tools:** Executable functions that perform actions or computations. Can modify state, return results via `tools/call`.

**Prompts:** Predefined instruction templates for common tasks. Discoverable via `prompts/list`, executable as slash commands.

**Sampling:** Advanced capability allowing servers to request LLM completions — enables agentic behaviors and nested LLM calls.

**When combined:** Prompts + Sampling + Tools = True Agent Behavior

### 1.4 Protocol Specification

MCP consists of **six integrated layers**:

| Layer | Purpose | Required |
|---|---|---|
| Base Protocol | JSON-RPC 2.0 message framework | Yes |
| Lifecycle Management | Connection setup, capability negotiation | Yes |
| Authorization | Authentication for HTTP transports | Optional |
| Server Features | Resources, prompts, tools | Optional |
| Client Features | Sampling, directory listings | Optional |
| Utilities | Logging, argument completion | Optional |

**Connection Lifecycle:**
```
Transport Connection → Capability Negotiation → Feature Discovery → Active Session → Shutdown
```

### 1.5 Transport Layers

| Transport | Use Case | Recommendation |
|---|---|---|
| **stdio** | Local processes | Desktop apps, CLI tools |
| **HTTP** | Remote cloud services | **RECOMMENDED** for production |
| **SSE** | Streaming (DEPRECATED) | Migrate to HTTP |
| **WebSocket** | Bidirectional real-time | Interactive applications |
| **In-Memory** | Testing | Development, unit tests |

---

## Part II: MCP Integration Patterns

### 2.1 Claude Code Integration

**HTTP Servers (Recommended):**
```bash
claude mcp add --transport http github https://mcp.github.com
claude mcp add --transport http --auth-token "$GITHUB_TOKEN" github-api https://api.github.com/mcp
```

**Stdio Servers (Local):**
```bash
claude mcp add --transport stdio filesystem -- npx -y @modelcontextprotocol/server-filesystem /path
```

**Configuration Scopes:**

| Scope | File | Use Case | Sharing |
|---|---|---|---|
| Local | Project user settings | Personal experiments | Private |
| Project | `.mcp.json` in project root | Team collaboration | Version controlled |
| User | User settings directory | Cross-project utilities | Private |

**`.mcp.json` Example:**
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

### 2.2 Python Integration (Agno Framework)

```python
from agno.agent import Agent
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
from agno.agent import Agent
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
from agno.tools.mcp import MCPTools

mcp_tools = MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")
agent = Agent(id="support-agent", name="Support Agent", model=Claude(id="claude-sonnet-4-0"), tools=[mcp_tools])

agent_os = AgentOS(agents=[agent])
app = agent_os.get_app()
agent_os.serve(app="app:app")  # Available at http://localhost:7777/docs
```

### 2.3 TypeScript/JavaScript Integration

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

### 2.4 Dagger MCP Integration

Dagger has native MCP support — any Dagger module can be exposed as an MCP server:

```bash
# Start any Dagger module as an MCP server
dagger -m <module> mcp

# Examples:
dagger -m github.com/kpenfound/dag/puzzmo mcp
dagger -m ./my-local-module mcp
```

### 2.5 x402 Payment Protocol with MCP

The x402 payment protocol enables paid API requests through MCP servers. The MCP server acts as a bridge between Claude (or any MCP client) and a paid API:

```bash
# Clone and run the MCP server with x402
git clone https://github.com/coinbase/x402
cd x402/examples/typescript/mcp-server
pnpm install
cp .env-local .env  # Configure wallet and RPC URLs
pnpm dev
```

**Hono Server with x402 Middleware:**
```typescript
import { Hono } from 'hono';
import { x402 } from '@x402/hono';

const app = new Hono();
app.use('/api/*', x402({ network: 'base', receiver: '0x...' }));
```

### 2.6 Better Auth MCP Plugin

The Better Auth MCP plugin lets your app act as an OAuth provider for MCP clients:

```typescript
import { betterAuth } from "better-auth";
import { mcp } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [mcp({ loginPagePath: "/mcp/login" })]
});
```

---

## Part III: MCP Server Implementations

### 3.1 Python SDK (Low-Level)

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
        inputSchema={"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}
    )]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "calculate_sum":
        return [TextContent(type="text", text=str(arguments["a"] + arguments["b"]))]

if __name__ == "__main__":
    stdio_server(app)
```

### 3.2 FastMCP (High-Level Python)

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

### 3.3 TypeScript SDK

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

server.setRequestHandler('tools/call', async (request) => {
  const { a, b } = request.params.arguments;
  return { content: [{ type: 'text', text: String(a + b) }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 3.4 Shadcn MCP Server

The shadcn MCP server allows AI assistants to browse, search, and install components from registries:
```bash
npx shadcn mcp
```

### 3.5 Agno MCP Toolbox

```python
from agno.tools.mcp import MCPTools

# Connect to Google's MCP Toolbox for Databases
mcp_tools = MCPTools(
    transport="streamable-http",
    url="http://localhost:8080/mcp"
)

# Filter tools by toolset or tool name
agent = Agent(tools=[mcp_tools])
```

### 3.6 Z.ai MCP Servers

- **Vision MCP Server**: Provides `ui_to_artifact`, `extract_text_from_screenshot`, `Web Reader`
- **Web Search MCP Server**: Web search capabilities 
- **Web Reader MCP Server**: DOM text extraction and crawling
- **Zread MCP Server**: Document reading and parsing

---

## Part IV: MCP-UI — Interactive Agent Interfaces

### 4.1 Overview

MCP-UI is an open protocol (now standardized into MCP Apps) to build rich, dynamic interfaces for agentic apps. Three content delivery methods:

| Content Type | MIME Type | Delivery | Use Case |
|---|---|---|---|
| Inline HTML | `text/html` | `srcDoc` in iframe | Self-contained components |
| Remote URL | `text/uri-list` | `src` in iframe | External hosted resources |
| Remote DOM | `application/vnd.mcp-ui.remote-dom` | JS in Worker | Lightweight rendering |

**Security Model:** All content executes in sandboxed iframes. Remote DOM scripts run in Web Workers. UI changes communicated via JSON.

### 4.2 MCP-UI + Gradio Integration

Gradio has native MCP server support (`mcp_server=True`):

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

### 4.3 MCP-UI + Evidence.dev Integration

Evidence.dev generates static HTML from SQL + Markdown:

```python
from mcp_ui_server import url_resource, html_resource

@app.list_resources()
async def list_resources():
    return [
        types.Resource(
            uri="evidence://sales-dashboard",
            name="Sales Dashboard",
            mimeType="text/uri-list"
        )
    ]

@app.read_resource()
async def read_resource(uri: str):
    if uri == "evidence://sales-dashboard":
        return url_resource(
            url="https://my-evidence-app.netlify.app/dashboard",
            title="Sales Dashboard"
        )
```

### 4.4 Unified Architecture

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

**Technology Stack:**

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + @mcp-ui/client | Render MCP-UI resources |
| Orchestrator | Python FastAPI + MCP SDK | Route requests, coordinate services |
| ML Service | Gradio + mcp_server=True | Interactive ML inference |
| Analytics | Evidence.dev (static build) | BI dashboards |
| Database | PostgreSQL / DuckDB | Shared data |
| Cache | Redis | Performance optimization |

---

## Part V: Security and Best Practices

### 5.1 Five-Layer Authentication Model

1. **Agent Identity** - Each agent has traceable identity
2. **Delegator Authentication** - User must authenticate and consent
3. **Consent from Delegator** - Define what agent can do
4. **Access to MCP Server** - Agent authenticates to server
5. **Upstream Service Access** - Honor both agent and user permissions

### 5.2 OAuth 2.1 with PKCE

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

### 5.3 Key Security Do's and Don'ts

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

### 5.4 Attack Vectors

**Prompt Injection:** Sanitize all tool inputs, validate against schema
**Confused Deputy:** Use delegated user credentials, not server credentials
**Data Exfiltration:** Implement domain allowlists for fetch operations

### 5.5 Architectural Best Practices

**Agent-Ready Services Pattern:** Design tools around user intentions, not implementation details.

**Anti-Pattern:** `createUser()`, `updateUser()`, `deleteUser()`, `getUserById()`
**Best Practice:** `manageUser({action: 'create|update|delete', userId?, data?})`, `searchUsers({filters, pagination})`

---

## Part VI: SIWE (Sign In With Ethereum) with Better Auth

The SIWE plugin allows users to authenticate using Ethereum wallets following ERC-4361:

```typescript
import { betterAuth } from "better-auth";
import { siwe } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [siwe()]
});
```

---

## Part VII: MCP Ecosystem

### 7.1 Official Reference Servers (Anthropic)

| Server | Purpose |
|---|---|
| Everything | Reference/test server |
| Fetch | Web content retrieval |
| Filesystem | Secure file I/O |
| Git | Version control |
| Memory | Knowledge graph-based memory |
| Sequential Thinking | Complex reasoning |
| Time | Timezone conversions |

### 7.2 Key Categories (6,480+ servers as of 2025)

**Development:** GitHub, GitLab, Sentry, Socket
**Project Management:** Linear, Jira, Asana, Monday, Notion
**Databases:** PostgreSQL, MongoDB, BigQuery, Airtable
**Cloud:** Vercel, Netlify, Cloudflare, AWS
**Design:** Figma, Canva, Cloudinary
**Payments:** Stripe, PayPal, Square
**Communication:** Slack, Google Drive, Google Calendar, Gmail
**AI/LLM:** Puppeteer, Graphiti, AWS KB Retrieval
**Automation:** Zapier (8,000+ apps), Workato, Make

### 7.3 Server Discovery

- **PulseMCP**: 6,480+ servers — `www.pulsemcp.com/servers`
- **MCP Server Finder**: Categorized directory — `www.mcpserverfinder.com`
- **MCP Market**: Business-focused — `mcpmarket.com`
- **Claude Partners**: Official integrations — `claude.com/partners/mcp`

---

## Part VIII: Firecrawl Agent API

Firecrawl `/agent` is an autonomous web research API that searches, crawls, and collects data from complex websites:

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

Key features:
- No URL required — just describe what you need
- Deep web exploration and navigation
- Parallel processing for faster results
- Structured JSON schemas for typed output

---

## Part IX: Key Resources

### Official Documentation
- MCP Homepage: https://modelcontextprotocol.io
- Specification: https://modelcontextprotocol.io/specification/2025-06-18/basic
- Claude Code MCP docs: https://code.claude.com/docs/en/mcp

### SDKs
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- FastMCP (Python): `pip install fastmcp`
- FastMCP (TS): `npm install fastmcp`

### Tools
- MCP Inspector: `npx @modelcontextprotocol/inspector`
- Reference Servers: https://github.com/modelcontextprotocol/servers

### Learning
- Anthropic Course: https://anthropic.skilljar.com/model-context-protocol-advanced-topics
- Hugging Face Course: https://huggingface.co/learn/mcp-course

---

**MCP Version Referenced:** 2025-06-18 Specification
**Ecosystem Stats:** 6,480+ servers, supported by Anthropic, OpenAI, DeepMind, Microsoft
