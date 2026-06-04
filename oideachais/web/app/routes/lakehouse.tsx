import { useQuery } from "@tanstack/react-query";

interface HealthCheck {
  service: string;
  status: "online" | "offline" | "unknown";
  detail?: string;
}

async function fetchHealth(): Promise<HealthCheck[]> {
  try {
    const r = await fetch("/api/lakehouse/health");
    if (r.ok) {
      const data = (await r.json()) as { checks: HealthCheck[] };
      return data.checks;
    }
    return [];
  } catch {
    return [];
  }
}

export function Lakehouse() {
  const { data = [], isLoading, refetch } = useQuery({
    queryKey: ["lakehouse-health"],
    queryFn: fetchHealth,
    refetchInterval: 10_000,
  });

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <header className="flex items-baseline">
        <h1 className="font-cinzel text-3xl text-cyan-400">Lakehouse Inspector</h1>
        <button
          onClick={() => refetch()}
          className="ml-auto btn-tactile text-sm"
        >
          {isLoading ? "Checking…" : "Refresh"}
        </button>
      </header>

      {data.length === 0 ? (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-slate-400 text-sm">
          Health check endpoint <code>/api/lakehouse/health</code> not yet
          reachable. Start the lakehouse stack with{" "}
          <code>cd infrastructure/stacks/storage/lakehouse &amp;&amp; docker compose up -d</code>.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {data.map((c) => (
            <div
              key={c.service}
              className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center gap-3"
            >
              <div
                className={
                  "w-3 h-3 rounded-full " +
                  (c.status === "online"
                    ? "bg-emerald-500 animate-pulse"
                    : c.status === "offline"
                      ? "bg-red-500"
                      : "bg-slate-500")
                }
              />
              <div className="flex-1">
                <div className="font-mono text-sm text-slate-200">{c.service}</div>
                {c.detail && (
                  <div className="text-xs text-slate-500">{c.detail}</div>
                )}
              </div>
              <span
                className={
                  "text-xs uppercase font-bold " +
                  (c.status === "online" ? "text-emerald-400" : "text-red-400")
                }
              >
                {c.status}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-slate-400 text-sm">
        <h2 className="font-bold text-cyan-300 mb-2">Stack composition</h2>
        <ul className="space-y-1 list-disc list-inside">
          <li><strong>Garage S3</strong> — S3-compatible CRDT object storage on <code>:3900-3904</code></li>
          <li><strong>Lakekeeper</strong> — Iceberg REST catalog on <code>:8181</code></li>
          <li><strong>Lance NS</strong> — Iceberg adapter sidecar on <code>:8182</code></li>
          <li><strong>PostgreSQL</strong> — Lakekeeper metadata on <code>:5433</code></li>
          <li><strong>MotherDuck</strong> — cloud query engine (when <code>MOTHERDUCK_ENABLED=true</code>)</li>
        </ul>
      </div>
    </div>
  );
}
