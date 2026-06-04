import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate, useSearch } from "@tanstack/react-router";
import { listExamMaterials } from "../server/lakehouse";

const SUBJECTS = [
  "mathematics", "english", "gaeilge", "biology", "chemistry", "physics",
  "geography", "history", "french", "german", "spanish",
  "accounting", "business", "economics", "art", "music",
  "home-economics", "computer-science", "agricultural-science",
  "applied-mathematics", "classical-studies", "construction-studies",
  "design-and-communication-graphics", "engineering", "italian",
  "japanese", "latin", "physical-education", "religious-education",
  "technology", "irish",
] as const;

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

export function Exams() {
  const search = useSearch({ from: "/exams" });
  const navigate = useNavigate();
  const [chatOpen, setChatOpen] = useState(true);

  const setFilter = (patch: Partial<typeof search>) =>
    navigate({ search: (prev) => ({ ...prev, ...patch }), to: "/exams" });

  const { data: materials = [], isLoading } = useQuery({
    queryKey: ["exam-materials", search],
    queryFn: () =>
      listExamMaterials({
        data: {
          subject: search.subject,
          year: search.year,
          level: search.level as "leaving_certificate",
          materialType: search.materialType as "exam_papers",
        },
      }),
  });

  return (
    <div className="h-full flex gap-4">
      <aside className="w-64 shrink-0 bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col gap-4">
        <h2 className="font-cinzel text-lg text-emerald-400 mb-3">Filters</h2>

        <label className="text-xs uppercase tracking-wider text-slate-500">Subject</label>
        <select
          value={search.subject}
          onChange={(e) => setFilter({ subject: e.target.value })}
          className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm"
        >
          {SUBJECTS.map((s) => (
            <option key={s} value={s}>{s.replace(/-/g, " ")}</option>
          ))}
        </select>

        <label className="text-xs uppercase tracking-wider text-slate-500">Year</label>
        <select
          value={search.year}
          onChange={(e) => setFilter({ year: Number(e.target.value) })}
          className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm"
        >
          {YEARS.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        <label className="text-xs uppercase tracking-wider text-slate-500">Level</label>
        <div className="flex flex-col gap-1">
          {LEVELS.map((l) => (
            <label key={l.value} className="text-sm flex items-center gap-2">
              <input
                type="radio"
                checked={search.level === l.value}
                onChange={() => setFilter({ level: l.value })}
                className="accent-emerald-500"
              />
              {l.label}
            </label>
          ))}
        </div>

        <label className="text-xs uppercase tracking-wider text-slate-500">Material type</label>
        <div className="flex flex-col gap-1">
          {TYPES.map((t) => (
            <label key={t.value} className="text-sm flex items-center gap-2">
              <input
                type="radio"
                checked={search.materialType === t.value}
                onChange={() => setFilter({ materialType: t.value })}
                className="accent-emerald-500"
              />
              {t.label}
            </label>
          ))}
        </div>
      </aside>

      <section className="flex-1 flex flex-col gap-3 overflow-y-auto">
        <header className="flex items-baseline gap-3">
          <h1 className="font-cinzel text-2xl text-emerald-400">
            {search.subject.replace(/-/g, " ")} · {search.year}
          </h1>
          <span className="text-sm text-slate-400">
            {LEVELS.find((l) => l.value === search.level)?.label} ·{" "}
            {TYPES.find((t) => t.value === search.materialType)?.label}
          </span>
          <span className="ml-auto text-sm text-slate-500">
            {isLoading ? "Loading…" : `${materials.length} rows`}
          </span>
        </header>

        {materials.length === 0 ? (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-slate-400 text-sm">
            No rows match. The <code>exam_materials</code> Dagster asset may
            not have materialised this partition yet — run{" "}
            <code className="bg-slate-800 px-1 rounded">
              sec_examinations_leaving_certificate
            </code>{" "}
            from the marimo Mission Control.
          </div>
        ) : (
          <ul className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {materials.map((m, i) => (
              <li
                key={`${m.pdf_url}-${i}`}
                className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col gap-2"
              >
                <div className="flex items-baseline gap-2">
                  <h3 className="font-bold text-slate-100">
                    {m.title || (m.pdf_url as string).slice(0, 60) + "…"}
                  </h3>
                  <span className="ml-auto text-xs font-mono text-slate-500">
                    {String(m.scraper ?? "—")}
                  </span>
                </div>
                <div className="text-xs text-slate-400 flex gap-3">
                  <span>Level: {String(m.level)}</span>
                  <span>Type: {String(m.material_type)}</span>
                  <span>Status: {String(m.status ?? "—")}</span>
                </div>
                <a
                  href={String(m.pdf_url)}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-emerald-400 hover:text-emerald-300 break-all font-mono"
                >
                  {String(m.pdf_url).slice(0, 120)}
                </a>
              </li>
            ))}
          </ul>
        )}
      </section>

      <aside
        className={"shrink-0 transition-all " + (chatOpen ? "w-96" : "w-12")}
      >
        <div className="bg-slate-950 border border-slate-800 rounded-xl h-full flex flex-col">
          <div className="flex items-center justify-between p-3 border-b border-slate-800">
            {chatOpen && <span className="font-cinzel text-emerald-400">Awen Assistant</span>}
            <button
              onClick={() => setChatOpen(!chatOpen)}
              className="text-slate-400 hover:text-slate-200"
            >
              {chatOpen ? "→" : "←"}
            </button>
          </div>
          {chatOpen && (
            <div className="flex-1 p-3 text-xs text-slate-500 italic">
              Ask: <br />
              <code>"Compare Higher vs Ordinary 2024"</code>
              <br />
              <code>"Show marking scheme for Biology 2023"</code>
              <br />
              <code>"What concepts overlap with NCCA syllabus?"</code>
              <br />
              <br />
              Awen dispatches to <code>listExamMaterials</code>,{" "}
              <code>getMarkingSchemeSummary</code>, and{" "}
              <code>queryDuckLake</code> via TanStack Start server functions.
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
