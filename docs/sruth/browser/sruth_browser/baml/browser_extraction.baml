// BAML Schema for Browser Extraction
// Type-safe extraction schemas for web content
//
// Usage: Validate and extract structured data from web pages

// =============================================================================
// WEB PAGE STRUCTURES
// =============================================================================

// Generic extracted content from a web page
class WebPageContent {
    url string @description("Source URL of the page")
    title string @description("Page title")
    description string? @description("Meta description or summary")
    main_content string @description("Primary text content")
    author string? @description("Content author if available")
    published_date string? @description("Publication date if available")
    modified_date string? @description("Last modified date if available")
    language string? @description("Content language code (e.g., 'en', 'ga')")
}

// Navigation element on a page
class NavigationLink {
    text string @description("Link text")
    href string @description("Link URL")
    is_internal bool @description("Whether link is internal to the site")
    category string? @description("Navigation category (header, footer, sidebar)")
}

// Site structure from mapping
class SiteStructure {
    root_url string @description("Root URL of the site")
    pages NavigationLink[] @description("Discovered pages")
    sitemap_url string? @description("URL to sitemap.xml if found")
    robots_txt string? @description("Contents of robots.txt if found")
    total_pages int @description("Total pages discovered")
}

// =============================================================================
// IRISH EDUCATION SPECIFIC
// =============================================================================

// Curriculum document from curriculumonline.ie or similar
class CurriculumDocument {
    title string @description("Document title in original language")
    title_english string? @description("English translation of title")
    subject string @description("Subject name")
    level string @description("Education level (Primary, Junior Cycle, Senior Cycle)")

    key_skills string[]? @description("Key skills addressed")
    learning_outcomes string[]? @description("Learning outcomes or objectives")

    strands string[]? @description("Curriculum strands or units")
    strand_elements string[]? @description("Elements within strands")

    assessment_modes string[]? @description("Assessment methods")
    resources string[]? @description("Recommended resources")

    source_url string @description("Source URL")
    source_organization string @description("Publishing organization (NCCA, SEC, etc.)")
}

// Exam paper metadata from examinations.ie
class ExamPaperMeta {
    title string @description("Paper title")
    subject string @description("Subject name")
    level string @description("Level (Higher, Ordinary, Foundation)")
    year int @description("Exam year")

    paper_number int? @description("Paper number (1, 2, etc.)")
    duration_minutes int? @description("Exam duration in minutes")
    total_marks int? @description("Total marks available")

    sections ExamSection[]? @description("Paper sections")

    pdf_url string? @description("URL to PDF file")
    marking_scheme_url string? @description("URL to marking scheme")
    source_url string @description("Source page URL")
}

class ExamSection {
    name string @description("Section name or number")
    marks int @description("Marks for section")
    question_count int? @description("Number of questions")
    instructions string? @description("Section instructions")
}

// Circular from Department of Education
class EducationCircular {
    circular_number string @description("Circular reference number")
    title string @description("Circular title")
    date_issued string @description("Date issued")

    applies_to string[]? @description("Who it applies to (teachers, schools, etc.)")
    subject_areas string[]? @description("Subject areas affected")

    summary string? @description("Brief summary")
    key_points string[]? @description("Key points from the circular")

    pdf_url string? @description("URL to PDF")
    source_url string @description("Source page URL")
}

// =============================================================================
// RESEARCH AND KNOWLEDGE
// =============================================================================

// Research finding from deep research
class ResearchFinding {
    topic string @description("Research topic")
    summary string @description("Summary of findings")

    key_facts string[] @description("Key factual findings")
    sources ResearchSource[] @description("Sources consulted")

    confidence_score float @description("Confidence in findings (0-1)")
    gaps string[]? @description("Identified knowledge gaps")
}

class ResearchSource {
    title string @description("Source title")
    url string @description("Source URL")
    domain string @description("Source domain")
    relevance_score float @description("Relevance to topic (0-1)")
    excerpt string? @description("Relevant excerpt from source")
}

// Knowledge base entry for site memory
class SiteKnowledge {
    domain string @description("Website domain")
    last_visited string @description("Last visit timestamp")

    navigation_patterns NavigationPattern[]? @description("Known navigation patterns")
    form_patterns FormPattern[]? @description("Known form patterns")
    selector_cache SelectorCache[]? @description("Cached CSS selectors")

    access_issues string[]? @description("Known access issues (captcha, login, etc.)")
    optimal_backend string? @description("Best backend for this site")
}

class NavigationPattern {
    name string @description("Pattern name")
    description string @description("Pattern description")
    steps string[] @description("Navigation steps")
}

class FormPattern {
    form_name string @description("Form identifier or name")
    fields FormField[] @description("Form fields")
    submit_selector string? @description("Submit button selector")
}

class FormField {
    label string @description("Field label")
    selector string @description("CSS selector")
    field_type string @description("Field type (text, select, checkbox, etc.)")
    required bool @description("Whether field is required")
}

class SelectorCache {
    description string @description("What the selector targets")
    selector string @description("CSS selector")
    verified_date string @description("When selector was last verified")
    success_rate float @description("Historical success rate")
}

// =============================================================================
// EXTRACTION FUNCTIONS
// =============================================================================

function ExtractWebPage(html: string) -> WebPageContent {
    client "openai/gpt-4o"
    prompt #"
        Extract structured content from this web page HTML.
        Focus on the main content, ignoring navigation and ads.

        HTML:
        {{ html[:10000] }}

        {{ ctx.output_format }}
    "#
}

function ExtractCurriculumDocument(content: string, url: string) -> CurriculumDocument {
    client "openai/gpt-4o"
    prompt #"
        Extract curriculum document information from this content.
        This is from an Irish education website.
        Preserve Irish language text where present.

        Source URL: {{ url }}

        Content:
        {{ content }}

        {{ ctx.output_format }}
    "#
}

function ExtractExamPaper(content: string, url: string) -> ExamPaperMeta {
    client "openai/gpt-4o"
    prompt #"
        Extract exam paper metadata from this content.
        This is from the Irish State Examinations Commission (SEC).

        Source URL: {{ url }}

        Content:
        {{ content }}

        {{ ctx.output_format }}
    "#
}

function ExtractSiteStructure(links: string) -> SiteStructure {
    client "openai/gpt-4o-mini"
    prompt #"
        Analyze these links to understand the site structure.
        Categorize links and identify the site hierarchy.

        Links:
        {{ links }}

        {{ ctx.output_format }}
    "#
}

function SynthesizeResearch(sources: string, topic: string) -> ResearchFinding {
    client "openai/gpt-4o"
    prompt #"
        Synthesize research findings from multiple sources on this topic.

        Topic: {{ topic }}

        Sources and content:
        {{ sources }}

        Provide a comprehensive summary with key facts and source attribution.

        {{ ctx.output_format }}
    "#
}

// =============================================================================
// TESTS
// =============================================================================

test ExtractCurriculumTest {
    functions [ExtractCurriculumDocument]
    args {
        content #"
            Gaeilge - Senior Cycle

            Curriculum Specification

            Key Skills:
            - Communicating
            - Managing information and thinking
            - Being creative

            Learning Outcomes:
            - Students will be able to communicate effectively in Irish
            - Students will develop an appreciation for Irish literature

            Strands:
            - Teanga
            - Litríocht
        "#
        url "https://curriculumonline.ie/Senior-cycle/Languages/Gaeilge"
    }
}

test ExtractExamTest {
    functions [ExtractExamPaper]
    args {
        content #"
            Leaving Certificate Examination 2023
            Irish - Higher Level - Paper 1

            Duration: 2 hours 30 minutes
            Total Marks: 200

            Section A: Cluastuiscint (Listening) - 60 marks
            Section B: Ceapadóireacht (Composition) - 60 marks
            Section C: Próis (Prose) - 40 marks
            Section D: Filíocht (Poetry) - 40 marks
        "#
        url "https://examinations.ie/papers/2023/LC/Irish/Higher/Paper1.pdf"
    }
}
