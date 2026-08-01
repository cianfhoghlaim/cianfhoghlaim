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

enum MusicGenre {
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
  genre_associations MusicGenre[] @description("Music genres this artwork evokes")
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
  genre_associations MusicGenre[]
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

function AnalyzeArtwork(artwork: image) -> ArtworkAnalysis {
  client ArtworkAnalyzer
  prompt #"
    You are an expert album artwork analyst specializing in visual design,
    music genres, and generative art.

    Analyze this album artwork image in detail. Extract comprehensive
    information about its visual characteristics, style, and mood.

    Pay special attention to:
    - Visual style and artistic techniques
    - Color palette and color relationships
    - Composition and visual balance
    - Mood and emotional impact
    - Music genre associations based on visual style
    - Any text or typography
    - Artistic influences or movements

    Generate a prompt that could recreate this visual style for new artwork.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ artwork }}
  "#
}

function QuickAnalyzeArtwork(artwork: image) -> QuickAnalysis {
  client FastAnalyzer
  prompt #"
    Quickly analyze this album artwork. Identify the main visual style,
    mood, dominant color, and associated music genres.

    Keep the description brief (1-2 sentences).

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ artwork }}
  "#
}

function CompareArtworkStyles(artwork1: image, artwork2: image) -> StyleComparison {
  client ArtworkAnalyzer
  prompt #"
    Compare these two album artworks and analyze their stylistic similarities
    and differences.

    Calculate a similarity score (0-1) based on:
    - Visual style overlap
    - Color palette similarity
    - Mood alignment
    - Composition similarities

    Identify what styles and moods they share, and what makes them different.

    Create a generation prompt that combines the best elements of both styles.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    First artwork:
    {{ artwork1 }}

    Second artwork:
    {{ artwork2 }}
  "#
}

function GenerateArtworkSpec(
  subject: string,
  reference_artwork: image?,
  target_genre: MusicGenre,
  preferred_mood: MoodCategory?
) -> GenerationSpec {
  client ArtworkAnalyzer
  prompt #"
    Create a detailed specification for generating new album artwork.

    Subject/concept: {{ subject }}
    Target music genre: {{ target_genre }}
    {{ #if preferred_mood }}Preferred mood: {{ preferred_mood }}{{ /if }}

    {{ #if reference_artwork }}
    Use this reference artwork for style inspiration:
    {{ reference_artwork }}
    {{ /if }}

    Generate a complete specification including:
    - Detailed generation prompt
    - Negative prompt (what to avoid)
    - Style references
    - Color palette suggestions
    - Composition type
    - Recommended AI model

    The prompt should be optimized for image generation models like FLUX or SDXL.

    {{ ctx.output_format }}
  "#
}

function ExtractColorPalette(artwork: image) -> ColorInfo[] {
  client FastAnalyzer
  prompt #"
    Extract the color palette from this album artwork.

    Identify the 5-8 most prominent colors, including:
    - Dominant background colors
    - Primary subject colors
    - Accent/highlight colors

    For each color provide:
    - Exact hex code
    - Common color name
    - Approximate percentage of the image

    Order by prominence (most dominant first).

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ artwork }}
  "#
}

function GenerateVariationPrompt(artwork: image, variation_type: string) -> string {
  client FastAnalyzer
  prompt #"
    Analyze this album artwork and create a prompt for generating a variation.

    Variation type requested: {{ variation_type }}

    The prompt should:
    - Maintain the core visual style
    - Apply the requested variation
    - Be optimized for FLUX or SDXL

    Return only the generation prompt, no explanation.

    {{ _.role('user') }}
    {{ artwork }}
  "#
}

// Tests

test analyze_abstract {
  functions [QuickAnalyzeArtwork]
  args {
    artwork {
      url "https://i.scdn.co/image/ab67616d00001e02..."
    }
  }
}

test color_extraction {
  functions [ExtractColorPalette]
  args {
    artwork {
      file "../test_images/sample_artwork.jpg"
    }
  }
}
