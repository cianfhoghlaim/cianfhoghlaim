import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { client } from "../utils/orpc";

const SUBJECTS = [
  "mathematics", "english", "gaeilge", "biology", "chemistry", "physics",
  "geography", "history", "french", "german", "spanish",
  "accounting", "business", "economics", "art", "music",
  "home-economics", "computer-science", "agricultural-science",
  "applied-mathematics", "classical-studies", "construction-studies",
  "design-and-communication-graphics", "engineering", "italian",
  "japanese", "latin", "physical-education", "religious-education", "technology",
];

const LEVELS = [
  { value: "leaving_certificate", label: "Leaving Cert" },
  { value: "junior_cycle", label: "Junior Cycle" },
  { value: "leaving_certificate_applied", label: "LCA" },
] as const;

const TYPES = [
  { value: "exam_papers", label: "Exam papers" },
  { value: "marking_schemes", label: "Marking schemes" },
] as const;

const YEARS = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014] as const;

export function ExamsPage() {
  const [subject, setSubject] = useState("mathematics");
  const [year, setYear] = useState(2024);
  const [level, setLevel] = useState("leaving_certificate");
  const [materialType, setMaterialType] = useState("exam_papers");
  const [chatOpen, setChatOpen] = useState(true);

  const { data: materials = [], isLoading } = useQuery({
    queryKey: ["exams-list", subject, year, level, materialType],
    queryFn: () =>
      client.exams.list.call({
        subject,
        year,
        level: level as "leaving_certificate",
        materialType: materialType as "exam_papers",
      }),
  });

  return (
    <div className="h-full flex gap-4">
      <aside className="w-64 shrink-0 bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col gap-4">
        <h2 className="font-cinzel text-lg text-emerald-400">Filters</h2>
        <select value={subject} onChange={(e) => setSubject(e.target.value)} className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm">
          {SUBJECTS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={year} onChange={(e) => setYear(Number(e.target.value))} className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm">
          {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
        {LEVELS.map((l) => (
          <label key={l.value} className="text-sm flex items-center gap-2">
            <input type="radio" checked={level === l.value} onChange={() => setLevel(l.value)} className="accent-emerald-500" /> {l.label}
          </label>
        ))}
        {TYPES.map((t) => (
          <label key={t.value} className="text-sm flex items-center gap-2">
            <input type="radio" checked={materialType === t.value} onChange={() => setMaterialType(t.value)} className="accent-emerald-500" /> {t.label}
          </label>
        ))}
      </aside>

      <section className="flex-1 flex flex-col gap-3 overflow-y-auto">
        <header className="flex items-baseline gap-3">
          <h1 className="font-cinzel text-2xl text-emerald-400">{subject} · {year}</h1>
          <span className="text-sm text-slate-400">
            {LEVELS.find((l) => l.value === level)?.label} · {TYPES.find((t) => t.value === materialType)?.label}
          </span>
          <span className="ml-auto text-sm text-slate-500">{isLoading ? "Loading…" : `${materials.length} rows`}</span>
        </header>
        {materials.length === 0 ? (
          <p className="text-slate-400 text-sm">No rows. Run <code>sec_examinations_leaving_certificate</code> in Dagster.</p>
        ) : (
          <ul className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {materials.map((m: Record<string, unknown>, i: number) => (
              <li key={`${String(m.pdf_url)}-${i}`} className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col gap-2">
                <h3 className="font-bold text-slate-100">{String(m.title ?? m.pdf_url ?? "").slice(0, 60)}</h3>
                <div className="text-xs text-slate-400 flex gap-3">
                  <span>Level: {String(m.level)}</span><span>Type: {String(m.material_type)}</span>
                </div>
                <a href={String(m.pdf_url)} target="_blank" rel="noopener noreferrer" className="text-xs text-emerald-400 break-all font-mono">{String(m.pdf_url).slice(0, 120)}</a>
              </li>
            ))}
          </ul>
        )}
      </section>

      <aside className={`shrink-0 transition-all ${chatOpen ? "w-96" : "w-12"}`}>
        <div className="bg-slate-950 border border-slate-800 rounded-xl h-full flex flex-col">
          <div className="flex items-center justify-between p-3 border-b border-slate-800">
            {chatOpen && <span className="font-cinzel text-emerald-400">Oideachas</span>}
          </div>
        </div>
        <div className="h-1/2 border-t border-slate-800 overflow-y-auto p-4">
          {chatOpen && <div className="flex-1 p-3 text-xs text-slate-500 italic">Open Oideachas Chat (bottom-right) and ask: "Compare Higher vs Ordinary 2024 Mathematics"</div>}
        </div>
      </aside>
    </div>
  );
}
