// Logainm.ie - The Placenames Database of Ireland API
// BAML schema for structured extraction from Logainm API responses
// Based on API v1.0: https://docs.gaois.ie/en/data/logainm/v1.0/api
// December 2024

// ============================================================================
// ADMINISTRATIVE AND GEOGRAPHIC ENUMS
// ============================================================================

// Irish county codes (2-letter)
enum IrishCountyCode {
  AN @alias("Antrim")
  AR @alias("Armagh")
  CE @alias("Clare")
  CN @alias("Cavan")
  CO @alias("Cork")
  CW @alias("Carlow")
  DL @alias("Donegal")
  DN @alias("Down")
  DU @alias("Dublin")
  FE @alias("Fermanagh")
  GA @alias("Galway")
  KE @alias("Kerry")
  KK @alias("Kilkenny")
  KY @alias("Kildare")
  LD @alias("Longford")
  LH @alias("Louth")
  LK @alias("Limerick")
  LM @alias("Leitrim")
  LS @alias("Laois")
  LY @alias("Derry/Londonderry")
  MH @alias("Meath")
  MN @alias("Monaghan")
  MO @alias("Mayo")
  OY @alias("Offaly")
  RN @alias("Roscommon")
  SO @alias("Sligo")
  TE @alias("Tyrone")
  TY @alias("Tipperary")
  WD @alias("Waterford")
  WH @alias("Westmeath")
  WW @alias("Wicklow")
  WX @alias("Wexford")
}

// Administrative unit categories from Logainm
enum AdminUnitCategory {
  CON @alias("Country")
  PRO @alias("Province")
  C @alias("County")
  BAR @alias("Barony")
  PAR @alias("Parish")
  ED @alias("Electoral Division")
  T @alias("Townland")
  BF @alias("Baile Fearainn")
  SR @alias("Street")
  SRB @alias("Street (bilingual)")
  GAE @alias("Gaeltacht")
}

// Geographic feature categories
enum GeoFeatureCategory {
  BAY @alias("Bay")
  LAKE @alias("Lake/Loch")
  RIV @alias("River")
  IS @alias("Island")
  MT @alias("Mountain")
  PROM @alias("Promontory")
  HILL @alias("Hill")
  WOOD @alias("Wood/Forest")
  BOG @alias("Bog")
  STRAND @alias("Strand/Beach")
}

// ============================================================================
// CORE LOGAINM DATA STRUCTURES
// ============================================================================

// Geographic coordinates
class LogainmCoordinates {
  latitude float @description("WGS84 latitude")
  longitude float @description("WGS84 longitude")
  accurate bool @description("True if coordinates are precise, false if extrapolated")
}

// Placename in multiple languages
class PlacenameText {
  ga string? @description("Irish/Gaeilge name")
  en string? @description("English name")
  alternatives string[]? @description("Alternative spellings or historical names")
}

// Reference to a glossary word (placename element)
class GlossaryReference {
  id int @description("Glossary entry ID")
  word string @description("The word/element")
  meaning string? @description("Meaning of the element")
  language string @description("Language: ga or en")
}

// Parent place reference
class ParentPlace {
  id int @description("Logainm place ID")
  name PlacenameText @description("Place name")
  category string @description("Category code (C, PAR, BAR, etc.)")
}

// ============================================================================
// MAIN LOGAINM PLACE RECORD
// ============================================================================

// Full place record from Logainm API
class LogainmPlace {
  // Identification
  id int @description("Unique Logainm place identifier")
  cluster_id int? @description("Cluster ID for related places")
  
  // Names
  name PlacenameText @description("Official placename in Irish and English")
  similar_names PlacenameText[]? @description("Similar or related names found")
  
  // Classification
  category string @description("Category code (T, PAR, BAR, C, etc.)")
  category_name PlacenameText? @description("Category name in Irish/English")
  
  // Geographic
  coordinates LogainmCoordinates? @description("Geographic coordinates if available")
  
  // Administrative hierarchy
  county ParentPlace? @description("County this place belongs to")
  barony ParentPlace? @description("Barony containing this place")
  parish ParentPlace? @description("Parish containing this place")
  electoral_division ParentPlace? @description("ED containing this place")
  
  // Attributes
  gaeltacht bool @description("Whether place is in a Gaeltacht area")
  post_office bool @description("Whether place has/had a post office")
  northern_ireland bool @description("Whether place is in Northern Ireland")
  
  // Etymology
  glossary_entries GlossaryReference[]? @description("Placename elements/etymology")
  
  // Metadata
  created_at string? @description("ISO datetime when record created")
  modified_at string? @description("ISO datetime when record last modified")
}

// Paginated list response
class LogainmSearchResult {
  places LogainmPlace[] @description("List of places matching query")
  total_count int @description("Total number of results")
  page int @description("Current page number")
  per_page int @description("Results per page")
  has_more bool @description("Whether more pages are available")
}

// ============================================================================
// GLOSSARY (PLACENAME ELEMENTS)
// ============================================================================

// Glossary entry - common words in Irish placenames
class GlossaryEntry {
  id int @description("Glossary entry ID")
  headword string @description("The headword/lemma")
  headword_ga string? @description("Irish form of headword")
  headword_en string? @description("English form of headword")
  meaning string? @description("Meaning/definition")
  meaning_ga string? @description("Irish meaning")
  meaning_en string? @description("English meaning")
  examples string[]? @description("Example placenames using this word")
  related_entries int[]? @description("IDs of related glossary entries")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Parse Logainm API JSON response for a single place
function ParseLogainmPlace(
  json_response: string
) -> LogainmPlace {
  client Extractor
  prompt #"
    Parse this Logainm.ie API JSON response and extract structured place data.

    {{ ctx.output_format }}

    JSON Response:
    {{ json_response }}

    Extract all available fields:
    - Place ID and cluster ID
    - Names in Irish (ga) and English (en)
    - Category classification
    - Geographic coordinates (note if accurate or extrapolated)
    - Administrative hierarchy (county, barony, parish, ED)
    - Gaeltacht, post office, NI flags
    - Glossary references for etymology
    - Timestamps

    Important:
    - Preserve Irish text with fadas (á, é, í, ó, ú)
    - Extract both Irish and English name variants
    - Note coordinate accuracy
  "#
}

// Parse Logainm search results
function ParseLogainmSearchResults(
  json_response: string
) -> LogainmSearchResult {
  client Extractor
  prompt #"
    Parse this Logainm.ie API search results JSON and extract all places.

    {{ ctx.output_format }}

    JSON Response:
    {{ json_response }}

    Extract:
    - All places in the results array
    - Pagination metadata (total count, page, per_page)
    - Determine if more pages are available

    For each place, extract full details as per LogainmPlace schema.
  "#
}

// Extract placename etymology from glossary references
function ExtractPlacenameEtymology(
  place: LogainmPlace
) -> string {
  client Extractor
  prompt #"
    Given this Logainm place record, explain the etymology of the placename.

    Place:
    - Irish name: {{ place.name.ga }}
    - English name: {{ place.name.en }}
    - Glossary entries: {{ place.glossary_entries }}
    - Category: {{ place.category }}

    Provide a clear explanation of:
    1. The meaning of the Irish placename
    2. How the glossary elements combine
    3. Any historical or linguistic notes
    4. The relationship between Irish and English forms

    Write in clear, accessible English with Irish terms explained.
  "#
}

// Find places within a geographic radius
function ParseGeoQuery(
  json_response: string,
  center_lat: float,
  center_lon: float,
  radius_m: int
) -> LogainmSearchResult {
  client Extractor
  prompt #"
    Parse this Logainm.ie geographic query response.

    {{ ctx.output_format }}

    Query parameters:
    - Center: {{ center_lat }}, {{ center_lon }}
    - Radius: {{ radius_m }} metres

    JSON Response:
    {{ json_response }}

    Results are sorted by proximity to center point.
    Extract all places with their full details and note their relative positions.
  "#
}

// ============================================================================
// INTEGRATION WITH OTHER GAOIS RESOURCES
// ============================================================================

// Link Logainm place to Dúchas Schools Collection
class LogainmDuchasLink {
  logainm_id int @description("Logainm place ID")
  logainm_name PlacenameText @description("Place name from Logainm")
  duchas_school_count int @description("Number of schools in this place in CBÉS")
  duchas_story_count int @description("Number of stories from this place")
  duchas_volume_numbers string[]? @description("Volume numbers containing stories from here")
}

// Enrich place data with Dúchas folklore references
function EnrichPlaceWithFolklore(
  place: LogainmPlace,
  duchas_data: string
) -> LogainmDuchasLink {
  client Extractor
  prompt #"
    Link this Logainm place to Dúchas Schools Collection data.

    {{ ctx.output_format }}

    Logainm Place:
    - ID: {{ place.id }}
    - Name: {{ place.name.ga }} / {{ place.name.en }}
    - County: {{ place.county }}

    Dúchas data:
    {{ duchas_data }}

    Extract:
    - Number of schools in this place
    - Number of folklore stories collected here
    - Volume numbers containing stories from this location
  "#
}
