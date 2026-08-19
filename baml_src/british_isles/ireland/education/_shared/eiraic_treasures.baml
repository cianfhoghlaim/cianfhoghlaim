// =============================================================================
// Éraic na Coiced (the 13 Éraic Treasures of Lugh)
// =============================================================================
// At the Second Battle of Mag Tuired (Cath Maige Tuired), the Tuatha Dé Danann
// demanded éraic (compensation) from the Fomorians for the death of Cian mac
// Cainte. Lugh — the Samildánach himself — composed the list. The 13 treasures
// in this file are the canonical éraic paid by the Fomorians.
//
// Each treasure is also a pedagogical *competency signal* — a teaching
// superpower that maps to a single NCCA subject area. The BAML types below
// carry the full mythology provenance so the Cianfhoghlaim Educational MMO can
// anchor its 8-subject domain agents (math_agent, appm_agent, chem_agent,
// geog_agent, hist_agent, engl_agent, gael_agent, comp_agent — see
// .agents/skills/cianfhoghlaim-mmo/SKILL.md) to the originating myth.
//
// The 13 treasures + their primary subject mapping:
//
//   1.  Skin of the Pig of Dobar       (healing)                       → Biology
//   2.  Skin of the Heifer of Dobar    (efficacy across landscapes)    → Geography
//   3.  Spear of Assal                 (never misses; precision strike) → Mathematics
//   4.  Chariot of the king of Sidrach (vehicular dynamics, motion)     → Applied Mathematics
//   5.  Sword of Caladbolg             (two-handed cutting, iteration)  → Computer Science
//   6.  Seven pigs of Easmal           (regenerate daily)               → All subjects
//   7.  Whelp of the king of Ioruaidh  (pursuit narrative, hound)       → English
//   8.  Cooking spit of the woman of Innis Cera                        → Gaeilge
//   9.  Helmet + breastplate of the king of Clochur (defence & witness)  → History
//   10. Three apples of the Hesperides (cross-realm bounty)             → Cross-subject mastery
//   11. Pigskin bag of the healing well                                → Citation rigor
//   12. Feather of the Bird of Crannog                                 → Recovery from failure
//   13. Lugh's own samildanach         (master of all arts)             → Universal mastery
//
// Re-gen after changes:  `cd cianfhoghlaim && uv run baml-cli generate`
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum EiraicSubject {
  BIOLOGY
  GEOGRAPHY
  MATHEMATICS
  APPLIED_MATHEMATICS
  COMPUTER_SCIENCE
  ALL_SUBJECTS
  ENGLISH
  GAEILGE
  HISTORY
  CROSS_SUBJECT
  CITATION_RIGOR
  RECOVERY_FROM_FAILURE
  UNIVERSAL_MASTERY
}

enum EiraicCapability {
  HEALING
  LANDSCAPE_STEWARDSHIP
  PRECISION
  MOTION_DYNAMICS
  ITERATIVE_CUT
  REGENERATION
  NARRATIVE_PURSUIT
  LINGUISTIC_LIVELIHOOD
  HISTORICAL_DEFENCE
  CROSS_REALM_SYNTHESIS
  CITATION_HYGIENE
  RESILIENCE_AFTER_FAILURE
  UNIVERSAL_MASTERY
}

enum EiraicProvenance {
  TDD_DOBAR
  TDD_SIDRACH
  FOMORIAN_ASSAL
  FOMORIAN_CLOCHUR
  FOMORIAN_EASMAL
  FOMORIAN_IORUAIDH
  TDD_INNIS_CERA
  HESPERIDES
  TDD_LUGH
  TUATHA_DE_DANANN
}

// -----------------------------------------------------------------------------
// Bilingual title
// -----------------------------------------------------------------------------

class EiraicTitle {
  en string @description("English name of the treasure")
  ga string @description("Irish / Gaeilge name of the treasure")
}

// -----------------------------------------------------------------------------
// The 13 éraic treasure classes
//   Each class is named after the treasure and exposes the same canonical
//   shape: title (bilingual), provenance, capability, primary subject,
//   pedagogical rationale, and how it shows up in the Cianfhoghlaim MMO.
// -----------------------------------------------------------------------------

class PigSkinOfDobar {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_1_pig_skin_dobar'")
  title EiraicTitle @description("An Cranncin Muc Dobar / Skin of the Pig of Dobar")
  provenance EiraicProvenance @description("TDD_DOBAR")
  capability EiraicCapability @description("HEALING")
  primary_subject EiraicSubject @description("BIOLOGY")
  rationale_en string @description("Why this treasure maps to Biology")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class HeiferSkinOfDobar {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_2_heifer_skin_dobar'")
  title EiraicTitle @description("Craicean na Tarbh Gile Dobar / Skin of the Heifer of Dobar")
  provenance EiraicProvenance @description("TDD_DOBAR")
  capability EiraicCapability @description("LANDSCAPE_STEWARDSHIP")
  primary_subject EiraicSubject @description("GEOGRAPHY")
  rationale_en string @description("Why this treasure maps to Geography")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class SpearOfAssal {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_3_spear_assal'")
  title EiraicTitle @description("Sleagh Assail / Spear of Assal")
  provenance EiraicProvenance @description("FOMORIAN_ASSAL")
  capability EiraicCapability @description("PRECISION")
  primary_subject EiraicSubject @description("MATHEMATICS")
  rationale_en string @description("Why this treasure maps to Mathematics")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class ChariotOfSidrach {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_4_chariot_sidrach'")
  title EiraicTitle @description("Cairt Rí Shidrach / Chariot of the king of Sidrach")
  provenance EiraicProvenance @description("TDD_SIDRACH")
  capability EiraicCapability @description("MOTION_DYNAMICS")
  primary_subject EiraicSubject @description("APPLIED_MATHEMATICS")
  rationale_en string @description("Why this treasure maps to Applied Mathematics")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class SwordOfCaladbolg {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_5_sword_caladbolg'")
  title EiraicTitle @description("Claíomh Caladbolg / Sword of Caladbolg")
  provenance EiraicProvenance @description("TUATHA_DE_DANANN")
  capability EiraicCapability @description("ITERATIVE_CUT")
  primary_subject EiraicSubject @description("COMPUTER_SCIENCE")
  rationale_en string @description("Why this treasure maps to Computer Science")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class SevenPigsOfEasmal {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_6_pigs_easmal'")
  title EiraicTitle @description("Seacht Muc Easmal / Seven pigs of Easmal")
  provenance EiraicProvenance @description("FOMORIAN_EASMAL")
  capability EiraicCapability @description("REGENERATION")
  primary_subject EiraicSubject @description("ALL_SUBJECTS")
  rationale_en string @description("Why this treasure maps to all subjects")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class WhelpOfIoruaidh {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_7_whelp_ioruaidh'")
  title EiraicTitle @description("Cuileann Rí Ioruaidh / Whelp of the king of Ioruaidh")
  provenance EiraicProvenance @description("FOMORIAN_IORUAIDH")
  capability EiraicCapability @description("NARRATIVE_PURSUIT")
  primary_subject EiraicSubject @description("ENGLISH")
  rationale_en string @description("Why this treasure maps to English")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class CookingSpitOfInnisCera {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_8_spit_innis_cera'")
  title EiraicTitle @description("Bior Fréimh Mná Inis Cera / Cooking spit of the woman of Innis Cera")
  provenance EiraicProvenance @description("TDD_INNIS_CERA")
  capability EiraicCapability @description("LINGUISTIC_LIVELIHOOD")
  primary_subject EiraicSubject @description("GAEILGE")
  rationale_en string @description("Why this treasure maps to Gaeilge")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class ArmourOfClochur {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_9_armour_clochur'")
  title EiraicTitle @description("Clogas + Lucht Cíoch Clogur / Helmet + breastplate of the king of Clochur")
  provenance EiraicProvenance @description("FOMORIAN_CLOCHUR")
  capability EiraicCapability @description("HISTORICAL_DEFENCE")
  primary_subject EiraicSubject @description("HISTORY")
  rationale_en string @description("Why this treasure maps to History")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class ThreeApplesOfHesperides {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_10_apples_hesperides'")
  title EiraicTitle @description("Trí Úll Hesperides / Three apples of the Hesperides")
  provenance EiraicProvenance @description("HESPERIDES")
  capability EiraicCapability @description("CROSS_REALM_SYNTHESIS")
  primary_subject EiraicSubject @description("CROSS_SUBJECT")
  rationale_en string @description("Why this treasure maps to cross-subject mastery")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class PigSkinBagOfHealingWell {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_11_pigskin_bag_healing'")
  title EiraicTitle @description("Mála Craicinn Muice Tobair Sláine / Pigskin bag of the healing well")
  provenance EiraicProvenance @description("TDD_DOBAR")
  capability EiraicCapability @description("CITATION_HYGIENE")
  primary_subject EiraicSubject @description("CITATION_RIGOR")
  rationale_en string @description("Why this treasure maps to citation rigor")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class FeatherOfBirdOfCrannog {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_12_feather_bird_crannog'")
  title EiraicTitle @description("Cleit Éan Lochair / Feather of the Bird of Crannog")
  provenance EiraicProvenance @description("TUATHA_DE_DANANN")
  capability EiraicCapability @description("RESILIENCE_AFTER_FAILURE")
  primary_subject EiraicSubject @description("RECOVERY_FROM_FAILURE")
  rationale_en string @description("Why this treasure maps to recovery from failure")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

class SamildanachOfLugh {
  treasure_id string @description("Canonical ID, e.g. 'eiraic_13_samildanach_lugh'")
  title EiraicTitle @description("Samhildánacht Lugh / Lugh's own samildanach (master of all arts)")
  provenance EiraicProvenance @description("TDD_LUGH")
  capability EiraicCapability @description("UNIVERSAL_MASTERY")
  primary_subject EiraicSubject @description("UNIVERSAL_MASTERY")
  rationale_en string @description("Why this treasure maps to universal mastery")
  rationale_ga string? @description("Irish-language rationale; null if unattested")
  mmo_signal string @description("How the Cianfhoghlaim Educational MMO lights this up")
}

// -----------------------------------------------------------------------------
// Aggregator type — the 13 together
// -----------------------------------------------------------------------------

class EiraicTreasures {
  pig_skin_of_dobar PigSkinOfDobar @description("Éraic 1 — Skin of the Pig of Dobar")
  heifer_skin_of_dobar HeiferSkinOfDobar @description("Éraic 2 — Skin of the Heifer of Dobar")
  spear_of_assal SpearOfAssal @description("Éraic 3 — Spear of Assal")
  chariot_of_sidrach ChariotOfSidrach @description("Éraic 4 — Chariot of the king of Sidrach")
  sword_of_caladbolg SwordOfCaladbolg @description("Éraic 5 — Sword of Caladbolg")
  seven_pigs_of_easmal SevenPigsOfEasmal @description("Éraic 6 — Seven pigs of Easmal")
  whelp_of_ioruaidh WhelpOfIoruaidh @description("Éraic 7 — Whelp of the king of Ioruaidh")
  cooking_spit_of_innis_cera CookingSpitOfInnisCera @description("Éraic 8 — Cooking spit of the woman of Innis Cera")
  armour_of_clochur ArmourOfClochur @description("Éraic 9 — Helmet + breastplate of the king of Clochur")
  three_apples_of_hesperides ThreeApplesOfHesperides @description("Éraic 10 — Three apples of the Hesperides")
  pigskin_bag_of_healing_well PigSkinBagOfHealingWell @description("Éraic 11 — Pigskin bag of the healing well")
  feather_of_bird_of_crannog FeatherOfBirdOfCrannog @description("Éraic 12 — Feather of the Bird of Crannog")
  samildanach_of_lugh SamildanachOfLugh @description("Éraic 13 — Lugh's own samildanach")
  primary_treasures_for_subject EiraicSubject[] @description("The subject slugs whose primary éraic maps from the requested subject")
  total_count int @description("Always 13 — the canonical Lugh éraic count")
}

// -----------------------------------------------------------------------------
// GetEiraicTreasures(subject) — primary routing function
// -----------------------------------------------------------------------------
// Returns the full set of 13 éraic treasures, with the *primary* subject
// classification flagged for the requested subject. Other subjects' treasures
// are still returned (every treasure is part of the éraic — but the
// `primary_treasures_for_subject` array tells the caller which treasures are
// the canonical anchor for the given subject).
//
// Subject slugs (matches NCCA syllabus slugs + the cianfhoghlaim
// Educational MMO 8-subject roster):
//   mathematics, applied_mathematics, computer_science, biology,
//   geography, english, gaeilge, history

function GetEiraicTreasures(subject: string) -> EiraicTreasures {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
