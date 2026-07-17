/**
 * TanStack Start route: /biep-v3
 *
 * The 8-jurisdiction overview page (parallel to /biep-v2).
 * Per the 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 change.
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/biep-v3/")({
  component: BIEPv3OverviewPage,
  loader: async () => {
    return {
      loaded_at: new Date().toISOString(),
    };
  },
});

const JURISDICTIONS = [
  { code: "ireland",            display: "🇮🇪 Ireland",                  cohorts: 544 },
  { code: "england",            display: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 England",          cohorts: 276 },
  { code: "scotland",           display: "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland",        cohorts: 150 },
  { code: "wales",              display: "🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales",            cohorts: 160 },
  { code: "northern_ireland",   display: "🇬🇧 Northern Ireland",          cohorts: 70 },
  { code: "jersey",             display: "🇯🇪 Jersey",                    cohorts: 120 },
  { code: "guernsey",           display: "🇬🇬 Guernsey",                  cohorts: 120 },
  { code: "isle_of_man",        display: "🇮🇲 Isle of Man",               cohorts: 120 },
];

function BIEPv3OverviewPage() {
  return (
    <main className="biep-v3-overview">
      <h1>🇮🇪🇬🇧 BIEP v3 — 8 British Isles Jurisdictions</h1>
      <p>The canonical British Isles subject registry covers {JURISDICTIONS.reduce((a, j) => a + j.cohorts, 0):,} cohorts.</p>
      <div className="jurisdiction-grid">
        {JURISDICTIONS.map((j) => (
          <a key={j.code} href={`/biep-v3/${j.code.replace("_", "-")}`} className="jurisdiction-card">
            <h2>{j.display}</h2>
            <p>{j.cohorts} cohorts</p>
          </a>
        ))}
      </div>
    </main>
  );
}
