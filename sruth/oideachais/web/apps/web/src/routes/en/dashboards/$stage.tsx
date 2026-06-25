// /en/dashboards/$stage — Marimo dashboard mount (Cianfhoghlaim Oideachais)
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/dashboards/$stage")({
  component: DashboardComponent,
});

function DashboardComponent() {
  const { stage } = Route.useParams();
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-4">
      <h1 className="font-cinzel text-2xl font-bold text-slate-100">
        {stage} dashboard
      </h1>
      <p className="text-slate-400">
        Reads from `oideachais.{stage}` Cognee dataset + `{stage}_knowledge_graph` LanceDB.
        See `oideachais/notebooks/dashboards/{stage}.py` for the marimo source.
      </p>
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-center text-slate-500">
        Marimo dashboard embedding is a Phase 8 deliverable.
        The notebook is ready at oideachais/notebooks/dashboards/{stage}.py.
      </div>
    </div>
  );
}
