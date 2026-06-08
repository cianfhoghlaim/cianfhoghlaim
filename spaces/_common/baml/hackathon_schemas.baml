// spaces/_common/baml/hackathon_schemas.baml
//
// 4 NEW BAML schemas for the Build Small 2026 hackathon Spaces.
// These are *additions* — they don't replace the 4 REUSE schemas:
//   - tuatha/baml_src/mythology_extraction.baml           (Space 3 NPC base)
//   - tuatha/baml_src/celtic_curriculum.baml              (Space 2 CompareCurricula)
//   - tuatha/baml_src/player_assessment.baml              (Space 3 dialogue)
//   - oideachais/data_platform/baml_src/                  (Space 1 BAML extraction)
//
// The new schemas:
//
//   1. ExtractCircularMeta        -> Space 1 (An Scrúdú, Talamh)
//   2. GenerateExitCardQuestions  -> Space 4 (Mac Léinn, formative)
//   3. CompareCelticNations       -> Space 2 (Curaclam Trasteorann, Aer)
//   4. GenerateNpcDialogue        -> Space 3 (Cianfhoghlaim, Aer + Anam)
//
// All 4 use the BAML_HACKATHON_CHAINED client (3-tier fallback).

// =====================================================================
// Schema 1: ExtractCircularMeta (Space 1, An Scrúdú, Talamh)
// =====================================================================

class CircularReference {
  circular_number int
  issued_year int
  issuing_body string  // e.g. "Department of Education and Skills"
  title_en string
  title_ga string?
  subject string  // e.g. "Chemistry", "Irish", "Mathematics"
  level string    // e.g. "Leaving Certificate", "Junior Certificate"
}

class TopicDistribution {
  topic_code string  // e.g. "CH1", "IR1" — section code in the circular
  topic_label string
  marking_points int
  paper_section string  // e.g. "Section A", "Section B"
}

class MarkingSchemeSummary {
  total_marking_points int
  topics TopicDistribution[]
  estimated_paper_duration_min int
  has_orale bool  // Irish oral component?
  has_coursework bool
}

class CircularExtraction {
  circular CircularReference
  scheme MarkingSchemeSummary
  raw_text_excerpt string
  extraction_confidence float  // 0.0 - 1.0
}

function ExtractCircularMeta(
  pdf_text: string,
  filename: string,
) -> CircularExtraction {
  client BAML_HACKATHON_CHAINED
  prompt #"
    Extract the Irish Department of Education circular metadata and
    marking scheme structure from the following Leaving Certificate
    past-paper text.

    Filename: {{ filename }}

    Past-paper text (first 8,000 chars):
    ---
    {{ pdf_text }}
    ---

    Return a CircularExtraction with:
      - circular_number, issued_year, issuing_body, title_en, title_ga
      - subject, level (Leaving Cert or Junior Cert)
      - scheme.total_marking_points, scheme.topics (with topic_code,
        topic_label, marking_points, paper_section)
      - scheme.estimated_paper_duration_min
      - scheme.has_orale (true if Irish oral component)
      - scheme.has_coursework (true if any coursework/portfolio)
      - raw_text_excerpt: 200-300 char literal excerpt
      - extraction_confidence: 0.0 to 1.0
  "#
}

// =====================================================================
// Schema 2: GenerateExitCardQuestions (Space 4, Mac Léinn, formative)
// =====================================================================

class ExitCardQuestion {
  question_id string
  prompt_en string
  prompt_ga string
  question_type string  // "multiple_choice" | "short_answer" | "numeric"
  correct_answer string
  explanation_en string
  explanation_ga string
  bloom_level string  // "remember" | "understand" | "apply" | "analyze" | "evaluate" | "create"
  marking_point_ref string?  // e.g. "CH1.T3" — links back to the circular
}

class ExitCardSet {
  lesson_topic string
  subject string
  level string
  questions ExitCardQuestion[]
  total_questions int
  estimated_completion_min int
}

function GenerateExitCardQuestions(
  lesson_topic: string,
  subject: string,
  level: string,
  num_questions: int,
  curriculum_extract: CircularExtraction? = null,
) -> ExitCardSet {
  client BAML_HACKATHON_CHAINED
  prompt #"
    Generate a bilingual (EN + Gaeilge) "exit card" of {{ num_questions }}
    formative assessment questions for the topic "{{ lesson_topic }}"
    in {{ subject }} at {{ level }}.

    The exit card is a 3-minute end-of-lesson check for understanding.
    Mix question types: roughly half multiple_choice, a quarter
    short_answer, a quarter numeric.

    Each question must include:
      - prompt_en, prompt_ga (Irish translation)
      - question_type
      - correct_answer
      - explanation_en, explanation_ga
      - bloom_level (one of: remember, understand, apply, analyze, evaluate, create)
      - marking_point_ref: if curriculum_extract is provided, link
        to a topic_code from the marking scheme

    Aim for a balanced bloom distribution (don't put all 6 questions
    at "remember" level).
  "#
}

// =====================================================================
// Schema 3: CompareCelticNations (Space 2, Curaclam Trasteorann, Aer)
// =====================================================================

class CurriculumMapping {
  nation_code string  // "IE" | "NI" | "WLS" | "IM" | "SCT" | "COR" | "BRT"
  nation_name_en string
  nation_name_native string
  curriculum_body string  // e.g. "NCCA", "CCEA", "WJEC", "SQA"
  topic_label_en string
  topic_label_native string?
  year_level string
  topic_code string?  // official code if available
  similar_topics string[]  // topic_codes in other nations
}

class CrossNationComparison {
  topic_query string
  mappings CurriculumMapping[]
  shared_year_levels string[]
  notes string
}

function CompareCelticNations(
  topic_query: string,
  scope: string[] = ["IE", "NI", "WLS", "IM", "SCT"],
) -> CrossNationComparison {
  client BAML_HACKATHON_CHAINED
  prompt #"
    The user wants to know how "{{ topic_query }}" is taught across
    these Celtic-nation curricula: {{ scope }}.

    For each nation, return:
      - nation_code, nation_name_en, nation_name_native
      - curriculum_body (e.g. "NCCA" for ROI, "CCEA" for NI, etc.)
      - topic_label_en, topic_label_native (if not English)
      - year_level (e.g. "Senior Cycle", "A-Level", "Higher")
      - topic_code (the official code if known)
      - similar_topics: topic_codes from other nations that map

    Also produce:
      - shared_year_levels: the union of year_levels across nations
      - notes: a 1-2 sentence explanation of the cross-jurisdiction
        mapping (note any equivalences or divergences)
  "#
}

// =====================================================================
// Schema 4: GenerateNpcDialogue (Space 3, Cianfhoghlaim, Aer + Anam)
// =====================================================================

class NpcDialogue {
  speaker string
  nation_code string  // "IE" | "NI" | "WLS" | "IM" | "SCT" | "universal"
  era string  // e.g. "Iron Age", "Early Medieval", "Fictional"
  utterance_en string
  utterance_ga string
  scholarly_footnote_en string
  scholarly_footnote_ga string
  emotional_tone string  // "wry" | "wounded" | "curious" | "defiant" | "gentle"
  asks_player_about string  // prompt for the player's next turn
}

class NpcDialogueExchange {
  npc_name string
  npc_title string
  turn_index int
  dialogue NpcDialogue
  quest_offered string?
  artifact_granted string?
}

function GenerateNpcDialogue(
  npc_name: string,
  npc_title: string,
  nation_code: string,
  era: string,
  player_utterance: string,
  conversation_history: string,  // last 6 turns, formatted as "Speaker: text"
  scholarly_source: string,  // the cached Wikipedia article for this NPC
) -> NpcDialogueExchange {
  client BAML_HACKATHON_DIALOGUE
  prompt #"
    You are roleplaying {{ npc_name }} ({{ npc_title }}) from {{ nation_code }}
    in the {{ era }} era. You are one of 6 Celtic NPCs in a Hades-style
    dialogue game set on a navigable British Isles map.

    The player just said:
      "{{ player_utterance }}"

    Conversation so far:
    ---
    {{ conversation_history }}
    ---

    Your character's source material (Wikipedia excerpt, paraphrased):
    ---
    {{ scholarly_source }}
    ---

    Respond with:
      - utterance_en, utterance_ga (Irish translation, can be a brief
        poetic fragment)
      - scholarly_footnote_en, scholarly_footnote_ga: a 1-sentence
        citation pointing to the source material
      - emotional_tone: one of "wry", "wounded", "curious", "defiant",
        "gentle"
      - asks_player_about: a 1-sentence prompt for the next turn
      - quest_offered: (optional) a short quest hook
      - artifact_granted: (optional) an artifact name if the player
        earned something

    Voice rules:
      - Stay in character, never break the fourth wall
      - Ground every claim in the source material
      - Mix in 1 Irish-language phrase per 3 turns
      - Don't be longer than 3 sentences per turn
  "#
}
