import { Link, useRouterState } from "@tanstack/react-router";

const NAV = [
  { to: "/", label: "Curriculum", icon: "📚", end: true },
  { to: "/exams", label: "Exams (AGUI)", icon: "❖" },
  { to: "/marking-schemes", label: "Marking Schemes", icon: "✎" },
  { to: "/syllabus", label: "Syllabus", icon: "⊛" },
  { to: "/dives", label: "Dives (MotherDuck)", icon: "🦆" },
  { to: "/lakehouse", label: "Lakehouse", icon: "⌬" },
  { to: "/runs", label: "Dagster Runs", icon: "⏱" },
] as const;

export function Sidebar() {
  const location = useRouterState({ select: (s) => s.location.pathname });
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Oideachais Codex
        </h2>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
        {NAV.map((item) => {
          const active = item.end
            ? location === item.to
            : location.startsWith(item.to);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={
                "px-3 py-2 rounded-md text-slate-300 transition-colors font-medium text-sm flex items-center gap-2 " +
                (active
                  ? "bg-emerald-700/20 text-emerald-300 border border-emerald-800/50"
                  : "hover:bg-slate-800/50 border border-transparent")
              }
            >
              <span>{item.icon}</span> {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-slate-800 text-[10px] text-slate-500 font-mono">
        <div>MOTHERDUCK_ENABLED={String(Boolean(process.env.MOTHERDUCK_ENABLED))}</div>
        <div>LAKEHOUSE=ducklake</div>
        <div>PROXY=opencode-go</div>
      </div>
    </aside>
  );
}
