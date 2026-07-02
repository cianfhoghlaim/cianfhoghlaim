"use client";

// <Header> — Cianfhoghlaim OS top bar
// Renders:
//   1. The brand + Brown Ajah badge (russet brown knotwork)
//   2. The Brown Ajah tagline: "Aes Sedai — servants of all" (operator-visible lore only)
//   3. The Tuatha'an wagon icon (mobile client switch)
//   4. The BetterAuth user (sign-in / Pocket ID)
//   5. The TranslationToggle (EN ↔ GA — the Esker Riada divider)
//   6. The Streak flame (the Cauldron of the Dagda — never empties)
//
// Per docs/CIANFHLOGHLAIM_LORE.md and docs/BROWN_AJAH_THEMING.md:
//   - The Cian → Lugh mapping is documented in CIANFHLOGHLAIM_LORE.md only
//   - The Brown Ajah tagline is the only user-facing reference to the mythology

import * as React from "react";
import { CiButton } from "@cianfhoghlaim/ui";
import { CiBrownAjahBadge } from "@cianfhoghlaim/ui/lore/brown-ajah-badge";
import { CiStreakFlame } from "@cianfhoghlaim/ui/streak-flame";
import { CiTuathanWagon } from "@cianfhoghlaim/ui/lore/tuathan-wagon";
import { TranslationToggle } from "./TranslationToggle";

export interface HeaderProps {
  user?: { name: string; email: string; avatar?: string } | null;
  streakDays?: number;
  language: "en" | "ga";
  onLanguageChange?: (lang: "en" | "ga") => void;
  onSignIn?: () => void;
  onSwitchToMobile?: () => void;
}

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
        <CiBrownAjahBadge size={32} />
        <div className="flex flex-col">
          <h1 className="font-cinzel font-bold text-lg tracking-wider text-emerald-500">
            CIANFHOGHLAIM
          </h1>
          <span className="text-xs text-slate-500 italic">
            Aes Sedai — servants of all
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {streakDays > 0 && <CiStreakFlame days={streakDays} />}
        <button
          onClick={onSwitchToMobile}
          className="text-slate-400 hover:text-amber-400 transition-colors"
          title="Switch to mobile client (Tuatha'an wagon)"
        >
          <CiTuathanWagon size={20} />
        </button>
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
            Sign In
          </CiButton>
        )}
      </div>
    </header>
  );
}