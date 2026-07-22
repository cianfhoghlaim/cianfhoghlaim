"use client";

// <Header> — Cianfhoghlaim OS top bar
// Professional + minimal theming (per the 2026-07-09 WoT-theming cleanup).
// Renders:
//   1. The brand + Cianfhoghlaim brand badge (a clean letter-mark — no mythology)
//   2. The tagline: "Cianfhoghlaim — Coláiste na Déisigh" (bilingual EN+GA)
//   3. The BetterAuth user (sign-in / Pocket ID)
//   4. The TranslationToggle (EN ↔ GA — the Esker Riada divider)
//   5. The Streak flame (a daily-practice indicator)
//
// The Cian → Lugh mapping is operator-only and NEVER appears on the
// public surface. The mythology / historical-sources layer is deferred
// to BIEP-v2 (see openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/).

import * as React from "react";
import { Link } from "@tanstack/react-router";
import { CiButton } from "@cianfhoghlaim/ui";
import { CiStreakFlame } from "@cianfhoghlaim/ui/streak-flame";
import { TranslationToggle } from "./TranslationToggle";

export interface HeaderProps {
  user?: { name: string; email: string; avatar?: string } | null;
  streakDays?: number;
  language: "en" | "ga";
  onLanguageChange?: (lang: "en" | "ga") => void;
  onSignIn?: () => void;
  onSwitchToMobile?: () => void;
}

const HEADER_TITLE = {
  en: "Cianfhoghlaim — Coláiste na Déisigh",
  ga: "Cianfhoghlaim — Coláiste na Déisigh",
} as const;

export function Header({
  user,
  streakDays = 0,
  language,
  onLanguageChange,
  onSignIn,
  onSwitchToMobile,
}: HeaderProps) {
  return (
    <header className="h-14 bg-slate-950 border-b border-slate-800 flex items-center px-4 justify-between shrink-0">
      <div className="flex items-center gap-3">
        {/* <CiBrandBadge> — the "C" letter mark (clean professional brand) */}
        <div
          aria-label="Cianfhoghlaim"
          className="w-8 h-8 rounded-md bg-emerald-600 flex items-center justify-center font-bold text-white text-sm"
        >
          C
        </div>
        <div className="flex flex-col">
          <h1 className="font-cinzel font-bold text-lg tracking-wider text-emerald-500">
            CIANFHOGHLAIM
          </h1>
          <span className="text-xs text-slate-500 italic">
            {HEADER_TITLE[language]}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {streakDays > 0 && <CiStreakFlame days={streakDays} />}
        <Link
          to={"/en/about" as any}
          className="text-slate-300 hover:text-emerald-400 text-sm font-medium transition-colors"
          title="About — the public about page"
        >
          {language === "ga" ? "EN About" : "About"}
        </Link>
        <Link
          to={"/ga/about" as any}
          className="text-slate-300 hover:text-emerald-400 text-sm font-medium transition-colors"
          title="Faoi Cianfhoghlaim — an leathanach poiblí faoi"
        >
          {language === "ga" ? "Faoi" : "GA About"}
        </Link>
        <TranslationToggle
          language={language}
          onChange={(lang) => onLanguageChange?.(lang)}
        />
        {user ? (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-emerald-700 flex items-center justify-center text-white font-medium">
              {user.name.charAt(0)}
            </div>
          </div>
        ) : (
          <CiButton variant="primary" size="sm" onClick={onSignIn}>
            {language === "ga" ? "Sínigh Isteach" : "Sign In"}
          </CiButton>
        )}
      </div>
    </header>
  );
}