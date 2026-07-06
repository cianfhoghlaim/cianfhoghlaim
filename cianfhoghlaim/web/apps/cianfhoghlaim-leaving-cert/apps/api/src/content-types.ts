// apps/api/src/content-types.ts (mirror of apps/web/src/lib/content-types.ts)

export type ContentType = "Subject" | "PastPaper" | "MarkingScheme" | "PracticeItem" | "Foundation" | "Notebook";

export interface ContentTypeDef {
  slug: ContentType;
  name: string;
  description: string;
  count: number;
  icon: string;
  color: string;
}

export const CONTENT_TYPES: Record<ContentType, ContentTypeDef> = {
  Subject: { slug: "Subject", name: "Subjects", description: "The 8 NCCA Leaving Certificate subjects + the 5×8 mastery matrix + the 5-tab layout (Syllabus / Papers / Marking / Practice / Notebook).", count: 8, icon: "📚", color: "emerald" },
  PastPaper: { slug: "PastPaper", name: "Past Papers", description: "LC past exam papers (2017-2025), served from CF R2 via the dlt ncca_root_pdfs.py extraction.", count: 0, icon: "📄", color: "blue" },
  MarkingScheme: { slug: "MarkingScheme", name: "Marking Schemes", description: "LC marking schemes for the past papers, extracted via the baml.subject_rubric.baml schema.", count: 0, icon: "✅", color: "green" },
  PracticeItem: { slug: "PracticeItem", name: "Practice", description: "Formative item generation + scoring via the baml.qpack_{subject}.baml schema. Uses the ScoreFormativeResponse function.", count: 0, icon: "✏️", color: "amber" },
  Foundation: { slug: "Foundation", name: "Foundations", description: "The 5 NCCA root-level programme PDFs at leaving_certificate/{key-competencies,sc-l1-l2-programme,scr-advisory,online-learning,online-certification}.pdf.", count: 5, icon: "📚", color: "purple" },
  Notebook: { slug: "Notebook", name: "Notebooks", description: "The marimo notebooks at notebooks/leaving_cert/{subject}.py, embedded as interactive widgets.", count: 0, icon: "📓", color: "cyan" },
};

export const CONTENT_TYPES_LIST: ContentTypeDef[] = Object.values(CONTENT_TYPES);
export const TOTAL_CONTENT_COUNT = CONTENT_TYPES_LIST.reduce((acc, ct) => acc + ct.count, 0);