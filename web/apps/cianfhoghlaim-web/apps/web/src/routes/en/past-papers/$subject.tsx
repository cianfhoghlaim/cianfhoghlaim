// /en/past-papers/$subject — Past papers page (Cianfhoghlaim Oideachais)
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/past-papers/$subject")({
  component: PastPapersComponent,
});

function PastPapersComponent() {
  const { subject } = Route.useParams();
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        Past Papers — {subject.replace("-", " ")}
      </h1>
      <p className="text-slate-400">
        Lazy BAML-powered extraction. Click "Extract" on any paper to pull its
        structure, questions, and marking criteria via the on-demand BAML pipeline.
        The first 5 papers per session are free; afterwards, wait 24hrs for the daily
        ExtractionBudget to reset.
      </p>
      <div className="grid grid-cols-2 gap-4 mt-2" id="paper-list">
        {[2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015].map((year) => (
          <div key={year} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-sm font-bold text-slate-200">{year} — Higher Level</div>
            <div className="text-xs text-slate-500 mt-1">Paper 1 · Paper 2 · Marking Scheme</div>
            <button className="btn-tactile text-xs mt-2">Extract (lazy BAML)</button>
          </div>
        ))}
      </div>
    </div>
  );
}
