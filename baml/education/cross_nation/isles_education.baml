// BAML Schema for Celtic Education Content Extraction
// Supports: Irish (ga), Scottish Gaelic (gd), Welsh (cy), Manx (gv), Cornish (kw), English (en)
//
// Usage: Extract structured data from curriculum documents, exam papers, teaching resources

// =============================================================================
// CORE TYPES
// =============================================================================

// Bilingual/Multilingual text field supporting all Celtic languages
class BilingualTextIsles {
    en string? @description("English text")
    ga string? @description("Irish (Gaeilge) text")
    gd string? @description("Scottish Gaelic (Gàidhlig) text")
    cy string? @description("Welsh (Cymraeg) text")
    gv string? @description("Manx (Gaelg) text")
    kw string? @description("Cornish (Kernewek) text")
}

// Language codes following ISO 639-1
enum LanguageCodeIsles {
    EN @description("English")
    GA @description("Irish / Gaeilge")
    GD @description("Scottish Gaelic / Gàidhlig")
    CY @description("Welsh / Cymraeg")
    GV @description("Manx / Gaelg")
    KW @description("Cornish / Kernewek")
}

// Geographic regions
enum Region {
    IRELAND
    NORTHERN_IRELAND
    SCOTLAND
    WALES
    ISLE_OF_MAN
    CORNWALL
    ENGLAND
}

// =============================================================================
// EDUCATION LEVELS
// =============================================================================

// Education levels across different systems
enum EducationLevelIsles {
    // Ireland
    EARLY_CHILDHOOD @description("Aistear framework, ages 0-6")
    PRIMARY @description("Primary school, ages 4-12")
    JUNIOR_CYCLE @description("Junior Certificate, ages 12-15")
    SENIOR_CYCLE @description("Leaving Certificate, ages 15-18")
    TRANSITION_YEAR @description("Optional year between JC and LC")

    // Scotland
    EARLY_LEVEL @description("P1, ages 3-6")
    FIRST_LEVEL @description("P2-P4, ages 5-9")
    SECOND_LEVEL @description("P5-P7, ages 8-12")
    THIRD_LEVEL @description("S1-S3, ages 11-15")
    FOURTH_LEVEL @description("S4-S6, ages 14-18")
    NATIONAL_3 @description("SQA National 3")
    NATIONAL_4 @description("SQA National 4")
    NATIONAL_5 @description("SQA National 5")
    HIGHER @description("SQA Higher")
    ADVANCED_HIGHER @description("SQA Advanced Higher")

    // Wales
    FOUNDATION_PHASE @description("Ages 3-7")
    KEY_STAGE_2 @description("Ages 7-11")
    KEY_STAGE_3 @description("Ages 11-14")
    KEY_STAGE_4 @description("Ages 14-16, GCSE")
    GCSE @description("General Certificate of Secondary Education")
    AS_LEVEL @description("Advanced Subsidiary")
    A_LEVEL @description("Advanced Level")

    // Generic
    ENTRY_LEVEL @description("Entry level qualification")
    ADULT_LEARNER @description("Adult/continuing education")
}

// =============================================================================
// DOCUMENT TYPES
// =============================================================================

enum DocumentTypeIsles {
    CURRICULUM_SPECIFICATION @description("Official curriculum specification document")
    SYLLABUS @description("SubjectIsles syllabus")
    EXAM_PAPER @description("Past examination paper")
    MARKING_SCHEME @description("Marking scheme for exam")
    CHIEF_EXAMINER_REPORT @description("Examiner's report on exam session")
    TEACHING_RESOURCE @description("Teaching/learning resource")
    ASSESSMENT_GUIDELINES @description("Assessment guidance document")
    POLICY_DOCUMENT @description("Education policy document")
    STATUTORY_GUIDANCE @description("Statutory/legal guidance")
    TERMINOLOGY @description("Terminology database entry")
    TEXTBOOK @description("Textbook or course material")
}

// =============================================================================
// CURRICULUM STRUCTURES
// =============================================================================

class CrossNationLearningOutcomeIsles {
    code string? @description("Learning outcome code (e.g., 'LO 1.1')")
    description BilingualTextIsles @description("Description of what learner should achieve")
    strand string? @description("Curriculum strand or area")
    level EducationLevelIsles? @description("Education level this applies to")
    keywords string[]? @description("Key concepts covered")
}

class AssessmentCriteria {
    component string @description("Assessment component name")
    weight float? @description("Percentage weight (0-100)")
    format string? @description("Format (written, oral, practical, coursework)")
    duration string? @description("Duration of assessment")
    description BilingualTextIsles? @description("Description of assessment")
}

class SubjectIsles {
    name BilingualTextIsles @description("SubjectIsles name in available languages") @stream.not_null
    code string? @description("SubjectIsles code (e.g., 'GAE', 'MAT')")
    levels EducationLevelIsles[] @description("Available levels")
    strands string[]? @description("SubjectIsles strands or units")
    has_oral bool? @description("Has oral/speaking component")
    has_practical bool? @description("Has practical component")
    oral_weight float? @description("Oral component percentage")
}

// Main curriculum specification schema
class CurriculumSpecIsles {
    title BilingualTextIsles @description("Document title") @stream.not_null
    subject SubjectIsles @description("SubjectIsles information")
    region Region @description("Geographic region")
    education_system string? @description("Education system (e.g., 'Curriculum for Excellence')")
    level EducationLevelIsles @description("Education level")
    version string? @description("Specification version")
    effective_date string? @description("Date specification becomes effective")

    rationale BilingualTextIsles? @description("Rationale/aims of the specification")
    outcomes CrossNationLearningOutcomeIsles[] @description("Learning outcomes")
    assessment AssessmentCriteria[]? @description("Assessment information")

    cross_curricular_links string[]? @description("Links to other subjects")
    resources_required string[]? @description("Required resources/equipment")

    source_url string @description("Source URL of document")
    source_org string @description("Source organization")
  @@stream.done
}

// =============================================================================
// EXAM PAPER STRUCTURES
// =============================================================================

class ExamQuestionIsles {
    number string @description("Question number")
    marks int @description("Marks allocated")
    text BilingualTextIsles @description("Question text")
    parts ExamQuestionIsles[]? @description("Sub-parts of question")
    topic string? @description("Topic/strand being assessed")
    skill_type string? @description("Skill type (knowledge, comprehension, application, analysis)")
}

class ExamPaperIsles {
    title BilingualTextIsles @description("Paper title")
    subject SubjectIsles @description("SubjectIsles") @stream.not_null
    level EducationLevelIsles @description("Level")
    year int @description("Exam year")
    session string? @description("Exam session (e.g., 'Summer', 'Winter')")
    duration string @description("Paper duration")
    total_marks int @description("Total marks available")

    sections ExamSectionIsles[]? @description("Paper sections") @stream.with_state
    questions ExamQuestionIsles[] @description("Questions")

    instructions BilingualTextIsles? @description("Instructions to candidates")
    materials_required string[]? @description("Required materials")

    source_url string @description("Source URL")
    source_org string @description("Source organization")
  @@stream.done
}

class ExamSectionIsles {
    name BilingualTextIsles @description("Section name")
    instructions BilingualTextIsles? @description("Section instructions")
    marks int @description("Marks for section")
    questions_required int? @description("Number of questions to answer")
}

// =============================================================================
// TERMINOLOGY
// =============================================================================

class TermEntry {
    term BilingualTextIsles @description("The term in available languages")
    definition BilingualTextIsles? @description("Definition")
    domain string @description("SubjectIsles domain (e.g., 'Mathematics', 'Science')")
    context string? @description("Usage context")
    related_terms string[]? @description("Related terms")
    source string? @description("Source of term")
  @@stream.done
}

// =============================================================================
// TEACHING RESOURCE
// =============================================================================

class TeachingResource {
    title BilingualTextIsles @description("Resource title")
    description BilingualTextIsles? @description("Resource description")
    resource_type string @description("Type (worksheet, lesson plan, video, etc.)")
    subject SubjectIsles? @description("SubjectIsles")
    level EducationLevelIsles[]? @description("Applicable levels")

    learning_outcomes CrossNationLearningOutcomeIsles[]? @description("Learning outcomes addressed")
    duration string? @description("Estimated time to complete")

    file_url string? @description("URL to resource file")
    file_format string? @description("File format (PDF, DOCX, etc.)")

    source_url string @description("Source URL")
    source_org string @description("Source organization")
    license string? @description("License/copyright")
  @@stream.done
}

// =============================================================================
// EXTRACTION FUNCTIONS
// =============================================================================

function ExtractCurriculumSpec(document: string) -> CurriculumSpecIsles {
    client Claude
    prompt #"
        Extract structured curriculum specification data from the following document.
        Preserve text in its original language(s) - do not translate.

        Document:
        {{ document }}

        {{ ctx.output_format }}
    "#
}

function ExtractExamPaper(document: string) -> ExamPaperIsles {
    client Claude
    prompt #"
        Extract structured exam paper data from the following document.
        Include all questions with their marks and any sub-parts.
        Preserve text in its original language(s).

        Document:
        {{ document }}

        {{ ctx.output_format }}
    "#
}

function ExtractTerminology(document: string) -> TermEntry[] {
    client Claude
    prompt #"
        Extract terminology entries from the following document.
        Include terms in all available languages.

        Document:
        {{ document }}

        {{ ctx.output_format }}
    "#
}

function ExtractTeachingResource(document: string) -> TeachingResource {
    client Claude
    prompt #"
        Extract teaching resource metadata from the following document.
        Preserve text in its original language(s).

        Document:
        {{ document }}

        {{ ctx.output_format }}
    "#
}

function DetectDocumentType(document: string) -> DocumentTypeIsles {
    client ClaudeMini
    prompt #"
        Classify the following education document into one of these types:
        - CURRICULUM_SPECIFICATION
        - SYLLABUS
        - EXAM_PAPER
        - MARKING_SCHEME
        - CHIEF_EXAMINER_REPORT
        - TEACHING_RESOURCE
        - ASSESSMENT_GUIDELINES
        - POLICY_DOCUMENT
        - STATUTORY_GUIDANCE
        - TERMINOLOGY
        - TEXTBOOK

        Document excerpt:
        {{ document[:2000] }}

        {{ ctx.output_format }}
    "#
}

function DetectLanguages(text: string) -> LanguageCodeIsles[] {
    client ClaudeMini
    prompt #"
        Detect which languages are present in the following text.
        Return all languages found, not just the primary one.

        Text:
        {{ text[:1000] }}

        {{ ctx.output_format }}
    "#
}

// =============================================================================
// TEST CASES
// =============================================================================

test ExtractIrishSpec {
    functions [ExtractCurriculumSpec]
    args {
        document #"
            Sonraíocht Churaclaim
            Gaeilge - Ardteistiméireacht

            Cuspóirí:
            - Scileanna cumarsáide a fhorbairt
            - Tuiscint ar litríocht na Gaeilge

            Measúnú:
            - Páipéar 1: 40%
            - Páipéar 2: 20%
            - Scrúdú Béil: 40%
        "#
    }
}

test ExtractWelshSpec {
    functions [ExtractCurriculumSpec]
    args {
        document #"
            Manyleb TGAU Cymraeg

            Amcanion:
            - Datblygu sgiliau cyfathrebu
            - Deall llenyddiaeth Gymraeg

            Asesiad:
            - Uned 1: Llafar 25%
            - Uned 2: Darllen 25%
            - Uned 3: Ysgrifennu 50%
        "#
    }
}
