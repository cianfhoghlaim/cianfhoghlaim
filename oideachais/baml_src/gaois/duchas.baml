// Duchas.ie - National Folklore Collection API
// BAML schema for structured extraction from Duchas API responses
// Based on API v0.6: https://docs.gaois.ie/en/data/duchas/v0.6/api
// December 2024

// ============================================================================
// DUCHAS COLLECTION ENUMS
// ============================================================================

// Collections within the National Folklore Collection
enum DuchasCollection {
  CBE @alias("Main Manuscript Collection - 2,400 volumes since 1932")
  CBES @alias("Schools Collection - 740,000 pages from 1937-1939")
  CBEG @alias("Photographic Collection - 80,000+ photographs")
  CBED @alias("Persons Database - cross-collection person records")
}

// Editorial status (privileged access only)
enum EditorialStatus {
  DRAFT @alias("Draft - 0")
  PENDING @alias("Pending review - 1")
  REVIEWED @alias("Reviewed - 2")
  APPROVED @alias("Approved - 3")
  PUBLISHED @alias("Published - 4")
}

// Person occupations from CBED
enum FolkloreOccupation {
  IASC @alias("Fisher - Iascaire")
  FEIRM @alias("Farmer - Feirmeoir")
  MUINT @alias("Teacher - Muinteoir")
  SIUIN @alias("Carpenter - Siuinéir")
  SAGRT @alias("Priest - Sagart")
  BANALTR @alias("Nurse - Banaltra")
  CEOLT @alias("Musician - Ceoltóir")
  SCEAL @alias("Storyteller - Scéalaí")
  TINC @alias("Tinsmith - Tinceir")
}

// A Handbook of Irish Folklore topic codes
enum HandbookTopicCode {
  A @alias("Settlement and Dwelling")
  B @alias("Livelihood and Household Support")
  C @alias("Communication and Trade")
  D @alias("The Community")
  E @alias("Human Life")
  F @alias("Nature")
  G @alias("Folk Medicine")
  H @alias("Time")
  I @alias("Principles and Rules of Popular Belief")
  J @alias("Mythological Tradition")
  K @alias("Historical Tradition")
  L @alias("Religious Tradition")
  M @alias("Popular Oral Literature")
  N @alias("Sports and Pastimes")
}

// ============================================================================
// PERSON RECORDS (CBED)
// ============================================================================

// Person record from the Persons Database
class DuchasPerson {
  id int @description("CBED person identifier")
  
  // Names
  names DuchasPersonName[] @description("Person's names (may have variants)")
  gender string? @description("Gender: f or m")
  
  // Biographical data
  birth_year int? @description("Year of birth")
  birth_year_accuracy string? @description("APPROX, INFER, or QUESTION")
  death_year int? @description("Year of death")
  death_year_accuracy string? @description("APPROX, INFER, or QUESTION")
  
  // Location
  county_id int? @description("Logainm county ID")
  place_id int? @description("Logainm place ID")
  country string? @description("ISO 3166 country code")
  geoname_id int? @description("GeoNames ID if outside Ireland")
  
  // Occupation
  occupations FolkloreOccupation[]? @description("Person's occupations")
  
  // External links
  ainm_id int? @description("Ainm.ie biography ID")
  viaf_id int? @description("VIAF authority ID")
  
  // Metadata
  created_at string? @description("ISO datetime created")
  modified_at string? @description("ISO datetime modified")
}

// Person name structure
class DuchasPersonName {
  forename string? @description("First name")
  surname string? @description("Surname/family name")
  maiden_name string? @description("Maiden name if applicable")
  full_name string @description("Full name as displayed")
  language string? @description("Language of name: ga or en")
}

// ============================================================================
// SCHOOLS COLLECTION (CBES)
// ============================================================================

// Schools Collection volume
class DuchasSchoolsVolume {
  id int @description("Volume ID")
  volume_number string @description("Archival reference (e.g., 0154)")
  
  // School information
  school DuchasSchool @description("School that created this volume")
  
  // Content
  total_pages int @description("Total pages in volume")
  parts DuchasSchoolsPart[]? @description("Parts/sections within volume")
  
  // Status
  status int? @description("Editorial status (0-4)")
  
  // Metadata
  created_at string? @description("ISO datetime created")
  modified_at string? @description("ISO datetime modified")
}

// School record
class DuchasSchool {
  name string @description("School name")
  name_ga string? @description("School name in Irish")
  roll_number string? @description("Official school roll number")
  
  // Location
  county_id int @description("Logainm county ID")
  place_id int? @description("Logainm place ID")
  latitude float? @description("School latitude")
  longitude float? @description("School longitude")
  
  // Teacher
  teacher DuchasPersonName? @description("Supervising teacher")
  teacher_id int? @description("Teacher's CBES ID")
}

// Part/section within a Schools Collection volume
class DuchasSchoolsPart {
  id int @description("Part ID")
  title string? @description("Part title")
  title_ga string? @description("Title in Irish")
  pages int @description("Number of pages")
  items DuchasSchoolsItem[]? @description("Items/stories within this part")
}

// Individual item/story in Schools Collection
class DuchasSchoolsItem {
  id int @description("Item ID")
  
  // Content
  title string? @description("Story title")
  title_ga string? @description("Title in Irish")
  
  // Classification
  topics DuchasSchoolsTopic[]? @description("Topic classifications")
  language string @description("Primary language: ga or en")
  
  // People
  collectors DuchasPersonName[]? @description("Student collectors")
  informants DuchasPersonName[]? @description("Story informants")
  
  // Location
  county_id int? @description("Logainm county ID of story origin")
  place_id int? @description("Logainm place ID")
  
  // Transcription
  transcription DuchasTranscription? @description("Page transcription if available")
}

// Topic from Schools Collection Subject List
class DuchasSchoolsTopic {
  id int @description("Topic ID")
  name string @description("Topic name")
  name_ga string? @description("Topic name in Irish")
  parent_id int? @description("Parent topic ID for hierarchy")
}

// Page transcription
class DuchasTranscription {
  text string @description("Transcribed text")
  language string @description("Language of transcription: ga or en")
  pages int[] @description("Page numbers covered")
  confidence float? @description("Transcription confidence 0-1")
  verified bool @description("Whether human-verified")
}

// ============================================================================
// MAIN MANUSCRIPT COLLECTION (CBE)
// ============================================================================

// Main Manuscript volume
class DuchasManuscriptVolume {
  id int @description("Volume ID")
  volume_number string @description("Archival reference")
  
  // Content
  total_pages int @description("Total pages")
  items DuchasManuscriptItem[]? @description("Items in volume")
  
  // Status and metadata
  status int? @description("Editorial status")
  created_at string?
  modified_at string?
}

// Item in Main Manuscript Collection
class DuchasManuscriptItem {
  id int @description("Item ID")
  
  // Content
  title string? @description("Item title")
  title_ga string? @description("Title in Irish")
  language string @description("Primary language")
  
  // People (linked to CBED)
  collector_id int? @description("Collector's CBED ID")
  informant_id int? @description("Informant's CBED ID")
  
  // Location
  county_id int? @description("Logainm county ID")
  place_id int? @description("Logainm place ID")
  
  // Date
  date_from int? @description("Year from")
  date_to int? @description("Year to")
  date_accuracy string? @description("APPROX, INFER, QUESTION")
}

// ============================================================================
// PHOTOGRAPHIC COLLECTION (CBEG)
// ============================================================================

// Photograph record
class DuchasPhotograph {
  id int @description("Photograph ID")
  
  // Image
  image_url string? @description("URL to image file")
  digitized bool @description("Whether digitized")
  
  // Metadata
  title string? @description("Photograph title/caption")
  description string? @description("Full description")
  
  // Classification
  handbook_topic HandbookTopicCode? @description("Handbook topic code")
  
  // People
  photographer_id int? @description("Photographer's CBED ID")
  relevant_persons int[]? @description("People depicted - CBED IDs")
  
  // Location
  county_id int? @description("Logainm county ID")
  place_id int? @description("Logainm place ID")
  country string? @description("ISO country code")
  
  // Date
  date_from int? @description("Year from")
  date_to int? @description("Year to")
  date_accuracy string? @description("APPROX, INFER, QUESTION")
  
  // Rights
  copyright string? @description("Copyright holder code")
  condition int? @description("Physical condition 0-3")
  
  // Metadata
  created_at string?
  modified_at string?
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Parse CBES volume response
function ParseSchoolsVolume(
  json_response: string
) -> DuchasSchoolsVolume {
  client Extractor
  prompt #"
    Parse this Dúchas Schools Collection (CBÉS) API response.

    {{ ctx.output_format }}

    JSON Response:
    {{ json_response }}

    Extract:
    - Volume ID and number
    - School information (name, location, teacher)
    - All parts and items within the volume
    - Topic classifications
    - Collector and informant information
    - Any available transcriptions

    Important:
    - Preserve Irish text with fadas
    - Link place IDs to Logainm
    - Note transcription availability and quality
  "#
}

// Parse CBED person response
function ParsePerson(
  json_response: string
) -> DuchasPerson {
  client Extractor
  prompt #"
    Parse this Dúchas Persons Database (CBÉD) API response.

    {{ ctx.output_format }}

    JSON Response:
    {{ json_response }}

    Extract all biographical information:
    - Name variants (Irish and English forms)
    - Birth and death years with accuracy notes
    - Location (county, place, country)
    - Occupations
    - External links (Ainm.ie, VIAF)
  "#
}

// Parse CBEG photograph response
function ParsePhotograph(
  json_response: string
) -> DuchasPhotograph {
  client Extractor
  prompt #"
    Parse this Dúchas Photographic Collection (CBÉG) API response.

    {{ ctx.output_format }}

    JSON Response:
    {{ json_response }}

    Extract:
    - Image URL and digitization status
    - Title and description
    - Handbook topic classification
    - People (photographer and subjects)
    - Location and date information
    - Copyright and condition
  "#
}

// Extract folklore topics from a Schools Collection item
function ClassifyFolkloreTopic(
  item_text: string,
  available_topics: DuchasSchoolsTopic[]
) -> DuchasSchoolsTopic[] {
  client Extractor
  prompt #"
    Classify this folklore text according to the Schools Collection Subject List.

    {{ ctx.output_format }}

    Text:
    {{ item_text }}

    Available topics:
    {{ available_topics }}

    Select all applicable topics from the list. Consider:
    - Primary subject matter
    - Secondary themes mentioned
    - Cultural practices described
    - Historical references
    - Supernatural elements

    Return the topic objects that best match this content.
  "#
}

// Link Schools Collection story to modern Logainm places
function LinkStoryToPlaces(
  story: DuchasSchoolsItem,
  mentioned_places: string[]
) -> int[] {
  client Extractor
  prompt #"
    Identify Logainm place IDs for locations mentioned in this folklore story.

    Story:
    - Title: {{ story.title }}
    - From: County ID {{ story.county_id }}, Place ID {{ story.place_id }}

    Places mentioned in text:
    {{ mentioned_places }}

    For each mentioned place, provide the most likely Logainm place ID.
    Consider:
    - Spelling variations (old vs modern Irish)
    - English anglicizations
    - Local vs official names
    - Geographic context from the story's origin

    Return a list of Logainm IDs.
  "#
}
