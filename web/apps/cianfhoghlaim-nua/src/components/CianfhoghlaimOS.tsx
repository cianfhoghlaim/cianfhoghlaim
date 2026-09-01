/**
 * CianfhoghlaimOS — the unified app shell for the consolidated
 * cianfhoghlaim-nua web app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change.
 * Combines the 5 previous app shells (oideachais Header/Sidebar +
 * cianfhoghlaimOS + croilar Header + tuatha MMO shell + admin
 * dashboard sidebar) into one.
 */

import * as React from "react";

import { StageOverview, DEFAULT_BRITISH_ISLES_STAGES } from "@cianfhoghlaim/a2ui";

export interface CianfhoghlaimOSProps {
  children: React.ReactNode;
  activeRouteGroup?: "student" | "educator" | "researcher" | "author" | "mmo" | "admin";
  onSelectRouteGroup?: (group: "student" | "educator" | "researcher" | "author" | "mmo" | "admin") => void;
}

const ROUTE_GROUP_LABELS: Record<string, string> = {
  student: "Student",
  educator: "Educator",
  researcher: "Researcher",
  author: "Author",
  mmo: "MMO",
  admin: "Admin",
};

export function CianfhoghlaimOS({
  children,
  activeRouteGroup = "student",
  onSelectRouteGroup,
}: CianfhoghlaimOSProps): React.ReactElement {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <header
        className="border-b border-slate-200 bg-white px-6 py-3 shadow-sm"
        role="banner"
      >
        <div className="mx-auto flex max-w-7xl items-baseline justify-between gap-4">
          <h1 className="text-xl font-bold text-slate-900">
            cianfhoghlaim-nua
          </h1>
          <span className="text-xs text-slate-500">
            consolidated platform · v6 era · 2026-09-01
          </span>
        </div>
      </header>

      <nav
        className="border-b border-slate-200 bg-white px-6 py-2"
        aria-label="Audience route groups"
      >
        <ol className="mx-auto flex max-w-7xl flex-wrap gap-2">
          {(Object.keys(ROUTE_GROUP_LABELS) as Array<keyof typeof ROUTE_GROUP_LABELS>).map(
            (group) => (
              <li key={group}>
                <button
                  type="button"
                  onClick={onSelectRouteGroup ? () => onSelectRouteGroup(group) : undefined}
                  aria-pressed={group === activeRouteGroup}
                  className={
                    "rounded-md border px-3 py-1.5 text-sm transition " +
                    (group === activeRouteGroup
                      ? "border-indigo-500 bg-indigo-50 font-medium text-indigo-700"
                      : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50")
                  }
                >
                  {ROUTE_GROUP_LABELS[group]}
                </button>
              </li>
            ),
          )}
        </ol>
      </nav>

      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-6" role="main">
        <StageOverview
          stages={DEFAULT_BRITISH_ISLES_STAGES}
          selectedStage="leaving_cert"
        />
        <div className="mt-6">{children}</div>
      </main>

      <footer
        className="border-t border-slate-200 bg-white px-6 py-3 text-xs text-slate-500"
        role="contentinfo"
      >
        <div className="mx-auto max-w-7xl">
          Cianfhoghlaim v6 era · Phase 3 web consolidation · A2UI v0.9
          catalog mounted via <code>@cianfhoghlaim/a2ui/createCatalog()</code>
        </div>
      </footer>
    </div>
  );
}

export default CianfhoghlaimOS;