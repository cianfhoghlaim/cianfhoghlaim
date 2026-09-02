// apps/web/src/lib/lineage-routes.ts
//
// Shared utilities for the per-subject `/[lang]/leaving-cert/[subject]/lineage`
// route family. Handles slug resolution (EN ↔ GA) + bilingual label sets.
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R26 (Per-subject `/[lang]/leaving-cert/[subject]/lineage` route × 6 subjects).

import {
  getBIEPSubject,
  BIEP_SUBJECT_BY_SLUG,
  type BIEPSubjectSlug,
} from "./bi-ep";

export type BIEPGaSlug =
  | "mata"
  | "ceimic"
  | "tireolaiocht"
  | "gaeilge"
  | "bearla"
  | "riomheolaiocht";

export type BIEPRouteLanguage = "en" | "ga";

export interface BIEPResolvedSubject {
  /** The canonical EN BIEP v1 subject slug. Always present for valid inputs. */
  en_slug: BIEPSubjectSlug;
  /** The GA route slug (one of the 6 above). Always present for valid inputs. */
  ga_slug: BIEPGaSlug;
  /** Resolved canonical subject metadata (BIEPSubjectDef). `null` for invalid inputs. */
  subject: ReturnType<typeof getBIEPSubject>;
  /** The parsed language (defaults to "en" for EN paths). */
  language: BIEPRouteLanguage;
}

// =============================================================================
// Slug resolution (EN ↔ GA)
// =============================================================================

/** The reverse GA → EN mapping (Irish slug → English BIEP slug). */
export const GA_TO_EN_SUBJECT: Readonly<Record<BIEPGaSlug, BIEPSubjectSlug>> = {
  mata: "mathematics",
  ceimic: "chemistry",
  tireolaiocht: "geography",
  gaeilge: "gaeilge",
  bearla: "english",
  riomheolaiocht: "computer_science",
};

export const EN_TO_GA_SUBJECT: Readonly<Record<BIEPSubjectSlug, BIEPGaSlug>> = {
  mathematics: "mata",
  chemistry: "ceimic",
  geography: "tireolaiocht",
  gaeilge: "gaeilge",
  english: "bearla",
  computer_science: "riomheolaiocht",
};

export function isBIEPGaSlug(value: string): value is BIEPGaSlug {
  return value in GA_TO_EN_SUBJECT;
}

export function isBIEPEnSlug(value: string): value is BIEPSubjectSlug {
  return value in EN_TO_GA_SUBJECT;
}

/**
 * Resolve a `$subject` URL param to the canonical `BIEPResolvedSubject`.
 * `language` is "ga" when the GA slug is provided, "en" otherwise.
 *
 * Returns `null` if the slug doesn't match any of the 6 BIEP v1 subjects.
 */
export function resolveLineageSubject(
  rawSlug: string,
  explicitLanguage?: BIEPRouteLanguage,
): BIEPResolvedSubject | null {
  if (isBIEPGaSlug(rawSlug)) {
    const en_slug = GA_TO_EN_SUBJECT[rawSlug];
    const subject = BIEP_SUBJECT_BY_SLUG[en_slug];
    return {
      en_slug,
      ga_slug: rawSlug,
      subject,
      language: explicitLanguage ?? "ga",
    };
  }
  if (isBIEPEnSlug(rawSlug)) {
    const en_slug = rawSlug;
    const ga_slug = EN_TO_GA_SUBJECT[en_slug];
    const subject = BIEP_SUBJECT_BY_SLUG[en_slug];
    return {
      en_slug,
      ga_slug,
      subject,
      language: explicitLanguage ?? "en",
    };
  }
  return null;
}

/**
 * Build the mirrored route URL for a subject + language.
 * Used by the "EN ↔ GA" toggle in the lineage viewer.
 */
export function lineageRouteFor(
  en_slug: BIEPSubjectSlug,
  language: BIEPRouteLanguage,
): string {
  const slug = language === "ga" ? EN_TO_GA_SUBJECT[en_slug] : en_slug;
  return `/${language}/leaving-cert/${slug}/lineage`;
}

// =============================================================================
// Bilingual label sets (R26)
// =============================================================================

export interface LineageLabels {
  /** Page heading (h1). */
  page_heading: string;
  /** Short blurb shown under the heading. */
  blurb: string;
  /** Sub-heading for the StepPreview pane (left pane). */
  step_preview_heading: string;
  /** Sub-heading for the LineageDag pane (right pane). */
  dag_heading: string;
  /** Sub-heading for the PdfViewer pane (bottom). */
  pdf_viewer_heading: string;
  /** Pill text for the marimo-cell reference (R29). */
  marimo_pill: string;
  /** Pill text for the MotherDuck reference (R29). */
  motherduck_pill: string;
  /** "Click any field to highlight" hint. */
  click_hint: string;
  /** "View source page" link text (R31). */
  view_source: string;
  /** "Not found" error. */
  not_found: string;
}

export const LINEAGE_LABELS: Readonly<Record<BIEPRouteLanguage, LineageLabels>> = {
  en: {
    page_heading: "Document Lineage",
    blurb:
      "Click any field or DAG node to trace its source PDF, BAML extraction, marimo cell, and MotherDuck pipeline.",
    step_preview_heading: "Step-by-step preview",
    dag_heading: "Lineage DAG",
    pdf_viewer_heading: "Source PDF",
    marimo_pill: "marimo",
    motherduck_pill: "MotherDuck",
    click_hint: "Click any field to highlight upstream + downstream.",
    view_source: "View source page",
    not_found: "Subject not found.",
  },
  ga: {
    page_heading: "Líníocht Doiciméad",
    blurb:
      "Cliceáil réimse nó nód DAG ar bith chun a fhoinse PDF, eastóscadh BAML, cill marimo, agus píblíne MotherDuck a rianú.",
    step_preview_heading: "Réamhamharc céim ar chéim",
    dag_heading: "DAG Líníochta",
    pdf_viewer_heading: "PDF Foinse",
    marimo_pill: "marimo",
    motherduck_pill: "MotherDuck",
    click_hint: "Cliceáil réimse ar bith chun súgradh suas agus síos aird a thabhairt.",
    view_source: "Féach ar an leathanach foinse",
    not_found: "Ní bhfuarthas an t-ábhar.",
  },
};

export function getLineageLabels(language: BIEPRouteLanguage): LineageLabels {
  return LINEAGE_LABELS[language];
}