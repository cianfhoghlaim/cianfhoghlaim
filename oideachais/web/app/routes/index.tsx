export function Index() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 h-full">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">Welcome to Awen Hub</h1>
        <p className="text-slate-400 text-lg">
          Your agentic gateway to the Oideachais Celtic Education Engine — DLT
          ingestion, DuckLake catalog, MotherDuck Dives, and CopilotKit AGUI
          visualisers.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <a
          href="/exams"
          className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-emerald-700"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-emerald-500">❖</span> Exam Visualiser
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Full AGUI: sidebar + cards + CopilotKit chat + TanStack AI tools
            against the MotherDuck / DuckLake lakehouse.
          </p>
          <span className="btn-tactile inline-block text-sm">Open Exam Visualiser →</span>
        </a>

        <a
          href="/dives"
          className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-blue-700"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-blue-500">⟠</span> Embedded Dives
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Interactive, zero-latency MotherDuck Dive embeds via the REST API
            embed-session endpoint.
          </p>
          <span className="btn-tactile inline-block text-sm">Open MotherDuck →</span>
        </a>

        <a
          href="/marking-schemes"
          className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-amber-700"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-amber-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-amber-500">✎</span> Marking Schemes
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Per-subject rubric patterns (PCLM, SRPs, equation steps) with
            cross-year comparison.
          </p>
          <span className="btn-tactile inline-block text-sm">Analyse →</span>
        </a>

        <a
          href="/syllabus"
          className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-purple-700"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-purple-500">⊛</span> Syllabus Visualiser
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            NCCA / CCEA / SQA / CfW concept graph and Celtic-language coverage
            matrix.
          </p>
          <span className="btn-tactile inline-block text-sm">Open →</span>
        </a>

        <a
          href="/lakehouse"
          className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-cyan-700"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-cyan-500">⌬</span> Lakehouse Inspector
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Garage S3, Lakekeeper, Lance NS, DuckLake console in one pane.
          </p>
          <span className="btn-tactile inline-block text-sm">Inspect →</span>
        </a>

        <a
          href="/runs"
          className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-rose-700"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-rose-600/10 rounded-bl-full -z-10 group-hover:scale-110 transition-transform"></div>
          <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
            <span className="text-rose-500">⏱</span> Dagster Runs
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Recent asset materialisations, retry heatmap, slowest partitions.
          </p>
          <span className="btn-tactile inline-block text-sm">View runs →</span>
        </a>
      </div>
    </div>
  );
}
