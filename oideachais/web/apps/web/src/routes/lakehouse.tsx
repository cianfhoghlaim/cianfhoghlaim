import { useQuery } from "@tanstack/react-query";
import { client } from "../utils/orpc";

export function LakehousePage() {
  const { data } = useQuery({
    queryKey: ["lakehouse-health"],
    queryFn: () => client.lakehouse.health.call({}),
    refetchInterval: 10_000,
  });

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl text-cyan-400">Lakehouse Inspector</h1>
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
        {data ? <div className="flex items-center gap-3"><div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" /><span className="font-mono text-sm text-slate-200">Status: {(data as { status: string }).status}</span></div> : <p className="text-slate-400 text-sm">Connecting via oRPC…</p>}
      </div>
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-sm text-slate-400">
        <h2 className="font-bold text-cyan-300 mb-2">Stack</h2>
        Garage S3 · Lakekeeper · Lance NS · PostgreSQL · Hono+oRPC · MotherDuck
      </div>
    </div>
  );
}
