// /en/stages/$stage — Stage overview page (English locale)
import { createFileRoute, notFound } from "@tanstack/react-router";

export const Route = createFileRoute("/en/stages/$stage")({
  loader: ({ params }) => {
    if (!STAGES.find((s) => s.slug === params.stage)) {
      throw notFound();
    }
    return { stage: params.stage };
  },
  component: StageComponent,
});

function StageComponent() {
  const { stage } = Route.useParams();
  const s = STAGES.find((x) => x.slug === stage)!;
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        {s.icon} {s.title_en}
      </h1>
      <p className="text-slate-400 font-mono text-sm">{s.title_ga}</p>
      <p className="text-slate-300 text-lg">{s.description_en}</p>
      <div className="grid grid-cols-3 gap-4 mt-4">
        {s.components.map((c) => (
          <div
            key={c}
            className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-sm text-slate-300"
          >
            {c}
          </div>
        ))}
      </div>
    </div>
  );
}

const STAGES = [
  {
    slug: "aistear",
    icon: "🌱",
    title_en: "Aistear (Early Childhood)",
    title_ga: "Aistear (Luath-Óige)",
    description_en: "4 themes × 4 age bands × ~30 learning goals × 14 source PDFs + naíonra directory + parent tips.",
    components: ["AistearThemesGrid", "NaionraMap", "ParentTip"],
  },
  {
    slug: "primary",
    icon: "📘",
    title_en: "Primary",
    title_ga: "Bunscoil",
    description_en: "NCCA Primary Curriculum Framework — 12 curriculum areas × 4 stages. Strands × outcomes × cross-curricular links.",
    components: ["PrimaryStrandTree", "StageOutcomesMapper"],
  },
  {
    slug: "junior_cycle",
    icon: "📗",
    title_en: "Junior Cycle",
    title_ga: "Iar-Bhunscoil",
    description_en: "18 core subjects + 16 short courses, 2 CBAs each, 4 Achievement Levels per CBA.",
    components: ["JCCBATimeline", "JCShortCourseBadge", "L2LPSpecialist"],
  },
  {
    slug: "senior_cycle",
    icon: "🎓",
    title_en: "Senior Cycle",
    title_ga: "Scoil Daraigh",
    description_en: "50+ Leaving Certificate subjects across 7 families. Exam papers, marking schemes, Chief Examiner reports.",
    components: [
      "SCExamPaperCard",
      "SCMarkingSchemePanel",
      "SCRubricDescriptorList",
      "SCPracticeEssayEditor",
      "SCPointsCalculator",
      "SCMatriculationAuditor",
    ],
  },
  {
    slug: "tertiary",
    icon: "🏛️",
    title_en: "Tertiary",
    title_ga: "Ardteistiméireacht / Tríú",
    description_en: "CAO courses, NUI/HEI matriculation, QQI FET awards, Apprenticeships, application timeline.",
    components: [
      "TertiaryCAOCourseCard",
      "TertiaryQQILadder",
      "TertiaryApprenticeshipCard",
      "TertiaryApplicationTimeline",
      "TertiaryCAOPointsTrend",
    ],
  },
];
