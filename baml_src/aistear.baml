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
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{text}}
"#
}

function ExtractNaionraListing(page_markdown: string) -> Naionra[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{page_markdown}}
"#
}

function BridgeAistearToPrimary(aistear_doc: AistearDocument, primary_doc: PrimaryCurriculumArea) -> BridgeEdge[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Extract the requested data.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    {{aistear_doc}}
"#
}
