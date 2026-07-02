// @cianfhoghlaim/i18n — Bilingual string tables (EN + GA)
// Phase 1 T1.2 — packages/i18n scaffolding.
//
// The 5 NCCA Key Competencies, the 8 NCCA subjects, the 6 subnations,
// the 4 diagram modes, and the 4 formative feedback channels are all
// bilingual EN + GA so that the Brown Ajah welcome banner can flip
// between languages without losing the Tuatha Dé Danann lore.

export const en = {
  common: {
    yes: "Yes",
    no: "No",
    cancel: "Cancel",
    submit: "Submit",
    next: "Next",
    previous: "Previous",
    close: "Close",
    open: "Open",
    loading: "Loading…",
    error: "Error",
    retry: "Retry",
  },
  header: {
    tagline: "Aes Sedai — servants of all",
    signIn: "Sign In",
    signOut: "Sign Out",
  },
  nav: {
    curriculum: "Curriculum",
    exams: "Exams",
    markingSchemes: "Marking Schemes",
    practice: "Practice",
    assets: "Assets",
    dagsterRuns: "Dagster Runs",
    settings: "Settings",
    map: "Map",
    keyCompetencies: "Key Competencies",
  },
  subject: {
    mathematics: "Mathematics",
    applied_mathematics: "Applied Mathematics",
    chemistry: "Chemistry",
    geography: "Geography",
    history: "History",
    english: "English",
    gaeilge: "Gaeilge",
    computer_science: "Computer Science",
  },
  subnation: {
    eire: "Éire",
    "northern-ireland": "Northern Ireland",
    scotland: "Scotland",
    england: "England",
    wales: "Wales",
    "isle-of-man": "Isle of Man",
  },
  keyCompetency: {
    communicating: {
      name: "Communicating",
      name_ga: "Cumarsáid",
      deity: "Brigid",
      description: "The healing of the language — bilingual EN+GA throughout.",
      description_ga: "Cneasú na teanga — dátheangach EN+GA ar feadh an churaclaim.",
    },
    "information-processing": {
      name: "Information Processing",
      name_ga: "Próiseáil Faisnéise",
      deity: "Ogma",
      description: "The healing of the data — Ogma invented Ogham.",
      description_ga: "Cneasú na sonraí — chruthaigh Ogma Ogham.",
    },
    "critical-creative-thinking": {
      name: "Critical & Creative Thinking",
      name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
      deity: "Lugh",
      description: "The healing of the reasoning — Lugh's samildanach (master of all arts).",
      description_ga: "Cneasú an réasúnaithe — samildanach Lugh (máistir gach ealaíne).",
    },
    "personal-effectiveness": {
      name: "Personal Effectiveness",
      name_ga: "Éifeachtacht Phearsanta",
      deity: "Dian Cecht",
      description: "The healing of the discipline — Dian Cecht was the physician of the Tuatha Dé.",
      description_ga: "Cneasú na disciplíne — ba leigheasóir na Tuatha Dé é Dian Cecht.",
    },
    "working-with-others": {
      name: "Working with Others",
      name_ga: "Ag Obair le Daoine Eile",
      deity: "Trí Dé Dána",
      description: "The healing of the community — the Trí Dé Dána (Brigid + Dian Cecht + Ogma) collectively.",
      description_ga: "Cneasú an phobail — na Trí Dé Dána (Brigid + Dian Cecht + Ogma) le chéile.",
    },
  },
  diagramMode: {
    "concept-map": {
      name: "Concept Map",
      name_ga: "Léarscáil Choinceapa",
      description: "5 NCCA Key Competencies as the root + the 8 LC subjects as children.",
      description_ga: "5 Phríochomhardaigh NCCA mar fhréamh + na 8 n-ábhar LC mar pháistí.",
    },
    "topic-heatmap": {
      name: "Topic Heatmap",
      name_ga: "Téamhléarscáil Topaicí",
      description: "Question × Paper × Topic × Year frequency grid.",
      description_ga: "Eangach mhinicíochta Ceist × Páipéar → Topaic → Bliain.",
    },
    "pclm-flow": {
      name: "PCLM Flow",
      name_ga: "Sreabh PCLM",
      description: "Partial Credit, Logical Marking — per-question criteria flow.",
      description_ga: "Creidmheas Páirteach, Marcáil Loighciúil — sreabh na gcritéar in aghaidh an cheist.",
    },
    "question-sankey": {
      name: "Question Sankey",
      name_ga: "Sankey na gCeisteanna",
      description: "Question → Topic → Difficulty → Year directional flow.",
      description_ga: "Sreabh treochaí Ceist → Topaic → Deacracht → Bliain.",
    },
  },
  feedbackChannel: {
    "subject-tutor": {
      name: "Subject Tutor",
      name_ga: "Teagascóir Ábhar",
      description: "Concrete worked-example feedback from the per-subject ADK agent.",
      description_ga: "Aiseolas samplach oibre ón gníomhaire ADK in aghaidh an ábhair.",
    },
    "quest-guide": {
      name: "Quest Guide",
      name_ga: "Treoir Taiscéalaithe",
      description: "4 graduated hint levels (Level 1 nudge → Level 4 step-by-step).",
      description_ga: "4 leibhéal leide céimnithe (Leibhéal 1 smeach → Leibhéal 4 céim ar chéim).",
    },
    "curriculum-lookup": {
      name: "Curriculum Lookup",
      name_ga: "Cuardach Curaclaim",
      description: "Direct NCCA LO citation + source page reference via BAML extraction.",
      description_ga: "Sleachta dhíreach LO ón NCCA + tagairt leathanaigh foinse trí eastóscadh BAML.",
    },
    "research-assistant": {
      name: "Research Assistant",
      name_ga: "Cúntóir Taighde",
      description: "Cross-topic + cross-subject synthesis via the meaisínfhoghlaim ADK agent.",
      description_ga: "Sintéis tras-topaic + tras-ábhar trí ghníomhaire ADK an mheaisínfhoghlaim.",
    },
  },
} as const;

export const ga = {
  common: {
    yes: "Tá",
    no: "Níl",
    cancel: "Cealaigh",
    submit: "Seol",
    next: "Ar aghaidh",
    previous: "Roimhe seo",
    close: "Dún",
    open: "Oscail",
    loading: "Á lódáil…",
    error: "Earráid",
    retry: "Atriail",
  },
  header: {
    tagline: "Aes Sedai — freastalaithe ar gach duine",
    signIn: "Sínigh Isteach",
    signOut: "Sínigh Amach",
  },
  nav: {
    curriculum: "Curaclam",
    exams: "Scrúduithe",
    markingSchemes: "Scéimeanna Marcála",
    practice: "Cleachtadh",
    assets: "Sócmhainní",
    dagsterRuns: "Rithanna Dagster",
    settings: "Socruithe",
    map: "Léarscáil",
    keyCompetencies: "Príochomhardaigh",
  },
  subject: {
    mathematics: "Mata",
    applied_mathematics: "Mata Feidhmíoch",
    chemistry: "Ceimic",
    geography: "Tíreolaíocht",
    history: "Stair",
    english: "Béarla",
    gaeilge: "Gaeilge",
    computer_science: "Ríomheolaíocht",
  },
  subnation: {
    eire: "Éire",
    "northern-ireland": "Tuaisceart Éireann",
    scotland: "Albain",
    england: "Sasana",
    wales: "an Bhreatain Bheag",
    "isle-of-man": "Ellan Vannin",
  },
  keyCompetency: {
    communicating: {
      name: "Cumarsáid",
      name_ga: "Cumarsáid",
      deity: "Brigid",
      description: "Cneasú na teanga — dátheangach EN+GA ar feadh an churaclaim.",
      description_ga: "Cneasú na teanga — dátheangach EN+GA ar feadh an churaclaim.",
    },
    "information-processing": {
      name: "Próiseáil Faisnéise",
      name_ga: "Próiseáil Faisnéise",
      deity: "Ogma",
      description: "Cneasú na sonraí — chruthaigh Ogma Ogham.",
      description_ga: "Cneasú na sonraí — chruthaigh Ogma Ogham.",
    },
    "critical-creative-thinking": {
      name: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
      name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
      deity: "Lugh",
      description: "Cneasú an réasúnaithe — samildanach Lugh (máistir gach ealaíne).",
      description_ga: "Cneasú an réasúnaithe — samildanach Lugh (máistir gach ealaíne).",
    },
    "personal-effectiveness": {
      name: "Éifeachtacht Phearsanta",
      name_ga: "Éifeachtacht Phearsanta",
      deity: "Dian Cecht",
      description: "Cneasú na disciplíne — ba leigheasóir na Tuatha Dé é Dian Cecht.",
      description_ga: "Cneasú na disciplíne — ba leigheasóir na Tuatha Dé é Dian Cecht.",
    },
    "working-with-others": {
      name: "Ag Obair le Daoine Eile",
      name_ga: "Ag Obair le Daoine Eile",
      deity: "Trí Dé Dána",
      description: "Cneasú an phobail — na Trí Dé Dána (Brigid + Dian Cecht + Ogma) le chéile.",
      description_ga: "Cneasú an phobail — na Trí Dé Dána (Brigid + Dian Cecht + Ogma) le chéile.",
    },
  },
  diagramMode: {
    "concept-map": {
      name: "Léarscáil Choinceapa",
      name_ga: "Léarscáil Choinceapa",
      description: "5 Phríochomhardaigh NCCA mar fhréamh + na 8 n-ábhar LC mar pháistí.",
      description_ga: "5 Phríochomhardaigh NCCA mar fhréamh + na 8 n-ábhar LC mar pháistí.",
    },
    "topic-heatmap": {
      name: "Téamhléarscáil Topaicí",
      name_ga: "Téamhléarscáil Topaicí",
      description: "Eangach mhinicíochta Ceist × Páipéar → Topaic → Bliain.",
      description_ga: "Eangach mhinicíochta Ceist × Páipéar → Topaic → Bliain.",
    },
    "pclm-flow": {
      name: "Sreabh PCLM",
      name_ga: "Sreabh PCLM",
      description: "Creidmheas Páirteach, Marcáil Loighciúil — sreabh na gcritéar in aghaidh an cheist.",
      description_ga: "Creidmheas Páirteach, Marcáil Loighciúil — sreabh na gcritéar in aghaidh an cheist.",
    },
    "question-sankey": {
      name: "Sankey na gCeisteanna",
      name_ga: "Sankey na gCeisteanna",
      description: "Sreabh treochaí Ceist → Topaic → Deacracht → Bliain.",
      description_ga: "Sreabh treochaí Ceist → Topaic → Deacracht → Bliain.",
    },
  },
  feedbackChannel: {
    "subject-tutor": {
      name: "Teagascóir Ábhar",
      name_ga: "Teagascóir Ábhar",
      description: "Aiseolas samplach oibre ón gníomhaire ADK in aghaidh an ábhair.",
      description_ga: "Aiseolas samplach oibre ón gníomhaire ADK in aghaidh an ábhair.",
    },
    "quest-guide": {
      name: "Treoir Taiscéalaithe",
      name_ga: "Treoir Taiscéalaithe",
      description: "4 leibhéal leide céimnithe (Leibhéal 1 smeach → Leibhéal 4 céim ar chéim).",
      description_ga: "4 leibhéal leide céimnithe (Leibhéal 1 smeach → Leibhéal 4 céim ar chéim).",
    },
    "curriculum-lookup": {
      name: "Cuardach Curaclaim",
      name_ga: "Cuardach Curaclaim",
      description: "Sleachta dhíreach LO ón NCCA + tagairt leathanaigh foinse trí eastóscadh BAML.",
      description_ga: "Sleachta dhíreach LO ón NCCA + tagairt leathanaigh foinse trí eastóscadh BAML.",
    },
    "research-assistant": {
      name: "Cúntóir Taighde",
      name_ga: "Cúntóir Taighde",
      description: "Sintéis tras-topaic + tras-ábhar trí ghníomhaire ADK an mheaisínfhoghlaim.",
      description_ga: "Sintéis tras-topaic + tras-ábhar trí ghníomhaire ADK an mheaisínfhoghlaim.",
    },
  },
} as const;

export type Strings = typeof en;
export type Language = "en" | "ga";
export type KeyCompetencySlug =
  | "communicating"
  | "information-processing"
  | "critical-creative-thinking"
  | "personal-effectiveness"
  | "working-with-others";
export type SubjectSlug =
  | "mathematics"
  | "applied_mathematics"
  | "chemistry"
  | "geography"
  | "history"
  | "english"
  | "gaeilge"
  | "computer_science";
export type SubnationSlug =
  | "eire"
  | "northern-ireland"
  | "scotland"
  | "england"
  | "wales"
  | "isle-of-man";
export type DiagramModeSlug =
  | "concept-map"
  | "topic-heatmap"
  | "pclm-flow"
  | "question-sankey";
export type FeedbackChannelSlug =
  | "subject-tutor"
  | "quest-guide"
  | "curriculum-lookup"
  | "research-assistant";

export const KEY_COMPETENCY_SLUGS: readonly KeyCompetencySlug[] = [
  "communicating",
  "information-processing",
  "critical-creative-thinking",
  "personal-effectiveness",
  "working-with-others",
] as const;
export const SUBJECT_SLUGS: readonly SubjectSlug[] = [
  "mathematics",
  "applied_mathematics",
  "chemistry",
  "geography",
  "history",
  "english",
  "gaeilge",
  "computer_science",
] as const;
export const SUBNATION_SLUGS: readonly SubnationSlug[] = [
  "eire",
  "northern-ireland",
  "scotland",
  "england",
  "wales",
  "isle-of-man",
] as const;
export const DIAGRAM_MODE_SLUGS: readonly DiagramModeSlug[] = [
  "concept-map",
  "topic-heatmap",
  "pclm-flow",
  "question-sankey",
] as const;
export const FEEDBACK_CHANNEL_SLUGS: readonly FeedbackChannelSlug[] = [
  "subject-tutor",
  "quest-guide",
  "curriculum-lookup",
  "research-assistant",
] as const;

export function getStrings(language: Language): Strings {
  return language === "ga" ? (ga as unknown as Strings) : en;
}