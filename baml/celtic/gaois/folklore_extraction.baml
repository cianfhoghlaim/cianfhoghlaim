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
) -> DuchasXMLRecord {
  client Extractor
  prompt #"
    Parse this Dúchas.ie XML metadata and extract structured information.

    {{ ctx.output_format }}

    XML Content:
    {{ xml_content }}

    Extract all fields from the XML structure:
    - Entry ID from the entryID attribute
    - Volume information from the <volume> element
    - School location from <schoolLocation> with lat/lon coordinates
    - School name and roll number
    - Teacher name from <teacherName>
    - Any collector/informant information
    - Story title if present
    - Page image URLs

    Important:
    - Preserve Irish names with fadas (á, é, í, ó, ú)
    - County codes are 2-letter (GA=Galway, DO=Donegal, etc.)
    - Coordinates have 16 decimal precision
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
) -> HandwritingExtraction {
  client VisionExtractor
  prompt #"
    Extract text from this handwritten Irish manuscript page.

    {{ ctx.output_format }}

    {% if context %}
    Context from XML metadata:
    - Volume: {{ context.volume_number }}
    - School: {{ context.school_name }}
    - Teacher: {{ context.teacher_name.full_name }}
    - Location: {{ context.location.name_ga }}, Co. {{ context.location.county_code }}
    {% endif %}

    Image:
    {{ page_image }}

    Tasks:
    1. Transcribe all handwritten text, preserving Irish spelling and fadas
    2. Identify the primary language (Irish/English/Mixed)
    3. Note any titles, headings, or section breaks
    4. Describe any illustrations or drawings
    5. Assess legibility and note any difficult passages
    6. Look for collector/informant names written on the page

    For Irish text:
    - Preserve pre-reform spelling if used (e.g., 'aithne' not 'aithint')
    - Note any dialectal spellings
    - Preserve séimhiú (lenition) marks correctly
  "#
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
) -> StoryExtraction {
  client VisionExtractor
  prompt #"
    Extract and combine a complete story from these manuscript pages.

    {{ ctx.output_format }}

    Metadata:
    {{ metadata }}

    Process each page image in order:
    {% for img in page_images %}
    Page {{ loop.index }}: {{ img }}
    {% endfor %}

    Tasks:
    1. Transcribe each page in order
    2. Combine into a single coherent transcription
    3. Identify and classify the folklore topic(s)
    4. Generate a brief summary
    5. Note the languages used throughout

    For story classification, use these categories:
    - LOCAL_HISTORY: Stories about local events, places, people
    - FOLK_TALES: Traditional stories and legends
    - SONGS_POETRY: Songs, rhymes, poetry
    - CUSTOMS_BELIEFS: Traditional practices and beliefs
    - SUPERNATURAL: Fairies, ghosts, supernatural events
    - PLACE_NAMES: Stories explaining placenames
    - CRAFTS_TRADES: Traditional skills and occupations
  "#
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
