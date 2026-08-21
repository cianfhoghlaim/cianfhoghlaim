// OCR Validation Schema for Document Processing
// Validates OCR outputs from PaddleOCR, Docling, Unstract, and Vision models
// December 2024
//
// Provides type-safe validation for:
// - OCR quality assessment
// - Irish language content validation
// - Document structure extraction
// - Model comparison results

// ============================================================================
// OCR RESULT VALIDATION
// ============================================================================

// Validated OCR result with quality metrics
class OCRValidationResult {
  // Quality assessment
  quality OCRQuality @description("Overall quality assessment")
  confidence_score float @description("Confidence score 0-1")

  // Text analysis
  detected_language LanguageCodeOcr @description("Detected language")
  text_length int @description("Character count")
  word_count int @description("Word count")

  // Irish content analysis (if detected)
  irish_content_quality IrishContentQuality? @description("Irish language quality if detected")

  // Review status
  needs_manual_review bool @description("Whether human review is needed")
  review_reasons string[]? @description("Reasons for manual review")

  // Model info
  model_id string @description("Model that produced this result")
  processing_time_seconds float @description("Time to process")
}

// OCR quality levels
enum OCRQuality {
  EXCELLENT @description("High confidence, clean text")
  GOOD @description("Minor issues, usable")
  FAIR @description("Some errors, needs review")
  POOR @description("Many errors, unreliable")
  FAILED @description("OCR failed or unusable")
}

// Supported language codes
enum LanguageCodeOcr {
  EN @description("English")
  GA @description("Irish (Gaeilge)")
  GD @description("Scottish Gaelic")
  CY @description("Welsh")
  GV @description("Manx")
  MIXED @description("Multiple languages")
  UNKNOWN @description("Could not detect")
}

// ============================================================================
// IRISH LANGUAGE VALIDATION
// ============================================================================

// Irish content quality assessment
class IrishContentQuality {
  // Fada accuracy
  fada_accuracy float @description("Accuracy of fadas (á, é, í, ó, ú) 0-1")
  fada_count int @description("Number of fadas detected")
  missing_fadas FadaError[]? @description("Potentially missing fadas")
  incorrect_fadas FadaError[]? @description("Incorrectly placed fadas")

  // Spelling standard
  spelling_standard IrishSpellingStandard @description("Pre-reform, modern, or mixed")

  // Dialect indicators
  dialect_indicators DialectIndicator[]? @description("Detected dialect markers")

  // Vocabulary assessment
  common_errors CommonIrishError[]? @description("Common OCR errors for Irish")
}

// Irish spelling standards
enum IrishSpellingStandard {
  PRE_REFORM @description("Pre-1948 spelling")
  MODERN @description("Modern Caighdeán spelling")
  MIXED @description("Mix of spellings")
  UNKNOWN @description("Could not determine")
}

// Fada error details
class FadaError {
  word string @description("The word with the error")
  position int @description("Character position in text")
  expected string @description("Expected character")
  found string @description("Found character")
  correction string @description("Suggested correction")
}

// Dialect indicator
class DialectIndicator {
  feature string @description("The linguistic feature")
  dialect IrishDialectOcr @description("Which dialect it indicates")
  example string @description("Example from text")
  confidence float @description("Confidence 0-1")
}

// Irish dialects
enum IrishDialectOcr {
  CONNACHT @description("Connacht Irish (Galway, Mayo)")
  MUNSTER @description("Munster Irish (Cork, Kerry)")
  ULSTER @description("Ulster Irish (Donegal)")
  STANDARD @description("Standard/Caighdeán")
  UNKNOWN @description("Could not determine")
}

// Common Irish OCR errors
class CommonIrishError {
  error_type IrishOCRErrorType @description("Type of error")
  original string @description("Text as OCR'd")
  corrected string @description("Suggested correction")
  frequency int @description("How often this appears")
}

// Types of Irish OCR errors
enum IrishOCRErrorType {
  MISSING_FADA @description("Fada missing (a instead of á)")
  WRONG_FADA @description("Wrong vowel has fada")
  LENITION_ERROR @description("Missing or incorrect lenition (h)")
  ECLIPSIS_ERROR @description("Missing or incorrect eclipsis")
  DOTTED_LETTER @description("Old script ċ/ṡ confusion")
  ABBREVIATION @description("Unrecognized abbreviation")
}

// ============================================================================
// DOCUMENT STRUCTURE VALIDATION
// ============================================================================

// Document structure extracted from OCR
class DocumentStructure {
  // Document type
  document_type DocumentTypeOcr @description("Type of document")

  // Structure elements
  has_title bool @description("Document has identifiable title")
  title string? @description("Extracted title")

  has_headers bool @description("Document has section headers")
  headers HeaderElement[]? @description("Extracted headers")

  has_tables bool @description("Document contains tables")
  tables TableElement[]? @description("Extracted tables")

  has_lists bool @description("Document contains lists")
  list_count int @description("Number of lists")

  // Layout
  page_count int @description("Number of pages")
  column_count int @description("Number of columns per page")
  reading_order ReadingOrder @description("Detected reading order")
  @@stream.done
}

// Document types
enum DocumentTypeOcr {
  CURRICULUM @description("NCCA curriculum document")
  EXAM_PAPER @description("SEC examination paper")
  COURSE_MATERIAL @description("Educational course material")
  TEXTBOOK @description("Textbook or reference")
  WORKSHEET @description("Student worksheet")
  CIRCULAR @description("Department circular")
  UNKNOWN @description("Unknown document type")
}

// Header element from document
class HeaderElement {
  level int @description("Header level (1=main, 2=sub, etc.)")
  text string @description("Header text")
  page int @description("Page number")
  position int @description("Character position")
}

// Table element from document
class TableElement {
  row_count int @description("Number of rows")
  column_count int @description("Number of columns")
  has_header_row bool @description("First row is header")
  content string @description("Table content as markdown")
  page int @description("Page number")
}

// Reading order detection
enum ReadingOrder {
  LEFT_TO_RIGHT @description("Standard LTR reading")
  RIGHT_TO_LEFT @description("RTL reading")
  TOP_TO_BOTTOM @description("Vertical reading")
  MULTI_COLUMN @description("Multiple columns")
}

// ============================================================================
// MODEL COMPARISON VALIDATION
// ============================================================================

// Comparison between multiple OCR models
class ModelComparisonResult {
  // Document info
  document_id string @description("Document identifier")
  document_path string @description("File path")

  // Models compared
  models_tested string[] @description("Models that were compared")
  total_models int @description("Number of models tested")

  // Best result
  best_model_id string @description("Model with best result")
  best_confidence float @description("Best confidence score")
  best_reasoning string @description("Why this model was selected")

  // Comparison details
  per_model_results ModelResult[] @description("Results per model")

  // Consensus analysis
  text_consensus TextConsensus @description("How much models agree")

  // Irish-specific
  best_irish_model string? @description("Best model for Irish content")
  irish_best_reasoning string? @description("Why for Irish")
}

// Result from a single model
class ModelResult {
  model_id string @description("Model identifier")
  model_name string @description("Display name")
  backend string @description("Backend (llama-swap, mlx, etc.)")

  confidence float @description("Confidence score 0-1")
  text_length int @description("Output text length")
  processing_seconds float @description("Time taken")

  quality OCRQuality @description("Quality assessment")
  irish_quality IrishContentQuality? @description("Irish quality if applicable")

  strengths string[] @description("What this model did well")
  weaknesses string[] @description("Where this model struggled")
}

// Text consensus between models
class TextConsensus {
  agreement_score float @description("How much models agree 0-1")
  common_text string @description("Text all models extracted")
  disagreement_regions TextDisagreement[]? @description("Where models differ")
  recommended_text string @description("Best combined result")
}

// Region where models disagree
class TextDisagreement {
  position int @description("Character position")
  length int @description("Length of disagreement")
  variants DisagreementVariant[] @description("Different readings")
  recommended string @description("Recommended reading")
}

// Variant reading from a model
class DisagreementVariant {
  model_id string @description("Model ID")
  text string @description("Model's reading")
  confidence float @description("Model's confidence")
}

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

// Validate OCR output quality
function ValidateOCRResult(
  ocr_text: string,
  model_id: string,
  processing_time: float
) -> OCRValidationResult {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Validate Irish language quality specifically
function ValidateIrishContent(
  text: string
) -> IrishContentQuality {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Extract document structure
function ExtractDocumentStructure(
  ocr_text: string,
  page_count: int
) -> DocumentStructure {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Compare results from multiple OCR models
function CompareOCRModels(
  document_id: string,
  model_results: ModelResult[]
) -> ModelComparisonResult {  client ExtractEn
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
// TEST BLOCKS (DEPRECATED 2026-08-15)
//
// The two test blocks below were written for an older BAML CLI version
// and use syntax that is no longer valid in baml-py 0.223.0:
//
//   - Float literals (e.g. `processing_time 2.5`)
//
//   - Inline JSON-style test data (e.g. `strengths ["math notation"]`)
//
//   - Old enum syntax (e.g. `quality #GOOD`)
//
// These have been commented out to allow `baml-cli generate` to
// succeed (which now activates the TypeScript codegen at
// `baml_client_ts/` per `centralized-schema-registry` capability).
//
// To re-enable these tests, rewrite them using the new BAML test
// format (see https://docs.boundaryml.com/v0.223.0/get-started/testing).
// The test data references models (`qwen3-vl-8b`, `gemma-4-26B-A4B`)
// that exist in `MODEL_REGISTRY` — these are valid model keys.
//
// Removed tests:
//   - test ValidateOCRResult { ... }
//   - test CompareOCRModels { ... }
// ============================================================================

// ============================================================================
// CLIENT DEFINITIONS
// ============================================================================

client<llm> Validator {
  provider openai
  options {
    // MODEL_REGISTRY: family="text_llm", role="fast" → "gpt-4o-mini"
    // Canonical home: meaisinfhoghlaim/models/model_registry.py
    model "gpt-4o-mini"
    temperature 0.1
  }
}

client<llm> IrishValidator {
  provider openai
  options {
    // MODEL_REGISTRY: family="text_llm", role="strong" → "gpt-4o"
    // (legacy; the canonical registry marks "gpt-4o" as available)
    model "gpt-4o"  // Better for Irish
    temperature 0.1
  }
}

client<llm> Analyzer {
  provider openai
  options {
    // MODEL_REGISTRY: family="text_llm", role="strong" → "gpt-4o"
    // Canonical home: meaisinfhoghlaim/models/model_registry.py
    model "gpt-4o"
    temperature 0.2
  }
}
