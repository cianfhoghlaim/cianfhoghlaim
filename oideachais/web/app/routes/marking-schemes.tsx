import { useQuery } from "@tanstack/react-query";
import { useNavigate, useSearch } from "@tanstack/react-router";
import { getMarkingSchemeSummary } from "../server/lakehouse";

const SUBJECTS = [
  "english", "gaeilge", "mathematics", "biology", "chemistry", "physics",
  "geography", "history", "french", "german", "spanish", "irish",
] as const;

export function MarkingSchemes() {
  const search = useSearch({ from: "/marking-schemes" });
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ["marking-scheme-summary", search.subject],
    queryFn: () => getMarkingSchemeSummary({ data: { subject: search.subject } }),
  });

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <header>
        <h1 className="font-cinzel text-3xl text-amber-400">Marking Scheme Analyser</h1>
        <p className="text-slate-400">
          Per-subject rubric patterns and most recent scheme year.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        {SUBJECTS.map((s) => (
          <button
            key={s}
            onClick={() => navigate({ search: { subject: s }, to: "/marking-schemes" })}
            className={
              "px-3 py-1 rounded-full text-sm border " +
              (search.subject === s
                ? "bg-amber-700/30 border-amber-600 text-amber-200"
                : "bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800")
            }
          >
            {s}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-slate-500 text-sm">Loading…</div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
            <h2 className="font-bold text-amber-300 mb-2">Canonical rubric</h2>
            <p className="text-slate-200">{data.rubric}</p>
          </div>
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
            <h2 className="font-bold text-amber-300 mb-2">Recent scheme years</h2>
            <ul className="text-sm">
              {data.recentYears.map((y: { year: number; schemes: number }) => (
                <li
                  key={y.year}
                  className="flex justify-between border-b border-slate-800 py-1"
                >
                  <span className="text-slate-300">{y.year}</span>
                  <span className="font-mono text-amber-400">{y.schemes}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-slate-400 text-sm">
          No data. Run the <code>sec_examinations_leaving_certificate</code>{" "}
          Dagster job to ingest marking schemes first.
        </div>
      )}
    </div>
  );
}
