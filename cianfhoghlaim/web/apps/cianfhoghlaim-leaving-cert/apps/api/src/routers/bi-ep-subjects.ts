// apps/api/src/routers/bi-ep-subjects.ts
// The BIEP v1 6-priority-subjects Hono router.
// Returns the live BIEP table contents as JSON for SPA hydration +
// serves a manifest endpoint for the 6 per-subject web surfaces.
//
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/.

import { Hono } from "hono";

export const biEpSubjects = new Hono();

// ── BIEP subjects data (mirrored from apps/web/src/lib/bi-ep.ts) ──────────
type BIEPSubjectSlug =
  | "mathematics"
  | "chemistry"
  | "geography"
  | "gaeilge"
  | "english"
  | "computer_science";

interface BIEPSubjectData {
  slug: BIEPSubjectSlug;
  name: string;
  name_ga: string;
  code: string;
  level: "hl" | "ol" | "fl";
  color: string;
  eiraic_tier: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13;
  primary_agent: string;
  en_route: string;
  ga_route: string;
  notebook_module: string;
  table_ref: {
    ducklake_database: string;
    ducklake_schema: string;
    tables: ReadonlyArray<string>;
  };
  baml_ref: {
    baml_path: string;
    functions: ReadonlyArray<string>;
  };
  dlt_ref: {
    dlt_path: string;
    resources: ReadonlyArray<string>;
  };
  partner_subjects: ReadonlyArray<BIEPSubjectSlug>;
  key_competencies: ReadonlyArray<{ slug: string; weight: number }>;
  notebook_embed: {
    embed_url: string;
    height: number;
    full_height: number;
  };
  visualizations: ReadonlyArray<{
    id: string;
    title: string;
    title_ga: string;
    description: string;
    marimo_cell: string;
    baml_function?: string;
  }>;
}

const BIEP_SUBJECTS: ReadonlyArray<BIEPSubjectData> = [
  {
    slug: "mathematics",
    name: "Mathematics",
    name_ga: "Mata",
    code: "LC-MA",
    level: "hl",
    color: "var(--ci-subject-mathematics)",
    eiraic_tier: 3,
    primary_agent: "mathematics",
    en_route: "/en/subjects/mathematics",
    ga_route: "/ga/subjects/mata",
    notebook_module: "cianfhoghlaim/notebooks/03_leaving_cert/23_mathematics_biep_v1.py",
    table_ref: {
      ducklake_database: "oideachais",
      ducklake_schema: "leaving_cert",
      tables: ["mathematics_syllabus", "mathematics_papers", "mathematics_marking_schemes", "mathematics_topics"],
    },
    baml_ref: {
      baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
      functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
    },
    dlt_ref: {
      dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
      resources: ["mathematics_topics", "mathematics_syllabus", "mathematics_papers", "mathematics_marking_schemes"],
    },
    partner_subjects: ["computer_science", "gaeilge", "chemistry"],
    key_competencies: [
      { slug: "communicating", weight: 72 },
      { slug: "information-processing", weight: 94 },
      { slug: "critical-creative-thinking", weight: 84 },
      { slug: "personal-effectiveness", weight: 58 },
      { slug: "working-with-others", weight: 46 },
    ],
    notebook_embed: {
      embed_url: "/_notebooks/mathematics.html",
      height: 400,
      full_height: 800,
    },
    visualizations: [
      { id: "topic_frequency", title: "Topic Frequency (per year) — Mathematics", title_ga: "Mincicíocht Topaicí (in aghaidh an bhliain) — Mata", description: "Line chart of topic counts grouped by year.", marimo_cell: "mathematics_topic_frequency_cell", baml_function: "ExtractCurriculumSyllabus" },
      { id: "exam_paper_difficulty", title: "Exam Paper Difficulty Trend — Mathematics", title_ga: "Treocht Deacrachta an Scrúda — Mata", description: "Bar chart of average marks per year.", marimo_cell: "mathematics_exam_paper_difficulty_cell", baml_function: "ExtractExamPaperLayout" },
      { id: "marking_scheme_complexity", title: "Marking Scheme Complexity — Mathematics", title_ga: "Castacht na Scéime Marcála — Mata", description: "Heatmap of mark allocation per question.", marimo_cell: "mathematics_marking_scheme_complexity_cell", baml_function: "ExtractMarkingSchemeGuideline" },
      { id: "cross_linguistic_mapping", title: "Cross-Linguistic Mapping (GA ↔ EN) — Mathematics", title_ga: "Léarscáil Thras-theangach (GA ↔ EN) — Mata", description: "Irish ↔ English topic mappings.", marimo_cell: "mathematics_cross_linguistic_mapping_cell", baml_function: "ExtractCrossLinguisticConcept" },
      { id: "asset_generator", title: "Asset Generator (3D + 2D) — Mathematics", title_ga: "Gineadóir Sócmhainní (3D + 2D) — Mata", description: "Per-topic asset gallery (FIBO + TRELLIS.2).", marimo_cell: "mathematics_asset_generator_cell" },
    ],
  },
  {
    slug: "chemistry",
    name: "Chemistry",
    name_ga: "Ceimic",
    code: "LC-CH",
    level: "hl",
    color: "var(--ci-subject-chemistry)",
    eiraic_tier: 1,
    primary_agent: "chemistry",
    en_route: "/en/subjects/chemistry",
    ga_route: "/ga/subjects/ceimic",
    notebook_module: "cianfhoghlaim/notebooks/03_leaving_cert/18_chemistry_biep_v1.py",
    table_ref: {
      ducklake_database: "oideachais",
      ducklake_schema: "leaving_cert",
      tables: ["chemistry_syllabus", "chemistry_papers", "chemistry_marking_schemes", "chemistry_topics"],
    },
    baml_ref: {
      baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
      functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
    },
    dlt_ref: {
      dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
      resources: ["chemistry_topics", "chemistry_syllabus", "chemistry_papers", "chemistry_marking_schemes"],
    },
    partner_subjects: ["mathematics", "geography", "computer_science"],
    key_competencies: [
      { slug: "communicating", weight: 63 },
      { slug: "information-processing", weight: 83 },
      { slug: "critical-creative-thinking", weight: 75 },
      { slug: "personal-effectiveness", weight: 89 },
      { slug: "working-with-others", weight: 62 },
    ],
    notebook_embed: {
      embed_url: "/_notebooks/chemistry.html",
      height: 400,
      full_height: 800,
    },
    visualizations: [
      { id: "topic_frequency", title: "Topic Frequency (per year) — Chemistry", title_ga: "Mincicíocht Topaicí (in aghaidh an bhliain) — Ceimic", description: "Line chart of topic counts grouped by year.", marimo_cell: "chemistry_topic_frequency_cell", baml_function: "ExtractCurriculumSyllabus" },
      { id: "exam_paper_difficulty", title: "Exam Paper Difficulty Trend — Chemistry", title_ga: "Treocht Deacrachta an Scrúda — Ceimic", description: "Bar chart of average marks per year.", marimo_cell: "chemistry_exam_paper_difficulty_cell", baml_function: "ExtractExamPaperLayout" },
      { id: "marking_scheme_complexity", title: "Marking Scheme Complexity — Chemistry", title_ga: "Castacht na Scéime Marcála — Ceimic", description: "Heatmap of mark allocation per question.", marimo_cell: "chemistry_marking_scheme_complexity_cell", baml_function: "ExtractMarkingSchemeGuideline" },
      { id: "cross_linguistic_mapping", title: "Cross-Linguistic Mapping (GA ↔ EN) — Chemistry", title_ga: "Léarscáil Thras-theangach (GA ↔ EN) — Ceimic", description: "Irish ↔ English topic mappings.", marimo_cell: "chemistry_cross_linguistic_mapping_cell", baml_function: "ExtractCrossLinguisticConcept" },
      { id: "asset_generator", title: "Asset Generator (3D + 2D) — Chemistry", title_ga: "Gineadóir Sócmhainní (3D + 2D) — Ceimic", description: "Per-topic asset gallery (FIBO + TRELLIS.2).", marimo_cell: "chemistry_asset_generator_cell" },
    ],
  },
  {
    slug: "geography",
    name: "Geography",
    name_ga: "Tíreolaíocht",
    code: "LC-GG",
    level: "hl",
    color: "var(--ci-subject-geography)",
    eiraic_tier: 2,
    primary_agent: "geography",
    en_route: "/en/subjects/geography",
    ga_route: "/ga/subjects/tireolaiocht",
    notebook_module: "cianfhoghlaim/notebooks/03_leaving_cert/22_geography_biep_v1.py",
    table_ref: {
      ducklake_database: "oideachais",
      ducklake_schema: "leaving_cert",
      tables: ["geography_syllabus", "geography_papers", "geography_marking_schemes", "geography_topics"],
    },
    baml_ref: {
      baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
      functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
    },
    dlt_ref: {
      dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
      resources: ["geography_topics", "geography_syllabus", "geography_papers", "geography_marking_schemes"],
    },
    partner_subjects: ["english", "gaeilge", "mathematics"],
    key_competencies: [
      { slug: "communicating", weight: 86 },
      { slug: "information-processing", weight: 72 },
      { slug: "critical-creative-thinking", weight: 68 },
      { slug: "personal-effectiveness", weight: 66 },
      { slug: "working-with-others", weight: 78 },
    ],
    notebook_embed: {
      embed_url: "/_notebooks/geography.html",
      height: 400,
      full_height: 800,
    },
    visualizations: [
      { id: "topic_frequency", title: "Topic Frequency (per year) — Geography", title_ga: "Mincicíocht Topaicí (in aghaidh an bhliain) — Tíreolaíocht", description: "Line chart of topic counts grouped by year.", marimo_cell: "geography_topic_frequency_cell", baml_function: "ExtractCurriculumSyllabus" },
      { id: "exam_paper_difficulty", title: "Exam Paper Difficulty Trend — Geography", title_ga: "Treocht Deacrachta an Scrúda — Tíreolaíocht", description: "Bar chart of average marks per year.", marimo_cell: "geography_exam_paper_difficulty_cell", baml_function: "ExtractExamPaperLayout" },
      { id: "marking_scheme_complexity", title: "Marking Scheme Complexity — Geography", title_ga: "Castacht na Scéime Marcála — Tíreolaíocht", description: "Heatmap of mark allocation per question.", marimo_cell: "geography_marking_scheme_complexity_cell", baml_function: "ExtractMarkingSchemeGuideline" },
      { id: "cross_linguistic_mapping", title: "Cross-Linguistic Mapping (GA ↔ EN) — Geography", title_ga: "Léarscáil Thras-theangach (GA ↔ EN) — Tíreolaíocht", description: "Irish ↔ English topic mappings.", marimo_cell: "geography_cross_linguistic_mapping_cell", baml_function: "ExtractCrossLinguisticConcept" },
      { id: "asset_generator", title: "Asset Generator (3D + 2D) — Geography", title_ga: "Gineadóir Sócmhainní (3D + 2D) — Tíreolaíocht", description: "Per-topic asset gallery (FIBO + TRELLIS.2).", marimo_cell: "geography_asset_generator_cell" },
    ],
  },
  {
    slug: "gaeilge",
    name: "Gaeilge",
    name_ga: "Gaeilge",
    code: "LC-GA",
    level: "hl",
    color: "var(--ci-subject-gaeilge)",
    eiraic_tier: 8,
    primary_agent: "gaeilge",
    en_route: "/en/subjects/gaeilge",
    ga_route: "/ga/subjects/gaeilge",
    notebook_module: "cianfhoghlaim/notebooks/03_leaving_cert/21_gaeilge_biep_v1.py",
    table_ref: {
      ducklake_database: "oideachais",
      ducklake_schema: "leaving_cert",
      tables: ["gaeilge_syllabus", "gaeilge_papers", "gaeilge_marking_schemes", "gaeilge_topics"],
    },
    baml_ref: {
      baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
      functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
    },
    dlt_ref: {
      dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
      resources: ["gaeilge_topics", "gaeilge_syllabus", "gaeilge_papers", "gaeilge_marking_schemes"],
    },
    partner_subjects: ["english", "geography", "mathematics"],
    key_competencies: [
      { slug: "communicating", weight: 100 },
      { slug: "information-processing", weight: 48 },
      { slug: "critical-creative-thinking", weight: 78 },
      { slug: "personal-effectiveness", weight: 76 },
      { slug: "working-with-others", weight: 72 },
    ],
    notebook_embed: {
      embed_url: "/_notebooks/gaeilge.html",
      height: 400,
      full_height: 800,
    },
    visualizations: [
      { id: "topic_frequency", title: "Topic Frequency (per year) — Gaeilge", title_ga: "Mincicíocht Topaicí (in aghaidh an bhliain) — Gaeilge", description: "Line chart of topic counts grouped by year.", marimo_cell: "gaeilge_topic_frequency_cell", baml_function: "ExtractCurriculumSyllabus" },
      { id: "exam_paper_difficulty", title: "Exam Paper Difficulty Trend — Gaeilge", title_ga: "Treocht Deacrachta an Scrúda — Gaeilge", description: "Bar chart of average marks per year.", marimo_cell: "gaeilge_exam_paper_difficulty_cell", baml_function: "ExtractExamPaperLayout" },
      { id: "marking_scheme_complexity", title: "Marking Scheme Complexity — Gaeilge", title_ga: "Castacht na Scéime Marcála — Gaeilge", description: "Heatmap of mark allocation per question.", marimo_cell: "gaeilge_marking_scheme_complexity_cell", baml_function: "ExtractMarkingSchemeGuideline" },
      { id: "cross_linguistic_mapping", title: "Cross-Linguistic Mapping (GA ↔ EN) — Gaeilge", title_ga: "Léarscáil Thras-theangach (GA ↔ EN) — Gaeilge", description: "Irish ↔ English topic mappings.", marimo_cell: "gaeilge_cross_linguistic_mapping_cell", baml_function: "ExtractCrossLinguisticConcept" },
      { id: "asset_generator", title: "Asset Generator (3D + 2D) — Gaeilge", title_ga: "Gineadóir Sócmhainní (3D + 2D) — Gaeilge", description: "Per-topic asset gallery (FIBO + TRELLIS.2).", marimo_cell: "gaeilge_asset_generator_cell" },
    ],
  },
  {
    slug: "english",
    name: "English",
    name_ga: "Béarla",
    code: "LC-EN",
    level: "hl",
    color: "var(--ci-subject-english)",
    eiraic_tier: 7,
    primary_agent: "english",
    en_route: "/en/subjects/english",
    ga_route: "/ga/subjects/bearla",
    notebook_module: "cianfhoghlaim/notebooks/03_leaving_cert/20_english_biep_v1.py",
    table_ref: {
      ducklake_database: "oideachais",
      ducklake_schema: "leaving_cert",
      tables: ["english_syllabus", "english_papers", "english_marking_schemes", "english_topics"],
    },
    baml_ref: {
      baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
      functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
    },
    dlt_ref: {
      dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
      resources: ["english_topics", "english_syllabus", "english_papers", "english_marking_schemes"],
    },
    partner_subjects: ["gaeilge", "geography", "english"],
    key_competencies: [
      { slug: "communicating", weight: 97 },
      { slug: "information-processing", weight: 58 },
      { slug: "critical-creative-thinking", weight: 95 },
      { slug: "personal-effectiveness", weight: 72 },
      { slug: "working-with-others", weight: 88 },
    ],
    notebook_embed: {
      embed_url: "/_notebooks/english.html",
      height: 400,
      full_height: 800,
    },
    visualizations: [
      { id: "topic_frequency", title: "Topic Frequency (per year) — English", title_ga: "Mincicíocht Topaicí (in aghaidh an bhliain) — Béarla", description: "Line chart of topic counts grouped by year.", marimo_cell: "english_topic_frequency_cell", baml_function: "ExtractCurriculumSyllabus" },
      { id: "exam_paper_difficulty", title: "Exam Paper Difficulty Trend — English", title_ga: "Treocht Deacrachta an Scrúda — Béarla", description: "Bar chart of average marks per year.", marimo_cell: "english_exam_paper_difficulty_cell", baml_function: "ExtractExamPaperLayout" },
      { id: "marking_scheme_complexity", title: "Marking Scheme Complexity — English", title_ga: "Castacht na Scéime Marcála — Béarla", description: "Heatmap of mark allocation per question.", marimo_cell: "english_marking_scheme_complexity_cell", baml_function: "ExtractMarkingSchemeGuideline" },
      { id: "cross_linguistic_mapping", title: "Cross-Linguistic Mapping (GA ↔ EN) — English", title_ga: "Léarscáil Thras-theangach (GA ↔ EN) — Béarla", description: "Irish ↔ English topic mappings.", marimo_cell: "english_cross_linguistic_mapping_cell", baml_function: "ExtractCrossLinguisticConcept" },
      { id: "asset_generator", title: "Asset Generator (3D + 2D) — English", title_ga: "Gineadóir Sócmhainní (3D + 2D) — Béarla", description: "Per-topic asset gallery (FIBO + TRELLIS.2).", marimo_cell: "english_asset_generator_cell" },
    ],
  },
  {
    slug: "computer_science",
    name: "Computer Science",
    name_ga: "Ríomheolaíocht",
    code: "LC-CS",
    level: "hl",
    color: "var(--ci-subject-computer_science)",
    eiraic_tier: 5,
    primary_agent: "computer_science",
    en_route: "/en/subjects/computer_science",
    ga_route: "/ga/subjects/riomheolaiocht",
    notebook_module: "cianfhoghlaim/notebooks/03_leaving_cert/19_computer_science_biep_v1.py",
    table_ref: {
      ducklake_database: "oideachais",
      ducklake_schema: "leaving_cert",
      tables: ["cs_syllabus", "cs_papers", "cs_marking_schemes", "cs_topics"],
    },
    baml_ref: {
      baml_path: "cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml",
      functions: ["ExtractCurriculumSyllabus", "ExtractExamPaperLayout", "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept", "ExtractSyllabusDiagram"],
    },
    dlt_ref: {
      dlt_path: "cianfhoghlaim/dlt/british_isles/ireland/ncca_root_pdfs.py",
      resources: ["cs_topics", "cs_syllabus", "cs_papers", "cs_marking_schemes"],
    },
    partner_subjects: ["mathematics", "english", "gaeilge"],
    key_competencies: [
      { slug: "communicating", weight: 53 },
      { slug: "information-processing", weight: 100 },
      { slug: "critical-creative-thinking", weight: 86 },
      { slug: "personal-effectiveness", weight: 82 },
      { slug: "working-with-others", weight: 64 },
    ],
    notebook_embed: {
      embed_url: "/_notebooks/computer_science.html",
      height: 400,
      full_height: 800,
    },
    visualizations: [
      { id: "topic_frequency", title: "Topic Frequency (per year) — Computer Science", title_ga: "Mincicíocht Topaicí (in aghaidh an bhliain) — Ríomheolaíocht", description: "Line chart of topic counts grouped by year.", marimo_cell: "computer_science_topic_frequency_cell", baml_function: "ExtractCurriculumSyllabus" },
      { id: "exam_paper_difficulty", title: "Exam Paper Difficulty Trend — Computer Science", title_ga: "Treocht Deacrachta an Scrúda — Ríomheolaíocht", description: "Bar chart of average marks per year.", marimo_cell: "computer_science_exam_paper_difficulty_cell", baml_function: "ExtractExamPaperLayout" },
      { id: "marking_scheme_complexity", title: "Marking Scheme Complexity — Computer Science", title_ga: "Castacht na Scéime Marcála — Ríomheolaíocht", description: "Heatmap of mark allocation per question.", marimo_cell: "computer_science_marking_scheme_complexity_cell", baml_function: "ExtractMarkingSchemeGuideline" },
      { id: "cross_linguistic_mapping", title: "Cross-Linguistic Mapping (GA ↔ EN) — Computer Science", title_ga: "Léarscáil Thras-theangach (GA ↔ EN) — Ríomheolaíocht", description: "Irish ↔ English topic mappings.", marimo_cell: "computer_science_cross_linguistic_mapping_cell", baml_function: "ExtractCrossLinguisticConcept" },
      { id: "asset_generator", title: "Asset Generator (3D + 2D) — Computer Science", title_ga: "Gineadóir Sócmhainní (3D + 2D) — Ríomheolaíocht", description: "Per-topic asset gallery (FIBO + TRELLIS.2).", marimo_cell: "computer_science_asset_generator_cell" },
    ],
  },
];

const BIEP_SUBJECT_BY_SLUG: Readonly<Record<BIEPSubjectSlug, BIEPSubjectData>> =
  BIEP_SUBJECTS.reduce(
    (acc, s) => ({ ...acc, [s.slug]: s }),
    {} as Record<BIEPSubjectSlug, BIEPSubjectData>,
  );

const BIEP_SUBJECT_SLUGS: ReadonlyArray<BIEPSubjectSlug> = BIEP_SUBJECTS.map((s) => s.slug);

// ── Routes ────────────────────────────────────────────────────────────────

biEpSubjects.get("/", (c) => {
  return c.json({
    status: "ok",
    bi_ep_version: "v1",
    source_change: "openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/",
    count: BIEP_SUBJECT_SLUGS.length,
    subjects: BIEP_SUBJECTS,
  });
});

biEpSubjects.get("/manifest", (c) => {
  return c.json({
    status: "ok",
    bi_ep_version: "v1",
    source_change: "openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/",
    subjects: BIEP_SUBJECT_SLUGS.map((slug) => {
      const s = BIEP_SUBJECT_BY_SLUG[slug];
      return {
        slug: s.slug,
        name: s.name,
        name_ga: s.name_ga,
        en_route: s.en_route,
        ga_route: s.ga_route,
        notebook: s.notebook_module,
        table: `${s.table_ref.ducklake_database}.${s.table_ref.ducklake_schema}`,
        primary_agent: s.primary_agent,
      };
    }),
  });
});

biEpSubjects.get("/:slug", (c) => {
  const slug = c.req.param("slug");
  const subject = BIEP_SUBJECT_BY_SLUG[slug as BIEPSubjectSlug];
  if (!subject) {
    return c.json(
      {
        error: "BIEP subject not found",
        available_subjects: BIEP_SUBJECT_SLUGS,
      },
      404,
    );
  }
  return c.json({ status: "ok", subject });
});

biEpSubjects.get("/:slug/syllabus", (c) => {
  const slug = c.req.param("slug");
  const subject = BIEP_SUBJECT_BY_SLUG[slug as BIEPSubjectSlug];
  if (!subject) return c.json({ error: "BIEP subject not found" }, 404);
  return c.json({
    status: "ok",
    subject_slug: subject.slug,
    subject_code: subject.code,
    level: subject.level,
    language: c.req.query("language") ?? "en",
    source: `${subject.table_ref.ducklake_database}.${subject.table_ref.ducklake_schema}.${subject.table_ref.tables[0]}`,
    baml_function: subject.baml_ref.functions[0],
    rows: [], // populated by the Dagster `lc5_<subject>_extract` asset
    note:
      "Empty until the BIEP v1 Dagster assets materialise. Run `mise run dagster:oideachais` then materialize `lc5_<subject>_extract`.",
  });
});

biEpSubjects.get("/:slug/papers", (c) => {
  const slug = c.req.param("slug");
  const subject = BIEP_SUBJECT_BY_SLUG[slug as BIEPSubjectSlug];
  if (!subject) return c.json({ error: "BIEP subject not found" }, 404);
  return c.json({
    status: "ok",
    subject_slug: subject.slug,
    level: subject.level,
    year_from: Number(c.req.query("year_from") ?? 2017),
    year_to: Number(c.req.query("year_to") ?? 2025),
    language: c.req.query("language") ?? "en",
    source: `${subject.table_ref.ducklake_database}.${subject.table_ref.ducklake_schema}.${subject.table_ref.tables[1]}`,
    baml_function: subject.baml_ref.functions[1],
    rows: [],
  });
});

biEpSubjects.get("/:slug/marking-schemes", (c) => {
  const slug = c.req.param("slug");
  const subject = BIEP_SUBJECT_BY_SLUG[slug as BIEPSubjectSlug];
  if (!subject) return c.json({ error: "BIEP subject not found" }, 404);
  return c.json({
    status: "ok",
    subject_slug: subject.slug,
    level: subject.level,
    language: c.req.query("language") ?? "en",
    source: `${subject.table_ref.ducklake_database}.${subject.table_ref.ducklake_schema}.${subject.table_ref.tables[2]}`,
    baml_function: subject.baml_ref.functions[2],
    rows: [],
  });
});

biEpSubjects.get("/:slug/topics", (c) => {
  const slug = c.req.param("slug");
  const subject = BIEP_SUBJECT_BY_SLUG[slug as BIEPSubjectSlug];
  if (!subject) return c.json({ error: "BIEP subject not found" }, 404);
  return c.json({
    status: "ok",
    subject_slug: subject.slug,
    language: c.req.query("language") ?? "en",
    source: `${subject.table_ref.ducklake_database}.${subject.table_ref.ducklake_schema}.${subject.table_ref.tables[3]}`,
    baml_function: subject.baml_ref.functions[3],
    rows: [],
  });
});

export default biEpSubjects;
