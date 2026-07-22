// apps/web/src/lib/bi-ep.ts
// The 6 BIEP (British-Isles Education Pipeline) v1 priority subjects.
//
// Per openspec/specs/british-isles-education-pipeline/spec.md (R1+R6)
// and openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1.
//
// The 6 priority subjects are: Mathematics, Chemistry, Geography,
// Gaeilge, English, Computer Science. These are the subjects whose
// end-to-end NCCA + SEC + gov.ie + BAML + CocoIndex + marimo + Dagster
// pipelines are fully wired (per the BIEP v1 spec).

export type BIEPSubjectSlug =
  | "mathematics"
  | "chemistry"
  | "geography"
  | "gaeilge"
  | "english"
  | "computer_science";

export type BIEPLevel = "hl" | "ol" | "fl";
export type BIEPLanguage = "en" | "ga";

export interface BIEPVisualization {
  id: string;
  title: string;
  title_ga: string;
  description: string;
  /**
   * @deprecated Use `marimo_cell_id` instead. Retained for backward
   * compatibility with the existing per-subject pages.
   */
  marimo_cell: string;
  /** The marimo notebook cell that renders this visualization (e.g. `"topic_frequency_cell"`). Used by R29 of the lineage viewer. */
  marimo_cell_id: string;
  /** The BAML function the visualization is sourced from (if any). */
  baml_function?: string;
  /**
   * The MotherDuck Dive + Flight that own the underlying data. Renders as
   * a clickable pill in the lineage viewer (R29).
   */
  motherduck_ref: BIEPMotherDuckRef;
}

export interface BIEPMotherDuckRef {
  /** MotherDuck Dive name (e.g. `"lc_syllabus_topics"`). */
  dive_name: string;
  /** MotherDuck Flight name (e.g. `"lc_pdf_sync_flight"`). */
  flight_name: string;
  /** Canonical MotherDuck Dive URL — opened in a new tab from the lineage viewer. */
  dive_url: string;
}

export interface BIEPNotebookPath {
  /** Path to the per-subject BIEP v1 marimo notebook. */
  python_module: string;
}

export interface BIEPTableRef {
  /** The canonical MotherDuck / DuckLake table backing the data. */
  ducklake_database: string;
  ducklake_schema: string;
  tables: ReadonlyArray<string>;
}

export interface BIEPBAMLRef {
  /** Path to the canonical BAML extraction schema. */
  baml_path: string;
  functions: ReadonlyArray<string>;
}

export interface BIEPDLTSource {
  /** The DLT source module. */
  dlt_path: string;
  resources: ReadonlyArray<string>;
}

export interface BIEPNotebookEmbed {
  /** The marimo notebook embed URL (R2-signed or local). */
  embed_url: string;
  height: number;
  full_height: number;
}

export interface BIEPKCGPatterns {
  mo_sql_engine: string;
  ibis_first: boolean;
  pep_723_inline_deps: boolean;
  reads_pdf_paths_from_env: string;
}

export interface BIEPVisualizations {
  topic_frequency: BIEPVisualization;
  exam_paper_difficulty: BIEPVisualization;
  marking_scheme_complexity: BIEPVisualization;
  cross_linguistic_mapping: BIEPVisualization;
  asset_generator: BIEPVisualization;
}

export interface BIEPPerLanguageContent {
  language: BIEPLanguage;
  title: string;
  title_native: string;
  heading: string;
  blurb: string;
  syllabus_topics_link: string;
}

export interface BIEPBilingualContent {
  en: BIEPPerLanguageContent;
  ga: BIEPPerLanguageContent;
}

export interface BIEPClientConfig {
  notebook: BIEPNotebookPath;
  table_ref: BIEPTableRef;
  baml: BIEPBAMLRef;
  dlt: BIEPDLTSource;
  notebook_embed: BIEPNotebookEmbed;
  kcg_patterns: BIEPKCGPatterns;
  visualizations: BIEPVisualizations;
  bilingual: BIEPBilingualContent;
}

export interface BIEPSubjectDef {
  slug: BIEPSubjectSlug;
  name: string;
  name_ga: string;
  color: string;
  level: BIEPLevel;
  code: string;
  description: string;
  description_ga: string;
  primary_agent: string;
  eiraic_tier: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13;
  partner_subjects: ReadonlyArray<BIEPSubjectSlug>;
  key_competencies: ReadonlyArray<{ slug: string; weight: number }>;
  client: BIEPClientConfig;
}

const BASE_BIEP_TABLES: Record<BIEPSubjectSlug, BIEPTableRef> = {
  mathematics: {
    ducklake_database: "oideachais",
    ducklake_schema: "leaving_cert",
    tables: ["mathematics_syllabus", "mathematics_papers", "mathematics_marking_schemes", "mathematics_topics"],
  },
  chemistry: {
    ducklake_database: "oideachais",
    ducklake_schema: "leaving_cert",
    tables: ["chemistry_syllabus", "chemistry_papers", "chemistry_marking_schemes", "chemistry_topics"],
  },
  geography: {
    ducklake_database: "oideachais",
    ducklake_schema: "leaving_cert",
    tables: ["geography_syllabus", "geography_papers", "geography_marking_schemes", "geography_topics"],
  },
  gaeilge: {
    ducklake_database: "oideachais",
    ducklake_schema: "leaving_cert",
    tables: ["gaeilge_syllabus", "gaeilge_papers", "gaeilge_marking_schemes", "gaeilge_topics"],
  },
  english: {
    ducklake_database: "oideachais",
    ducklake_schema: "leaving_cert",
    tables: ["english_syllabus", "english_papers", "english_marking_schemes", "english_topics"],
  },
  computer_science: {
    ducklake_database: "oideachais",
    ducklake_schema: "leaving_cert",
    tables: ["cs_syllabus", "cs_papers", "cs_marking_schemes", "cs_topics"],
  },
};

const BASE_BIEP_BAML: Record<BIEPSubjectSlug, BIEPBAMLRef> = {
  mathematics: {
    baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
    functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
  },
  chemistry: {
    baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
    functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
  },
  geography: {
    baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
    functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
  },
  gaeilge: {
    baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
    functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
  },
  english: {
    baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
    functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
  },
  computer_science: {
    baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
    functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
  },
};

const BASE_BIEP_DLT: Record<BIEPSubjectSlug, BIEPDLTSource> = {
  mathematics: {
    dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
    resources: ["mathematics_topics", "mathematics_syllabus", "mathematics_papers", "mathematics_marking_schemes"],
  },
  chemistry: {
    dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
    resources: ["chemistry_topics", "chemistry_syllabus", "chemistry_papers", "chemistry_marking_schemes"],
  },
  geography: {
    dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
    resources: ["geography_topics", "geography_syllabus", "geography_papers", "geography_marking_schemes"],
  },
  gaeilge: {
    dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
    resources: ["gaeilge_topics", "gaeilge_syllabus", "gaeilge_papers", "gaeilge_marking_schemes"],
  },
  english: {
    dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
    resources: ["english_topics", "english_syllabus", "english_papers", "english_marking_schemes"],
  },
  computer_science: {
    dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
    resources: ["cs_topics", "cs_syllabus", "cs_papers", "cs_marking_schemes"],
  },
};

const BASE_BIEP_NOTEBOOK: Record<BIEPSubjectSlug, BIEPNotebookPath> = {
  mathematics: { python_module: "cianfhoghlaim/notebooks/03_leaving_cert/23_mathematics_biep_v1.py" },
  chemistry: { python_module: "cianfhoghlaim/notebooks/03_leaving_cert/18_chemistry_biep_v1.py" },
  geography: { python_module: "cianfhoghlaim/notebooks/03_leaving_cert/22_geography_biep_v1.py" },
  gaeilge: { python_module: "cianfhoghlaim/notebooks/03_leaving_cert/21_gaeilge_biep_v1.py" },
  english: { python_module: "cianfhoghlaim/notebooks/03_leaving_cert/20_english_biep_v1.py" },
  computer_science: { python_module: "cianfhoghlaim/notebooks/03_leaving_cert/19_computer_science_biep_v1.py" },
};

function makeBilingual(opts: {
  title: string;
  title_ga: string;
  heading: string;
  heading_ga: string;
  blurb_en: string;
  blurb_ga: string;
}): BIEPBilingualContent {
  return {
    en: {
      language: "en",
      title: opts.title,
      title_native: opts.title,
      heading: opts.heading,
      blurb: opts.blurb_en,
      syllabus_topics_link: "/en/leaving-cert",
    },
    ga: {
      language: "ga",
      title: opts.title_ga,
      title_native: opts.title_ga,
      heading: opts.heading_ga,
      blurb: opts.blurb_ga,
      syllabus_topics_link: "/ga/leaving-cert",
    },
  };
}

function makeVisualizations(slug: BIEPSubjectSlug): BIEPVisualizations {
  const subject = slug.charAt(0).toUpperCase() + slug.slice(1).replace("_", " ");
  return {
    topic_frequency: {
      id: "topic_frequency",
      title: `Topic Frequency (per year) — ${subject}`,
      title_ga: `Mincicíocht Topaicí (in aghaidh an bhliain) — ${subject}`,
      description:
        "Line chart of topic counts grouped by year (BAML `ExtractCurriculumSyllabus` × NCCA syllabus PDFs).",
      marimo_cell: `${slug}_topic_frequency_cell`,
      marimo_cell_id: `${slug}_topic_frequency_cell`,
      baml_function: "ExtractCurriculumSyllabus",
      motherduck_ref: {
        dive_name: "lc_syllabus_topics",
        flight_name: "lc_pdf_sync_flight",
        dive_url: `https://app.motherduck.com/dive/${slug}_syllabus_topics`,
      },
    },
    exam_paper_difficulty: {
      id: "exam_paper_difficulty",
      title: `Exam Paper Difficulty Trend — ${subject}`,
      title_ga: `Treocht Deacrachta an Scrúda — ${subject}`,
      description:
        "Bar chart of average marks per year (Bloom's taxonomy + BAML `ExtractExamPaperLayout`).",
      marimo_cell: `${slug}_exam_paper_difficulty_cell`,
      marimo_cell_id: `${slug}_exam_paper_difficulty_cell`,
      baml_function: "ExtractExamPaperLayout",
      motherduck_ref: {
        dive_name: "lc_exam_paper_difficulty",
        flight_name: "lc_pdf_sync_flight",
        dive_url: `https://app.motherduck.com/dive/${slug}_exam_paper_difficulty`,
      },
    },
    marking_scheme_complexity: {
      id: "marking_scheme_complexity",
      title: `Marking Scheme Complexity — ${subject}`,
      title_ga: `Castacht na Scéime Marcála — ${subject}`,
      description:
        "Heatmap of mark allocation per question (BAML `ExtractMarkingSchemeGuideline`).",
      marimo_cell: `${slug}_marking_scheme_complexity_cell`,
      marimo_cell_id: `${slug}_marking_scheme_complexity_cell`,
      baml_function: "ExtractMarkingSchemeGuideline",
      motherduck_ref: {
        dive_name: "lc_marking_complexity",
        flight_name: "lc_pdf_sync_flight",
        dive_url: `https://app.motherduck.com/dive/${slug}_marking_complexity`,
      },
    },
    cross_linguistic_mapping: {
      id: "cross_linguistic_mapping",
      title: `Cross-Linguistic Mapping (GA ↔ EN) — ${subject}`,
      title_ga: `Léarscáil Thras-theangach (GA ↔ EN) — ${subject}`,
      description:
        "Irish ↔ English topic mappings (BAML `ExtractCrossLinguisticConcept`).",
      marimo_cell: `${slug}_cross_linguistic_mapping_cell`,
      marimo_cell_id: `${slug}_cross_linguistic_mapping_cell`,
      baml_function: "ExtractCrossLinguisticConcept",
      motherduck_ref: {
        dive_name: "lc_syllabus_topics",
        flight_name: "lc_pdf_sync_flight",
        dive_url: `https://app.motherduck.com/dive/${slug}_syllabus_topics`,
      },
    },
    asset_generator: {
      id: "asset_generator",
      title: `Asset Generator (3D + 2D) — ${subject}`,
      title_ga: `Gineadóir Sócmhainní (3D + 2D) — ${subject}`,
      description:
        "Per-topic asset gallery (FIBO 2D sprite atlases + TRELLIS.2 / SAM-3D-Objects 3D meshes, queued via the Dagster `asset_generation_<subject>` asset).",
      marimo_cell: `${slug}_asset_generator_cell`,
      marimo_cell_id: `${slug}_asset_generator_cell`,
      motherduck_ref: {
        dive_name: "lc_syllabus_topics",
        flight_name: "lc_pdf_sync_flight",
        dive_url: `https://app.motherduck.com/dive/${slug}_syllabus_topics`,
      },
    },
  };
}

function buildBIEPClient(slug: BIEPSubjectSlug): BIEPClientConfig {
  const table_ref = BASE_BIEP_TABLES[slug];
  const baml = BASE_BIEP_BAML[slug];
  const dlt = BASE_BIEP_DLT[slug];
  const notebook = BASE_BIEP_NOTEBOOK[slug];
  return {
    notebook,
    table_ref,
    baml,
    dlt,
    notebook_embed: {
      embed_url: `/_notebooks/${slug}.html`,
      height: 400,
      full_height: 800,
    },
    kcg_patterns: {
      mo_sql_engine: "md:oideachais",
      ibis_first: true,
      pep_723_inline_deps: true,
      reads_pdf_paths_from_env: "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
    },
    visualizations: makeVisualizations(slug),
    bilingual: makeBilingual({
      title: "Mathematics",
      title_ga: "Mata",
      heading: "Mathematics — BIEP v1",
      heading_ga: "Mata — BIEP v1",
      blurb_en:
        "Pure mathematics at Leaving Certificate level: algebra, functions, calculus, probability, statistics, geometry.",
      blurb_ga:
        "Matamaitic chomhtháite ag leibhéal na hArdteistiméireachta: ailgéabar, feidhmeanna, calcalas, dóchúlacht, staidreamh, geoiméadracht.",
    }),
  };
}

export const BIEP_SUBJECTS: ReadonlyArray<BIEPSubjectDef> = ([
  {
    slug: "mathematics",
    name: "Mathematics",
    name_ga: "Mata",
    color: "var(--ci-subject-mathematics)",
    level: "hl",
    code: "LC-MA",
    description:
      "Pure mathematics at Leaving Certificate level: algebra, functions, calculus, probability, statistics, geometry.",
    description_ga:
      "Matamaitic chomhtháite ag leibhéal na hArdteistiméireachta: ailgéabar, feidhmeanna, calcalas, dóchúlacht, staidreamh, geoiméadracht.",
    primary_agent: "mathematics",
    eiraic_tier: 3,
    partner_subjects: ["computer_science", "gaeilge", "chemistry"],
    key_competencies: [
      { slug: "communicating", weight: 72 },
      { slug: "information-processing", weight: 94 },
      { slug: "critical-creative-thinking", weight: 84 },
      { slug: "personal-effectiveness", weight: 58 },
      { slug: "working-with-others", weight: 46 },
    ],
    client: buildBIEPClient("mathematics"),
  },
  {
    slug: "chemistry",
    name: "Chemistry",
    name_ga: "Ceimic",
    color: "var(--ci-subject-chemistry)",
    level: "hl",
    code: "LC-CH",
    description:
      "Atomic structure, bonding, stoichiometry, organic chemistry, equilibrium, rates.",
    description_ga:
      "Struchtúr adamhach, nascadh, steoichiomeatra, ceimic orgánach, cothromaíocht, rátaí.",
    primary_agent: "chemistry",
    eiraic_tier: 1,
    partner_subjects: ["mathematics", "geography", "computer_science"],
    key_competencies: [
      { slug: "communicating", weight: 63 },
      { slug: "information-processing", weight: 83 },
      { slug: "critical-creative-thinking", weight: 75 },
      { slug: "personal-effectiveness", weight: 89 },
      { slug: "working-with-others", weight: 62 },
    ],
    client: buildBIEPClient("chemistry"),
  },
  {
    slug: "geography",
    name: "Geography",
    name_ga: "Tíreolaíocht",
    color: "var(--ci-subject-geography)",
    level: "hl",
    code: "LC-GG",
    description:
      "Physical + regional geography: climate, geomorphology, economic activities, global development.",
    description_ga:
      "Tíreolaíocht fhisiciúil + réigiúnach: aeráid, geoimorfolaíocht, gníomhaíochtaí eacnamaíocha, forbairt dhomhanda.",
    primary_agent: "geography",
    eiraic_tier: 2,
    partner_subjects: ["english", "gaeilge", "mathematics"],
    key_competencies: [
      { slug: "communicating", weight: 86 },
      { slug: "information-processing", weight: 72 },
      { slug: "critical-creative-thinking", weight: 68 },
      { slug: "personal-effectiveness", weight: 66 },
      { slug: "working-with-others", weight: 78 },
    ],
    client: buildBIEPClient("geography"),
  },
  {
    slug: "gaeilge",
    name: "Gaeilge",
    name_ga: "Gaeilge",
    color: "var(--ci-subject-gaeilge)",
    level: "hl",
    code: "LC-GA",
    description:
      "Léamh, scríbhneoireacht, cluastuiscint, litríocht, gramadach.",
    description_ga:
      "Léamh, scríbhneoireacht, cluastuiscint, litríocht, gramadach — an teanga féin is sprioc foghlama.",
    primary_agent: "gaeilge",
    eiraic_tier: 8,
    partner_subjects: ["english", "geography", "mathematics"],
    key_competencies: [
      { slug: "communicating", weight: 100 },
      { slug: "information-processing", weight: 48 },
      { slug: "critical-creative-thinking", weight: 78 },
      { slug: "personal-effectiveness", weight: 76 },
      { slug: "working-with-others", weight: 72 },
    ],
    client: buildBIEPClient("gaeilge"),
  },
  {
    slug: "english",
    name: "English",
    name_ga: "Béarla",
    color: "var(--ci-subject-english)",
    level: "hl",
    code: "LC-EN",
    description:
      "Comprehension, composition, comparative + single text, poetry.",
    description_ga:
      "Léamhthuiscint, comhréir, comparáid + aon téacs, filíocht.",
    primary_agent: "english",
    eiraic_tier: 7,
    partner_subjects: ["gaeilge", "geography", "english"],
    key_competencies: [
      { slug: "communicating", weight: 97 },
      { slug: "information-processing", weight: 58 },
      { slug: "critical-creative-thinking", weight: 95 },
      { slug: "personal-effectiveness", weight: 72 },
      { slug: "working-with-others", weight: 88 },
    ],
    client: buildBIEPClient("english"),
  },
  {
    slug: "computer_science",
    name: "Computer Science",
    name_ga: "Ríomheolaíocht",
    color: "var(--ci-subject-computer_science)",
    level: "hl",
    code: "LC-CS",
    description:
      "Algorithms, data structures, computer systems, networks.",
    description_ga:
      "Algartaim, struchtúir shonraí, córais ríomhaireachta, líonraí.",
    primary_agent: "computer_science",
    eiraic_tier: 5,
    partner_subjects: ["mathematics", "english", "gaeilge"],
    key_competencies: [
      { slug: "communicating", weight: 53 },
      { slug: "information-processing", weight: 100 },
      { slug: "critical-creative-thinking", weight: 86 },
      { slug: "personal-effectiveness", weight: 82 },
      { slug: "working-with-others", weight: 64 },
    ],
    client: buildBIEPClient("computer_science"),
  },
] satisfies ReadonlyArray<BIEPSubjectDef>);

export const BIEP_SUBJECT_BY_SLUG: Readonly<Record<BIEPSubjectSlug, BIEPSubjectDef>> =
  BIEP_SUBJECTS.reduce(
    (acc, subject) => ({ ...acc, [subject.slug]: subject }),
    {} as Record<BIEPSubjectSlug, BIEPSubjectDef>,
  );

export const BIEP_SUBJECT_SLUGS: ReadonlyArray<BIEPSubjectSlug> = BIEP_SUBJECTS.map(
  (s) => s.slug,
);

export function isBIEPSubject(slug: string): slug is BIEPSubjectSlug {
  return BIEP_SUBJECT_SLUGS.includes(slug as BIEPSubjectSlug);
}

export function getBIEPSubject(slug: string): BIEPSubjectDef | undefined {
  if (isBIEPSubject(slug)) return BIEP_SUBJECT_BY_SLUG[slug];
  return undefined;
}

/**
 * Returns the Irish-language slug for an English BIEP subject.
 * Used by the `/ga/subjects/{slug}.tsx` mirror routes.
 */
export function getGASlug(enSlug: BIEPSubjectSlug): string {
  const map: Record<BIEPSubjectSlug, string> = {
    mathematics: "mata",
    chemistry: "ceimic",
    geography: "tireolaiocht",
    gaeilge: "gaeilge",
    english: "bearla",
    computer_science: "riomheolaiocht",
  };
  return map[enSlug];
}

/** The reverse lookup (Irish slug → English slug). */
export function getEnglishSlugFromGA(gaSlug: string): BIEPSubjectSlug | undefined {
  for (const enSlug of BIEP_SUBJECT_SLUGS) {
    if (getGASlug(enSlug) === gaSlug) return enSlug;
  }
  return undefined;
}
