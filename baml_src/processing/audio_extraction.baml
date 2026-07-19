// Canúint.ie Audio Recording Extraction
// Irish dialect audio with transcriptions and geolocation
// December 2024
//
// Canúint.ie contains audio recordings of traditional Irish speakers
// from the three main dialect regions: Munster, Connacht, and Ulster.

// ============================================================================
// AUDIO RECORDING METADATA
// ============================================================================

// Complete audio recording record from Canúint.ie
class CanuintRecording {
  // Identification
  recording_id string @description("Unique recording ID (QQTRIN*, OD*, QAC* formats)")
  source_url string @description("Web page URL")
  audio_url string? @description("Direct URL to audio file")

  // Speaker information
  speaker CanuintSpeaker @description("Primary speaker details")
  additional_speakers CanuintSpeaker[]? @description("Other speakers if present")

  // Location
  location CanuintLocation @description("Recording location")
  barony_id int @description("Barony ID from URL structure")

  // Recording metadata
  recording_year int? @description("Year the recording was made")
  duration_seconds int? @description("Duration in seconds")
  audio_quality string? @description("Audio quality assessment")

  // Transcription
  transcription_status string @description("available, coming_soon, none")
  transcription CanuintTranscription? @description("Transcription if available")

  // Dialect classification
  dialect IrishDialect @description("Dialect classification")
  dialect_features string[]? @description("Notable dialect features identified")
  @@stream.done
}

// Speaker information
class CanuintSpeaker {
  name string @description("Speaker name in Irish")
  name_standardized string? @description("Standardized name spelling")
  townland string @description("Speaker's townland")
  townland_ga string? @description("Townland name in Irish")
  birth_year int? @description("Birth year if known")
  age_at_recording int? @description("Age at time of recording")
  gender string? @description("Gender: male, female")
  occupation string? @description("Traditional occupation if mentioned")
  native_speaker bool @description("Whether native Irish speaker")
}

// Location details from Canúint
class CanuintLocation {
  barony_name string @description("Barony name")
  barony_name_ga string? @description("Barony name in Irish")
  county string @description("County name")
  county_code string? @description("2-letter county code")
  townland string? @description("Specific townland")
  townland_ga string? @description("Townland in Irish")
  latitude float? @description("WGS84 latitude")
  longitude float? @description("WGS84 longitude")
  gaeltacht_area string? @description("Gaeltacht region if applicable")
}

// Transcription with alignment
class CanuintTranscription {
  full_text string @description("Complete transcription text")
  language CelticLanguage @description("Primary language")
  word_count int @description("Number of words")

  // Time-aligned segments if available
  segments TranscriptionSegment[]? @description("Time-aligned segments")

  // Quality metadata
  transcription_source string @description("Who created: human, asr, hybrid")
  confidence float? @description("Confidence score 0-1")
  verified bool @description("Human verified")
  verifier string? @description("Who verified")

  // Linguistic annotations
  dialect_notes string[]? @description("Notes on dialect features")
  vocabulary_notes VocabularyNote[]? @description("Notable vocabulary items")
}

// Time-aligned transcription segment
class TranscriptionSegment {
  start_seconds float @description("Start time in seconds")
  end_seconds float @description("End time in seconds")
  text string @description("Segment text")
  speaker string? @description("Speaker identifier if multiple")
  confidence float? @description("ASR confidence for this segment")
}

// Notable vocabulary annotation
class VocabularyNote {
  word string @description("The word or phrase")
  standard_form string? @description("Standard Irish equivalent")
  meaning string @description("Meaning in English")
  dialect_specific bool @description("Whether specific to this dialect")
  frequency string? @description("How common: rare, occasional, common")
}

// ============================================================================
// BROWSERBASE STAGEHAND EXTRACTION
// ============================================================================

// Extract recording metadata from Canúint.ie page using Stagehand
function ExtractCanuintPage(
  page_content: string,
  barony_id: int
) -> CanuintRecording {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Extract multiple recordings from barony listing page
function ExtractBaronyRecordings(
  page_content: string,
  barony_id: int,
  barony_name: string
) -> CanuintRecording[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// DIALECT ANALYSIS
// ============================================================================

// Phonetic and morphological dialect features
class DialectAnalysis {
  recording_id string @description("Recording this analysis is for")
  dialect IrishDialect @description("Overall dialect classification")

  // Phonetic features
  phonetic_features PhoneticFeature[] @description("Identified phonetic traits")

  // Morphological features
  morphological_features MorphologicalFeature[] @description("Grammar/morphology traits")

  // Lexical features
  dialect_vocabulary VocabularyNote[] @description("Dialect-specific vocabulary")

  // Comparison
  similarity_scores DialectSimilarity[] @description("Similarity to other recordings")

  // Classification confidence
  confidence float @description("Confidence in dialect classification")
  notes string? @description("Analyst notes")
}

// Phonetic dialect feature
class PhoneticFeature {
  feature_name string @description("Name of the feature")
  description string @description("Description of the phonetic trait")
  examples string[] @description("Examples from the recording")
  typical_of IrishDialect[] @description("Which dialects show this feature")
}

// Morphological/grammatical feature
class MorphologicalFeature {
  feature_name string @description("Name of the feature")
  description string @description("Description of the grammatical trait")
  examples string[] @description("Examples from the recording")
  standard_form string? @description("Standard Irish equivalent")
}

// Similarity to other dialect recordings
class DialectSimilarity {
  compared_recording_id string @description("Recording compared to")
  similarity_score float @description("Similarity score 0-1")
  shared_features string[] @description("Shared dialect features")
  differing_features string[] @description("Differing features")
}

// Analyze dialect features from transcription
function AnalyzeDialect(
  transcription: CanuintTranscription,
  speaker: CanuintSpeaker,
  location: CanuintLocation
) -> DialectAnalysis {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
