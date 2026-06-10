# TanStack Start — React Full-Stack Framework

## Overview

TanStack Start is a full-stack React framework by the TanStack team (creators of React Query, React Router, TanStack Table). It provides server-side rendering, file-based routing, streaming suspense, and server functions — a modern alternative to Next.js with first-class TypeScript support and a focus on fine-grained reactivity.

## Why This Matters for Kings' College Galway

The student-facing web app (`oideachais/web/`) is built on TanStack Start. Its server-side rendering ensures fast initial page loads for curriculum content, and streaming suspense enables progressive loading of AI-generated study assets (images, prerequisite graphs, RAGAS scores) without blocking the UI. The file-based routing maps cleanly to the curriculum structure: `/subjects/mathematics/senior-cycle/differentiation` is a natural URL pattern for educational content. TanStack Start's Bun-native support aligns with the project's TypeScript toolchain.

## Key Features

- **Server-side rendering** — Fast initial loads with hydration
- **File-based routing** — URL structure mirrors the filesystem
- **Streaming suspense** — Progressive content loading
- **Server functions** — Type-safe RPC between client and server
- **React Server Components** — Server-rendered components with zero client JS

## Installation

```bash
bun add @tanstack/react-start
```

## Integration with Our Stack

TanStack Start powers the `oideachais/web/` application. It connects to Convex for real-time data, Hono for API routes, and the LiteLLM gateway for AI features. CopilotKit provides the AI chat/tutor interface within the TanStack app.

## Upstream

- **Repository**: <https://github.com/TanStack/start>
- **Documentation**: <https://tanstack.com/start>
- **Latest**: v1.94+ (2025) — React Server Components, edge runtime, streaming suspense, Bun support

## Screenshot

TanStack Start's output is a web application. The development server (`bun run dev`) shows routes, server functions, and build output in the terminal. The browser displays the rendered React application. The `.agents/skills/tanstack-start/` skill documents project-specific patterns.
