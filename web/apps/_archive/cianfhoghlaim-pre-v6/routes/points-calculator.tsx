// /en/points-calculator — CAO points calculator (H1-H8, O1-O8, H6+25 bonus)
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createFileRoute("/points-calculator")({
  component: PointsCalcComponent,
});

// CAO points table (per Leaving Certificate standard)
const POINTS: Record<string, number> = {
  H1: 100, H2: 88, H3: 77, H4: 66, H5: 56, H6: 46, H7: 37, H8: 0,
  O1: 56, O2: 46, O3: 37, O4: 28, O5: 20, O6: 12, O7: 0, O8: 0,
};

const GRADES = Object.keys(POINTS);

function PointsCalcComponent() {
  const [grades, setGrades] = useState<string[]>(Array(6).fill(""));

  const set = (i: number, v: string) => {
    const next = [...grades];
    next[i] = v;
    setGrades(next);
  };

  const total = grades.reduce(
    (acc, g) => acc + (POINTS[g] ?? 0),
    0,
  );
  const mathBonus = grades[0] === "H1" || grades[0] === "H2" || grades[0] === "H3" || grades[0] === "H4" || grades[0] === "H5" || grades[0] === "H6" ? 25 : 0;

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        CAO Points Calculator
      </h1>
      <p className="text-slate-400">
        Six best subjects. Higher Level Maths at H6+ adds +25 bonus points. The same subject
        is counted only once even if taken at both levels (Higher grade wins).
      </p>
      <div className="grid grid-cols-3 gap-4">
        {grades.map((g, i) => (
          <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-slate-500 text-xs mb-2">Subject {i + 1}</div>
            <select
              value={g}
              onChange={(e) => set(i, e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-100"
            >
              <option value="">—</option>
              {GRADES.map((k) => (
                <option key={k} value={k}>
                  {k} ({POINTS[k]})
                </option>
              ))}
            </select>
            <div className="text-right text-emerald-400 font-mono mt-1">
              {POINTS[g] ?? 0}
            </div>
          </div>
        ))}
      </div>
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 flex items-center justify-between">
        <div>
          <div className="text-slate-500 text-xs">Total</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            {total}
            {mathBonus > 0 && (
              <span className="text-emerald-500"> + {mathBonus} bonus</span>
            )}
          </div>
        </div>
        {mathBonus > 0 && (
          <div className="text-sm text-slate-400 text-right">
            Higher Level Maths at {grades[0] || "—"} qualifies for the +25 bonus.
          </div>
        )}
      </div>
    </div>
  );
}
