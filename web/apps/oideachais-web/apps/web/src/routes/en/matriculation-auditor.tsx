// /en/matriculation-auditor — Audits an applicant's LC grades against NUI/HEI
// matriculation rules. Calls the apps/api oRPC tertiary.auditMatriculation procedure.
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { client } from "../utils/orpc";

export const Route = createFileRoute("/en/matriculation-auditor")({
  component: AuditComponent,
});

const HEI_OPTIONS = [
  "NUI/UCD", "NUI/UCG", "NUI/UCC", "NUI/UL", "NUI/Maynooth",
  "Trinity", "DCU", "ATU", "TUS", "SETU", "MTU", "RCSI", "MIC",
];

const SUBJECT_OPTIONS = [
  "english", "irish", "mathematics", "french", "german", "spanish",
  "biology", "chemistry", "physics", "history", "geography",
  "music", "art", "economics", "business", "accounting",
];

const GRADES = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8"];

function AuditComponent() {
  const [institution, setInstitution] = useState("NUI/UCD");
  const [pathway, setPathway] = useState<"leaving_certificate" | "qqi_fet" | "mature_student" | "dare" | "hear">("leaving_certificate");
  const [grades, setGrades] = useState<Record<string, string>>({
    english: "H3", irish: "H3", mathematics: "H2",
    french: "H4", biology: "H4",
  });

  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setResult(null);
    try {
      const r = await client.tertiary.auditMatriculation.call({
        institution,
        pathway,
        applicant_grades: grades,
      });
      setResult(r);
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        Matriculation Auditor
      </h1>
      <p className="text-slate-400">
        Audits your LC grades against the standard matriculation rules for the chosen
        institution and pathway. Backend calls baml.AuditMatriculation (uses Claude Sonnet 4).
      </p>
      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <div className="text-slate-500 text-xs mb-1">Institution</div>
          <select
            value={institution}
            onChange={(e) => setInstitution(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-100"
          >
            {HEI_OPTIONS.map((h) => (
              <option key={h}>{h}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <div className="text-slate-500 text-xs mb-1">Pathway</div>
          <select
            value={pathway}
            onChange={(e) => setPathway(e.target.value as typeof pathway)}
            className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-100"
          >
            <option value="leaving_certificate">Leaving Certificate</option>
            <option value="qqi_fet">QQI FET</option>
            <option value="mature_student">Mature Student</option>
            <option value="dare">DARE</option>
            <option value="hear">HEAR</option>
          </select>
        </label>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {SUBJECT_OPTIONS.map((subj) => (
          <label key={subj} className="block">
            <div className="text-slate-500 text-xs mb-1 capitalize">{subj}</div>
            <select
              value={grades[subj] ?? ""}
              onChange={(e) =>
                setGrades({ ...grades, [subj]: e.target.value })
              }
              className="w-full bg-slate-800 border border-slate-700 rounded p-1 text-sm text-slate-100"
            >
              <option value="">—</option>
              {GRADES.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <button
        onClick={run}
        disabled={busy}
        className="btn-tactile w-fit"
      >
        {busy ? "Auditing…" : "Audit Matriculation"}
      </button>
      {result && (
        <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-xs text-slate-300 overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
