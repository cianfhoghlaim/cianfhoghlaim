---
name: dlthub-router
description: "DEPRECATED — canonical replacement is `dlt` (the KCG dlt router). Routes the user to the right dlthub workflow toolkit and installs it on demand. Use when the user asks 'what can I build', 'how do I build a pipeline', 'how do I deploy / schedule a pipeline', or seems unsure what to do next after setup."
---

> **DEPRECATION NOTICE (2026-07-06):** This skill is retained for backward
> compatibility but is no longer the canonical KCG pattern. The canonical
> replacement is `dlt` at
> `.agents/skills/dlt/SKILL.md`. Use the canonical `dlt` skill for new work.

# dlthub-router

Route the user to the right toolkit and skill, then install it. **Fast path first** — the always-loaded toolkit index (in your project rules / `AGENTS.md`) already maps intent → toolkit → install command → entry skill, so you usually do **not** need any discovery round-trip.

> **Router vs handovers.** This skill handles **cold start** — picking and installing a toolkit when none relevant is installed. Once inside a workflow, a toolkit's `workflow.md` **handover** sections take over: they carry context forward (pipeline name, dataset, destination) and route to a specific skill. Do **not** use this skill mid-workflow when the relevant toolkit is already installed. But when a handover names a toolkit that **isn't installed yet**, that's your cue — install it via the index below, then follow the handover's entry point + context.

## Step 1: Route from the always-loaded index (fast path)

The `# toolkits` index is already in your context. Match the user's intent to a row, then:

1. **Install** it: `dlthub --non-interactive ai toolkit install <name>`
2. **Confirm** (Step 3) and **hand over** to that toolkit's entry skill (Step 4).

This needs **no MCP call** — the index is authoritative for the shipped toolkits and is the fast path. Use it whenever the intent matches a row.

## Step 2: Live discovery (fallback only)

Use this **only** when the index has no matching row (an unfamiliar need, or you suspect a newer toolkit exists):

- **Prefer MCP** — `list_toolkits` from `dlt-workspace-mcp` for the live catalog, then `toolkit_info <name>` for skill details.
- **CLI fallback** (MCP not connected): `dlthub --non-interactive ai toolkit list`, then `dlthub --non-interactive ai toolkit info <name>`.

Match intent to the best toolkit, then install as in Step 1. Toolkits marked `(installed: <version>)` are already available.

## Step 3: Confirm & enable MCP

```
uv run dlthub ai status
```
1. You should see the new toolkit and its entry skill.
2. If you see any **WARNING** about the MCP server (e.g. cannot be started), **fix it** using the error message.

## Step 4: Handover (no restart needed)

The `dlt-workspace-mcp` server is already running (installed with `init`) and toolkits reuse it — installing one adds **no new MCP server**, so continue in this session. Do **not** ask the user to restart; that would lose the conversation context.

1. **Load the new toolkit inline** — prefer `toolkit_info <name>` (MCP), which is agent-agnostic and returns the entry skill + workflow rule. If MCP is unavailable, read the installed files directly; the install path depends on the agent (`.claude/`, `.cursor/`, or `.agents/`) — e.g. `<agent-dir>/skills/<entry-skill>/SKILL.md` and the toolkit's workflow rule.
2. **Follow that workflow rule and start at the entry skill**, continuing the user's task with the context you already have. Do not start unrelated workflows on your own.
3. The new skills become natively registered (`/`-invocable, always-loaded workflow rule) on the next natural session start — no need to restart now.

> Exception: if a future toolkit ever ships its **own** MCP server (none do today), that server only starts on restart — suggest a restart **only** in that case, and use CLI fallbacks until then.

<!-- Loading the new skill/rule inline is a stopgap: until the harness can hot-reload skills/rules after install, newly installed components aren't natively registered until the next session start. Tracked in dlt-hub/dlthub-ai-workbench-internal#72. -->

