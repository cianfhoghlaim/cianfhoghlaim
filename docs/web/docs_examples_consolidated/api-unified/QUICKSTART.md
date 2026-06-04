# Quick Start Guide

Get the API Unified server running in under 5 minutes.

## Prerequisites

- Node.js 18+ installed
- npm or pnpm
- Anthropic API key (for AI chat features)

## Step 1: Install Dependencies

```bash
npm install
```

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Step 3: Start the Server

```bash
npm run dev
```

The server will start at `http://localhost:3000`

## Step 4: Explore the API

### Option A: Use the Interactive Swagger UI

Open your browser to:
```
http://localhost:3000/api/~docs
```

This provides an interactive interface to test all REST endpoints.

### Option B: Run cURL Examples

```bash
./examples/curl-examples.sh
```

### Option C: Use the TypeScript Client

```bash
tsx examples/client.ts
```

## Testing Each Feature

### 1. Test MCP Tools

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": { "a": 5, "b": 3 }
    }
  }'
```

### 2. Test oRPC (Type-Safe RPC)

```bash
curl -X POST http://localhost:3000/rpc/public/health \
  -H "Content-Type: application/json"
```

### 3. Test OpenAPI (REST)

```bash
curl http://localhost:3000/api/public/health
```

### 4. Test AI Chat

```bash
curl -X POST http://localhost:3000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "Hello!" }
    ]
  }'
```

## Next Steps

1. **Explore the Swagger UI** at `/api/~docs` to see all available endpoints
2. **View the OpenAPI spec** at `/api/~openapi.json` to generate clients
3. **Read the README** for detailed documentation
4. **Check the code** in `src/` to understand the patterns

## Common Issues

### "ANTHROPIC_API_KEY not found"

Make sure you've created a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Port 3000 already in use

Change the port in `.env`:
```
PORT=3001
```

### Type errors during development

Run type checking:
```bash
npm run type-check
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     API Unified Server                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │    MCP      │  │     oRPC     │  │   AI Streaming  │   │
│  │   Tools     │  │  Procedures  │  │      Chat       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│         │                 │                    │           │
│         └─────────────────┼────────────────────┘           │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │  Shared Schemas │                       │
│                  │   (Zod Types)   │                       │
│                  └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         ┌────▼───┐    ┌────▼───┐   ┌────▼────┐
         │  MCP   │    │  HTTP  │   │   AI    │
         │ Client │    │ Client │   │  Client │
         └────────┘    └────────┘   └─────────┘
```

## Key Features

- ✅ **Single Codebase** - One server, multiple protocols
- ✅ **Type Safety** - End-to-end TypeScript types
- ✅ **Auto-Generated Docs** - OpenAPI spec + Swagger UI
- ✅ **Modern Protocols** - Latest MCP Streamable-HTTP
- ✅ **AI Ready** - Streaming chat with tool calling
- ✅ **Developer Friendly** - Great DX with hot reload

## Learn More

- [Full README](./README.md) - Comprehensive documentation
- [Example Client](./examples/client.ts) - TypeScript client examples
- [cURL Examples](./examples/curl-examples.sh) - Command-line examples
- [API Reference](http://localhost:3000/api/~docs) - Interactive API docs
