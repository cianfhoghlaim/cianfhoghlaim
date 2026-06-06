// =============================================================================
// Aistear (Early Childhood, ages 0-6) — BAML Schema
// Bilingual EN/GA extraction of the Irish Aistear framework.
// See: docs/meaisínfhoghlaim/celtic/Celtic Data Scraping and Integration Plan.md
//      docs/bonneagar/education-subject-inventory.md (14 Aistear source PDFs)
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum AistearTheme {
  WELL_BEING
    @description("Biú Folláine — emotional resilience, mental health, physical health")
  IDENTITY_BELONGING
    @description("Céannacht agus Muintearas — sense of self, family, community, cultural identity")
  COMMUNICATING
    @description("Cumarsáid — verbal/non-verbal expression, language, listening, responding")
  EXPLORING_THINKING
    @description("Taiscéalaíocht agus Smaointeoireacht — curiosity, investigation, problem-solving, making meaning")
}

enum AistearAgeBand {
  INFANTS                 @description("0-18 months")
  TODDLERS                @description("1-3 years")
  PRE_SCHOOL              @description("3-5 years")
  EARLY_PRIMARY_BRIDGE    @description("5-6 years (transition into Primary Stage 1)")
}

enum AistearLanguageMedium {
  IRISH_MEDIUM    @description("Gaeltacht or Irish-medium pre-school (naíonra lán-Ghaeilge)")
  ENGLISH_MEDIUM  @description("English-medium pre-school")
  BILINGUAL       @description("Bilingual pre-school (Irish + English)")
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class AistearPrinciple {
  name_en string        @description("e.g., 'Building partnerships with parents'")
  name_ga string?       @description("e.g., 'Comhpháirtíocht le tuismitheoirí'")
  description_en string
  description_ga string?
  age_band AistearAgeBand
  theme AistearTheme
  examples_en string[]  @description("Concrete practice examples in English")
  examples_ga string?   @description("Concrete practice examples in Irish (newline-separated)")
}

class AistearLearningGoal {
  id string                       @description("Unique code, e.g., 'AISTEAR-WB-INF-1'")
  theme AistearTheme
  age_band AistearAgeBand
  text_en string                  @description("The full learning goal text in English")
  text_ga string?                 @description("The full learning goal text in Irish")
  sample_practice_en string?      @description("Concrete practice example, e.g., 'circle time', 'free play', 'sensory tray'")
  sample_practice_ga string?      @description("Irish-language practice example")
  parent_tip_en string?           @description("Actionable parenting advice in English")
  parent_tip_ga string?           @description("Actionable parenting advice in Irish")
  linked_primary_outcome string? @description("Primary Stage 1 outcome code if bridged, e.g., 'LO-PRI-EN-1.1'")
}

class GeoPoint {
  lat float @description("Latitude")
  lon float @description("Longitude")
}

class Naionra {
  id string
  name_en string
  name_ga string
  county string
  eircode string?
  language_medium AistearLanguageMedium
  age_range_months int[]         @description("e.g., [24, 36, 48, 60] for ages 2-5")
  enrollment int?
  source_url string
  geo GeoPoint
}

class AistearDocument {
  document_id string
  title_en string
  title_ga string?
  source_url string
  age_band AistearAgeBand
  themes AistearTheme[]
  principles AistearPrinciple[]
  learning_goals AistearLearningGoal[]
  extracted_at string             @description("ISO 8601 timestamp")
  language string                 @description("en | ga | bilingual")
}

class BridgeEdge {
  aistear_id string             @description("AISTEAR-*-*-*")
  primary_id string             @description("LO-PRI-*-*-*")
  strength float                @description("0.0-1.0 confidence")
  rationale_en string
  rationale_ga string?
}

// -----------------------------------------------------------------------------
// Functions
// -----------------------------------------------------------------------------

function ExtractAistearFramework(text: string, language: string) -> AistearDocument {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish early-childhood (Aistear) curriculum analyst.

    Extract the Aistear framework structure. Aistear is qualitative; preserve nuance.
    CRITICAL: Always extract BOTH English and Irish versions of every field.
    If the source text is in one language, translate the other.
    Preserve the 4 Aistear themes: Well-being, Identity & Belonging, Communicating, Exploring & Thinking.
    Preserve the 4 age bands: Infants, Toddlers, Pre-school, Early-Primary Bridge.

    LANGUAGE: {{ language }}

    DOCUMENT TEXT:
    {{ text }}

    Return the structured AistearDocument as {{ ctx.output_format }}.
  "#
}

function ExtractNaionraListing(page_markdown: string) -> Naionra[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an Irish pre-school directory parser.

    Extract every naíonra (Irish-medium pre-school) listing from the page markdown.
    For each, capture the name (Irish + English where given), county, eircode,
    language medium (Irish / English / Bilingual), age range, and source URL.
    Geocode is null (filled in by a downstream spatial pass).

    PAGE MARKDOWN:
    {{ page_markdown }}

    Return the Naionra[] as {{ ctx.output_format }}.
  "#
}

function BridgeAistearToPrimary(aistear_doc: AistearDocument, primary_doc: PrimaryCurriculumArea) -> BridgeEdge[] {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an Irish early-childhood / primary curriculum analyst.

    Find the strongest conceptual bridges between the Aistear learning goals (early childhood)
    and the Primary Curriculum learning outcomes (Stage 1: Junior/Senior Infants, ages 4-6).

    AISTEAR DOCUMENT:
    Themes: {{ aistear_doc.themes }}
    Learning Goals:
    {% for g in aistear_doc.learning_goals %}
    - {{ g.id }}: {{ g.text_en }}
    {% endfor %}

    PRIMARY DOCUMENT:
    Area: {{ primary_doc.name }}
    Strands:
    {% for s in primary_doc.strands %}
    - Strand: {{ s.name }}
    {% for o in s.outcomes %}
      - Outcome: {{ o.id }}: {{ o.text_en }}
    {% endfor %}
    {% endfor %}

    Return BridgeEdge[] as {{ ctx.output_format }}.
    Only include bridges with strength >= 0.5.
  "#
}
