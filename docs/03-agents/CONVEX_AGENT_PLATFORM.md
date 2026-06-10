# Convex Agent Platform Reference

## Merged From
- `convex/AI Agent.md`
- `convex/Convex MCP Server _ Convex Developer Hub.md`

---

## Convex AI Agent Component

The Agent component is a core building block for building AI agents on Convex. It manages threads and messages around which agents can cooperate in static or dynamic workflows.

### Installation
```bash
npm install @convex-dev/agent
```

### Core Capabilities

- **Agents:** Units of use-case-specific prompting with models, prompts, tool calls, and behavior
- **Threads:** Persist messages and can be shared by multiple users and agents including human agents
- **Streaming:** Text and objects using deltas over WebSockets — all clients stay in sync efficiently
- **Conversation Context:** Auto-included in each LLM call, includes built-in hybrid vector/text search
- **RAG:** Supported for prompt augmentation, integrates with the RAG Component or DIY
- **Workflows:** Multi-step operations spanning agents and users, durably and reliably
- **Files:** Supported in thread history with automatic saving to file storage and ref-counting
- **Debugging:** Callbacks, agent playground, dashboard inspection
- **Usage Tracking:** Per-provider, per-model, per-user, per-agent attribution
- **Rate Limiting:** Via the Rate Limiter Component

```bash
git clone https://github.com/get-convex/agent.git
```

---

## Convex MCP Server

The Convex MCP Server provides tools for AI agents to interact with Convex deployments.

### Setup
```bash
npx -y convex@latest mcp start
```

Claude Code:
```bash
claude mcp add-json convex '{"type":"stdio","command":"npx","args":["convex","mcp","start"]}'
```

### Available Tools

**Deployment:**
- `status`: Queries available deployments, returns deployment selector

**Table Tools:**
- `tables`: Lists all tables with schema
- `data`: Queries table data
- SQL queries against Convex databases

Editors supported: Cursor, Windsurf, VS Code, Claude Code
