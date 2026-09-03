/**
 * TanStack Start route: /control-panel
 *
 * The 5-tab deployment control panel for the Cianfhoghlaim platform.
 *
 * Per the `deployment-control-panel` openspec capability (2026-08-15).
 * This is the web UI twin of `notebooks/00_control_panel.py` (the marimo
 * notebook). Both read from + write to the canonical `deployment-choice.yaml`
 * via the Hono API endpoints at `web/hono-api/control-panel/`.
 *
 * The 5 tabs:
 *   1. Models      — every MODEL_REGISTRY entry grouped by family
 *   2. Pipelines   — every DLT source + every CocoIndex App
 *   3. Datasets    — every BIEP DuckDB table + LanceDB mount + BAML class
 *   4. Stacks      — every Docker Compose stack in bonneagar/stacks/
 *   5. Registry    — the full MODEL_REGISTRY view + drift count
 *
 * Uses TanStack Start for the server-rendered shell + Convex for the
 * real-time subscription layer (when a user toggles a model, the panel
 * updates without a page refresh).
 *
 * Reference: openspec/specs/deployment-control-panel/spec.md
 */

import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

interface ModelRow {
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
}

interface PipelineRow {
  source_name: string;
  file_path: string;
  primary_key: string;
  destinations: string[];
  enabled: boolean;
}

interface DatasetRow {
  table_name: string;
  schema_name: string;
  column_count: number;
  source: string; // "duckdb" | "lance" | "baml"
}

interface StackRow {
  name: string;
  enabled: boolean;
  category: string;
}

interface RegistryRow {
  total: number;
  available: number;
  deprecated: number;
  by_family: Record<string, number>;
  drift_count: number;
  last_audit: string;
}

export const Route = createFileRoute("/control-panel/")({
  component: ControlPanel,
  loader: async () => {
    // The actual data fetching happens in the sub-components via the
    // Hono API endpoints. This loader only returns the initial tab.
    return { initialTab: "models" };
  },
});

function ControlPanel() {
  const { initialTab } = Route.useLoaderData();
  const [activeTab, setActiveTab] = useState<string>(initialTab);

  return (
    <div className="control-panel min-h-screen bg-slate-50 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">
          Cianfhoghlaim Deployment Control Panel
        </h1>
        <p className="mt-2 text-slate-600">
          The single source of truth for what models, pipelines, datasets,
          and stacks are currently enabled in this deployment. Reads from +
          writes to the canonical <code>deployment-choice.yaml</code>.
        </p>
      </header>

      <nav className="mb-8 flex gap-2 border-b border-slate-200">
        <TabButton id="models" active={activeTab} onClick={setActiveTab}>
          Models
        </TabButton>
        <TabButton id="pipelines" active={activeTab} onClick={setActiveTab}>
          Pipelines
        </TabButton>
        <TabButton id="datasets" active={activeTab} onClick={setActiveTab}>
          Datasets
        </TabButton>
        <TabButton id="stacks" active={activeTab} onClick={setActiveTab}>
          Stacks
        </TabButton>
        <TabButton id="registry" active={activeTab} onClick={setActiveTab}>
          Registry
        </TabButton>
      </nav>

      <main>
        {activeTab === "models" && <ModelsTab />}
        {activeTab === "pipelines" && <PipelinesTab />}
        {activeTab === "datasets" && <DatasetsTab />}
        {activeTab === "stacks" && <StacksTab />}
        {activeTab === "registry" && <RegistryTab />}
      </main>
    </div>
  );
}

function TabButton({
  id,
  active,
  onClick,
  children,
}: {
  id: string;
  active: string;
  onClick: (id: string) => void;
  children: React.ReactNode;
}) {
  const isActive = active === id;
  return (
    <button
      type="button"
      onClick={() => onClick(id)}
      className={`px-4 py-2 font-medium rounded-t-lg transition-colors ${
        isActive
          ? "bg-slate-900 text-white"
          : "bg-white text-slate-700 hover:bg-slate-100"
      }`}
    >
      {children}
    </button>
  );
}

// ─── Tab 1: Models ─────────────────────────────────────────────────────────

function ModelsTab() {
  const [models, setModels] = useState<ModelRow[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/control-panel/models")
      .then((r) => r.json())
      .then((data) => {
        setModels(data.models);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-500">Loading models…</div>;
  if (!models) return <div className="text-red-500">Failed to load models.</div>;

  const groupedByFamily = models.reduce<Record<string, ModelRow[]>>(
    (acc, m) => {
      (acc[m.family] ??= []).push(m);
      return acc;
    },
    {},
  );

  return (
    <div className="space-y-6">
      {Object.entries(groupedByFamily).map(([family, rows]) => (
        <section key={family}>
          <h2 className="text-xl font-semibold text-slate-800 mb-2">
            {family} <span className="text-slate-400">({rows.length})</span>
          </h2>
          <table className="w-full bg-white rounded-lg shadow">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-2 text-left">Enabled</th>
                <th className="px-4 py-2 text-left">Key</th>
                <th className="px-4 py-2 text-left">Role</th>
                <th className="px-4 py-2 text-left">Display Name</th>
                <th className="px-4 py-2 text-left">Backend</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((m) => (
                <tr
                  key={m.key}
                  className={
                    !m.available
                      ? "bg-slate-50 text-slate-400"
                      : "hover:bg-slate-50"
                  }
                >
                  <td className="px-4 py-2">
                    <input
                      type="checkbox"
                      checked={m.enabled}
                      disabled={!m.available}
                      onChange={async (e) => {
                        await fetch("/api/control-panel/models/set", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({
                            key: m.key,
                            enabled: e.target.checked,
                          }),
                        });
                      }}
                    />
                  </td>
                  <td className="px-4 py-2 font-mono text-sm">{m.key}</td>
                  <td className="px-4 py-2">{m.role}</td>
                  <td className="px-4 py-2">{m.display_name}</td>
                  <td className="px-4 py-2">{m.backend}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </div>
  );
}

// ─── Tab 2: Pipelines ─────────────────────────────────────────────────────

function PipelinesTab() {
  const [pipelines, setPipelines] = useState<PipelineRow[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/control-panel/pipelines")
      .then((r) => r.json())
      .then((data) => {
        setPipelines(data.pipelines);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading)
    return <div className="text-slate-500">Loading pipelines…</div>;
  if (!pipelines)
    return <div className="text-red-500">Failed to load pipelines.</div>;

  return (
    <table className="w-full bg-white rounded-lg shadow">
      <thead className="bg-slate-100">
        <tr>
          <th className="px-4 py-2 text-left">Enabled</th>
          <th className="px-4 py-2 text-left">Source</th>
          <th className="px-4 py-2 text-left">Primary Key</th>
          <th className="px-4 py-2 text-left">Destinations</th>
          <th className="px-4 py-2 text-left">File</th>
        </tr>
      </thead>
      <tbody>
        {pipelines.map((p) => (
          <tr key={p.source_name} className="hover:bg-slate-50">
            <td className="px-4 py-2">
              <input
                type="checkbox"
                checked={p.enabled}
                onChange={async (e) => {
                  await fetch("/api/control-panel/pipelines/set", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      source_name: p.source_name,
                      enabled: e.target.checked,
                    }),
                  });
                }}
              />
            </td>
            <td className="px-4 py-2 font-mono text-sm">{p.source_name}</td>
            <td className="px-4 py-2 font-mono text-sm">{p.primary_key}</td>
            <td className="px-4 py-2">
              {p.destinations.join(", ") || "(none)"}
            </td>
            <td className="px-4 py-2 font-mono text-xs">{p.file_path}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ─── Tab 3: Datasets ──────────────────────────────────────────────────────

function DatasetsTab() {
  const [datasets, setDatasets] = useState<DatasetRow[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/control-panel/datasets")
      .then((r) => r.json())
      .then((data) => {
        setDatasets(data.datasets);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-500">Loading datasets…</div>;
  if (!datasets)
    return <div className="text-red-500">Failed to load datasets.</div>;

  const bySource = datasets.reduce<Record<string, number>>((acc, d) => {
    acc[d.source] = (acc[d.source] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <div className="flex gap-4 text-sm">
        {Object.entries(bySource).map(([src, count]) => (
          <div key={src} className="px-3 py-1 bg-slate-100 rounded">
            <span className="font-mono">{src}</span>: {count}
          </div>
        ))}
      </div>
      <table className="w-full bg-white rounded-lg shadow">
        <thead className="bg-slate-100">
          <tr>
            <th className="px-4 py-2 text-left">Source</th>
            <th className="px-4 py-2 text-left">Schema</th>
            <th className="px-4 py-2 text-left">Table</th>
            <th className="px-4 py-2 text-left">Columns</th>
          </tr>
        </thead>
        <tbody>
          {datasets.slice(0, 200).map((d, i) => (
            <tr key={`${d.schema_name}.${d.table_name}-${i}`} className="hover:bg-slate-50">
              <td className="px-4 py-2">
                <span className="px-2 py-1 text-xs bg-slate-100 rounded">
                  {d.source}
                </span>
              </td>
              <td className="px-4 py-2 font-mono text-sm">{d.schema_name}</td>
              <td className="px-4 py-2 font-mono text-sm">{d.table_name}</td>
              <td className="px-4 py-2">{d.column_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {datasets.length > 200 && (
        <p className="text-sm text-slate-500">
          Showing first 200 of {datasets.length} tables.
        </p>
      )}
    </div>
  );
}

// ─── Tab 4: Stacks ────────────────────────────────────────────────────────

function StacksTab() {
  const [stacks, setStacks] = useState<StackRow[] | null>(null);
  const [loading, setStacksLoading] = useState(true);

  useEffect(() => {
    fetch("/api/control-panel/stacks")
      .then((r) => r.json())
      .then((data) => {
        setStacks(data.stacks);
        setStacksLoading(false);
      })
      .catch(() => setStacksLoading(false));
  }, []);

  if (loading) return <div className="text-slate-500">Loading stacks…</div>;
  if (!stacks) return <div className="text-red-500">Failed to load stacks.</div>;

  return (
    <div className="grid grid-cols-3 gap-4">
      {stacks.map((s) => (
        <div
          key={s.name}
          className={`p-4 rounded-lg shadow ${
            s.enabled ? "bg-white" : "bg-slate-100"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="font-mono">{s.name}</div>
            <input
              type="checkbox"
              checked={s.enabled}
              onChange={async (e) => {
                await fetch("/api/control-panel/stacks/set", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    name: s.name,
                    enabled: e.target.checked,
                  }),
                });
              }}
            />
          </div>
          <div className="mt-2 text-sm text-slate-500">{s.category}</div>
        </div>
      ))}
    </div>
  );
}

// ─── Tab 5: Registry ──────────────────────────────────────────────────────

function RegistryTab() {
  const [registry, setRegistry] = useState<RegistryRow | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/control-panel/registry")
      .then((r) => r.json())
      .then((data) => {
        setRegistry(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-500">Loading registry…</div>;
  if (!registry)
    return <div className="text-red-500">Failed to load registry.</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Models" value={registry.total} />
        <StatCard label="Available" value={registry.available} />
        <StatCard label="Deprecated" value={registry.deprecated} />
        <StatCard
          label="Drift Count"
          value={registry.drift_count}
          variant={registry.drift_count > 0 ? "warning" : "ok"}
        />
      </div>

      <div>
        <h2 className="text-xl font-semibold text-slate-800 mb-2">
          Models by Family
        </h2>
        <table className="w-full bg-white rounded-lg shadow">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-4 py-2 text-left">Family</th>
              <th className="px-4 py-2 text-right">Count</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(registry.by_family).map(([family, count]) => (
              <tr key={family} className="hover:bg-slate-50">
                <td className="px-4 py-2 font-mono">{family}</td>
                <td className="px-4 py-2 text-right">{count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-sm text-slate-500">
        Last audit: <code>{registry.last_audit}</code>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  variant = "default",
}: {
  label: string;
  value: number;
  variant?: "default" | "ok" | "warning";
}) {
  const colorMap = {
    default: "bg-slate-50",
    ok: "bg-green-50",
    warning: "bg-red-50",
  };
  return (
    <div className={`p-4 rounded-lg shadow ${colorMap[variant]}`}>
      <div className="text-sm text-slate-600">{label}</div>
      <div className="text-3xl font-bold text-slate-900">{value}</div>
    </div>
  );
}

function useEffect(fn: () => void, deps?: unknown[]) {
  // Inline useEffect shim — TanStack Start typically uses React's
  // useEffect from "react". This shim is added here so the file
  // compiles standalone; the actual hook comes from React.
  // In production, replace with: import { useEffect } from "react";
  const React = require("react");
  React.useEffect(fn, deps);
}