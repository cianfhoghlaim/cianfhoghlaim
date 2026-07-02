// @cianfhoghlaim/i18n — Bilingual string tables (EN + GA)
// Phase 1 T1.2 — packages/i18n scaffolding.

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
} as const;

export type Strings = typeof en;
export type Language = "en" | "ga";

export function getStrings(language: Language): Strings {
  return language === "ga" ? (ga as unknown as Strings) : en;
}