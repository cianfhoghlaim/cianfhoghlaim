// Dúchas.ie Schools Collection Extraction Functions
// XML metadata and handwriting image processing
// December 2024
//
// The Schools Collection (Bailiúchán na Scol / CBES) contains 740,000 pages
// of handwritten manuscripts collected from Irish schoolchildren in 1937-1939.

// ============================================================================
// DÚCHAS XML PARSING
// ============================================================================

// Parsed XML metadata from Dúchas API
class DuchasXMLRecord {
  // Core identification
  entry_id string @description("Unique entry ID (e.g., 4606492)")
  url string @description("Canonical XML URL")

  // Volume information
  volume_number string @description("Volume number (0001-2400)")
  volume_id string @description("Volume entry ID")
  volume_status int @description("Processing status code")

  // School location
  location DuchasLocation @description("School and townland location")

  // School metadata
  school_name string @description("School name")
  school_name_ga string? @description("School name in Irish")
  school_roll_number string @description("Official school roll number")

  // Teacher information
  teacher_name DuchasPersonNameExtraction @description("Teacher who supervised collection")

  // Collector/informant (if specified in XML)
  collector DuchasPersonNameExtraction? @description("Student collector if specified")
  informant DuchasPersonNameExtraction? @description("Person who told the story")

  // Story metadata
  title string? @description("Story title if present")
  title_ga string? @description("Story title in Irish")
  pages int? @description("Number of pages in this entry")
  topics string[]? @description("Topic classifications if present")

  // Images
  image_urls string[] @description("URLs to manuscript page images")
}

// Location from Dúchas XML
class DuchasLocation {
  name_ga string @description("Townland name in Irish")
  name_en string @description("Townland name in English")
  latitude float @description("WGS84 latitude (16 decimal precision)")
  longitude float @description("WGS84 longitude (16 decimal precision)")
  county_code string @description("2-letter county code (GA, DO, KE, etc.)")
  county_name string? @description("Full county name")
  barony string? @description("Barony name")
  parish string? @description("Parish name")
  logainm_id int? @description("Logainm.ie placename ID")
}

// Person name structure from Dúchas XML
class DuchasPersonNameExtraction {
  pretext string? @description("Name prefix (e.g., 'Seán Ó', 'Máire Ní')")
  text string @description("Main name/surname")
  full_name string? @description("Reconstructed full name")
}

// Parse Dúchas XML response
function ParseDuchasXML(
  xml_content: string
) -> DuchasXMLRecord {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// ============================================================================
// HANDWRITING IMAGE EXTRACTION
// ============================================================================

// Extracted content from handwritten manuscript page
class HandwritingExtraction {
  page_number int @description("Page number in the volume")
  image_url string @description("Source image URL")

  // Text extraction
  transcription string @description("Full transcription of handwritten text")
  language CelticLanguage @description("Primary language detected")
  confidence TranscriptionConfidence @description("Confidence in extraction")

  // Layout analysis
  has_title bool @description("Whether page has a title")
  title string? @description("Title text if present")
  has_illustrations bool @description("Whether page has drawings")
  illustration_descriptions string[]? @description("Descriptions of any illustrations")

  // Writing analysis
  writer_estimated_age string? @description("Estimated age of writer (child/adult)")
  legibility string @description("Legibility assessment: clear, fair, poor")
  special_features string[]? @description("Special features: crossouts, marginalia, etc.")
  @@stream.done
}

// Extract text from handwritten manuscript image
function ExtractHandwriting(
  page_image: image,
  context: DuchasXMLRecord?
) -> HandwritingExtraction {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    HandwritingExtraction {}
  }
}

// Batch extraction for multi-page stories
class StoryExtraction {
  metadata DuchasXMLRecord @description("XML metadata for this story")
  pages HandwritingExtraction[] @description("Extracted content from each page")
  full_transcription string @description("Combined transcription of entire story")
  word_count int @description("Total word count")
  languages_used CelticLanguage[] @description("All languages used in the story")
  topics FolkloreTopic[] @description("Classified folklore topics")
  summary string @description("Brief summary of the story content")
  summary_ga string? @description("Summary in Irish")
  @@stream.done
}

// Extract complete story from multiple pages
function ExtractStory(
  page_images: image[],
  metadata: DuchasXMLRecord
) -> StoryExtraction {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    StoryExtraction {}
  }
}

// ============================================================================
// VOLUME-LEVEL AGGREGATION
// ============================================================================

// Summary of a complete volume
class VolumeSummary {
  volume_number string @description("Volume identifier")
  volume_id string @description("Volume entry ID")
  school DuchasLocation @description("School location")
  teacher DuchasPersonNameExtraction @description("Supervising teacher")

  // Content summary
  total_stories int @description("Number of stories in volume")
  total_pages int @description("Total number of pages")
  topics_covered FolkloreTopic[] @description("All topics represented")
  languages_used CelticLanguage[] @description("Languages present")

  // Statistics
  average_story_length int @description("Average words per story")
  transcription_coverage float @description("Percentage of pages transcribed")

  // Geographic context
  townlands_mentioned string[] @description("Townlands referenced in stories")
  neighboring_schools string[]? @description("Related school volumes")
}
