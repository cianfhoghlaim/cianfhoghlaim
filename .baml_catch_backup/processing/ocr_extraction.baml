// Hidden Heritages HTR/OCR Extraction
// Folklore tales from Ireland and Scotland with AI transcriptions
// December 2024
//
// Decoding Hidden Heritages uses AI (HTR - Handwritten Text Recognition)
// to transcribe historical folklore manuscripts from the National Folklore
// Collection (Ireland) and School of Scottish Studies (Scotland).

// ============================================================================
// HIDDEN HERITAGES TALE RECORD
// ============================================================================

// Complete tale record from Hidden Heritages
class HiddenHeritagesTale {
  // Identification
  tale_id string @description("Unique tale identifier")
  source_url string @description("Web page URL")
  source_collection string @description("NFC (Ireland) or SSS (Scotland)")

  // Tale metadata
  title string @description("Tale title")
  title_original string? @description("Original language title if different")

  // People involved
  collector string @description("Person who collected the tale")
  informant string @description("Person who told the tale")
  informant_details InformantDetails? @description("Additional informant information")

  // Location
  location HHTLocation @description("Collection location")

  // Temporal
  collection_date string? @description("Date of collection")
  collection_year int? @description("Year of collection")

  // Content
  language CelticLanguage @description("Language of the tale")
  transcription HHTTranscription @description("HTR transcription")

  // Classification
  tale_type TaleType? @description("Aarne-Thompson-Uther classification")
  motifs string[]? @description("Thompson motif index references")
  topics FolkloreTopic[] @description("Thematic topic tags")

  // Related tales
  related_tales string[]? @description("IDs of related tales")
  same_informant_tales string[]? @description("Other tales from same informant")
  @@stream.done
}

// Informant (storyteller) details
class InformantDetails {
  name string @description("Full name")
  age int? @description("Age at time of collection")
  birth_year int? @description("Birth year")
  occupation string? @description("Occupation")
  townland string? @description("Home townland")
  native_speaker bool? @description("Native language speaker")
  literacy string? @description("Literacy level if noted")
  reputation string? @description("Known as good storyteller, etc.")
}

// Location from Hidden Heritages
class HHTLocation {
  townland string? @description("Townland name")
  townland_ga string? @description("Irish name")
  townland_gd string? @description("Scottish Gaelic name")
  parish string? @description("Parish name")
  county string? @description("County name")
  country string @description("Ireland or Scotland")
  latitude float? @description("WGS84 latitude")
  longitude float? @description("WGS84 longitude")
}

// HTR transcription with confidence
class HHTTranscription {
  full_text string @description("Complete transcription")
  language CelticLanguage @description("Language of text")
  word_count int @description("Number of words")

  // HTR metadata
  htr_model string? @description("HTR model used")
  htr_confidence float @description("Overall confidence score 0-1")
  processing_date string? @description("When HTR was run")

  // Quality indicators
  line_confidences float[]? @description("Per-line confidence scores")
  low_confidence_sections LowConfidenceSection[]? @description("Sections needing review")

  // Human corrections
  human_reviewed bool @description("Whether human reviewed")
  reviewer string? @description("Who reviewed")
  corrections_made int? @description("Number of corrections")
}

// Section with low HTR confidence
class LowConfidenceSection {
  start_position int @description("Character position start")
  end_position int @description("Character position end")
  original_text string @description("HTR output")
  suggested_text string? @description("Suggested correction")
  confidence float @description("Confidence for this section")
  issue_type string @description("unclear, damaged, abbreviation, etc.")
}

// Tale type classification (Aarne-Thompson-Uther)
class TaleType {
  atu_number string @description("ATU classification number (e.g., 'ATU 480')")
  title string @description("Standard tale type title")
  category string @description("Tale category (Animal, Ordinary, etc.)")
  description string? @description("Brief description of tale type")
}

// ============================================================================
// FIRECRAWL SCRAPE EXTRACTION
// ============================================================================

// Extract tale from Hidden Heritages page
function ExtractHiddenHeritagesTale(
  page_content: string,
  tale_id: string
) -> HiddenHeritagesTale {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

test ExtractHiddenHeritagesTale {
  functions [ExtractHiddenHeritagesTale]
  args {
    page_content #"
      The Three Sorrows of Storytelling
      NFC: tale-1234
      Collector: Séamus Ó Conghaile (Dublin, 1938)
      Informant: Mícheál Ó Briain (Galway, 1870-1952)

      There were once three sorrows that came to storytelling in Ireland:
      the loss of the old language, the emigrant that never came home,
      and the song that died on the lips. The first sorrow was the
      language of the Gaels, which died a little each time the last
      speaker of a dialect passed away. The second was the broken
      promise of the boy who went to Boston and never returned.
      The third was the song that was sung only once, and then
      mislaid, and no one could remember how the second verse
      went after the fire of the cottage of Mícheál Ó Briain in
      the year of the great wind.
    "#
    tale_id "tale-1234"
  }
}

// Extract tales listing from browse page
function ExtractTalesListing(
  page_content: string,
  page_number: int
) -> TalesListingPage {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Summary of tales on a listing page
class TalesListingPage {
  page_number int @description("Current page number")
  total_pages int? @description("Total pages if known")
  tales TaleSummary[] @description("Tale summaries on this page")
  has_next_page bool @description("Whether there's a next page")
  @@stream.done
}

// Brief tale summary from listing
class TaleSummary {
  tale_id string @description("Tale identifier")
  url string @description("Full URL to tale")
  title string @description("Tale title")
  collector string? @description("Collector name")
  informant string? @description("Informant name")
  location string? @description("Brief location")
  language CelticLanguage? @description("Language")
  source_collection string @description("CBE or SA")
}

// ============================================================================
// CROSS-COLLECTION ANALYSIS
// ============================================================================

// Compare tale variants across collections
class TaleVariantAnalysis {
  primary_tale HiddenHeritagesTale @description("Primary tale being analyzed")
  variants TaleVariant[] @description("Variant versions found")

  // Comparative analysis
  common_elements string[] @description("Elements appearing in all variants")
  variable_elements string[] @description("Elements that vary")
  geographic_distribution GeoDistribution @description("Where variants are found")

  // Tale type
  atu_classification TaleType? @description("Shared ATU classification")
  motif_analysis MotifAnalysis @description("Motif pattern analysis")
}

// Variant of a tale
class TaleVariant {
  tale_id string @description("Variant tale ID")
  source FolkloreSource @description("Source collection")
  location HHTLocation @description("Collection location")
  similarity_score float @description("Similarity to primary tale 0-1")
  unique_elements string[] @description("Elements unique to this variant")
  language CelticLanguage @description("Language of variant")
}

// Geographic distribution of tale variants
class GeoDistribution {
  total_variants int @description("Total number of variants")
  countries_represented string[] @description("Countries with variants")
  counties_represented string[] @description("Counties/regions")
  centroid GeoLocation @description("Geographic centroid")
  spread_km float @description("Approximate spread in kilometers")
}

// Analysis of motif patterns
class MotifAnalysis {
  motifs MotifOccurrence[] @description("Motifs and their occurrences")
  core_motifs string[] @description("Motifs in all variants")
  regional_motifs RegionalMotif[] @description("Motifs specific to regions")
}

// Motif occurrence tracking
class MotifOccurrence {
  motif_id string @description("Thompson Motif Index ID")
  motif_title string @description("Motif title")
  occurrence_count int @description("How many tales contain it")
  occurrence_rate float @description("Percentage of tales")
}

// Region-specific motif
class RegionalMotif {
  motif_id string @description("Motif ID")
  region string @description("Geographic region")
  frequency float @description("Frequency in this region")
  interpretation string? @description("Regional significance")
}
