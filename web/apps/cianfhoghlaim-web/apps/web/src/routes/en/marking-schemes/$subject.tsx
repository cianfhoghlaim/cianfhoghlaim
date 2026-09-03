// /en/marking-schemes/$subject (Cianfhoghlaim Oideachais)
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/marking-schemes/$subject")({
  component: MarkingSchemesComponent,
});

function MarkingSchemesComponent() {
  const { subject } = Route.useParams();
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        Marking Schemes — {subject.replace("-", " ")}
      </h1>
      <p className="text-slate-400">
        Per-subject marking scheme data from SEC (State Examinations Commission).
        Surfaces PCLM, SRP, EQUATION_STEPS, and the 9 other RubricStyle values per subject.
      </p>
    </div>
  );
}
