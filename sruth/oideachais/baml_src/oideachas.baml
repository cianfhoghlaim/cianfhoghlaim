// education.baml
// BAML schemas for extracting structured data from educational content

// ============================================================================
// CURRICULUM SPECIFICATION EXTRACTION
// ============================================================================

enum SubjectArea {
  Languages @description("Irish, English, Modern Languages")
  Mathematics @description("Mathematics, Applied Mathematics")
  Science @description("Physics, Chemistry, Biology, Agricultural Science")
  SocialStudies @description("History, Geography, Politics")
  Arts @description("Music, Art, Drama")
  Technology @description("Engineering, Technology, Computer Science")
  Business @description("Business, Economics, Accounting")
  HealthPE @description("Physical Education, SPHE, Home Economics")
  Religious @description("Religious Education, Ethics")
}

enum AssessmentType {
  WrittenExam @description("Traditional written examination")
  Practical @description("Practical/laboratory assessment")
  Oral @description("Oral examination or aural test")
  Project @description("Extended project or portfolio")
  Continuous @description("Continuous assessment throughout year")
  Coursework @description("Assessed coursework component")
}

class LearningOutcome {
  id string?                      // e.g., "LO1.2.3"
  description string
  strand string?                  // Curriculum strand
  strand_unit string?             // Sub-strand
  skills string[]                 // Associated skills
  knowledge_areas string[]        // Content areas
  is_core bool                    // Core vs optional
}

class AssessmentComponent {
  name string
  type AssessmentType
  weight_percentage int?
  duration_minutes int?
  description string?
}

class SyllabusExtraction {
  subject_name string
  subject_code string?            // e.g., "L108" for Gaeilge
  level EducationLevel
  area SubjectArea

  rationale string?               // Why this subject matters
  aims string[]
  objectives string[]

  learning_outcomes LearningOutcome[]
  strands string[]                // Major content areas
  strand_units string[]           // Sub-areas

  assessment AssessmentComponent[]
  total_marks int?

  prerequisites string[]
  recommended_hours int?

  language string                 // "en", "ga", "cy", "gd"
  jurisdiction string             // "Ireland", "Scotland", "Wales", "NI"

  source_url string?
  last_updated string?
}

function ExtractSyllabus(content: string, metadata: string) -> SyllabusExtraction {
  client Claude
  prompt #"
    Extract structured syllabus information from this curriculum document.

    Metadata: {{ metadata }}

    Focus on:
    1. Subject identification (name, code, level)
    2. Learning outcomes with strand organization
    3. Assessment structure and weightings
    4. Skills and competencies developed
    5. Content strands and units

    For Irish curriculum:
    - Primary: Senior Infants to 6th Class
    - Junior Cycle: 1st-3rd Year (ages 12-15)
    - Senior Cycle: 5th-6th Year (ages 16-18)

    Document:
    {{ content }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// EXAM PAPER EXTRACTION
// ============================================================================

class ExamQuestion {
  number string                   // "1a", "2(i)", etc.
  marks int?
  topic string?
  difficulty string?              // "basic", "intermediate", "advanced"
  question_text string
  subquestions ExamQuestion[]
}

class ExamSection {
  name string                     // "Section A", "Part 1"
  instructions string?
  total_marks int?
  questions_required int?         // How many to answer
  questions ExamQuestion[]
}

class ExamPaperExtraction {
  subject string
  level string                    // "Higher", "Ordinary", "Foundation"
  year int
  session string                  // "June", "November"

  duration_minutes int?
  total_marks int?

  instructions string[]
  sections ExamSection[]

  topics_covered string[]
  skills_tested string[]

  language string
  source_url string?
}

function ExtractExamPaper(content: string) -> ExamPaperExtraction {
  client Claude
  prompt #"
    Extract structured information from this examination paper.

    Focus on:
    1. Paper identification (subject, level, year)
    2. Structure (sections, questions, marks)
    3. Topics and skills being assessed
    4. Question types and difficulty distribution

    Content:
    {{ content }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// MARKING SCHEME EXTRACTION
// ============================================================================

class MarkingPoint {
  point string                    // The marking point text
  marks int
  alternative bool                // Is this an alternative acceptable answer?
}

class QuestionMarking {
  question_number string
  total_marks int
  marking_points MarkingPoint[]
  notes string?                   // Examiner notes
}

class MarkingSchemeExtraction {
  subject string
  level string
  year int

  general_instructions string[]
  question_markings QuestionMarking[]

  common_errors string[]
  examiner_comments string?
}

function ExtractMarkingScheme(content: string) -> MarkingSchemeExtraction {
  client Claude
  prompt #"
    Extract structured marking scheme information.

    Focus on:
    1. Mark allocation per question/part
    2. Acceptable answers and alternatives
    3. Examiner notes and common errors
    4. Partial credit guidance

    Content:
    {{ content }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// CURRICULUM CONCEPT GRAPH
// ============================================================================

class ConceptNode {
  id string
  name string
  description string?
  subject SubjectArea
  level EducationLevel
  strand string?
}

class ConceptRelation {
  source_id string
  target_id string
  relationship string             // "prerequisite", "extends", "applies_to", "related"
  strength float?                 // 0.0 to 1.0
}

class CurriculumGraph {
  concepts ConceptNode[]
  relations ConceptRelation[]

  subjects_covered string[]
  levels_covered EducationLevel[]

  bottleneck_concepts string[]    // High betweenness centrality
  foundation_concepts string[]    // High out-degree, low in-degree
}

function BuildCurriculumGraph(syllabi: SyllabusExtraction[]) -> CurriculumGraph {
  client Claude
  prompt #"
    Build a concept graph from these curriculum specifications.

    Identify:
    1. Key concepts from each syllabus
    2. Prerequisite relationships between concepts
    3. Cross-subject connections
    4. Bottleneck concepts (many dependencies)
    5. Foundation concepts (many dependents)

    Syllabi:
    {{ syllabi }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// CELTIC LANGUAGE SPECIFIC
// ============================================================================

class CelticLanguageContent {
  language string                 // "ga" (Irish), "cy" (Welsh), "gd" (Scottish Gaelic)
  dialect string?                 // Regional variation
  register string?                // "formal", "informal", "literary", "spoken"

  vocabulary string[]
  grammar_points string[]
  cultural_references string[]

  pronunciation_notes string?
  orthography_notes string?       // Spelling conventions

  cefr_level string?              // A1-C2
  proficiency_descriptors string[]
}

class BilingualResource {
  source_language string
  target_language string

  source_text string
  target_text string

  context string?
  domain string?                  // "education", "legal", "literary"
}

function ExtractCelticLanguageContent(content: string, language: string) -> CelticLanguageContent {
  client Claude
  prompt #"
    Extract Celtic language educational content from this document.

    Target language: {{ language }}

    Focus on:
    1. Vocabulary and terminology (with translations)
    2. Grammar points and structures
    3. Cultural and historical context
    4. Pronunciation and orthography notes
    5. CEFR level mapping if applicable

    For Irish (ga):
    - Note Caighdeán Oifigiúil vs dialect forms
    - Identify Gaeltacht references

    For Welsh (cy):
    - Note literary vs colloquial forms
    - Identify regional variations

    For Scottish Gaelic (gd):
    - Note orthographic conventions
    - Identify dialect markers

    Content:
    {{ content }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// CLIENT CONFIGURATION
// ============================================================================

client<llm> Claude {
  provider anthropic
  options {
    model claude-sonnet-4-20250514
    max_tokens 8192
  }
}

client<llm> ClaudeOpus {
  provider anthropic
  options {
    model claude-opus-4-20250514
    max_tokens 16384
  }
}

// For bilingual content extraction
client<llm> LocalQwen {
  provider openai-generic
  options {
    base_url "http://localhost:8080/v1"
    model "qwen2.5-vl-32b"
    max_tokens 4096
  }
}
