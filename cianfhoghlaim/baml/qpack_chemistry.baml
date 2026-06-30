// BAML schema: Chemistry Quest Pack Generator (LC + JC)
//
// NCCA Leaving Certificate Chemistry (OL + HL) + Junior Cycle Science.
// Topics: Atomic Structure, Bonding, Stoichiometry, Acids/Bases,
// Organic Chemistry, Thermodynamics, Electrochemistry, Equilibria,
// Periodic Table, Rates of Reaction, etc.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum ChemNCCALevel {
  JC       @description("Junior Cycle Science")
  LC_OL    @description("Leaving Certificate Ordinary Level Chemistry")
  LC_HL    @description("Leaving Certificate Higher Level Chemistry")
}

enum ChemTopicArea {
  ATOMIC_STRUCTURE        @description("Atomic theory; electron configuration; periodic trends")
  BONDING                 @description("Ionic, covalent, metallic bonding; VSEPR; shapes")
  STOICHIOMETRY           @description("Mole concept; balancing equations; limiting reagent")
  ACIDS_BASES             @description("pH; buffers; titrations; indicators")
  ORGANIC_CHEMISTRY       @description("Functional groups; reactions; mechanisms; isomers")
  THERMODYNAMICS          @description("Enthalpy; entropy; Gibbs free energy")
  ELECTROCHEMISTRY        @description("Redox; electrolysis; galvanic cells; Faraday's laws")
  EQUILIBRIA              @description("Le Chatelier; equilibrium constants; ICE tables")
  PERIODIC_TABLE          @description("Periodic trends; transition metals; s/p/d-block")
  RATES_OF_REACTION       @description("Rate laws; Arrhenius; catalysis; mechanisms")
  STATES_OF_MATTER        @description("Gas laws; liquids; solids; phase transitions")
  WATER_CHEMISTRY         @description("Hardness; treatment; pH of natural water")
  CHEMICAL_EQUILIBRIUM    @description("Kp, Kc, Ksp calculations")
  ATOMIC_SPECTROSCOPY      @description("Flame tests; emission/absorption spectroscopy")
  NUCLEAR_CHEMISTRY        @description("Radioactivity; fission; fusion; half-life")
}

enum ChemItemType {
  SHORT_ANSWER
  WORKED_SOLUTION
  BALANCE_EQUATION
  STRUCTURE_DRAWING         @description("Lewis structure or 3D molecule drawing")
  CONCEPTUAL
  VISUAL_INTERPRETATION     @description("Read from diagrams, spectra, apparatus")
  WORD_PROBLEM
  LAB_PROCEDURE             @description("Mandatory practical experiment (LC mandatory experiments)")
}

enum ChemFeedbackChannel {
  CHEM_TUTOR
  QUEST_GUIDE
  CURRICULUM_LOOKUP
  LAB_ASSISTANT             @description("Mandatory experiment guidance")
  RESEARCH_ASSISTANT
}

class ChemBilingualText {
  text_en: string
  text_ga: string?
}

class ChemEvidenceLink {
  source_pdf: string
  source_page: int
  excerpt_en: string
  excerpt_ga: string?
  ncca_url: string?
}

class ChemNCCALearningOutcome {
  lo_code: string
  framework: string
  level: ChemNCCALevel
  topic: ChemTopicArea
  competency_text: ChemBilingualText
  marking_scheme_excerpt: ChemBilingualText?
  evidence: ChemEvidenceLink
}

class ChemFormativeItem {
  id: string
  lo_code: string
  level: ChemNCCALevel
  topic: ChemTopicArea
  item_type: ChemItemType
  difficulty: int @description("1-5")
  prompt: ChemBilingualText
  expected_answer: ChemBilingualText
  marking_scheme: ChemBilingualText
  common_errors: ChemBilingualText[]
  hints: ChemBilingualText[] @description("4 graduated hints")
  evidence: ChemEvidenceLink
  feedback_channel: ChemFeedbackChannel
  est_time_minutes: int
}

class ChemFormativeItemAttempt {
  item_id: string
  student_response: string
  response_format: string @description("text / latex / image / structure")
  time_taken_seconds: int
  hints_used: int
}

class ChemScoreBreakdown {
  item_id: string
  lo_code: string
  total_marks: int
  marks_awarded: int
  marks_per_step: int[]
  is_correct: bool
  partial_credit_pct: float
  feedback_en: string
  feedback_ga: string?
  next_recommended_lo: string?
  badge_earned: bool
}

class ChemQuestPack {
  id: string
  subject: string @description("Always 'chemistry'")
  framework: string
  level: ChemNCCALevel
  title: ChemBilingualText
  description: ChemBilingualText
  total_items: int
  total_marks: int
  est_time_minutes: int
  los_covered: string[]
  items: ChemFormativeItem[]
  prerequisites: string[]
  cross_subject_links: string[] @description("LC-APPM, LC-MATHS for cross-subject synthesis")
  generated_at: string
  generated_by: string @description("Always 'chem_agent'")
}

class ChemQuestPackValidation {
  pack_id: string
  is_valid: bool
  errors: string[]
  warnings: string[]
}

function GenerateChemQuestPack(
  syllabus: LeavingCertSyllabus,
  past_papers: LeavingCertPastPaper[],
  marking_schemes: LeavingCertMarkingScheme[],
  level: string
) -> ChemQuestPack {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate Chemistry expert. Build a
    formative assessment quest pack for NCCA Chemistry at the {{ level }}
    level (JC, LC_OL, or LC_HL).

    Cover ALL learning outcomes with ≥1 FormativeItem each. Reference
    the source NCCA PDF page in each item's evidence. Order items by
    difficulty (1 → 5). Suggest cross-subject links to Applied
    Mathematics (mechanics for kinetics) and to Physics (atomic
    structure, waves for spectroscopy).

    Syllabus: {{ syllabus }}
    Past papers: {{ past_papers }}
    Marking schemes: {{ marking_schemes }}

    {{ ctx.output_format }}
  "#
}

function ExtractChemLOStatement(paragraph: string) -> string[] {
  client ExtractEn
  prompt #"
    Extract all Chemistry learning outcome statements from the
    following NCCA syllabus paragraph.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateChemFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string
) -> ChemFormativeItem {
  client ExtractEnStrong
  prompt #"
    Generate a single formative assessment item for the NCCA Chemistry
    learning outcome {{ lo_code }}.

    Difficulty: {{ difficulty }}
    Level: {{ level }} (JC / LC_OL / LC_HL)
    Topic: {{ topic }}

    Include 4 graduated hints, ≥2 common errors, evidence.source_page,
    bilingual EN + GA, est_time_minutes 1-30.

    {{ ctx.output_format }}
  "#
}

function ScoreChemFormativeResponse(
  item: ChemFormativeItem,
  attempt: ChemFormativeItemAttempt
) -> ChemScoreBreakdown {
  client ExtractEnStrong
  prompt #"
    Score the Chemistry formative item attempt.

    Item: {{ item }}
    Attempt: {{ attempt }}

    Compute marks, feedback_en + feedback_ga, badge_earned.

    {{ ctx.output_format }}
  "#
}

function ValidateChemQuestPack(pack: ChemQuestPack) -> ChemQuestPackValidation {
  client ExtractEn
  prompt #"
    Validate the Chemistry quest pack. Check LO codes + difficulty
    bounds + time bounds.

    Pack: {{ pack }}

    {{ ctx.output_format }}
  "#
}