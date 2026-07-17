# AG-UI Protocol — KCG Summary

## What It Is
The Agent User Interaction Protocol (AG-UI) is an open standard for connecting AI agents to user interfaces. It defines a streaming event protocol that lets AI agents communicate with frontend UIs in real-time — sending text chunks, tool calls, structured data, and state updates. The protocol is framework-agnostic and supports multiple language backends (Python, TypeScript) with client SDKs for React, Solid, Vue, and Svelte.

## Why This Matters for Kings' College Galway
AG-UI is the core streaming protocol used across all sruth/ frontends — `tuath/` (game HUD with CopilotKit agents), `sruth/cianfhoghlaim/` (generative UI components), `sruth/crypteolas/` (AI copilot), `aleyum/` (agent chat), and `códeolas/` (code intelligence). The protocol bridges Python AI backends (Pydantic AI, Agno) to TypeScript React frontends. The agent-spec defines the protocol contract; the framework integrations show how to embed AG-UI into existing agent frameworks. Understanding the event types (text, tool_call, state_snapshot, etc.) is essential for building any CopilotKit-based frontend.

## Key Patterns Preserved
- **docs/web/ag-ui/docs/README.md** — Official AG-UI documentation publishing guide
- **docs/web/ag-ui/docs/ag_ui.md** — Core AG-UI protocol specification and event types
- **docs/web/ag-ui/agent-spec/python/README.md** — Python agent specification library for AG-UI
- **docs/web/ag-ui/agent-spec/python/examples/README.md** — Python AG-UI agent examples
- **docs/web/ag-ui/agno/python/examples/README.md** — Agno framework integration with AG-UI protocol (Python)
- **docs/web/ag-ui/agno/typescript/README.md** — Agno framework AG-UI adapter for TypeScript
- **docs/web/ag-ui/pydantic-ai/python/examples/README.md** — Pydantic AI integration with AG-UI protocol
- **docs/web/ag-ui/pydantic-ai/typescript/README.md** — Pydantic AI AG-UI TypeScript client adapter

## Source Files
Full example repository source code removed (2026-06-06). Original repos available at <https://github.com/ag-ui-protocol>. Protocol specification and framework integration patterns retained.

## What Was Removed
- All Python source files (.py)
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All configuration files (package.json, pyproject.toml, tsconfig.json, etc.)
- All build artifacts and lock files
- All CSS/Styles
- All image/assets
- .git directories
- All non-.md files
