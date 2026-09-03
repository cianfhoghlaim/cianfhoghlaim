// BAML Schemas for Artwork Analysis
// Type-safe extraction of visual characteristics from album artwork

// Enums for visual style categories

enum ArtStyle {
  ABSTRACT
  PHOTOGRAPHIC
  ILLUSTRATED
  MINIMALIST
  PSYCHEDELIC
  GEOMETRIC
  SURREAL
  COLLAGE
  TYPOGRAPHIC
  GRADIENT
  RETRO
  FUTURISTIC
  ORGANIC
  GLITCH
  THREE_D
}

enum MoodCategory {
  ENERGETIC
  CALM
  DARK
  UPLIFTING
  MELANCHOLIC
  MYSTERIOUS
  DREAMY
  AGGRESSIVE
  NOSTALGIC
  ETHEREAL
}

enum ColorScheme {
  MONOCHROMATIC
  COMPLEMENTARY
  ANALOGOUS
  TRIADIC
  SPLIT_COMPLEMENTARY
  WARM
  COOL
  NEUTRAL
  HIGH_CONTRAST
  PASTEL
}

enum CompositionType {
  CENTERED
  RULE_OF_THIRDS
  ASYMMETRIC
  RADIAL
  DIAGONAL
  FRAMED
  MINIMALIST
  COMPLEX
}

enum MusicGenreArtwork {
  ELECTRONIC
  AMBIENT
  DNB
  LIQUID
  TECHNO
  HOUSE
  CHILLOUT
  JAZZ
  CLASSICAL
  EXPERIMENTAL
  HIP_HOP
  ROCK
  POP
}

// Core data classes

class ColorInfo {
  hex string @description("Hex color code like #FF5733")
  name string? @description("Common color name if applicable")
  percentage float @description("Percentage of image area")
  @@stream.done
}

class StyleAnalysis {
  primary_style ArtStyle @description("Main visual style")
  secondary_styles ArtStyle[] @description("Supporting visual styles")
  color_scheme ColorScheme @description("Color harmony type")
  dominant_colors ColorInfo[] @description("Top 3-5 dominant colors")
  accent_colors ColorInfo[] @description("Accent/highlight colors")
  mood MoodCategory @description("Primary emotional mood")
  mood_keywords string[] @description("Additional mood descriptors")
  composition CompositionType @description("Composition style")
  visual_weight string @description("heavy, light, or balanced")
  texture string @description("smooth, grainy, textured, etc.")
  lighting string @description("bright, dark, high_contrast, etc.")
  depth string @description("flat, layered, 3d")
  movement string @description("static, dynamic, flowing")
}

class ArtworkAnalysis {
  description string @description("2-3 sentence description of the artwork")
  style StyleAnalysis @description("Detailed style analysis")
  genre_associations MusicGenreArtwork[] @description("Music genres this artwork evokes")
  visual_elements string[] @description("Key visual elements present")
  text_detected string? @description("Any text visible in the artwork")
  subjects string[] @description("Main subjects or motifs")
  influences string[] @description("Artistic movements or influences")
  generation_prompt string @description("Prompt to recreate this style")
}

class QuickAnalysis {
  description string @description("Brief description")
  primary_style ArtStyle
  mood MoodCategory
  dominant_color string @description("Main color hex")
  genre_associations MusicGenreArtwork[]
}

class StyleComparison {
  similarity_score float @description("0-1 score of style similarity")
  shared_styles ArtStyle[]
  shared_moods MoodCategory[]
  key_differences string[]
  combined_generation_prompt string @description("Prompt combining both styles")
}

class GenerationSpec {
  prompt string @description("Full generation prompt")
  negative_prompt string @description("What to avoid")
  style_references ArtStyle[]
  color_palette ColorInfo[]
  mood MoodCategory
  composition CompositionType
  suggested_model string @description("Recommended model: flux, sdxl, etc.")
}

// Extraction functions

function AnalyzeArtwork(artwork: image) -> ArtworkAnalysis {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function QuickAnalyzeArtwork(artwork: image) -> QuickAnalysis {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function CompareArtworkStyles(artwork1: image, artwork2: image) -> StyleComparison {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function GenerateArtworkSpec(
  subject: string,
  reference_artwork: image?,
  target_genre: MusicGenreArtwork,
  preferred_mood: MoodCategory?
) -> GenerationSpec {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function ExtractColorPalette(artwork: image) -> ColorInfo[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    ColorInfo[] {}
  }
}

function GenerateVariationPrompt(artwork: image, variation_type: string) -> string {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Tests

// test analyze_abstract {
//   functions [QuickAnalyzeArtwork]
//   args {
//     artwork {
//       url "https://i.scdn.co/image/ab67616d00001e02..."
//     }
//   }
// }

// test color_extraction {
//   functions [ExtractColorPalette]
//   args {
//     artwork {
//       file "../test_images/sample_artwork.jpg"
//     }
//   }
// }
