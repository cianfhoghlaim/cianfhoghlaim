import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { client } from "../utils/orpc";

const SUBJECTS = ["english", "gaeilge", "mathematics", "biology", "chemistry", "physics", "geography", "history", "french", "german", "spanish", "irish"] as const;

export function MarkingSchemesPage() {
  const [subject, setSubject] = useState<string>("english");
  const { data, isLoading } = useQuery({
    queryKey: ["marking-summary", subject],
    queryFn: () => client.exams.summary.call({ subject }),
  });

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl text-amber-400">Marking Scheme Analyser</h1>
      <div className="flex flex-wrap gap-2">
        {SUBJECTS.map((s) => (
          <button key={s} onClick={() => setSubject(s)} className={`px-3 py-1 rounded-full text-sm border ${subject === s ? "bg-amber-700/30 border-amber-600 text-amber-200" : "bg-slate-900 border-slate-700 text-slate-300"}`}>{s}</button>
        ))}
      </div>
      {isLoading ? <p className="text-slate-500">Loading…</p> : data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6"><h2 className="font-bold text-amber-300 mb-2">Canonical rubric</h2><p className="text-slate-200">{(data as { rubric: string }).rubric}</p></div>
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6"><h2 className="font-bold text-amber-300 mb-2">Recent scheme years</h2>{(data as { recentYears: Array<{ year: number; schemes: number }> }).recentYears.map((y) => <div key={y.year} className="text-slate-300">{y.year}: {y.schemes}</div>)}</div>
        </div>
      ) : <p className="text-slate-400">No data.</p>}
    </div>
  );
}
