// =============================================================================
// Aistear (Early Childhood, ages 0-6) — BAML Schema
// Bilingual EN/GA extraction of the Irish Aistear framework.
// Merged from:
//   - baml/aistear.baml (208 LOC) — the canonical aistear schema
//   - baml/cianfhoghlaim_other/aistear.baml (31 LOC) — the URL-extraction variant
//   - baml/early_childhood.baml (82 LOC) — the simplified early_childhood variant
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

enum AistearDialect {
  MUNSTER    @description("Gaeilge na Mumhan - Kerry, Cork, Waterford")
  CONNACHT   @description("Gaeilge Chonnacht - Galway, Mayo, Roscommon")
  ULSTER     @description("Gaeilge Uladh - Donegal")
  STANDARD   @description("An Caighdeán Oifigiúil - Official Standard")
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

// Simplified version from early_childhood.baml — kept for backward compat
class AistearPrincipleSimple {
  name string @description("Short name of the principle (e.g. 'Children are capable and confident').")
  description string @description("One-paragraph explanation of the principle.")
  age_band string @description("Applicable age band: 'BIRTH_TO_3', '3_TO_4', '4_TO_5', '5_TO_6', or 'ALL'.")
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

// Simplified version from early_childhood.baml — kept for backward compat
class AistearLearningGoalSimple {
  goal_id string @description("Stable ID, e.g. 'WB_1', 'IB_2', 'CO_3', 'ET_4'.")
  description string @description("The full text of the learning goal (often bilingual EN/GA).")
  theme string @description("One of: 'WELL_BEING', 'IDENTITY_BELONGING', 'COMMUNICATING', 'EXPLORING_THINKING'.")
  age_band string @description("Applicable age band: 'BIRTH_TO_3', '3_TO_4', '4_TO_5', '5_TO_6', or 'ALL'.")
}

class AistearFramework {
  themes string[] @description("The 4 Aistear themes in English: 'Well-being', 'Identity and Belonging', 'Communicating', 'Exploring and Thinking'.")
  principles AistearPrincipleSimple[] @description("The 12 Aistear principles extracted from the document.")
  learning_goals AistearLearningGoalSimple[] @description("All learning goals extracted (typically 40-60 per document).")
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
  framework AistearFramework?     @description("The full framework extracted from the document (from early_childhood.baml)")
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

function ExtractAistearFrameworkFromText(
  text: string,
  language: string
) -> AistearDocument {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}


function ExtractNaionraListing(
  page_markdown: string
) -> Naionra[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}


function BridgeAistearToPrimary(
  aistear_doc: AistearDocument,
  primary_doc: PrimaryCurriculumArea
) -> BridgeEdge[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}


function ExtractAistearFrameworkFromUrl(
  source_url: string
) -> AistearDocument {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}


function ExtractAistearFrameworkFromPdf(
  pdf_text: string
) -> AistearFramework {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// =============================================================================
// Backward-compat aliases (preserve original call signatures)
// =============================================================================

// Alias for the canonical aistear.baml ExtractAistearFramework(text, language) call
function ExtractAistearFramework(
  text: string,
  language: string
) -> AistearDocument {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

// Alias for the early_childhood.baml ExtractAistearFramework(pdf_text) call
function ExtractAistearFrameworkLegacy(
  pdf_text: string
) -> AistearFramework {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
