// =============================================================================
// BAML Image Generation Schemas
// =============================================================================
// Used by the oideachais/data_platform/dagster_assets/asset_generation.py
// Dagster asset. Takes a learning outcome from a subject syllabus and:
//   1. Generates an ImagePromptSpec (camera, lighting, mood, style)
//   2. Builds a Bria FIBO JSON config (deterministic image gen)
//   3. Optionally renders via Z-Image-Turbo / Qwen-Image / FLUX.2
//
// The rendered image is uploaded to Garage S3 at
// s3://ducklake-assets/study/{subject}/{cycle}/{outcome_id}.png
// =============================================================================

// =============================================================================
// Image spec
// =============================================================================

enum CameraAngle {
  WIDE
  MEDIUM
  CLOSE_UP
  OVERHEAD
  MACRO
  ISOMETRIC
  THREE_QUARTER
}

enum LightingStyle {
  NATURAL
  STUDIO
  DRAMATIC
  GOLDEN_HOUR
  MOONLIT
  NEON
  CANDLELIT
  BACKLIT
}

enum Mood {
  NEUTRAL
  ENCOURAGING
  FOCUSED
  CALM
  INSPIRING
  CURIOUS
  PLAYFUL
  SERIOUS
}

enum VisualStyle {
  EDUCATIONAL_DIAGRAM       // textbook-style infographic
  ILLUSTRATION             // editorial illustration
  PHOTOREALISTIC           // photo-quality
  SKETCH                   // hand-drawn / chalkboard
  FLAT_VECTOR              // flat colour vector
  ISOMETRIC_DIAGRAM        // 3D axonometric diagram
  WATERCOLOUR
  NEON                     // dark mode accent
}

enum ImagePurpose {
  STUDY_CARD         // a flashcard-style image
  EXAM_PREP          // past-paper style diagram
  CONCEPT_INTRO      // introduces a new concept
  WORKED_EXAMPLE     // step-by-step illustration
  MNEMONIC           // memory aid
  ILLUSTRATION       // general illustration
}

class ImagePromptSpec {
  purpose ImagePurpose
  subject_text string @description("The subject in plain language (e.g. 'photosynthesis cell', 'quadratic equation y = x^2 + 2x - 3')")
  subject_domain string @description("High-level domain (mathematics, biology, history, irish, ...)")
  camera_angle CameraAngle
  lighting LightingStyle
  mood Mood
  style VisualStyle
  composition string @description("Layout description (e.g. 'centered subject with annotated labels around it')")
  text_overlays string[] @description("Text to overlay on the image (formulas, labels, key terms)")
  negative_prompts string[] @description("What to avoid (photorealistic photos for diagrams, photographic faces, copyrighted characters)")
  cta_text string? @description("Optional call-to-action or tagline")
  bria_json_config string @description("The Bria FIBO JSON config (filled by BuildFIBOConfig)")
  irish_translation string? @description("Irish (Gaeilge) translation of the subject_text + overlays, if available")
}

// =============================================================================
// FIBO JSON config
// =============================================================================

class FIBOConfig {
  prompt string @description("Positive text prompt (concise)")
  negative_prompt string @description("Negative prompt (what to avoid)")
  seed int @description("Deterministic seed for reproducibility")
  width int @description("Image width in pixels (default 1024)")
  height int @description("Image height in pixels (default 1024)")
  steps int @description("Number of inference steps (default 30)")
  cfg_scale float @description("Classifier-free guidance scale (default 7.0)")
  sampler string @description("Sampler name (e.g. 'euler_a', 'dpmpp_2m')")
  scheduler string @description("Scheduler (e.g. 'karras')")
  style_preset string? @description("Optional style preset (e.g. 'photographic', 'cinematic')")
  camera json @description("Camera parameters (focal_length, aperture, etc.)")
  lighting json @description("Lighting parameters (key_light_angle, fill_intensity, etc.)")
  composition json @description("Composition parameters (rule_of_thirds, depth_of_field)")
  output_format string @description("Output format (png, jpeg, webp)")
  metadata json @description("Free-form metadata (subject, outcome_id, syllabus_path)")
}

// =============================================================================
// Functions
// =============================================================================

function ExtractImagePrompt(
  outcome_text: string,
  subject: string,
  cycle: string,
  purpose: ImagePurpose
) -> ImagePromptSpec {
  client LiteLLM
  prompt #"
    You are an expert educational illustrator specialising in {subject} for the
    {cycle} cycle. You are designing a single study-asset image whose purpose is
    to help a student learn the following learning outcome:

    <outcome>
    {{ outcome_text }}
    </outcome>

    Design an image that captures the essence of this outcome. The image will
    be rendered by the Bria FIBO model (JSON-config driven) with a fallback
    to Qwen-Image / Z-Image-Turbo.

    Choose:
      - purpose: {{ purpose }} (already specified)
      - camera_angle, lighting, mood, style, composition
      - text_overlays: short labels, formulas, or definitions
      - negative_prompts: things to avoid
      - cta_text: optional tagline

    If the outcome is in English but the student is Irish, provide an
    `irish_translation` of subject_text and text_overlays.

    Return the spec as {{ ctx.output_format }}.
  "#
}

function BuildFIBOConfig(
  spec: ImagePromptSpec,
  outcome_id: string,
  syllabus_path: string
) -> FIBOConfig {
  client LiteLLM
  prompt #"
    You translate an educational ImagePromptSpec into a deterministic Bria
    FIBO JSON config. The config will be sent verbatim to
    http://mlx-omni:10240/v1/images/generations (or a fallback generator).

    Spec:
    - purpose:       {{ spec.purpose }}
    - subject:       {{ spec.subject_text }}
    - camera:        {{ spec.camera_angle }}
    - lighting:      {{ spec.lighting }}
    - mood:          {{ spec.mood }}
    - style:         {{ spec.style }}
    - composition:   {{ spec.composition }}
    - text_overlays: {{ spec.text_overlays }}
    - negatives:     {{ spec.negative_prompts }}
    - cta:           {{ spec.cta_text }}

    Context:
    - outcome_id:    {{ outcome_id }}
    - syllabus_path: {{ syllabus_path }}

    Construct a FIBOConfig with:
      - seed: deterministic — derive from outcome_id (use SHA-256 first 8 hex digits)
      - width/height: 1024×1024 by default
      - steps: 30
      - cfg_scale: 7.0
      - camera / lighting / composition: fill in with the chosen values
      - metadata.outcome_id: {{ outcome_id }}
      - metadata.syllabus_path: {{ syllabus_path }}

    Return the config as {{ ctx.output_format }}.
  "#
}
