// Celtic Language Data Sources - Core Enums and Base Classes
// Source-agnostic schema for Dúchas, Canúint, Hidden Heritages, and Census data
// December 2024
//
// This file defines the unified data model for Celtic language resources
// from Ireland, Scotland, Wales, and the Crown Dependencies.

// ============================================================================
// CELTIC LANGUAGE ENUMS
// ============================================================================

// Celtic and related languages of the British Isles
enum CelticLanguage {
  GA @alias("Irish (Gaeilge)")
  GD @alias("Scottish Gaelic (Gàidhlig)")
  CY @alias("Welsh (Cymraeg)")
  GV @alias("Manx (Gaelg)")
  KW @alias("Cornish (Kernewek)")
  EN @alias("English")
  SCO @alias("Scots")
  ULS @alias("Ulster Scots")
}

// Primary folklore and dialect data sources
enum FolkloreSource {
  DUCHAS @alias("Dúchas.ie - Schools Collection")
  CANUINT @alias("Canúint.ie - Repository of Irish Dialects")
  HIDDEN_HERITAGES @alias("Decoding Hidden Heritages")
  NFC @alias("National Folklore Collection, UCD")
  SSS @alias("School of Scottish Studies Archives")
}

// Media types for scraped content
enum MediaType {
  XML_METADATA @alias("Structured XML metadata")
  HANDWRITING_IMAGE @alias("Scanned handwritten manuscript")
  AUDIO_RECORDING @alias("Audio recording (MP3/WAV)")
  TRANSCRIPTION_TEXT @alias("Text transcription")
  HTR_OUTPUT @alias("Handwritten Text Recognition output")
  OCR_OUTPUT @alias("Optical Character Recognition output")
  JSON_API @alias("JSON API response")
}

// Irish dialect regions
enum IrishDialect {
  MUNSTER @alias("Gaeilge na Mumhan - Kerry, Cork, Waterford")
  CONNACHT @alias("Gaeilge Chonnacht - Galway, Mayo, Roscommon")
  ULSTER @alias("Gaeilge Uladh - Donegal")
  STANDARD @alias("An Caighdeán Oifigiúil - Official Standard")
}

// Transcription confidence levels
enum TranscriptionConfidence {
  HIGH @alias("High confidence (>90%)")
  MEDIUM @alias("Medium confidence (70-90%)")
  LOW @alias("Low confidence (<70%)")
  PENDING @alias("Awaiting transcription")
  HUMAN_VERIFIED @alias("Human verified transcription")
}

// Census data geographic granularity
enum GeographicGranularity {
  COUNTRY @alias("Country level")
  REGION @alias("Regional/Provincial level")
  COUNTY @alias("County level")
  LAD @alias("Local Authority District")
  MSOA @alias("Middle Super Output Area")
  LSOA @alias("Lower Super Output Area")
  DATA_ZONE @alias("Scotland Data Zone")
  ELECTORAL_DIVISION @alias("Ireland Electoral Division")
  SMALL_AREA @alias("Ireland Small Area")
  GAELTACHT @alias("Gaeltacht region")
  PARISH @alias("Parish (Crown Dependencies)")
  TOWNLAND @alias("Townland level")
}

// Census/statistics source agencies
enum StatisticsAgency {
  ONS @alias("Office for National Statistics (England & Wales)")
  NRS @alias("National Records of Scotland")
  CSO @alias("Central Statistics Office (Ireland)")
  NISRA @alias("Northern Ireland Statistics and Research Agency")
  WELSH_GOV @alias("Welsh Government Statistics")
  IOM_GOV @alias("Isle of Man Government")
  JERSEY_GOV @alias("States of Jersey")
  GUERNSEY_GOV @alias("States of Guernsey")
}

// ============================================================================
// BASE LOCATION CLASSES
// ============================================================================

// Geographic location with optional Logainm/placename linkage
class GeoLocation {
  latitude float? @description("WGS84 latitude")
  longitude float? @description("WGS84 longitude")
  county string? @description("County name")
  county_code string? @description("2-letter county code (GA, DO, etc.)")
  townland string? @description("Townland name (finest Irish geographic unit)")
  townland_ga string? @description("Townland name in Irish")
  barony string? @description("Historical barony name")
  parish string? @description("Civil or ecclesiastical parish")
  logainm_id int? @description("Logainm.ie placename ID for linking")
  osm_id string? @description("OpenStreetMap relation ID")
}

// Multi-scale geographic identifier for statistics
class GeographicUnit {
  granularity GeographicGranularity @description("Level of geographic detail")
  code string @description("Official geographic code (e.g., E09000001, S01000001)")
  name string @description("Area name")
  name_ga string? @description("Irish language name if applicable")
  parent_code string? @description("Parent area code for hierarchical linking")
  centroid GeoLocation? @description("Centroid coordinates")
  hilbert_index int? @description("Hilbert curve index for spatial ordering")
}

// ============================================================================
// UNIFIED SOURCE RECORD
// ============================================================================

// Source-agnostic record that can represent any Celtic language resource
class UnifiedSourceRecord {
  // Identification
  id string @description("Unique record identifier")
  source FolkloreSource @description("Which source this came from")
  source_url string @description("Canonical URL of the source")
  source_id string? @description("Source-specific ID (volume number, recording ID, etc.)")

  // Content metadata
  languages CelticLanguage[] @description("Languages present in the content")
  primary_language CelticLanguage @description("Primary language of the content")
  media_type MediaType @description("Type of media/content")

  // Location
  location GeoLocation? @description("Geographic origin of the content")

  // Temporal metadata
  collection_date string? @description("When the content was originally collected")
  collection_year int? @description("Year of collection (parsed)")
  scraped_at string @description("ISO timestamp when scraped")

  // Content
  title string? @description("Title or headline of the record")
  title_ga string? @description("Title in Irish if different")
  transcription string? @description("Text transcription if available")
  transcription_confidence TranscriptionConfidence? @description("Confidence in transcription")

  // People
  collector string? @description("Person who collected the content")
  informant string? @description("Person who provided the content")
  teacher string? @description("Teacher name (for Schools Collection)")

  // School metadata (Dúchas-specific)
  school_name string? @description("School name")
  school_roll_number string? @description("School roll number")

  // Audio metadata (Canúint-specific)
  audio_url string? @description("URL to audio file")
  audio_duration_seconds int? @description("Duration of audio in seconds")
  dialect IrishDialect? @description("Irish dialect classification")

  // Linking
  related_records string[]? @description("IDs of related records")
  volume_id string? @description("Parent volume/collection ID")
}

// ============================================================================
// SCRAPING METADATA
// ============================================================================

// Metadata about a scraping session
class ScrapingSession {
  session_id string @description("Unique session identifier")
  started_at string @description("ISO timestamp when session started")
  ended_at string? @description("ISO timestamp when session ended")
  source FolkloreSource @description("Source being scraped")
  tool_used string @description("Tool used: firecrawl, stagehand, http")
  records_scraped int @description("Number of records scraped")
  errors int @description("Number of errors encountered")
  sample_strategy string? @description("Sampling strategy used")
  notes string? @description("Additional session notes")
}

// ============================================================================
// FOLKLORE TOPIC CLASSIFICATION
// ============================================================================

// Standard folklore topic classification (based on Dúchas topics)
enum FolkloreTopic {
  LOCAL_HISTORY @alias("Local History and Traditions")
  FOLK_TALES @alias("Folk Tales and Legends")
  SONGS_POETRY @alias("Songs, Music, and Poetry")
  CUSTOMS_BELIEFS @alias("Customs and Beliefs")
  GAMES_PASTIMES @alias("Games and Pastimes")
  CRAFTS_TRADES @alias("Crafts and Traditional Trades")
  FOOD_DRINK @alias("Food and Drink")
  NATURE_WEATHER @alias("Nature and Weather Lore")
  PLACE_NAMES @alias("Placename Lore")
  FESTIVALS @alias("Festivals and Calendar Customs")
  RELIGION @alias("Religious Practices")
  MEDICINE @alias("Folk Medicine")
  DEATH_BURIAL @alias("Death and Burial Customs")
  SUPERNATURAL @alias("Supernatural Beings and Events")
}

// Classified folklore record with topic tags
class ClassifiedFolkloreRecord {
  record UnifiedSourceRecord @description("The base record")
  topics FolkloreTopic[] @description("Classified topic tags")
  topic_confidence float @description("Confidence in topic classification (0-1)")
  keywords string[] @description("Extracted keywords")
  summary string? @description("Brief summary of content")
  summary_ga string? @description("Summary in Irish")
}
