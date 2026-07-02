"use client";

// <TranslationToggle> — EN ↔ GA toggle (the Esker Riada divider)
// Per docs/BROWN_AJAH_THEMING.md, the toggle is the visual reference for
// the Esker Riada (Dublin Bay to Galway Bay) — flipping from EN to GA
// crosses the esker from Connacht to Munster.

import * as React from "react";
import { CiButton } from "@cianfhoghlaim/ui";

export interface TranslationToggleProps {
  language: "en" | "ga";
  onChange: (language: "en" | "ga") => void;
}

export function TranslationToggle({ language, onChange }: TranslationToggleProps) {
  return (
    <div className="flex items-center gap-1 bg-slate-800 px-2 py-1 rounded-full border border-slate-700">
      <button
        onClick={() => onChange("en")}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
          language === "en"
            ? "bg-emerald-600 text-white"
            : "text-slate-400 hover:text-slate-100"
        }`}
        aria-label="Switch to English"
        title="Esker Riada — Leath Cuinn (Conn's Half)"
      >
        EN
      </button>
      <button
        onClick={() => onChange("ga")}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
          language === "ga"
            ? "bg-emerald-600 text-white"
            : "text-slate-400 hover:text-slate-100"
        }`}
        aria-label="Switch to Irish (Gaeilge)"
        title="Esker Riada — Leath Moga (Mogha's Half)"
      >
        GA
      </button>
    </div>
  );
}