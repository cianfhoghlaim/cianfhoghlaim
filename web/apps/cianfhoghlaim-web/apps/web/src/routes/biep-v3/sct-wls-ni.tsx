/**
 * TanStack Start route: /biep-v3/sct-wls-ni
 * SCT + WLS + NI cohorts dashboard (380).
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/biep-v3/sct-wls-ni")({
  component: BIEPv3SctWlsNiPage,
  loader: async () => {
    return { jurisdictions: ["scotland", "wales", "northern_ireland"], expected_cohorts: 380 };
  },
});

function BIEPv3SctWlsNiPage() {
  const { jurisdictions, expected_cohorts } = Route.useLoaderData();
  return (
    <main className="biep-v3-sct-wls-ni">
      <h1>🏴󠁧󠁢󠁳󠁣󠁴󠁿🏴󠁧󠁢󠁷󠁬󠁳󠁿🇬🇧 BIEP v3 — Scotland + Wales + Northern Ireland</h1>
      <p>Expected: {expected_cohorts} cohorts across {jurisdictions.join(" + ")}.</p>
      <ul>
        <li>Scotland (SQA): 50 SCQF subjects × 3 levels = 150 cohorts</li>
        <li>Wales (WJEC): 80 WJEC subjects × 2 levels = 160 cohorts</li>
        <li>Northern Ireland (CCEA): 35 CCEA subjects × 2 levels = 70 cohorts</li>
      </ul>
    </main>
  );
}
