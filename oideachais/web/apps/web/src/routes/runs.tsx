import { useQuery } from "@tanstack/react-query";

interface DagsterRun {
  runId: string; jobName: string; status: string; startTime: string; endTime?: string;
}

async function fetchRuns(): Promise<DagsterRun[]> {
  const url = import.meta.url;
  try {
    const r = await fetch("http://localhost:3000/graphql?query={runsOrError(limit:20){__typename...on Runs{results{runId jobName status startTime endTime}}}}");
    if (!r.ok) return [];
    const p = await r.json() as { data?: { runsOrError?: { results?: DagsterRun[] } } };
    return p.data?.runsOrError?.results ?? [];
  } catch { return []; }
}

export function RunsPage() {
  const { data, isLoading, refetch } = useQuery({ queryKey: ["dagster-runs"], queryFn: fetchRuns, refetchInterval: 15_000 });
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-4">
      <header className="flex items-baseline"><h1 className="font-cinzel text-3xl text-rose-400">Dagster Runs</h1><button onClick={() => refetch()} className="ml-auto btn-tactile text-sm">{isLoading ? "Refreshing…" : "Refresh"}</button></header>
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
        {data && data.length > 0 ? (
          <table className="w-full text-sm"><thead><tr className="text-left text-rose-300 border-b border-slate-800"><th className="py-2 px-2">Run ID</th><th className="py-2 px-2">Job</th><th className="py-2 px-2">Status</th></tr></thead>
            <tbody>{data.map((r) => <tr key={r.runId} className="border-b border-slate-900"><td className="py-2 px-2 font-mono text-xs text-slate-400">{r.runId.slice(0,8)}</td><td className="py-2 px-2 text-slate-200">{r.jobName}</td><td className="py-2 px-2"><span className={`px-2 py-0.5 rounded text-xs font-bold ${r.status==="SUCCESS"?"bg-emerald-700/30 text-emerald-300":"bg-slate-700/30 text-slate-300"}`}>{r.status}</span></td></tr>)}</tbody></table>) : <p className="text-slate-400 text-sm">No runs visible. Start Dagster.</p>}
      </div>
    </div>
  );
}
