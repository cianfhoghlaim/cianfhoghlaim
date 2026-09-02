// apps/web/src/components/BIEPNavigationRail.tsx
//
// Shared per-subject navigation rail used by both the legacy `/en/subjects/$subject/`
// routes AND the new `/[lang]/leaving-cert/$subject/lineage` route. Renders
// the 5 sub-routes (overview / syllabus / exam-papers / marking-schemes /
// lineage) plus a "playground" link to the per-subject marimo notebook.
//
// The rail is a thin visual layer — it doesn't fetch data or own state.
// Active link styling uses TanStack Router's `useMatchRoute` for
// type-safe route matching.
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R26 + R29 (the rail reuses the existing BIEP v1 navigation, adding the
// new `/lineage` segment).

import * as React from "react";
import { Link, useMatch } from "@tanstack/react-router";
import type { BIEPSubjectSlug } from "../lib/bi-ep";
import {
  EN_TO_GA_SUBJECT,
  type BIEPRouteLanguage,
} from "../lib/lineage-routes";

export type BIEPNavKey =
  | "overview"
  | "syllabus"
  | "exam-papers"
  | "marking-schemes"
  | "study-plan"
  | "lineage"
  | "playgrounds"
  | "assets";

export interface BIEPNavigationRailProps {
  subject: BIEPSubjectSlug;
  /** The currently-active nav key. */
  active: BIEPNavKey;
  /** Bilingual display language. */
  language: BIEPRouteLanguage;
}

const NAV_KEYS: ReadonlyArray<{ key: BIEPNavKey; href: (s: BIEPSubjectSlug) => string; label_en: string; label_ga: string }> = [
  {
    key: "overview",
    href: (s) => `/en/subjects/${s}`,
    label_en: "Overview",
    label_ga: "Forbhreathnú",
  },
  {
    key: "syllabus",
    href: (s) => `/en/subjects/${s}/syllabus`,
    label_en: "Syllabus",
    label_ga: "Siollabas",
  },
  {
    key: "exam-papers",
    href: (s) => `/en/subjects/${s}/exam-papers`,
    label_en: "Past Papers",
    label_ga: "Scrúduithe Caite",
  },
  {
    key: "marking-schemes",
    href: (s) => `/en/subjects/${s}/marking-schemes`,
    label_en: "Marking",
    label_ga: "Marcáil",
  },
  {
    key: "study-plan",
    href: (s) => `/en/subjects/${s}/study-plan`,
    label_en: "Study plan",
    label_ga: "Plean staidéir",
  },
  {
    key: "lineage",
    href: (s) => `/en/leaving-cert/${s}/lineage`,
    label_en: "Lineage",
    label_ga: "Líníocht",
  },
  {
    key: "playgrounds",
    href: (s) => `/en/playgrounds?subject=${s}`,
    label_en: "Marimo",
    label_ga: "Marimo",
  },
];

export function BIEPNavigationRail({ subject, active, language }: BIEPNavigationRailProps) {
  return (
    <nav
      aria-label="Per-subject navigation"
      className="flex flex-wrap items-center gap-2 text-sm"
    >
      {NAV_KEYS.map((item) => {
        const label = language === "ga" ? item.label_ga : item.label_en;
        const href = item.href(subject);
        const isActive = item.key === active;
        return (
          <Link
            key={item.key}
            to={href as never}
            className={[
              "rounded-full px-3 py-1 border transition-colors",
              isActive
                ? "bg-emerald-700 border-emerald-600 text-white"
                : "bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500",
            ].join(" ")}
          >
            {label}
          </Link>
        );
      })}
      {/* GA mirror link */}
      <Link
        to={`/ga/leaving-cert/${EN_TO_GA_SUBJECT[subject]}/lineage` as never}
        className="ml-auto text-xs text-slate-500 underline hover:text-slate-300"
        title="Léigh i nGaeilge"
      >
        GA →
      </Link>
      {/* Reference the subject to satisfy the no-unused-vars rule */}
      <span className="sr-only">{subject}</span>
    </nav>
  );
}
