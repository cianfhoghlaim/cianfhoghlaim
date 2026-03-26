# Coding Agent

This repository contains a coding agent _demo_ built on [Restate.dev](https://restate.dev)
Key features:

* Conversation management — Maintains multi-turn context and session state so the agent can follow, clarify, and continue user interactions reliably.
* Orchestrated subagent execution — Coordinates and supervises subagents and workflows to break complex tasks into manageable jobs, with planning, retries, and interruption handling.
* Sandbox lifecycle and resource management — Provisions, locks, releases, and reclaims isolated execution sandboxes (with timeouts) so user code runs safely and reproducibly.

## How does this works

This section summarizes how the agent is structured and how requests flow through the system.

The system has three primary responsibilities:
- Orchestration: [agent.ts](packages/agent/src/agent.ts) receives user messages, maintains conversation state and session context, decides when to start/stop or interrupt workflows, and routes work to the executor.
- Workflow execution: [agent_executor.ts](packages/agent/src/agent_executor.ts) turns high‑level requests and context into stepwise plans (ToDos), runs sub‑workflows, manages retries and error handling, and reports progress back to the orchestrator.
- Sandbox management [sandbox.ts](packages/agent/src/sandbox.ts): provisions isolated runtimes, enforces timeouts and resource limits, and locks/releases sandboxes to ensure safe, reproducible execution.

Typical request lifecycle:

1. The orchestrator accepts a message and updates conversation context.
2. The executor generates a plan of concrete tasks based on the current context.
3. The executor executes each task, as a subagent workflow, while tools run inside sandboxes that the sandbox manager provisions and locks.
4. The orchestrator updates the session state, presents results to the user, and reclaims sandbox resources.

# Quick Start

* Start restate
```bash
docker run --net host restatedev/restate
```

* You would need the `OPENAI_API_KEY` in your env

```bash
export OPENAI_API_KEY=...
```

* Modal labs sandboxes

Make sure to expose the relevant env variables for modal, (i.e. `MODAL_PROFILE`) and then set the

* Start the services
```bash
pnpm install
pnpm build
pnpm start 
```

* Register the services with restate

Use the webui/cli or
```bash
curl http://localhost:9070/deployments --json '{ "uri" : "http://localhost:9080"}'
```

* Demo UI

[Agent UI](http://localhost:3000)


# Disclaimer

This demo is for illustrative purposes, it's purpose is to highlight the capabilities of the Restate.dev as a platform for AI applications.
