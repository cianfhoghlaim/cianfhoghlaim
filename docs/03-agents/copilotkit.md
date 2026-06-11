---
title: 'CopilotKit — AI Agent UI Components'
domain: 'agents'
status: 'stable'
description: 'CopilotKit is an open-source React component library for building AI agent interfaces. It provides pre-built chat UI components, agent state management, and multi-agent support — enabling developers to add AI chat, copilot sidebars, and agent-driven UI to React applications with'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/copilotkit.md
ccc_query_hints:
  - copilotkit — ai agent ui components
---

# CopilotKit — AI Agent UI Components

## Overview

CopilotKit is an open-source React component library for building AI agent interfaces. It provides pre-built chat UI components, agent state management, and multi-agent support — enabling developers to add AI chat, copilot sidebars, and agent-driven UI to React applications with minimal code.

## Why This Matters for Kings' College Galway

The curriculum web app includes an AI tutor that helps students navigate learning outcomes, answer questions about prerequisite concepts, and generate personalised study paths. CopilotKit provides the chat interface and agent state management for this tutor — the student types a question, the CopilotKit UI streams the AI response, and the agent state tracks conversation context across multiple interactions. Multi-agent support means different agents (math tutor, Irish language assistant, study planner) can participate in the same conversation with appropriate context switching.

## Key Features

- **Pre-built chat UI** — Production-ready chat components with streaming
- **Agent state management** — Persistent conversation context
- **Multi-agent support** — Multiple specialised agents in one interface
- **React integration** — Hooks and components for TanStack Start
- **Streaming responses** — Real-time token-by-token display

## Installation

```bash
bun add @copilotkit/react-core @copilotkit/react-ui
```

## Integration with Our Stack

CopilotKit components are embedded in the TanStack Start web app. They connect to the LiteLLM gateway for LLM access, Convex for real-time state sync, and the curriculum knowledge graph (Cognee/Graphiti) for educational context retrieval. The `.agents/skills/copilotkit/` skill documents integration patterns.

## Upstream

- **Repository**: <https://github.com/CopilotKit/CopilotKit>
- **Documentation**: <https://docs.copilotkit.ai>
- **Latest**: Active development — multi-agent support, streaming improvements, React Server Components

## Screenshot

CopilotKit provides React components: `<CopilotKit>` provider, `<CopilotChat>` for the chat interface, and `<CopilotSidebar>` for a slide-out panel. The demo at `copilotkit.ai` shows the chat UI with streaming text, action buttons, and agent status indicators. In the Kings' College Galway app, the CopilotKit tutor appears as a sidebar chat panel with subject-specific icons.
