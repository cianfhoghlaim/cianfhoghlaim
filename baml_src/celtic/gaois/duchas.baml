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
) -> DuchasSchoolsVolume {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Parse CBED person response
function ParsePerson(
  json_response: string
) -> DuchasPerson {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Parse CBEG photograph response
function ParsePhotograph(
  json_response: string
) -> DuchasPhotograph {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract folklore topics from a Schools Collection item
function ClassifyFolkloreTopic(
  item_text: string,
  available_topics: DuchasSchoolsTopic[]
) -> DuchasSchoolsTopic[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Link Schools Collection story to modern Logainm places
function LinkStoryToPlaces(
  story: DuchasSchoolsItem,
  mentioned_places: string[]
) -> int[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// MANUSCRIPT RECORD + BOUNDING BOX ALIGNMENT (added 2026-07-17)
// ============================================================================

// Unified manuscript record across all 4 Dúchas collections (cbe/cbes/cbeg/cbef)
class DuchasManuscriptRecord {
  page_id string @description("Canonical page ID (e.g., cbes/0460/6492)")
  collection DuchasCollection @description("Which collection this page belongs to")
  volume_id int @description("Volume ID")
  page_number int @description("Page number within volume")
  image_url string @description("URL to the digitised manuscript page image")
  image_width_px int @description("Image width in pixels")
  image_height_px int @description("Image height in pixels")
  school DuchasSchool? @description("For CBES: school that created the manuscript")
  primary_language string @description("Primary language of the manuscript (ga or en)")
  ga_text string? @description("Manuscript text in Irish (if any)")
  en_translation string? @description("English translation (if available)")
  topic_codes HandbookTopicCode[] @description("Handbook of Irish Folklore topic classifications")
  collector DuchasPersonName? @description("Student collector (CBES only)")
  informant DuchasPersonName? @description("Story informant (if specified)")
  teacher DuchasPersonName? @description("Supervising teacher (CBES only)")
  transcription_confidence float? @description("OCR confidence 0-1")
  human_verified bool @description("Whether the transcription was human-verified")
}

// A single bounding box at one of the 5 layout levels
class DuchasBoundingBox {
  page_id string @description("Canonical page ID (links to DuchasManuscriptRecord.page_id)")
  level string @description("One of: page, region, sentence, word, letter")
  parent_bbox_id string? @description("Bounding box ID of the parent (region > sentence > word > letter)")
  bbox_id string @description("Unique bounding box ID")
  x1 int @description("Left edge (px)")
  y1 int @description("Top edge (px)")
  x2 int @description("Right edge (px)")
  y2 int @description("Bottom edge (px)")
  text string? @description("Text content within this bbox (NULL if region/letter level)")
  ga_text string? @description("Irish text within this bbox (NULL if EN-only or pre-letter)")
  en_translation string? @description("English translation within this bbox (NULL if GA-only)")
  confidence float? @description("OCR confidence 0-1 (NULL if not measured)")
  handwritten bool @description("True if handwritten (vs typeset)")
}

// A transcribed line (the LLM/vision model output before bbox alignment)
class DuchasTranscriptionLine {
  page_id string @description("Canonical page ID")
  line_number int @description("Line number within page (1-indexed)")
  ga_text string @description("Irish text of this line")
  en_translation string? @description("English translation of this line (NULL if GA-only)")
  confidence float @description("OCR confidence 0-1")
  handwritten bool @description("True if handwritten")
  // Approximate bbox (the vision model gives a rough position; bbox alignment refines this)
  approx_x1 int? @description("Approximate left edge (px)")
  approx_y1 int? @description("Approximate top edge (px)")
  approx_x2 int? @description("Approximate right edge (px)")
  approx_y2 int? @description("Approximate bottom edge (px)")
}

// ============================================================================
// NEW EXTRACTION FUNCTIONS (added 2026-07-17 for the gaois-celtic-language-pipeline-v1 change)
// ============================================================================

// Parse a Dúchas manuscript page (image + transcript) into a unified record
// Uses `molmo2-8b` (diagram pointing) + `dots-ocr` (layout) via LlamaSwap routing.
function ExtractDuchasManuscript(
  xml_record: string,
  image_path: string?
) -> DuchasManuscriptRecord {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract 5-level bounding box alignment from a handwritten manuscript page
// Uses `dots-ocr` (layout specialist) via LlamaSwap routing. Returns the
// hierarchical bbox tree (page → region → sentence → word → letter).
function ExtractDuchasImageBoundingBox(
  image_path: string,
  transcript: string,
  collection: DuchasCollection
) -> DuchasBoundingBox[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract a transcription line-by-line from a handwritten manuscript page
// Uses `qwen3-vl-8b` (workhorse VLM) via LlamaSwap routing.
function ExtractDuchasTranscription(
  handwritten_image: string,
  collection: DuchasCollection,
  language_hint: string?
) -> DuchasTranscriptionLine[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
