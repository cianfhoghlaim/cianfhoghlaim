// BAML schema: Computer Science Quest Pack Generator (LC + JC)
// NCCA Leaving Certificate Computer Science (OL + HL).
// Topics: Algorithms, Data Structures, Programming (Python),
// Computational Thinking, Computer Systems, Networks, Databases,
// Web Development, Ethics.

enum CompNCCALevel { JC_CODING_SHORT_COURSE, LC_OL, LC_HL }

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

class CompBilingualText { text_en: string; text_ga: string? }
class CompEvidenceLink { source_pdf: string; source_page: int; excerpt_en: string; excerpt_ga: string?; ncca_url: string? }
class CompNCCALearningOutcome {
  lo_code: string
  framework: string
  level: CompNCCALevel
  topic: CompTopicArea
  competency_text: CompBilingualText
  marking_scheme_excerpt: CompBilingualText?
  evidence: CompEvidenceLink
}
class CompFormativeItem {
  id: string
  lo_code: string
  level: CompNCCALevel
  topic: CompTopicArea
  item_type: CompItemType
  difficulty: int
  prompt: CompBilingualText
  expected_answer: CompBilingualText
  marking_scheme: CompBilingualText
  common_errors: CompBilingualText[]
  hints: CompBilingualText[]
  evidence: CompEvidenceLink
  feedback_channel: CompFeedbackChannel
  est_time_minutes: int
}
class CompFormativeItemAttempt {
  item_id: string
  student_response: string
  response_format: string @description("text / code / pseudocode")
  time_taken_seconds: int
  hints_used: int
}
class CompScoreBreakdown {
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
class CompQuestPack {
  id: string
  subject: string @description("Always 'computer_science'") @stream.not_null
  framework: string
  level: CompNCCALevel
  title: CompBilingualText @stream.not_null
  description: CompBilingualText
  total_items: int
  total_marks: int
  est_time_minutes: int
  los_covered: string[]
  items: CompFormativeItem[] @stream.with_state
  prerequisites: string[]
  cross_subject_links: string[] @description("LC-MATHS for algorithms, LC-APPM for computational modelling")
  generated_at: string
  generated_by: string @description("Always 'comp_agent'")
}
class CompQuestPackValidation {
  pack_id: string
  is_valid: bool
  errors: string[]
  warnings: string[]
}

function GenerateCompQuestPack(syllabus: LeavingCertSyllabus, past_papers: LeavingCertPastPaper[], marking_schemes: LeavingCertMarkingScheme[], level: string) -> CompQuestPack {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate Computer Science expert.
    Build a formative assessment quest pack for NCCA Computer Science at the {{ level }} level.

    Cover ALL learning outcomes with ≥1 FormativeItem each. Reference the
    source NCCA PDF page in each item's evidence. Order by difficulty (1-5).
    Suggest cross-subject links to Mathematics (algorithms, complexity) and
    to Applied Mathematics (computational modelling).

    Syllabus: {{ syllabus }}
    Past papers: {{ past_papers }}
    Marking schemes: {{ marking_schemes }}

    {{ ctx.output_format }}
  "#
}

function ExtractCompLOStatement(paragraph: string) -> string[] {
  client ExtractEn
  prompt #"
    Extract all Computer Science learning outcome statements from the following NCCA syllabus paragraph.
    Paragraph: {{ paragraph }}
    {{ ctx.output_format }}
  "#
}

function GenerateCompFormativeItem(lo_code: string, difficulty: int, level: string, topic: string) -> CompFormativeItem {
  client ExtractEnStrong
  prompt #"
    Generate a CS formative item for NCCA LO {{ lo_code }}.
    Difficulty: {{ difficulty }}; Level: {{ level }}; Topic: {{ topic }}
    4 graduated hints, ≥2 common errors, evidence.source_page, bilingual EN+GA.
    For CODE_COMPLETION items, include a Python code snippet in the prompt.
    {{ ctx.output_format }}
  "#
}

function ScoreCompFormativeResponse(item: CompFormativeItem, attempt: CompFormativeItemAttempt) -> CompScoreBreakdown {
  client ExtractEnStrong
  prompt #"
    Score the CS formative item attempt.
    Item: {{ item }}; Attempt: {{ attempt }}
    For code items, run the code mentally + check correctness.
    {{ ctx.output_format }}
  "#
}

function ValidateCompQuestPack(pack: CompQuestPack) -> CompQuestPackValidation {
  client ExtractEn
  prompt #"
    Validate the Computer Science quest pack. Pack: {{ pack }}
    {{ ctx.output_format }}
  "#
}