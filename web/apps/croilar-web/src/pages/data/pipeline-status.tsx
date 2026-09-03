interface Asset {
  name: string;
  group: string;
  status: "idle" | "running" | "success" | "failed";
  lastRun: string;
}

const GROUP_COLORS: Record<string, string> = {
  music: "bg-violet-600/10 text-violet-400 border-violet-800/50",
  cv: "bg-emerald-600/10 text-emerald-400 border-emerald-800/50",
  teaching: "bg-cyan-600/10 text-cyan-400 border-cyan-800/50",
  identity: "bg-amber-600/10 text-amber-400 border-amber-800/50",
  "cross-link": "bg-rose-600/10 text-rose-400 border-rose-800/50",
};

const STATUS_DOTS: Record<string, string> = {
  idle: "bg-slate-500",
  running: "bg-blue-500 animate-pulse",
  success: "bg-emerald-500",
  failed: "bg-red-500",
};

export function PipelineStatusSection({ assets }: { assets: Asset[] }) {
  const groups = [...new Set(assets.map((a) => a.group))];

  return (
    <section>
      <h2 className="text-2xl font-bold mb-6">Pipeline Assets</h2>
      {groups.map((group) => (
        <div key={group} className="mb-8">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            {group}
          </h3>
          <div className="space-y-2">
            {assets
              .filter((a) => a.group === group)
              .map((asset) => (
                <div
                  key={asset.name}
                  className="flex items-center justify-between rounded-lg bg-card border border-border px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-2 h-2 rounded-full ${STATUS_DOTS[asset.status]}`} />
                    <code className="text-sm">{asset.name}</code>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${GROUP_COLORS[group]}`}>
                      {group}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground font-mono">{asset.lastRun}</span>
                </div>
              ))}
          </div>
        </div>
      ))}
    </section>
  );
}
