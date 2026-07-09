// /en/key-competencies/$slug — Detail page for one of the 5 NCCA Key Competencies
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md + the 13 éraic treasures BAML.

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiSemanticPill, CiProgressRing } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/key-competencies/$slug")({
  component: KeyCompetencyDetailPage,
});

const KEY_COMPETENCIES: Record<string, {
  code: string;
  name_en: string;
  name_ga: string;
  tuatha_de: string;
  tuatha_de_role: string;
  color: string;
  description_en: string;
  description_ga: string;
  subject_examples: Array<{ subject: string; lo_example: string; rationale: string }>;
  ieraic_treasures: number[];
  brown_ajah: boolean;
}> = {
  "communicating": {
    code: "KC-CO",
    name_en: "Communicating",
    name_ga: "Cumarsáid",
    tuatha_de: "Brigid",
    tuatha_de_role: "Poetry + healing",
    color: "#059669",
    description_en: "The healing of the language — bilingual EN+GA throughout. The ability to communicate effectively in a variety of contexts.",
    description_ga: "An cumas cumarsáid éifeachtach a dhéanamh i gcomhthéacsanna éagsúla.",
    subject_examples: [
      { subject: "English", lo_example: "LC-EN-LO-1.1", rationale: "Reading + writing + speaking + listening are all forms of communication" },
      { subject: "Gaeilge", lo_example: "LC-GA-LO-1.1", rationale: "Bilingual communication in Irish + English" },
    ],
    ieraic_treasures: [7, 8],  // Whelp of Ioruaidh + Cooking spit of Innis Cera
    brown_ajah: true,
  },
  "information-processing": {
    code: "KC-IP",
    name_en: "Information Processing",
    name_ga: "Próiseáil Faisnéise",
    tuatha_de: "Ogma",
    tuatha_de_role: "Eloquence + learning (inventor of Ogham)",
    color: "#2563eb",
    description_en: "The healing of the data — Ogma invented Ogham, the earliest Celtic script. The ability to access, evaluate, interpret, and manage information.",
    description_ga: "An cumas rochtain, meastóireacht, léirmhíniú agus bainistíocht faisnéise a dhéanamh.",
    subject_examples: [
      { subject: "Computer Science", lo_example: "LC-CS-LO-2.1", rationale: "Data structures + algorithms + databases" },
      { subject: "Mathematics", lo_example: "LC-MA-LO-2.1", rationale: "Statistical analysis + mathematical modelling" },
    ],
    ieraic_treasures: [3, 5],  // Spear of Assal + Sword of Caladbolg
    brown_ajah: true,
  },
  "critical-creative-thinking": {
    code: "KC-CT",
    name_en: "Critical & Creative Thinking",
    name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
    tuatha_de: "Lugh",
    tuatha_de_role: "Samildanach (master of all arts)",
    color: "#ca8a04",
    description_en: "The healing of the reasoning — Lugh's samildanach is the master of all arts. The ability to think analytically, logically, and creatively.",
    description_ga: "An cumas smaointeoireacht anailíseach, loighciúil, cruthaitheach a dhéanamh.",
    subject_examples: [
      { subject: "History", lo_example: "LC-HI-LO-3.1", rationale: "Critical analysis of historical sources + causation" },
      { subject: "English", lo_example: "LC-EN-LO-3.1", rationale: "Critical reading + literary analysis" },
    ],
    ieraic_treasures: [10, 13],  // Three apples of the Hesperides + Lugh's samildanach
    brown_ajah: true,
  },
  "personal-effectiveness": {
    code: "KC-PE",
    name_en: "Personal Effectiveness",
    name_ga: "Éifeachtacht Phearsanta",
    tuatha_de: "Dian Cecht",
    tuatha_de_role: "Healing (the physician of the Tuatha Dé)",
    color: "#92400e",
    description_en: "The healing of the discipline — Dian Cecht was the physician. The ability to develop self-awareness, resilience, motivation.",
    description_ga: "An cumas féin-aird, athléimne, spreagadh a fhorbairt.",
    subject_examples: [
      { subject: "Chemistry", lo_example: "LC-CH-LO-4.1", rationale: "Lab safety + precision + systematic study" },
      { subject: "Biology", lo_example: "LC-BY-LO-4.1", rationale: "Self-directed learning + scientific method" },
    ],
    ieraic_treasures: [1, 11],  // Pig of Dobar (healing) + Pigskin bag of healing well
    brown_ajah: true,
  },
  "working-with-others": {
    code: "KC-WO",
    name_en: "Working with Others",
    name_ga: "Ag Obair le Daoine Eile",
    tuatha_de: "Trí Dé Dána",
    tuatha_de_role: "Brigid + Dian Cecht + Ogma (collectively)",
    color: "#b91c1c",
    description_en: "The healing of the community — the Trí Dé Dána collectively. The ability to interact and work collaboratively.",
    description_ga: "An cumas idirghníomhú agus comhoibriú a dhéanamh.",
    subject_examples: [
      { subject: "Geography", lo_example: "LC-GG-LO-5.1", rationale: "Fieldwork + group investigation + global citizenship" },
      { subject: "Applied Mathematics", lo_example: "LC-AM-LO-5.1", rationale: "Modelling real-world problems + team projects" },
    ],
    ieraic_treasures: [6, 9, 12],  // Seven pigs of Easmal + Armour of Clochur + Feather of Bird of Crannog
    brown_ajah: true,
  },
};

function KeyCompetencyDetailPage() {
  const { slug } = Route.useParams();
  const kc = KEY_COMPETENCIES[slug];

  if (!kc) {
    throw notFound({ data: { slug } });
  }

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <div className="text-3xl font-mono font-bold" style={{ color: kc.color }}>
          {kc.code}
        </div>
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {kc.name_en}
        </h1>
        <p className="text-slate-400 font-mono text-lg italic">{kc.name_ga}</p>
        <p className="text-slate-300 text-base max-w-2xl">
          {kc.description_en}
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          {kc.description_ga}
        </p>
      </div>

      <CiTextbookPanel title="The Tuatha Dé Connection" material="ink-wash">
        <div className="flex items-center gap-4 p-4 rounded-xl" style={{ backgroundColor: kc.color + "20" }}>
          <div className="text-3xl font-bold" style={{ color: kc.color }}>
            {kc.tuatha_de}
          </div>
          <div className="flex-1">
            <p className="text-slate-300">{kc.tuatha_de_role}</p>
          </div>
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="Subject Examples" material="parchment">
        <div className="grid grid-cols-1 gap-3">
          {kc.subject_examples.map((ex) => (
            <CiDetailCell
              key={ex.lo_example}
              icon={<span className="font-mono text-xs px-1.5 py-0.5 rounded" style={{ backgroundColor: kc.color + "40" }}>{ex.subject}</span>}
              title={ex.lo_example}
              metadata={ex.subject}
              description={ex.rationale}
            />
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The Éraic Treasures that Map" material="gold-leaf">
        <p className="text-slate-300 mb-4">
          For <strong>{kc.name_en}</strong> the relevant éraic-tier
          pedagogical anchors are:
        </p>
        <div className="flex flex-wrap gap-2">
          {kc.ieraic_treasures.map((tier) => (
            <CiSemanticPill
              key={tier}
              kind="eiraic"
              label={`Tier ${tier}/13`}
            />
          ))}
        </div>
        <Link
          to="/en/eiraic-treasures"
          className="inline-block mt-4 px-3 py-1.5 rounded-lg bg-amber-700 text-amber-100 hover:bg-amber-600 text-sm"
        >
          See all 13 Treasures →
        </Link>
      </CiTextbookPanel>

      <div className="flex justify-center">
        <Link
          to="/en/key-competencies"
          className="text-emerald-400 hover:text-emerald-300 text-sm"
        >
          ← Back to the 5×8 Mastery Matrix
        </Link>
      </div>
    </div>
  );
}