// === ARCHIVED 2026-06-24 ===
// The 5 functions in this file (ExtractCelticEntities,
// ExtractPersonEntities, ExtractPlaceEntities,
// ExtractSupernaturalEntities, ExtractFestivalEntities) have
// no current Python consumer in the oideachais quadrant. They
// are intended for the meaisinfhoghlaim/ Celtic-linguistic
// agents (e.g. duchas_assets.py would benefit from these for
// folklore entity extraction), which are not yet built.
//
// To re-activate:
// 1. Implement the consumer (e.g.
//    meaisinfhoghlaim/agents/celtic_ner.py OR wire into
//    oideachais/dagster_defs/assets/duchas_assets.py)
// 2. Move this file back to baml_src/ (git mv)
// 3. Remove the ARCHIVED header from the top
// 4. Update STATUS.md to mark the functions as wired
// 5. Update REFACTORING.md to remove the archive entry
//
// Reference: openspec/changes/archive-celtic-baml-orphans/
// =====================================================================

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
  @@stream.done
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
  @@stream.done
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
  @@stream.done
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
  @@stream.done
}

// Festival/calendar custom entity
class FestivalEntity {
  name string @description("Festival name")
  name_ga string @description("Irish name")
  date string @description("When it occurs")
  customs string? @description("Associated customs")
  foods string? @description("Associated foods")
  beliefs string? @description("Associated beliefs")
  @@stream.done
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Extract all named entities from Celtic text
function ExtractCelticEntities(
  text: string @description("Celtic folklore or historical text"),
  language: CelticLanguage @description("Language of the text")
) -> CelticNamedEntity[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract person entities with detailed metadata
function ExtractPersonEntities(
  text: string @description("Text containing person references")
) -> PersonEntity[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract and link place entities
function ExtractPlaceEntities(
  text: string @description("Text with place references")
) -> PlaceEntity[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract supernatural entities
function ExtractSupernaturalEntities(
  text: string @description("Folklore text about supernatural beings")
) -> SupernaturalEntity[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract festivals and calendar customs
function ExtractFestivalEntities(
  text: string @description("Text mentioning festivals or customs")
) -> FestivalEntity[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
