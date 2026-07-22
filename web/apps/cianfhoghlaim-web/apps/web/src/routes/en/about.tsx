// /en/about — About Cianfhoghlaim Oideachais
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/about")({
  component: AboutComponent,
});

function AboutComponent() {
  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        Cianfhoghlaim Oideachais
      </h1>
      <p className="text-slate-400">
        A bilingual (EN/GA) agentic platform covering the entire Irish education system:
        Aistear, Primary, Junior Cycle, Senior Cycle, and Tertiary.
      </p>
      <div className="prose prose-slate max-w-none text-sm">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-emerald-400 font-bold mb-2">5 stages</div>
            <div className="text-slate-400">Aistear → Primary → Junior Cycle → Senior Cycle → Tertiary</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-emerald-400 font-bold mb-2">50+ LC subjects</div>
            <div className="text-slate-400">Exam papers, marking schemes, Chief Examiner reports</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-emerald-400 font-bold mb-2">Bilingual EN/GA</div>
            <div className="text-slate-400">Every BAML field has *_en and *_ga variants</div>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-emerald-400 font-bold mb-2">Agentic AG-UI chat</div>
            <div className="text-slate-400">CopilotKit + Agno stage teams + Cognee knowledge graph</div>
          </div>
        </div>
      </div>
    </div>
  );
}
