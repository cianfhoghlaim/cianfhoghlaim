# Cianfhoghlaim Developer Portal

Internal developer dashboard for managing infrastructure, agents, and data pipelines.

## Overview

The portal provides a unified interface for:

- **Stack Management** - Monitor and control bonneagar infrastructure stacks
- **Agent Interface** - Chat with Tuath, Crypteolas, and Portal agents
- **Data Pipelines** - View and trigger Dagster pipelines
- **Monitoring** - Real-time logs, metrics, and LLM observability

## Quick Start

### Prerequisites

- Node.js 22+
- pnpm 9+

### Installation

```bash
cd sruth/aleyum/portal
pnpm install
```

### Development

```bash
pnpm dev
```

Portal available at: http://localhost:3001

### Build

```bash
pnpm build
pnpm start
```

## Architecture

```
portal/
├── src/
│   ├── routes/
│   │   ├── __root.tsx           # Root layout
│   │   ├── _layout.tsx          # Sidebar layout
│   │   └── _layout/
│   │       ├── index.tsx        # Dashboard home
│   │       ├── stacks/          # Stack management
│   │       ├── agents/          # Agent registry & chat
│   │       ├── data/            # Pipelines & schemas
│   │       └── monitoring/      # Logs & metrics
│   ├── components/              # UI components
│   ├── lib/                     # Utilities
│   └── server/                  # Server functions
├── package.json
├── vite.config.ts
└── app.config.ts
```

## Features

### Dashboard

Overview of system health:
- Stack status grid
- Active agent count
- Pipeline status
- Recent activity feed

### Stack Management

View and control bonneagar stacks:
- Health status indicators
- CPU/Memory metrics
- Container counts
- Quick actions (restart, logs, open UI)

### Agent Chat

Interactive chat with ADK agents:
- Tuath Agent - Celtic language learning
- Crypteolas Agent - DeFi analytics
- Portal Agent - Infrastructure management

Supports:
- Streaming responses
- Tool call visualization
- Markdown rendering
- Code highlighting

### Data Pipelines

Dagster pipeline management:
- Pipeline status overview
- Manual job triggers
- Asset dependency graph
- Run history

### Monitoring

Real-time observability:
- Container logs (Dozzle integration)
- System metrics (Beszel integration)
- LLM traces (Langfuse integration)

## Configuration

### Environment Variables

```bash
# API Endpoints
TUATH_API_URL=http://localhost:8000
CRYPTEOLAS_API_URL=http://localhost:8001
DAGSTER_URL=http://localhost:3000
BESZEL_URL=http://localhost:8090
DOZZLE_URL=http://localhost:9999
LANGFUSE_URL=http://localhost:3001

# Auth (if enabled)
JWT_SECRET=your-jwt-secret
```

### API Proxying

The development server proxies API requests:
- `/api/tuath/*` → Tuath API (port 8000)
- `/api/crypteolas/*` → Crypteolas API (port 8001)

## Integration

### MCP Server

The portal can use the dev-portal-mcp server for:
- Stack status queries
- Pipeline execution
- Metrics retrieval
- Code search

See: `bonneagar/uirlisí/dev-portal-mcp/`

### Agents

The portal integrates with ADK agents:

**Tuath Agent** (`tuath.agents.adk.root_agent`)
- Celtic language learning
- Mythology exploration
- Curriculum search

**Crypteolas Agent** (`crypteolas.agents.adk.root_agent`)
- Protocol research
- Code analysis
- DeFi analytics

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | TanStack Start |
| Styling | Tailwind CSS 4 |
| UI Components | Radix UI |
| AI Chat | AI SDK + AGUI patterns |
| MCP Client | @mcp-ui/client |
| Charts | Recharts |
| Icons | Lucide React |

## Related Documentation

- [Tuath Development](../../tuath/DEVELOPMENT.md)
- [Crypteolas Development](../../crypteolas/DEVELOPMENT.md)
- [MCP Server](../../../bonneagar/uirlisí/dev-portal-mcp/README.md)
