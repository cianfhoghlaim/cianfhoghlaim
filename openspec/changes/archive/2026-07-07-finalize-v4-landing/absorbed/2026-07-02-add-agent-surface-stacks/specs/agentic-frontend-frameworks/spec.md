# Agentic Frontend Frameworks — 3 Agent Surfaces Delta

> This file is the change-side delta for
> `2026-07-02-add-agent-surface-stacks`. It applies on
> top of the canonical `agentic-frontend-frameworks`
> spec at
> `../../../../specs/agentic-frontend-frameworks/spec.md`
> and on top of the prior 3 changes' deltas.

## ADDED Requirements

### Requirement: 3 agent runtime surfaces on bunchloch

The system SHALL expose 3 agent runtime surfaces on
`bunchloch` (the workload host), all routed through the
canonical `litellm` gateway (per
`agent-platform-cluster` §"LiteLLM chokepoint contract"):

- **hermes** — autonomous long-running agent runtime
  (NousResearch/hermes-agent v0.17.0)
- **openclaw** — channel-fanout gateway (Telegram +
  Slack + Discord + WhatsApp + WebChat + MS Teams)
- **openchamber** — OpenCode web/desktop UI (Bun +
  React, 18+ themes, bundled opencode-ai runtime)

All 3 surfaces SHALL be brought up via
`./scripts/stack.sh <name> up -d` (the dev-mode direct
CLI). The 3 surfaces complement the
`agentic-frontend-frameworks` canonical web/UI stack
(TanStack Start + CopilotKit + AG-UI + Hono + Convex)
by providing **runtime surfaces** rather than **user-
facing app surfaces**.

#### Scenario: 3 runtime surfaces on bunchloch
- **WHEN** an operator wants to interact with the
  Cianfhoghlaim agent fleet
- **THEN** they SHALL have 3 options:
  - `hermes` (autonomous long-running runtime with
    learning loop, reachable at
    `http://hermes.cianfhoghlaim.ie` via Pangolin)
  - `openclaw` (chat via Telegram / Slack / Discord
    / WhatsApp / WebChat / MS Teams, reachable via
    the enabled channel ingress)
  - `openchamber` (browser-based IDE with bundled
    opencode-ai, reachable at
    `http://openchamber.cianfhoghlaim.ie` via
    Pangolin)
- **AND** all 3 options SHALL route their LLM
  traffic through `http://litellm:4000/v1` (the M3
  chokepoint)
- **AND** all 3 options SHALL emit traces to
  `http://langfuse:3001/api/public`