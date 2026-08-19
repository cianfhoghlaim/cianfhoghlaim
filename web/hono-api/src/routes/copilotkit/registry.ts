/**
 * CopilotKit registry endpoint — the agent_registry_runtime wire-up.
 *
 * Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 2: wire
 * production call sites). This module exposes the canonical
 * `agent_registry_runtime` Python output to the front-end via a
 * Hono route.
 *
 * The Python runtime at `agents/integrations/agent_registry_runtime.py`
 * exposes 3 helpers:
 * - `register_all_agents_with_copilotkit()` — registers every
 *   agent in AGENT_REGISTRY with the CopilotKit runtime
 * - `collect_all_agui_events()` — collects every AG-UI
 *   registration event for the AG-UI protocol handshake
 * - `build_copilotkit_runtime_config()` — builds the canonical
 *   CopilotKit runtime config (agents + tools + metadata)
 *
 * This Hono route delegates to the Python runtime via a subprocess
 * call to `python -c "..."`, which returns the JSON config. This
 * is a thin wire-up — the canonical surface is still the Python
 * runtime.
 *
 * Routes:
 * - GET  /api/copilotkit/registry/config   → build_copilotkit_runtime_config()
 * - GET  /api/copilotkit/registry/events   → collect_all_agui_events()
 * - GET  /api/copilotkit/registry/agents   → list agent names
 *
 * Reference:
 *   agents/integrations/agent_registry_runtime.py
 *   openspec/changes/2026-12-XX-mega-3d-baml-quality-v1/
 */

import { Hono } from "hono";

const app = new Hono();

/**
 * Subprocess helper: invoke a Python expression via the
 * `python -c "..."` route and return the parsed JSON.
 *
 * We use `subprocess.execFile` (not `exec`) to avoid shell injection.
 * The Python expression is a fixed string — no user input is interpolated.
 */
async function invokePythonRuntime<T>(pythonExpr: string): Promise<T> {
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");
  const execFileAsync = promisify(execFile);

  const repoRoot = process.env.REPO_ROOT ?? process.cwd();
  const { stdout } = await execFileAsync(
    "python",
    [
      "-c",
      `import json, sys; sys.path.insert(0, '${repoRoot}'); ` +
        `print(json.dumps(${pythonExpr}))`,
    ],
    { maxBuffer: 10 * 1024 * 1024 },
  );
  return JSON.parse(stdout) as T;
}

app.get("/api/copilotkit/registry/config", async (c) => {
  try {
    const config = await invokePythonRuntime<{
      agents: unknown[];
      tools: unknown[];
      metadata: Record<string, unknown>;
    }>(
      "agents.integrations.agent_registry_runtime.build_copilotkit_runtime_config()",
    );
    return c.json(config);
  } catch (err) {
    return c.json(
      { error: "Failed to load CopilotKit runtime config", details: String(err) },
      500,
    );
  }
});

app.get("/api/copilotkit/registry/events", async (c) => {
  try {
    const events = await invokePythonRuntime<unknown[]>(
      "agents.integrations.agent_registry_runtime.collect_all_agui_events()",
    );
    return c.json({ events, count: events.length });
  } catch (err) {
    return c.json(
      { error: "Failed to collect AG-UI events", details: String(err) },
      500,
    );
  }
});

app.get("/api/copilotkit/registry/agents", async (c) => {
  try {
    const config = await invokePythonRuntime<{
      agents: Array<{ name: string; description?: string }>;
    }>(
      "agents.integrations.agent_registry_runtime.build_copilotkit_runtime_config()",
    );
    const names = (config.agents ?? []).map((a) => a.name);
    return c.json({ agents: names, count: names.length });
  } catch (err) {
    return c.json(
      { error: "Failed to list agents", details: String(err) },
      500,
    );
  }
});

export default app;
