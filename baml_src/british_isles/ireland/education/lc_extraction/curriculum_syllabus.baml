// Real BAML extraction prompts for the 6 LC priority subjects.
// Per the 2026-08-10-baml-extraction-completion-v1 change.
//
// Replaces the "Auto-generated extraction prompt" stub with subject-specific
// prompts for mathematics, applied_mathematics, chemistry, geography, english,
// gaeilge, computer_science. Each follows the canonical `{{ _.role("user") }}` +
// `{{ ctx.output_format }}` marker pattern.

function ExtractCurriculumSyllabus(text: string, subject: string) -> CurriculumSyllabus {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish Leaving Certificate syllabus extractor for the subject `{{ subject }}`.

    Extract the canonical NCCA structure from the syllabus text below.

    For each topic, capture:
    - `code`: NCCA LO code (e.g. "LC-CHEM-LO-023" for chemistry, "LC-MATH-LO-001" for maths)
    - `title`: the topic title (verbatim from the syllabus)
    - `learning_outcomes`: array of {code, text, blooms_level (remember|understand|apply|analyse|evaluate|create)}

    Also extract:
    - `strands`: array of {name, topics} — the major syllabus strands
    - `assessment_objectives`: array of the AO codes + descriptions
    - `key_competencies`: array of the 5 NCCA Key Competencies (Information Processing, Communicating, Working with Others, Personal Effectiveness, Critical & Creative Thinking)

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - Topics follow the 4 chemistry strands: Atomic Structure, Chemical Bonding, Stoichiometry, etc.
    - LO codes use prefix "LC-CHEM-LO-NNN"
    {% elif subject == "mathematics" %}
    - Topics are organised by the 5 syllabus strands (Statistics & Probability, Geometry & Trigonometry, Number, Algebra, Functions)
    - LO codes use prefix "LC-MATH-LO-NNN"
    - Capture all formula references as a separate `formulas` array
    {% elif subject == "geography" %}
    - Topics span Physical Geography, Regional Geography, Human Environment
    - LO codes use prefix "LC-GEOG-LO-NNN"
    {% elif subject == "english" %}
    - Capture the prescribed texts (poetry, prose, drama) under `prescribed_texts`
    - LO codes use prefix "LC-ENGL-LO-NNN"
    {% elif subject == "gaeilge" %}
    - Capture the prescribed texts under `prescribed_texts` (Irish-language titles)
    - LO codes use prefix "LC-GAEL-LO-NNN"
    {% elif subject == "computer_science" %}
    - Topics span Algorithms, Data, Networks, Programming, Systems
    - LO codes use prefix "LC-COMP-LO-NNN"
    {% elif subject == "applied_mathematics" %}
    - Topics: Statistics, Mechanics, Dynamics, Probability
    - LO codes use prefix "LC-APM-LO-NNN"
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ text }}
  "#
}

function ExtractExamPaperLayout(text: string, subject: string) -> ExamPaperLayout {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Leaving Certificate exam paper layout extractor for `{{ subject }}`.

    Extract from the exam paper text:
    - `exam_year`: 4-digit year (e.g. 2024)
    - `exam_level`: "Higher" | "Ordinary" | "Foundation"
    - `paper_number`: 1 | 2 | 3
    - `total_marks`: integer
    - `sections`: array of {label, marks, questions: [{question_number, marks, instruction, sub_questions: [{label, marks}]}]}
    - `duration_minutes`: integer (typically 180 or 240)
    - `examiner_notes`: array of strings

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - 3 sections typically: Section A (short Qs), Section B (experimental), Section C (long Qs)
    {% elif subject == "mathematics" %}
    - 2 papers: Paper 1 (calculators allowed, 150 marks), Paper 2 (same)
    - Each paper has Section A + Section B
    {% elif subject == "english" %}
    - 2 papers: Paper 1 (comprehension + composition), Paper 2 (single text study)
    - Section I + Section II in each
    {% endif %}

    {{ ctx.output_format }}

    EXAM PAPER TEXT:
    {{ text }}
  "#
}

function ExtractMarkingSchemeGuideline(text: string, subject: string) -> MarkingSchemeGuideline {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Leaving Certificate marking scheme extractor for `{{ subject }}`.

    Extract from the marking scheme text:
    - `exam_year`: 4-digit year
    - `marking_instructions`: array of {section, general_notes, common_mistakes}
    - `grade_boundaries`: array of {grade, percentage_lower_bound}
    - `question_specific_schemes`: array of {question_number, parts: [{label, scheme: string, marks: integer}]}
    - `distribution_of_marks`: dict of {cognitive_level, percentage}

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - Grade boundaries are typically 90/80/70/60/50/40/30 for H1-H7/O1-O8
    - Section A usually has 10 questions × 10 marks
    {% elif subject == "mathematics" %}
    - 2 papers, each 150 marks
    - Grade boundaries include F1-F3 (failures) below 30%
    {% elif subject == "english" %}
    - Grading is more qualitative for composition (60-70% on ideas + structure)
    - Comprehension is quantitative
    {% endif %}

    {{ ctx.output_format }}

    MARKING SCHEME TEXT:
    {{ text }}
  "#
}

function ExtractSyllabusDiagram(text: string, subject: string) -> SyllabusDiagram {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting diagrams from `{{ subject }}` Leaving Certificate syllabi.

    Extract from the syllabus text:
    - `figure_id`: identifier (e.g. "Figure 1.2" or "Diagram 2.3")
    - `caption`: the figure's caption/description
    - `diagram_type`: "molecular_structure" | "circuit" | "graph" | "process_flow" | "anatomical" | "geological_cross_section" | "other"
    - `associated_topic_code`: the NCCA LO code the diagram supports
    - `complexity`: "simple" | "moderate" | "complex"

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - Most diagrams are molecular structures or reaction mechanisms
    {% elif subject == "geography" %}
    - Diagrams are typically geological cross-sections, climate graphs, or population pyramids
    {% elif subject == "computer_science" %}
    - Diagrams are flowcharts, network topologies, or sorting algorithm visualisations
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ text }}
  "#
}

function ExtractCrossLinguisticConcept(en_text: string, ga_text: string) -> CrossLinguisticConcept {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert bilingual (English ↔ Irish) curriculum concept matcher.

    Given parallel English + Irish syllabus text, extract:
    - `en_concept`: {term, definition, ncca_lo_code}
    - `ga_concept`: {term, definition, ncca_lo_code}
    - `equivalence_score`: 0.0-1.0 (how well the concepts match across languages)
    - `cultural_notes`: any cultural context that differs between EN and GA treatments

    Example:
    {
      "en_concept": {"term": "Atomic Structure", "definition": "Composition of atoms", "ncca_lo_code": "LC-CHEM-LO-001"},
      "ga_concept": {"term": "Struchtúr Adamhach", "definition": "Comhdhéanamh adaimh", "ncca_lo_code": "LC-CEIM-LO-001"},
      "equivalence_score": 0.92,
      "cultural_notes": "GA term uses the older spelling 'Struchtúr' vs modern 'Struchtúr'"
    }

    {{ ctx.output_format }}

    ENGLISH TEXT:
    {{ en_text }}

    IRISH TEXT:
    {{ ga_text }}
  "#
}

function ExtractBilingualLearningOutcome(en_text: string, ga_text: string) -> BilingualLearningOutcome {
  client GaeilgeLCClient
  prompt #"
    {{ _.role("user") }}
    You are an expert bilingual (English ↔ Irish) Leaving Certificate LO pair extractor.

    Given parallel English + Irish syllabus text, extract paired LOs:
    - `en_lo_id`: English NCCA LO code (e.g. "LC-CHEM-LO-023")
    - `ga_lo_id`: Irish NCCA LO code (e.g. "LC-CEIM-LO-023")
    - `confidence`: 0.0-1.0 (pairing confidence)
    - `source_pairs`: array of {en_segment, ga_segment} — matching text segments

    Note: The Irish LO code uses different prefix (CEIM for Chemistry, MATA for Maths, TÍR for Geography, etc.)

    {{ ctx.output_format }}

    ENGLISH TEXT:
    {{ en_text }}

    IRISH TEXT:
    {{ ga_text }}
  "#
}

function ExtractCrossLinguisticGA(ga_text: string) -> CrossLinguisticConcept {
  client GaeilgeLCClient
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured concepts from Irish-language syllabus text.

    Given the GA text below, extract:
    - `ga_concept`: {term, definition, ncca_lo_code}
    - `related_en_terms`: array of English equivalents (if identifiable)

    Example:
    {
      "ga_concept": {"term": "Cothromaíocht Cheimiceach", "definition": "Staid ina bhfuil rátaí na frithghníomhanna ar aghaidh agus ar gcúl comhionann", "ncca_lo_code": "LC-CEIM-LO-045"},
      "related_en_terms": ["Chemical Equilibrium"]
    }

    {{ ctx.output_format }}

    IRISH TEXT:
    {{ ga_text }}
  "#
}

class CurriculumSyllabus {
  subject string
  topics SyllabusTopic[]
  strands Strand[]
  assessment_objectives AssessmentObjective[]
  key_competencies string[]
}

class SyllabusTopic {
  code string
  title string
  learning_outcomes LearningOutcome[]
}

class LearningOutcome {
  code string
  text string
  blooms_level string
}

class Strand {
  name string
  topics SyllabusTopic[]
}

class AssessmentObjective {
  code string
  description string
}

class ExamPaperLayout {
  exam_year int
  exam_level string
  paper_number int
  total_marks int
  duration_minutes int
  sections ExamSection[]
  examiner_notes string[]
}

class ExamSection {
  label string
  marks int
  questions ExamQuestion[]
}

class ExamQuestion {
  question_number int
  marks int
  instruction string
  sub_questions ExamSubQuestion[]
}

class ExamSubQuestion {
  label string
  marks int
}

class MarkingSchemeGuideline {
  exam_year int
  marking_instructions MarkingInstruction[]
  grade_boundaries GradeBoundary[]
  question_specific_schemes QuestionScheme[]
  distribution_of_marks map<string, int>
}

class MarkingInstruction {
  section string
  general_notes string
  common_mistakes string[]
}

class GradeBoundary {
  grade string
  percentage_lower_bound float
}

class QuestionScheme {
  question_number int
  parts QuestionPartScheme[]
}

class QuestionPartScheme {
  label string
  scheme string
  marks int
}

class SyllabusDiagram {
  figure_id string
  caption string
  diagram_type string
  associated_topic_code string
  complexity string
}

class CrossLinguisticConcept {
  en_concept BilingualConceptRef?
  ga_concept BilingualConceptRef?
  equivalence_score float
  cultural_notes string?
}

class BilingualConceptRef {
  term string
  definition string
  ncca_lo_code string
}

class BilingualLearningOutcome {
  en_lo_id string
  ga_lo_id string
  confidence float
  source_pairs BilingualSourcePair[]
}

class BilingualSourcePair {
  en_segment string
  ga_segment string
}
