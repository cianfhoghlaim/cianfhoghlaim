// Named Entity Recognition - Celtic Folklore and Place Names
// Extract people, places, supernatural beings from Celtic texts
// December 2024

// ============================================================================
// ENTITY TYPES
// ============================================================================

// Types of named entities in Celtic folklore
enum CelticEntityType {
  PERSON @alias("Person - Historical figure, collector, informant")
  PLACE @alias("Place - Townland, parish, county, geographic feature")
  SUPERNATURAL @alias("Supernatural - Fairies, ghosts, spirits")
  FESTIVAL @alias("Festival - Calendar customs, holy days")
  ARTIFACT @alias("Artifact - Holy wells, fairy forts, standing stones")
  CREATURE @alias("Creature - Mythical animals, sea monsters")
  DEITY @alias("Deity - Celtic gods, saints")
  CLAN @alias("Clan/Family - Surnames, clans, septs")
}

// Supernatural being subcategories
enum SupernaturalType {
  SI @alias("Sí / Aos Sí - The fairy folk")
  BANSHEE @alias("Bean Sí - Banshee, death messenger")
  POOKA @alias("Púca - Shape-shifting spirit")
  LEPRECHAUN @alias("Leipreachán - Fairy cobbler")
  CHANGELING @alias("Iarlais / Plentyn Newid - Changeling")
  GHOST @alias("Taibhse / Ysbryd - Ghost")
  WATER_SPIRIT @alias("Each Uisce / Kelpie - Water horse")
  MERROW @alias("Murúch - Mermaid/merman")
  DULLAHAN @alias("Dúlachán - Headless rider")
  FEAR_GORTA @alias("Fear Gorta - Famine ghost")
}

// Confidence in entity extraction
enum EntityConfidence {
  HIGH @alias("High confidence - explicit naming")
  MEDIUM @alias("Medium confidence - contextual")
  LOW @alias("Low confidence - inferred")
}

// ============================================================================
// ENTITY CLASSES
// ============================================================================

// A named entity from Celtic text
class CelticNamedEntity {
  text string @description("Entity as it appears in text")
  entity_type CelticEntityType @description("Type of entity")
  normalized_form string? @description("Standardized form")
  irish_form string? @description("Irish language form")
  english_form string? @description("English translation/form")
  confidence EntityConfidence @description("Extraction confidence")
}

// Person entity with role
class PersonEntity {
  name string @description("Person's name")
  name_ga string? @description("Name in Irish")
  role string? @description("Role: collector, informant, teacher, storyteller")
  gender string? @description("Gender if known")
  birth_year int? @description("Birth year if known")
  death_year int? @description("Death year if known")
  location string? @description("Associated location")
  occupation string? @description("Occupation if known")
}

// Place entity with Logainm linkage
class PlaceEntity {
  name string @description("Place name as written")
  name_ga string? @description("Irish form")
  name_en string? @description("English form")
  place_type string? @description("Type: townland, parish, county, etc.")
  county string? @description("County if applicable")
  province string? @description("Province")
  logainm_id int? @description("Logainm.ie ID for linking")
  latitude float? @description("Latitude if known")
  longitude float? @description("Longitude if known")
}

// Supernatural entity with folklore context
class SupernaturalEntity {
  name string @description("Entity name or type")
  name_ga string? @description("Irish name")
  supernatural_type SupernaturalType @description("Category of supernatural being")
  appearance string? @description("How it appears")
  behavior string? @description("What it does")
  associated_location string? @description("Where it appears")
  protection string? @description("How to protect against it")
  summoning string? @description("How to summon or attract it")
}

// Festival/calendar custom entity
class FestivalEntity {
  name string @description("Festival name")
  name_ga string @description("Irish name")
  date string @description("When it occurs")
  customs string? @description("Associated customs")
  foods string? @description("Associated foods")
  beliefs string? @description("Associated beliefs")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Extract all named entities from Celtic text
function ExtractCelticEntities(
  text string @description("Celtic folklore or historical text"),
  language CelticLanguage @description("Language of the text")
) -> CelticNamedEntity[] {
  client Claude
  prompt #"
    Extract all named entities from this {{ language }} text.

    Text: {{ text }}

    Look for:
    1. PERSON: Names of people, collectors, storytellers, historical figures
    2. PLACE: Townlands, parishes, counties, geographic features
       - Include both Irish and English forms
       - Note: Irish placenames often start with Baile, Cill, Ard, Cnoc, etc.
    3. SUPERNATURAL: Fairies (sí, sióg), ghosts (taibhse), spirits
       - Bean sí, púca, leipreachán, etc.
    4. FESTIVAL: Calendar customs - Samhain, Bealtaine, Lá Fhéile Bríde
    5. ARTIFACT: Holy wells (tobar), fairy forts (ráth, lios), standing stones

    For each entity provide:
    - The exact text as it appears
    - Normalized/standardized form
    - Both Irish and English forms if available
    - Confidence level

    {{ ctx.output_format }}
  "#
}

// Extract person entities with detailed metadata
function ExtractPersonEntities(
  text string @description("Text containing person references")
) -> PersonEntity[] {
  client Claude
  prompt #"
    Extract all person references from this folklore text.

    Text: {{ text }}

    For each person, identify:
    - Full name (as given)
    - Irish form of name if different
    - Role (collector, informant, teacher, priest, etc.)
    - Gender
    - Approximate dates if mentioned
    - Location association
    - Occupation if mentioned

    Common collector/informant patterns:
    - "collected by", "bailíodh ó", "told by", "from the mouth of"
    - Teacher names in Schools' Collection

    {{ ctx.output_format }}
  "#
}

// Extract and link place entities
function ExtractPlaceEntities(
  text string @description("Text with place references")
) -> PlaceEntity[] {
  client Claude
  prompt #"
    Extract all place references from this text.

    Text: {{ text }}

    For each place:
    - Name as written
    - Irish form (starting with Baile, Cill, etc.)
    - English form if different
    - Type: townland, parish, county, barony, province
    - County and province if determinable

    Irish placename elements:
    - Baile (town), Cill (church), Ard (height), Cnoc (hill)
    - Inis (island), Loch (lake), Abhainn (river)
    - Dún (fort), Ráth (ringfort), Caisleán (castle)

    {{ ctx.output_format }}
  "#
}

// Extract supernatural entities
function ExtractSupernaturalEntities(
  text string @description("Folklore text about supernatural beings")
) -> SupernaturalEntity[] {
  client Claude
  prompt #"
    Extract supernatural beings and folklore entities from this text.

    Text: {{ text }}

    Look for:
    - Fairies: sí, sióg, aos sí, daoine maithe, daoine uaisle
    - Banshee: bean sí (announces death)
    - Púca: shape-shifter, often a horse
    - Ghosts: taibhse, sprid
    - Changelings: iarlais, plentyn newid
    - Water spirits: each uisce (water horse), murúch (mermaid)
    - Other: dúlachán (headless), fear gorta (famine spirit)

    For each entity describe:
    - Name/type
    - How it appears
    - What it does
    - Where it's found
    - How to protect against it

    {{ ctx.output_format }}
  "#
}

// Extract festivals and calendar customs
function ExtractFestivalEntities(
  text string @description("Text mentioning festivals or customs")
) -> FestivalEntity[] {
  client Claude
  prompt #"
    Extract festival and calendar custom references from this text.

    Text: {{ text }}

    Major Celtic festivals:
    - Samhain (Oct 31/Nov 1) - Halloween, end of harvest
    - Bealtaine (May 1) - Start of summer
    - Imbolc / Lá Fhéile Bríde (Feb 1) - St. Brigid's Day
    - Lúnasa (Aug 1) - Harvest festival

    Christian adaptations:
    - Lá Nollag (Christmas)
    - Cáisc (Easter)
    - Féile Pádraig (St. Patrick's Day)

    For each festival describe:
    - Name in Irish and English
    - Date
    - Associated customs
    - Foods
    - Beliefs

    {{ ctx.output_format }}
  "#
}
