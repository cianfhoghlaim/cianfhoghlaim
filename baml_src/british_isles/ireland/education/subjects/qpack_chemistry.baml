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
  text_en string
  text_ga string?
}

class ChemEvidenceLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  ncca_url string?
}

class ChemNCCALearningOutcome {
  lo_code string
  framework string
  level ChemNCCALevel
  topic ChemTopicArea
  competency_text ChemBilingualText
  marking_scheme_excerpt ChemBilingualText?
  evidence ChemEvidenceLink
}

class ChemFormativeItem {
  id string
  lo_code string
  level ChemNCCALevel
  topic ChemTopicArea
  item_type ChemItemType
  difficulty int @description("1-5")
  prompt ChemBilingualText
  expected_answer ChemBilingualText
  marking_scheme ChemBilingualText
  common_errors ChemBilingualText[]
  hints ChemBilingualText[] @description("4 graduated hints")
  evidence ChemEvidenceLink
  feedback_channel ChemFeedbackChannel
  est_time_minutes int
}

class ChemFormativeItemAttempt {
  item_id string
  student_response string
  response_format string @description("text / latex / image / structure")
  time_taken_seconds int
  hints_used int
}

class ChemScoreBreakdown {
  item_id string
  lo_code string
  total_marks int
  marks_awarded int
  marks_per_step int[]
  is_correct bool
  partial_credit_pct float
  feedback_en string
  feedback_ga string?
  next_recommended_lo string?
  badge_earned bool
}

class ChemQuestPack {
  id string
  subject string @description("Always 'chemistry'") @stream.not_null
  framework string
  level ChemNCCALevel
  title ChemBilingualText @stream.not_null
  description ChemBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items ChemFormativeItem[] @stream.with_state
  prerequisites string[]
  cross_subject_links string[] @description("LC-APPM, LC-MATHS for cross-subject synthesis")
  generated_at string
  generated_by string @description("Always 'chem_agent'")
}

class ChemQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types rather than
// the superseded `_legacy/pdfs/leaving_cert_syllabus.baml` types.
// `level: JC` is Junior Cycle Science — no separate file.
// ============================================================================

function GenerateChemQuestPack(
  syllabus: SyllabusDocument,
  past_papers: ExamPaper[],
  marking_schemes: MarkingScheme[],
  level: string
) -> ChemQuestPack {  client ExtractEn
  prompt #"
    You are building a Chemistry formative-assessment quest pack for NCCA
    students at level {{ level }} ("JC" = Junior Cycle Science; "LC_OL"/
    "LC_HL" = Leaving Cert Ordinary/Higher Chemistry). Ground every item in
    the official syllabus, past exam papers, and marking scheme guidance
    below — do not invent topics, learning outcomes, or questions beyond
    what these documents actually establish.

    Official syllabus:
    {{ syllabus }}

    Past exam papers (for question style + marks allocation reference):
    {{ past_papers }}

    Marking scheme guidance (for grading bands + common-error reference):
    {{ marking_schemes }}

    Build a ChemQuestPack:
    - subject: "chemistry"
    - framework: "ncca-lc" if level starts with "LC", "ncca-jc" if level is "JC"
    - level: the ChemNCCALevel matching {{ level }}
    - title / description: bilingual; text_ga null only if the syllabus text
      itself is English-only
    - items: select up to 15 learning outcomes spanning as many distinct
      module_topics as the syllabus has (breadth over exhaustive LO
      coverage — a quest pack is a bounded, completable unit, not the
      entire syllabus in one response), and generate one ChemFormativeItem
      per selected LO, drawn from
      syllabus.module_topics[].learning_outcomes — prompt/expected_answer/
      marking_scheme grounded in the real syllabus wording, including
      mandatory-experiment procedure detail where the syllabus names one;
      where a past-paper question's related_lo_id matches, mirror its
      question style and mark allocation; hints escalate from a light nudge
      to a near-complete worked solution; evidence.source_page and
      evidence.excerpt_en/excerpt_ga copied verbatim from the grounding
      syllabus text, never invented; evidence.source_pdf from
      syllabus.source_pdf
    - los_covered: exactly the LO codes of the items you actually
      generated above (not the full syllabus's LO list)
    - total_items / total_marks / est_time_minutes: sums over the actual items
    - prerequisites / cross_subject_links: only what the syllabus's
      cross_curricular field or assessment_objectives actually name
    - generated_at: current ISO-8601 datetime
    - generated_by: "chem_agent"

    Count and cite carefully from the actual text. Output exactly one complete
    JSON object matching ChemQuestPack. Never use ellipses (...) or comments;
    include every one of your selected items in full (up to 15 — never
    truncate a generated item, but do not exceed the cap either).

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractChemLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct NCCA Chemistry learning-outcome statement from the
    syllabus paragraph below. Return each as its own string, verbatim from
    the text — do not merge multiple outcomes into one string, and do not
    paraphrase.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

// -----------------------------------------------------------------------------
// ExtractChemGaStatement (added 2026-07-13-baml-cocoindex-tutorials-ga-v1)
// -----------------------------------------------------------------------------
// The bilingual EN+GA variant of ExtractChemLOStatement. Same
// return shape (`string[]`); routes via `client Default`; the
// prompt asks for the Irish (Gaeilge) statements verbatim with a
// leading '[EN-only]' fallback marker for LOs the NCCA did not
// translate. LC Chemistry syllabi are mostly English-only, so the
// fallback path is the common case.

function ExtractChemGaStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct Irish-language (Gaeilge) NCCA Chemistry
    learning-outcome statement from the syllabus paragraph below. Return each
    as its own string, verbatim from the text. If the paragraph is
    English-only, return an empty list rather than translating.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateChemFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: ChemEvidenceLink
) -> ChemFormativeItem {  client ExtractEn
  prompt #"
    You are writing a single formative-assessment item for NCCA Chemistry
    learning outcome {{ lo_code }} (topic: {{ topic }}, level: {{ level }},
    target difficulty: {{ difficulty }}/5).

    Ground the item entirely in this verbatim evidence from the official
    syllabus — do not write a generic chemistry question unrelated to it:

    {{ evidence }}

    Build a ChemFormativeItem:
    - id: a fresh UUID
    - lo_code: {{ lo_code }}, level: the ChemNCCALevel matching {{ level }},
      topic: the ChemTopicArea matching {{ topic }}
    - item_type: choose the type that best fits the evidence (e.g.
      STRUCTURE_DRAWING for bonding outcomes, LAB_PROCEDURE for mandatory
      experiments, BALANCE_EQUATION for stoichiometry)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: bilingual, derived from the
      evidence excerpt, not a generic template
    - common_errors: plausible mistakes for this specific outcome
    - hints: exactly 4, escalating from a light nudge to a near-complete
      worked solution
    - evidence: pass the input evidence through unchanged
    - feedback_channel: LAB_ASSISTANT for practical items, CHEM_TUTOR for
      calculation items, CURRICULUM_LOOKUP for definitional items
    - est_time_minutes: realistic for the item's difficulty (1-30)

    Output exactly one complete JSON object matching ChemFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreChemFormativeResponse(
  item: ChemFormativeItem,
  attempt: ChemFormativeItemAttempt
) -> ChemScoreBreakdown {  client ExtractEn
  prompt #"
    You are marking a student's response to a Chemistry formative item,
    using the item's own marking scheme — do not apply an external standard.

    Item (including its expected_answer and marking_scheme):
    {{ item }}

    Student attempt:
    {{ attempt }}

    Build a ChemScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: derived from item.marking_scheme's stated allocation
    - marks_awarded / marks_per_step: award partial credit per the marking
      scheme's per-step breakdown, not all-or-nothing, unless the marking
      scheme itself is all-or-nothing
    - is_correct: true iff marks_awarded == total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_en / feedback_ga: specific to what the student actually wrote,
      referencing item.common_errors where applicable
    - next_recommended_lo: a plausible next LO only if the response reveals a
      specific gap; otherwise null
    - badge_earned: true iff partial_credit_pct >= 80

    Output exactly one complete JSON object matching ChemScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateChemQuestPack(pack: ChemQuestPack) -> ChemQuestPackValidation {  client ExtractEn
  prompt #"
    Validate the internal consistency of this ChemQuestPack — every item's
    lo_code SHOULD appear in los_covered, total_items SHOULD equal
    items.length, total_marks SHOULD equal the sum of each item's marking
    scheme allocation, and no item SHOULD have an empty evidence.excerpt_en
    and evidence.excerpt_ga.

    Quest pack:
    {{ pack }}

    Build a ChemQuestPackValidation: pack_id from the input, is_valid true
    only if no errors were found, errors for any hard inconsistency listed
    above, warnings for anything suspicious but not necessarily wrong.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}