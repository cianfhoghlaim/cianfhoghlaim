export function IndexComponent() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 h-full">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">Fáilte go Cianfhoghlaim Oideachais</h1>
        <p className="text-slate-400 text-lg">
          Your bilingual, agentic gateway to the entire Irish education system — Aistear,
          Primary, Junior Cycle, Senior Cycle, and Tertiary. BAML-extracted curriculum,
          exam papers, marking schemes, Chief Examiner reports, CAO points, and matriculation
          rules, all indexed in Cognee + LanceDB and served via CopilotKit AGUI.
        </p>
        <p className="text-slate-500 text-sm">
          <span className="font-mono">Welcome to Cianfhoghlaim Oideachais</span> · Bilingual EN/GA · 5 stages · 50+ LC subjects
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {[
          { to: "/exams", icon: "❖", title: "Exam Papers", desc: "Senior Cycle past papers, lazy BAML extraction, rubric-aware chat." },
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
