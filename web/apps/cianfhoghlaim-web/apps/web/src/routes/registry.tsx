/**
 * TanStack Start route: /registry
 * Renders the BIEP v3 4-tab companion notebook inline.
 */
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/registry")({
  component: BIEPv3RegistryPage,
  loader: async () => {
    return { notebook_url: "http://localhost:2718/notebooks/18_cianfhoghlaim_subject_registry.py" };
  },
});

function BIEPv3RegistryPage() {
  const { notebook_url } = Route.useLoaderData();
  return (
    <main className="biep-v3-registry">
      <h1>📚 Cianfhoghlaim British Isles Subject Registry</h1>
      <p>The canonical British Isles subject registry (BIEP v3). 4 tabs: Format doc + Nation comparison + Bridge explorer + Drift detector.</p>
      <iframe src={notebook_url} width="100%" height="1200" title="Cianfhoghlaim subject registry" />
    </main>
  );
}
