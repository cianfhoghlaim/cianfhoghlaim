# Restate.dev Coding Agent — KCG Summary

## What It Is

[Restate.dev](https://restate.dev) is a durable execution platform that provides workflow-as-code with built-in state management, retries, and exactly-once semantics. This cloned repo is Restate's official **coding agent demo** — a monorepo showcasing how to build resilient AI agents on top of durable execution primitives.

## Why It Matters for KCG

- **Durable execution for AI workflows** — Restate handles conversation state, retries, and interruption recovery natively, making it a candidate backbone for long-running agentic pipelines (exam generation, content processing, multi-step data workflows).
- **Agent orchestration patterns** — The demo implements proven agent architectures (planner-executor, parallel agents, routing, human-in-the-loop, evaluator-optimizer) that directly inform KCG's agent design for curriculum and assessment tools.
- **Real-time streaming** — The PubSub package demonstrates server→client streaming for agent progress, directly applicable to KCG's real-time student/teacher dashboards.
- **TypeScript monorepo structure** — pnpm workspace with shared types, demonstrating clean multi-package architecture relevant to KCG's own monorepo design.

## Key Patterns Preserved

| Pattern | Location | Relevance |
|---------|----------|-----------|
| Orchestrator-agent loop | `packages/agent/src/agent.ts` | Central conversation manager maintaining multi-turn context |
| Planner→Executor→Sandbox | `packages/agent/src/agent_executor.ts`, `plan.ts`, `sandbox.ts` | Stepwise task decomposition with isolated execution |
| PubSub real-time streaming | `packages/pubsub/src/` | Server→client progress for long-running agent tasks |
| Parallel agent execution | `typescript-patterns/src/parallel-agents.ts` | Run multiple sub-agents concurrently |
| Routing patterns | `typescript-patterns/src/routing-to-agent.ts`, `routing-to-tools.ts` | Intent-based agent/tool dispatch |
| Human-in-the-loop | `typescript-patterns/src/human-in-the-loop.ts` | Pause workflows for human approval |
| Evaluator-Optimizer | `typescript-patterns/src/evaluator-optimizer.ts` | Self-critique and refinement loop |
| Racing agents | `typescript-patterns/src/racing-agents.ts` | Competitive agent selection |
| shadcn/ui component library | `packages/ui/components/ui/` | Complete shadcn/ui component set (40+ components) |
| Next.js App Router UI | `packages/ui/app/` | Streaming chat UI with server-sent events |

## Agent Pattern Summary

The `typescript-patterns/` directory contains standalone, minimal implementations of core agent design patterns using Restate:

1. **Chaining** — Sequential task decomposition
2. **Routing** — Dispatch to specialized agents/tools based on intent
3. **Parallel agents** — Concurrent sub-agent execution with result merging
4. **Racing agents** — Run multiple agents and pick the fastest/best result
5. **Evaluator-Optimizer** — Generate → Evaluate → Refine loop
6. **Human-in-the-loop** — Pause for human review at decision points
7. **Parallel tools** — Concurrent tool execution

## What Was Removed

- All TypeScript source files (`.ts`, `.tsx`) — ~120 files
- Build/config files (`package.json`, `tsconfig.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `eslint.config.js`)
- CSS files (`globals.css`)
- Static assets (`public/` — placeholder images/SVGs)
- `components.json` (shadcn/ui config)
- `.gitignore`, `env.example`
- Build artifacts (`tsconfig.tsbuildinfo`)

Total removed: ~122 non-Markdown files, ~1.0 MB

## Remaining Artifacts

- `README.md` — Repo overview and quick start
- `packages/ui/README.md` — Demo UI description
- `packages/pubsub/README.md` — PubSub package docs
- `typescript-patterns/README.md` — Agent patterns overview
- `KCG_SUMMARY.md` — This file
