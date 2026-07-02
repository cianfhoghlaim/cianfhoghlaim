// Sidebar — Cianfhoghlaim OS left navigation
// Bilingual nav: 6 subnations / 8 subject realms / 4 diagram modes / practice / assets / dagster runs / lakehouse

"use client";

import * as React from "react";
import { Link, useRouterState } from "@tanstack/react-router";

const NAV: Array<{ to: string; label: string; ga: string; icon: string }> = [
  { to: "/", label: "Curriculum", ga: "Curaclam", icon: "📚" },
  { to: "/en/map", label: "Map", ga: "Léarscáil", icon: "🗺️" },
  { to: "/en/key-competencies", label: "Key Competencies", ga: "Príochomhardaigh", icon: "🎯" },
  { to: "/ga/leaving-cert/gaeilge", label: "Gaeilge (v1)", ga: "Gaeilge", icon: "🇮🇪" },
  { to: "/en/leaving-cert/mathematics", label: "Mathematics (v1)", ga: "Mata", icon: "🧮" },
  { to: "/en/assets/mathematics", label: "Assets Gallery", ga: "Sócmhainní", icon: "🎨" },
];

export function Sidebar() {
  const location = useRouterState({ select: (s) => s.location.pathname });

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Cianfhoghlaim OS
        </h2>
        <p className="text-[10px] text-slate-600 mt-1">
          Aes Sedai — servants of all
        </p>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
        {NAV.map((item) => {
          const active =
            item.to === "/" ? location === "/" : location.startsWith(item.to);
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
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-slate-800 text-[10px] text-slate-500 font-mono">
        <div>CONVEX=conic-leaving-cert</div>
        <div>API=Hono+oRPC</div>
        <div>Theming=Brown Ajah</div>
      </div>
    </aside>
  );
}