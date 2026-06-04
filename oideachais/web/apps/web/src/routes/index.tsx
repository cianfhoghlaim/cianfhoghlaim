export function IndexComponent() {
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
        {[
          { to: "/exams", icon: "❖", title: "Exam Papers", desc: "Full AGUI: sidebar + cards + chat. Browse SEC ?fp= URLs with CopilotKit tools." },
          { to: "/marking-schemes", icon: "✎", title: "Marking Schemes", desc: "Per-subject PCLM/SRPs rubric patterns, mark distribution, cross-year comparison." },
          { to: "/syllabus", icon: "⊛", title: "Syllabus Visualiser", desc: "NCCA/CCEA/SQA/CfW concept graph and Celtic-language coverage matrix." },
          { to: "/dives", icon: "🦆", title: "MotherDuck Dives", desc: "Zero-latency embedded Dives minted via the MotherDuck REST API embed-session endpoint." },
          { to: "/lakehouse", icon: "⌬", title: "Lakehouse Inspector", desc: "Garage S3, Lakekeeper, Lance NS, DuckLake console." },
          { to: "/runs", icon: "⏱", title: "Dagster Runs", desc: "Recent asset materialisations, retry heatmap, slowest partitions." },
        ].map((c) => (
          <a key={c.to} href={c.to} className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-emerald-700">
            <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
              <span>{c.icon}</span> {c.title}
            </h3>
            <p className="text-slate-400 text-sm mb-4">{c.desc}</p>
            <span className="btn-tactile inline-block text-sm">Open →</span>
          </a>
        ))}
      </div>
    </div>
  );
}
