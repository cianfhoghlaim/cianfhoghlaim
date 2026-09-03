/**
 * Hono API endpoints for the deployment control panel.
 *
 * Per the `deployment-control-panel` openspec capability (2026-08-15).
 *
 * Mirrors `notebooks/00_control_panel.py` (the marimo notebook) over
 * HTTP. The 5 endpoints back the 5 tabs:
 *
 *   GET  /api/control-panel/models          → Tab 1
 *   POST /api/control-panel/models/set       → toggle a model on/off
 *   GET  /api/control-panel/pipelines       → Tab 2
 *   POST /api/control-panel/pipelines/set    → toggle a pipeline on/off
 *   GET  /api/control-panel/datasets        → Tab 3
 *   GET  /api/control-panel/stacks          → Tab 4
 *   POST /api/control-panel/stacks/set       → toggle a stack on/off
 *   GET  /api/control-panel/registry        → Tab 5
 *
 * All GET endpoints call Python helpers via a subprocess wrapper at
 * `web/hono-api/control-panel/_python_bridge.py` (which imports
 * `notebooks._shared.schema` + `meaisinfhoghlaim.models.MODEL_REGISTRY`).
 *
 * The POST endpoints atomically write `deployment-choice.yaml` via
 * `notebooks/_shared/schema.py:write_deployment_choice` (with
 * `fcntl.flock` for concurrent-write safety).
 *
 * Reference: openspec/specs/deployment-control-panel/spec.md
 *            openspec/changes/archive/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/
 */

import { Hono } from "hono";

const app = new Hono();

const PYTHON_BRIDGE = "web/hono-api/control-panel/_python_bridge.py";

/**
 * Helper: invoke a Python helper and return the parsed JSON result.
 * Uses a subprocess call to the Python bridge (avoids bundling
 * ibis + pyarrow + LanceDB on the TypeScript side).
 */
async function invokePython(args: string[]): Promise<unknown> {
  const proc = Bun.spawn(["python3", PYTHON_BRIDGE, ...args], {
    stdout: "pipe",
    stderr: "pipe",
  });
  const stdout = await new Response(proc.stdout).text();
  const stderr = await new Response(proc.stderr).text();
  const exitCode = await proc.exited;
  if (exitCode !== 0) {
    throw new Error(`Python bridge failed (exit ${exitCode}): ${stderr}`);
  }
  return JSON.parse(stdout);
}

// ─── Tab 1: Models ─────────────────────────────────────────────────────────

app.get("/api/control-panel/models", async (c) => {
  try {
    const result = (await invokePython(["models"])) as {
      models: Array<{
        enabled: boolean;
        key: string;
        family: string;
        role: string;
        display_name: string;
        upstream_id: string;
        backend: string;
        available: boolean;
        litellm_alias: string;
        languages: string;
      }>;
    };
    return c.json(result);
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

app.post("/api/control-panel/models/set", async (c) => {
  try {
    const { key, enabled } = await c.req.json();
    await invokePython(["models", "set", "--key", key, "--enabled", String(enabled)]);
    return c.json({ ok: true });
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

// ─── Tab 2: Pipelines ─────────────────────────────────────────────────────

app.get("/api/control-panel/pipelines", async (c) => {
  try {
    const result = (await invokePython(["pipelines"])) as {
      pipelines: Array<{
        source_name: string;
        file_path: string;
        primary_key: string;
        destinations: string[];
        enabled: boolean;
      }>;
    };
    return c.json(result);
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

app.post("/api/control-panel/pipelines/set", async (c) => {
  try {
    const { source_name, enabled } = await c.req.json();
    await invokePython(["pipelines", "set", "--source_name", source_name, "--enabled", String(enabled)]);
    return c.json({ ok: true });
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

// ─── Tab 3: Datasets ──────────────────────────────────────────────────────

app.get("/api/control-panel/datasets", async (c) => {
  try {
    const result = (await invokePython(["datasets"])) as {
      datasets: Array<{
        table_name: string;
        schema_name: string;
        column_count: number;
        source: string;
      }>;
    };
    return c.json(result);
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

// ─── Tab 4: Stacks ────────────────────────────────────────────────────────

app.get("/api/control-panel/stacks", async (c) => {
  try {
    const result = (await invokePython(["stacks"])) as {
      stacks: Array<{
        name: string;
        enabled: boolean;
        category: string;
      }>;
    };
    return c.json(result);
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

app.post("/api/control-panel/stacks/set", async (c) => {
  try {
    const { name, enabled } = await c.req.json();
    await invokePython(["stacks", "set", "--name", name, "--enabled", String(enabled)]);
    return c.json({ ok: true });
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

// ─── Tab 5: Registry ──────────────────────────────────────────────────────

app.get("/api/control-panel/registry", async (c) => {
  try {
    const result = (await invokePython(["registry"])) as {
      total: number;
      available: number;
      deprecated: number;
      by_family: Record<string, number>;
      drift_count: number;
      last_audit: string;
    };
    return c.json(result);
  } catch (e) {
    return c.json({ error: String(e) }, 500);
  }
});

export default app;
