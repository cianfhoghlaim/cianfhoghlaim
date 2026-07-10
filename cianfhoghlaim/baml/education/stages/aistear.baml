// =============================================================================
// Aistear (Early Childhood, ages 0-6) — BAML Schema
// Bilingual EN/GA extraction of the Irish Aistear framework.
// Merged from:
//   - baml/aistear.baml (208 LOC) — the canonical aistear schema
//   - baml/oideachais_other/aistear.baml (31 LOC) — the URL-extraction variant
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
  @@stream.done
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
  @@stream.done
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
  @@stream.done
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

function ExtractAistearFrameworkFromText(text: string,
  language: string) -> AistearDocument {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing the Irish Aistear Framework for early childhood education (ages 0-6).

Parse the Aistear framework document and extract its complete structure.

LANGUAGE: {{ language }}

DOCUMENT TEXT:
{{ text }}

Extract:
1. Framework metadata (title_en, title_ga, year, version, NCCA publication reference, language)
2. All 4 Aistear themes with their English and Irish names:
   - Well-being / Folláine
   - Identity and Belonging / Féiniúlacht agus Cáilíocht
   - Communicating / Cumarsáid
   - Exploring and Thinking / Taiscéalaíocht agus Smaointeoireacht
3. For each theme, learning goals across the 4 age bands:
   - Babies (0-18 months)
   - Toddlers (1.5-3 years)
   - Young Children (3-6 years)
   - Pre-school to Primary Bridge
4. 12 Aistear principles (e.g., "The adult has a key role in supporting learning")
5. Sample learning opportunities for each age band

All content must be BILINGUAL (English and Irish). For each piece of text, provide both en and ga variants when available.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    LANGUAGE: {{ language }}
"#
}


function ExtractNaionraListing(page_markdown: string) -> Naionra[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at parsing listings of Irish-medium early childhood education services (naíonraí).

Parse a directory listing of naíonraí (Irish-medium pre-schools) and extract structured data.

PAGE MARKDOWN:
{{ page_markdown }}

For each naíonra, extract:
1. Name (English and Irish variants where available)
2. Address (street, town, county, Eircode)
3. Contact (phone, email, website)
4. Geo location (latitude, longitude) if present
5. Age range served (typically 0-6)
6. Capacity (number of children)
7. Operating hours / sessional hours
8. Language of instruction (Irish, bilingual, English)
9. Gaeltacht status (in Gaeltacht region or not)
10. AIM (Access and Inclusion Model) supports available
11. ECEC scheme affiliation (ECCE, CCSP, TEC)

This data supports the "Find nearest naíonra" feature in the Aistear team's NaionraFinder agent.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    ENTRIES: {{ page_markdown|length }} chars
"#
}


function BridgeAistearToPrimary(aistear_doc: AistearDocument,
  primary_doc: PrimaryCurriculumArea) -> BridgeEdge[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at identifying bridges between the Aistear early childhood framework and the Primary School curriculum.

Aistear is the curriculum framework for children aged 0-6, while Primary curriculum begins at Junior Infants (age 4-5). Identify how Aistear themes and learning goals support, prepare, or align with the Primary curriculum area.

AISTEAR FRAMEWORK:
{{ aistear_doc.title_en }} ({{ aistear_doc.year }})
Themes: {% for theme in aistear_doc.themes %}- {{ theme.name_en }} / {{ theme.name_ga }}{% endfor %}

PRIMARY CURRICULUM AREA:
{{ primary_doc.name }}
Strands: {% for strand in primary_doc.strands %}- {{ strand.name }}{% endfor %}

For each bridge edge, identify:
- Source: An Aistear learning goal (with age band)
- Target: A Primary curriculum area learning outcome
- Edge type (PREPARES_FOR, ALIGNS_WITH, CONTINUES_FROM, DEVELOPS_INTO)
- Confidence score (0.0-1.0)
- Rationale explaining how the Aistear goal bridges to the Primary outcome
- Bilingual labels for both source and target

These edges power the cross-stage cognify pass and enable "What did my pre-schooler learn in naíonra that prepares them for Primary school?" queries.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    AISTEAR: {{ aistear_doc.title_en }}
    PRIMARY: {{ primary_doc.name }}
"#
}


function ExtractAistearFrameworkFromUrl(source_url: string) -> AistearDocument {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish early-childhood (Aistear) curriculum analyst
    working for Cianfhoghlaim Oideachais (the bilingual agentic platform
    covering Aistear, Primary, Junior Cycle, Senior Cycle, and Tertiary).

    Source: {{ source_url }}

    The 4 Aistear themes are: Well-being, Identity & Belonging, Communicating,
    Exploring & Thinking. The 4 age bands are: Infants (0-18mo), Toddlers
    (1-3yr), Pre-school (3-5yr), Early-Primary Bridge (5-6yr).

    Always extract BOTH English and Irish versions of every field. The Irish
    term for Aistear is "Aistear" (same in both languages). The framework's
    principles of holistic child development are:
      - Building partnerships with parents (Comhpháirtíocht le tuismitheoirí)
      - High-quality early-learning environments
      - Play as a vehicle for learning (an imirt)
      - Aistear in practice — Lá na Sráide, Féach, Aimsigh, Déan, Cabhraigh,
        Smaoinigh, Labhair (the 8 Aistear key messages)

    Return the structured AistearDocument as {{ ctx.output_format }}.
  "#
}


function ExtractAistearFrameworkFromPdf(pdf_text: string) -> AistearFramework {
  client LitellmClient
  prompt #"
    You are an Aistear (Irish early childhood curriculum) expert.

    Extract the 4 Aistear themes, 12 principles, and all learning goals
    from the following Aistear document text.

    The 4 Aistear themes are:
      1. Well-being (Bheith go maith)
      2. Identity and Belonging (Féiniúlacht agus Cairdeas)
      3. Communicating (Cumarsáid)
      4. Exploring and Thinking (Iniúchadh agus Smaointeoireacht)

    Aistear principles include (but are not limited to):
      - Children are capable and confident
      - Children are active learners
      - Children learn through relationships
      - Children learn through play
      - Children learn through meaningful experiences
      - Children's early years lay the foundation for later learning
      - Equality and diversity are rights
      - Parents and families are the primary educators
      - Quality early childhood experiences make a difference
      - Holistic development matters
      - The voice of the child matters
      - Play is a key context for learning

    For each learning goal, return:
      - goal_id: stable ID like 'WB_1', 'IB_2', 'CO_3', 'ET_4'
      - description: full text (often bilingual)
      - theme: one of the 4 themes
      - age_band: BIRTH_TO_3 / 3_TO_4 / 4_TO_5 / 5_TO_6 / ALL

    Document text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// Backward-compat aliases (preserve original call signatures)
// =============================================================================

// Alias for the canonical aistear.baml ExtractAistearFramework(text, language) call
function ExtractAistearFramework(text: string,
  language: string) -> AistearDocument {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"Backward-compat alias for ExtractAistearFrameworkFromText.

    LANGUAGE: {{ language }}

    DOCUMENT TEXT:
    {{ text }}

    {{ ctx.output_format }}
  "#
}

// Alias for the early_childhood.baml ExtractAistearFramework(pdf_text) call
function ExtractAistearFrameworkLegacy(pdf_text: string) -> AistearFramework {
  client LitellmClient
  prompt #"Backward-compat alias for ExtractAistearFrameworkFromPdf.

    Document text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}