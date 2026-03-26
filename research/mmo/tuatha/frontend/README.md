# Frontend

This directory contains research on UI/UX architecture.

## Contents

- `tanstack-start.md` - Full-stack React meta-framework
- `mcp-ui-integration.md` - Interactive agent interfaces
- `gradio-assessment.md` - Quiz and assessment UIs
- `copilotkit-agents.md` - AI copilot integration

## Tech Stack

- **Framework**: TanStack Start (React 19)
- **Styling**: Tailwind CSS v4, shadcn/ui
- **State**: TanStack Query, Convex (real-time)
- **Auth**: SIWE (Sign-In with Ethereum), BetterAuth
- **Agents**: CopilotKit, MCP-UI

## Key Interfaces

### Player Dashboard
- Soul Level display
- Tuath balance
- Active Geasa (taboos)
- Anam Cara bonds

### Map Interface
- Real-world British Isles overlay
- Zone unlocking based on proficiency
- Live weather integration (Met Éireann, BBC)

### Assessment Interface
- MCP-UI embedded quizzes
- Voice input (Oracy Mining)
- Handwriting capture (Translation Mining)

### NFT Gallery
- Dynamic Cúchulainn avatar evolution
- Artifact collection
- Achievement badges

## Agent Integration (MCP-UI)

```typescript
// Quiz delivery via MCP tool
const quizTool = {
  name: "get_node_challenge",
  returns: UIResource<QuizComponent>,
  render: "inline_html" | "external_url"
}
```
