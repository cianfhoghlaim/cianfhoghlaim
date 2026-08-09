// BAML schema: Computer Science Quest Pack Generator (LC + JC)
// NCCA Leaving Certificate Computer Science (OL + HL).
// Topics: Algorithms, Data Structures, Programming (Python),
// Computational Thinking, Computer Systems, Networks, Databases,
// Web Development, Ethics.

enum CompNCCALevel {
  JC_CODING_SHORT_COURSE
  LC_OL
  LC_HL
}

enum CompTopicArea {
  ALGORITHMS              @description("Sorting, searching, complexity")
  DATA_STRUCTURES          @description("Arrays, lists, stacks, queues, trees, graphs")
  PROGRAMMING             @description("Python; variables, control flow, functions, OOP")
  COMPUTATIONAL_THINKING   @description("Decomposition, pattern recognition, abstraction, algorithms")
  COMPUTER_SYSTEMS        @description("CPU, memory, storage, OS")
  NETWORKS                 @description("LAN, WAN, protocols, internet")
  DATABASES                @description("SQL, normalisation, ER diagrams")
  WEB_DEVELOPMENT          @description("HTML, CSS, JavaScript basics")
  DATA_REPRESENTATION      @description("Binary, hex, character encoding")
  ETHICS                   @description("Privacy, AI ethics, intellectual property")
  PROBLEM_SOLVING          @description("Computational thinking + algorithm design")
}

enum CompItemType {
  SHORT_ANSWER
  CODE_COMPLETION
  CODE_TRACE
  CONCEPTUAL
  ALGORITHM_DESIGN
  DEBUGGING
  WORD_PROBLEM
}

enum CompFeedbackChannel {
  COMP_TUTOR
  QUEST_GUIDE
  CURRICULUM_LOOKUP
  CODE_REVIEWER
  RESEARCH_ASSISTANT
}

class CompBilingualText {
  text_en string?
  text_ga string
}
class CompEvidenceLink {
  source_pdf string
  source_page int
  excerpt_en string?
  excerpt_ga string
  ncca_url string?
}
class CompNCCALearningOutcome {
  lo_code string
  framework string
  level CompNCCALevel
  topic CompTopicArea
  competency_text CompBilingualText
  marking_scheme_excerpt CompBilingualText?
  evidence CompEvidenceLink
}
class CompFormativeItem {
  id string
  lo_code string
  level CompNCCALevel
  topic CompTopicArea
  item_type CompItemType
  difficulty int
  prompt CompBilingualText
  expected_answer CompBilingualText
  marking_scheme CompBilingualText
  common_errors CompBilingualText[]
  hints CompBilingualText[]
  evidence CompEvidenceLink
  feedback_channel CompFeedbackChannel
  est_time_minutes int
}
class CompFormativeItemAttempt {
  item_id string
  student_response string
  response_format string @description("text / code / pseudocode")
  time_taken_seconds int
  hints_used int
}
class CompScoreBreakdown {
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
class CompQuestPack {
  id string
  subject string @description("Always 'computer_science'") @stream.not_null
  framework string
  level CompNCCALevel
  title CompBilingualText @stream.not_null
  description CompBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items CompFormativeItem[] @stream.with_state
  prerequisites string[]
  cross_subject_links string[] @description("LC-MATHS for algorithms, LC-APPM for computational modelling")
  generated_at string
  generated_by string @description("Always 'comp_agent'")
}
class CompQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types. Note:
// `CompNCCALevel`'s Junior Cycle member is `JC_CODING_SHORT_COURSE` (not a
// plain `JC` — Computer Science is a JC short course, not a full subject).
// Also note CompBilingualText requires text_ga and makes text_en optional
// (the class's existing nullability, unchanged here).
// ============================================================================

function GenerateCompQuestPack(syllabus: SyllabusDocument, past_papers: ExamPaper[], marking_schemes: MarkingScheme[], level: string) -> CompQuestPack {  client ExtractEn
  prompt #"
    You are building a Computer Science formative-assessment quest pack for
    NCCA students at level {{ level }} ("JC_CODING_SHORT_COURSE" = Junior
    Cycle coding short course; "LC_OL"/"LC_HL" = Leaving Cert Ordinary/
    Higher Computer Science). Ground every item in the official syllabus,
    past exam papers, and marking scheme guidance below — do not invent
    topics, learning outcomes, or questions beyond what these documents
    actually establish.

    Official syllabus:
    {{ syllabus }}

    Past exam papers (for question style + marks allocation reference):
    {{ past_papers }}

    Marking scheme guidance (for grading bands + common-error reference):
    {{ marking_schemes }}

    Build a CompQuestPack:
    - subject: "computer_science"
    - framework: "ncca-lc" if level starts with "LC", "ncca-jc" if level is
      "JC_CODING_SHORT_COURSE"
    - level: the CompNCCALevel matching {{ level }}
    - title / description: text_ga always populated; text_en only if
      derivable from the source
    - items: select up to 15 learning outcomes spanning as many distinct
      module_topics as the syllabus has (breadth over exhaustive LO
      coverage — a quest pack is a bounded, completable unit, not the
      entire syllabus in one response), and generate one CompFormativeItem
      per selected LO, drawn from
      syllabus.module_topics[].learning_outcomes — prefer CODE_COMPLETION/
      CODE_TRACE/DEBUGGING item types where the syllabus text describes
      programming outcomes, ALGORITHM_DESIGN for computational-thinking
      outcomes; where a past-paper question's related_lo_id matches, mirror
      its style and mark allocation; hints escalate from a light nudge to a
      near-complete solution; evidence.source_page and evidence.excerpt_ga
      (+ excerpt_en if available) copied verbatim from the grounding text,
      never invented; evidence.source_pdf from syllabus.source_pdf
    - los_covered: exactly the LO codes of the items you actually
      generated above (not the full syllabus's LO list)
    - total_items / total_marks / est_time_minutes: sums over the actual items
    - prerequisites / cross_subject_links: only what the syllabus's
      cross_curricular field or assessment_objectives actually name
    - generated_at: current ISO-8601 datetime
    - generated_by: "comp_agent"

    Count and cite carefully from the actual text. Output exactly one complete
    JSON object matching CompQuestPack. Never use ellipses (...) or comments;
    include every one of your selected items in full (up to 15 — never
    truncate a generated item, but do not exceed the cap either).

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractCompLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct NCCA Computer Science learning-outcome statement
    from the syllabus paragraph below. Return each as its own string,
    verbatim from the text — do not merge multiple outcomes into one string.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateCompFormativeItem(lo_code: string, difficulty: int, level: string, topic: string, evidence: CompEvidenceLink) -> CompFormativeItem {  client ExtractEn
  prompt #"
    You are writing a single formative-assessment item for NCCA Computer
    Science learning outcome {{ lo_code }} (topic: {{ topic }}, level:
    {{ level }}, target difficulty: {{ difficulty }}/5).

    Ground the item entirely in this verbatim evidence from the official
    syllabus — do not write a generic programming question unrelated to it:

    {{ evidence }}

    Build a CompFormativeItem:
    - id: a fresh UUID
    - lo_code: {{ lo_code }}, level: the CompNCCALevel matching {{ level }},
      topic: the CompTopicArea matching {{ topic }}
    - item_type: choose the type that best fits the evidence (e.g.
      CODE_COMPLETION/CODE_TRACE/DEBUGGING for programming outcomes,
      ALGORITHM_DESIGN for computational-thinking outcomes)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: text_ga always populated,
      derived from the evidence excerpt, not a generic template. If the
      item is code-based, the code sample in prompt/expected_answer must be
      syntactically valid.
    - common_errors: plausible mistakes for this specific outcome
    - hints: exactly 4, escalating from a light nudge to a near-complete
      solution
    - evidence: pass the input evidence through unchanged
    - feedback_channel: CODE_REVIEWER for code items, COMP_TUTOR for
      conceptual items
    - est_time_minutes: realistic for the item's difficulty (1-30)

    Output exactly one complete JSON object matching CompFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreCompFormativeResponse(item: CompFormativeItem, attempt: CompFormativeItemAttempt) -> CompScoreBreakdown {  client ExtractEn
  prompt #"
    You are marking a student's response to a Computer Science formative
    item, using the item's own marking scheme. If the response is code, run
    it mentally against the expected_answer's logic rather than requiring an
    exact text match.

    Item (including its expected_answer and marking_scheme):
    {{ item }}

    Student attempt:
    {{ attempt }}

    Build a CompScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: derived from item.marking_scheme's stated allocation
    - marks_awarded / marks_per_step: partial credit per the marking scheme
    - is_correct: true iff marks_awarded == total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_en / feedback_ga: specific to what the student actually wrote
    - next_recommended_lo: a plausible next LO only if the response reveals a
      specific gap; otherwise null
    - badge_earned: true iff partial_credit_pct >= 80

    Output exactly one complete JSON object matching CompScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateCompQuestPack(pack: CompQuestPack) -> CompQuestPackValidation {  client ExtractEn
  prompt #"
    Validate the internal consistency of this CompQuestPack — every item's
    lo_code SHOULD appear in los_covered, total_items SHOULD equal
    items.length, total_marks SHOULD equal the sum of each item's marking
    scheme allocation, and no item SHOULD have an empty evidence.excerpt_ga.

    Quest pack:
    {{ pack }}

    Build a CompQuestPackValidation: pack_id from the input, is_valid true
    only if no errors were found, errors for hard inconsistencies, warnings
    for anything suspicious but not necessarily wrong.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}