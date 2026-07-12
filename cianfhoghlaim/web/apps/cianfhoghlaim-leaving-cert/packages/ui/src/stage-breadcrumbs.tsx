"use client";

// <CiStageBreadcrumbs> — the 5-stage education pipeline breadcrumbs
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R17.
//
// The 5 stages are:
//   1. Aistear (early childhood, ages 0–6)     — v2 deferred
//   2. Primary (ages 4–12)                    — v1 active
//   3. Junior Cycle (ages 12–16)              — v1 active
//   4. Leaving Cycle (ages 16–19)             — v1 active
//   5. Tertiary (ages 18+)                   — v2 deferred
//
// Each stage is populated from the existing per-stage BAML extraction files
// in `baml/education/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml`.
// Stages with deferred CocoIndex embedding apps show a "Phase 2 coming soon"
// badge (per R17 in the openspec change).
//
// Token-driven: uses --ci-stage-* tokens from the central tokens.css (single
// source of truth, per R22). No hardcoded colours.

import * as React from "react";
import { cn } from "./utils";

export type EducationalStage =
  | "aistear"
  | "primary"
  | "junior_cycle"
  | "leaving_cycle"
  | "tertiary";

export interface StageDef {
  slug: EducationalStage;
  title_en: string;
  title_ga: string;
  ages: string;
  href_en: string;
  href_ga: string;
  icon: string;
  /** Which NCCA source extents feed this stage. */
  baml_sources: readonly string[];
  /** Which CocoIndex v1 Apps feed this stage. */
  cocoindex_apps: readonly string[];
  /** v1 ships the 3 primary-stages; Aistear + Tertiary are deferred to v2. */
  status: "v1_active" | "phase_2_deferred";
  /** Why v2 is deferred — surfaces to the user as a Phase 2 badge tooltip. */
  phase_2_reason?: string;
}

export const STAGES: readonly StageDef[] = [
  {
    slug: "aistear",
    title_en: "Aistear",
    title_ga: "Aistear",
    ages: "0–6",
    href_en: "/en/portal/aistear",
    href_ga: "/ga/portal/aistear",
    icon: "🌱",
    baml_sources: ["baml/education/stages/aistear.baml"],
    cocoindex_apps: ["(aistear_embedding.py — deferred to v2)"],
    status: "phase_2_deferred",
    phase_2_reason:
      "The Aistear CocoIndex v1 App does not exist yet. Pending a follow-up change (2026-07-XX-ireland-aistear-cocoindex-v1).",
  },
  {
    slug: "primary",
    title_en: "Primary",
    title_ga: "Bunscoil",
    ages: "4–12",
    href_en: "/en/portal/primary",
    href_ga: "/ga/portal/primary",
    icon: "📒",
    baml_sources: [
      "baml/education/stages/primary.baml",
      "baml/education/primary/primary_extraction.baml",
    ],
    cocoindex_apps: ["primary_embedding.py"],
    status: "v1_active",
  },
  {
    slug: "junior_cycle",
    title_en: "Junior Cycle",
    title_ga: "An Timthriall Shóisearaí",
    ages: "12–16",
    href_en: "/en/portal/junior-cycle",
    href_ga: "/ga/portal/junior-cycle",
    icon: "🎒",
    baml_sources: [
      "baml/education/stages/junior_cycle.baml",
      "baml/education/junior_cycle/junior_cycle_extraction.baml",
    ],
    cocoindex_apps: ["junior_cycle_embedding.py"],
    status: "v1_active",
  },
  {
    slug: "leaving_cycle",
    title_en: "Leaving Cycle",
    title_ga: "An Timthriall Sinsearach",
    ages: "16–19",
    href_en: "/en/portal/leaving-cycle",
    href_ga: "/ga/portal/leaving-cycle",
    icon: "🎓",
    baml_sources: [
      "baml/education/stages/senior_cycle.baml",
      "baml/education/lc_extraction/*.baml",
      "6 per-subject web schemas (baml/education/web/<subject>_web.baml)",
    ],
    cocoindex_apps: [
      "mathematics_embedding.py",
      "chemistry_embedding.py",
      "geography_embedding.py",
      "gaeilge_embedding.py",
      "english_embedding.py",
      "computer_science_embedding.py",
      "cross_subject_competency_embedding.py",
      "applied_mathematics_embedding.py",
    ],
    status: "v1_active",
  },
  {
    slug: "tertiary",
    title_en: "Tertiary",
    title_ga: "Ardleibhéal",
    ages: "18+",
    href_en: "/en/portal/tertiary",
    href_ga: "/ga/portal/tertiary",
    icon: "🏛️",
    baml_sources: ["baml/education/stages/tertiary.baml"],
    cocoindex_apps: ["(tertiary_embedding.py — deferred to v2)"],
    status: "phase_2_deferred",
    phase_2_reason:
      "The Tertiary CocoIndex v1 App does not exist yet. Pending a follow-up change.",
  },
] as const;

export interface CiStageBreadcrumbsProps {
  currentStage?: EducationalStage;
  language: "en" | "ga";
  onStageClick?: (stage: EducationalStage) => void;
  className?: string;
}

/**
 * CiStageBreadcrumbs renders the 5-stage education pipeline as a horizontal
 * breadcrumb row. Active stage is highlighted; deferred stages show a
 * "Phase 2 coming soon" badge.
 */
export function CiStageBreadcrumbs({
  currentStage,
  language,
  onStageClick,
  className,
}: CiStageBreadcrumbsProps) {
  return (
    <nav
      aria-label={language === "ga" ? "Céimeanna an oideachais" : "Education pipeline stages"}
      className={cn(
        "grid grid-cols-5 gap-2 rounded-2xl border border-slate-700 bg-slate-800/40 p-3",
        className,
      )}
    >
      {STAGES.map((stage, idx) => {
        const isActive = stage.slug === currentStage;
        const isDeferred = stage.status === "phase_2_deferred";
        const title = language === "ga" ? stage.title_ga : stage.title_en;
        const href = language === "ga" ? stage.href_ga : stage.href_en;

        return (
          <React.Fragment key={stage.slug}>
            <a
              href={href}
              onClick={(e) => {
                if (onStageClick) {
                  e.preventDefault();
                  onStageClick(stage.slug);
                }
              }}
              aria-current={isActive ? "page" : undefined}
              title={
                isDeferred && stage.phase_2_reason
                  ? stage.phase_2_reason
                  : undefined
              }
              data-stage={stage.slug}
              data-status={stage.status}
              className={cn(
                "group relative flex flex-col gap-1 rounded-xl border px-3 py-2 transition-all",
                isActive
                  ? "border-(--ci-brand-primary) bg-(--ci-brand-primary)/15 ring-1 ring-(--ci-brand-primary)"
                  : isDeferred
                    ? "cursor-not-allowed border-slate-700 bg-slate-900/40 opacity-60 hover:opacity-80"
                    : "border-slate-700 bg-slate-900 hover:border-(--ci-brand-secondary) hover:bg-slate-800",
              )}
              style={
                isActive
                  ? {
                      borderColor: "var(--ci-brand-primary)",
                      background: "rgba(5,150,105,0.15)",
                    }
                  : undefined
              }
            >
              <div className="flex items-center justify-between">
                <span className="text-xl" aria-hidden="true">{stage.icon}</span>
                <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wide">
                  {stage.ages}
                </span>
              </div>
              <div className={cn(
                "text-sm font-semibold",
                isActive ? "text-emerald-300" : isDeferred ? "text-slate-500" : "text-slate-100",
              )}>
                {title}
              </div>
              <div className="text-[10px] text-slate-400 truncate">
                {isDeferred
                  ? language === "ga"
                    ? "Ní bronnadh fós"
                    : "Phase 2 coming soon"
                  : language === "ga"
                    ? "Gníomhach"
                    : "v1 active"}
              </div>
              {isDeferred && (
                <span
                  className="absolute -top-2 -right-2 rounded-full bg-amber-500 px-1.5 py-0.5 text-[8px] font-bold uppercase text-amber-950"
                  aria-label="Phase 2 deferred"
                >
                  v2
                </span>
              )}
            </a>
            {idx < STAGES.length - 1 && (
              <span aria-hidden="true" className="self-center text-slate-600">→</span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
