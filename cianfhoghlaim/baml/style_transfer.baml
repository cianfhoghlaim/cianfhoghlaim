// BAML Schemas for Style Transfer
// Functions for analyzing and transferring visual styles between artworks

// Style transfer-specific types

class StyleFeatures {
  color_temperature string @description("warm, cool, neutral")
  color_saturation string @description("vibrant, muted, desaturated")
  contrast_level string @description("high, medium, low")
  line_quality string @description("sharp, soft, organic, geometric")
  texture_type string @description("smooth, grainy, noisy, detailed")
  lighting_style string @description("soft, harsh, ambient, dramatic")
  perspective string @description("flat, depth, isometric, dynamic")
  edge_treatment string @description("clean, blurred, glowing, rough")
}

class StyleTransferSpec {
  content_description string @description("What to depict")
  style_features StyleFeatures @description("Style characteristics to apply")
  color_mapping ColorInfo[] @description("Colors to use from reference")
  composition_guide string @description("How to arrange elements")
  generation_prompt string @description("Complete prompt for generation")
  negative_prompt string @description("What to avoid")
  cfg_scale float @description("Recommended CFG scale 1-15")
  steps int @description("Recommended inference steps")
}

class StyleEmbedding {
  style_vector float[] @description("768-dim style embedding")
  key_features string[] @description("Top style features")
  prompt_keywords string[] @description("Keywords capturing style")
}

class StyleBlend {
  blend_ratio float @description("0-1, how much of style B vs A")
  blended_prompt string
  blended_negative string
  expected_characteristics string[]
}

// Style transfer functions

function ExtractStyleFeatures(artwork: image) -> StyleFeatures {
  client ArtworkAnalyzer
  prompt #"
    Analyze the visual style features of this artwork in technical terms.

    Examine:
    - Color temperature (warm/cool/neutral tones)
    - Color saturation levels
    - Contrast and tonal range
    - Line quality and edge treatment
    - Texture characteristics
    - Lighting approach
    - Spatial perspective
    - Edge treatment (sharp, blurred, etc.)

    Describe each feature concisely for style transfer purposes.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ artwork }}
  "#
}

function CreateStyleTransferSpec(
  content_prompt: string,
  style_reference: image
) -> StyleTransferSpec {
  client ArtworkAnalyzer
  prompt #"
    Create a complete style transfer specification.

    Content to generate: {{ content_prompt }}

    Analyze the style reference image and extract its key visual characteristics.
    Create a generation prompt that will produce the requested content in the
    style of the reference.

    The prompt should be optimized for FLUX.2-dev or SDXL and include:
    - Main subject description
    - Style modifiers from the reference
    - Color palette guidance
    - Composition suggestions
    - Technical quality terms

    Also provide a negative prompt and recommended parameters.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    Style reference:
    {{ style_reference }}
  "#
}

function BlendStyles(
  style_a: image,
  style_b: image,
  blend_ratio: float,
  content: string
) -> StyleBlend {
  client ArtworkAnalyzer
  prompt #"
    Blend two visual styles for generating new artwork.

    Blend ratio: {{ blend_ratio }} (0 = all style A, 1 = all style B)
    Content to generate: {{ content }}

    Analyze both style references:

    Style A (first image):
    {{ style_a }}

    Style B (second image):
    {{ style_b }}

    Create a blended generation prompt that combines elements from both styles
    according to the blend ratio. Describe what visual characteristics will
    result from this blend.

    {{ ctx.output_format }}
  "#
}

function GenerateSeriesPrompts(
  base_style: image,
  count: int,
  variation_axis: string
) -> string[] {
  client ArtworkAnalyzer
  prompt #"
    Generate a series of {{ count }} related artwork prompts based on this style reference.

    Variation axis: {{ variation_axis }}
    (e.g., "color temperature", "complexity", "mood progression", "time of day")

    Analyze the base style:
    {{ base_style }}

    Create {{ count }} prompts that:
    - Maintain the core visual style
    - Progressively vary along the specified axis
    - Form a cohesive series

    Return an array of generation prompts.

    {{ ctx.output_format }}
  "#
}

function AnalyzeForIPAdapter(artwork: image) -> StyleEmbedding {
  client FastAnalyzer
  prompt #"
    Analyze this artwork for IP-Adapter style transfer.

    Extract:
    - Key visual features that define the style
    - Keywords that capture the essence
    - Technical attributes for style matching

    The features should be specific enough to guide style transfer
    while being general enough to apply to different content.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ artwork }}
  "#
}

// Album-specific functions

function GenerateAlbumCoverSpec(
  album_title: string,
  artist_name: string,
  track_list: string[],
  style_reference: image?,
  genre: string
) -> StyleTransferSpec {
  client ArtworkAnalyzer
  prompt #"
    Create a specification for generating album artwork.

    Album: "{{ album_title }}" by {{ artist_name }}
    Genre: {{ genre }}

    Tracks:
    {{ #each track_list }}
    - {{ this }}
    {{ /each }}

    {{ #if style_reference }}
    Use this style reference for visual direction:
    {{ style_reference }}
    {{ /if }}

    Consider:
    - Album title and artist name (but don't include text in the image)
    - Track themes and mood
    - Genre conventions for cover art
    - Visual narrative that represents the album

    Generate a complete specification for the cover artwork.

    {{ ctx.output_format }}
  "#
}

function GenerateSingleCoverVariation(
  original_album_cover: image,
  single_title: string
) -> string {
  client FastAnalyzer
  prompt #"
    Create a prompt for generating a single cover that matches the album art style.

    Original album cover for style reference:
    {{ original_album_cover }}

    Single title: "{{ single_title }}"

    The single cover should:
    - Match the visual style of the album
    - Be recognizably related
    - Have a subtle variation that makes it distinct

    Return only the generation prompt.
  "#
}

test style_extraction {
  functions [ExtractStyleFeatures]
  args {
    artwork {
      file "../test_images/sample_artwork.jpg"
    }
  }
}

test style_transfer {
  functions [CreateStyleTransferSpec]
  args {
    content_prompt "abstract ocean waves at sunset"
    style_reference {
      file "../test_images/sample_artwork.jpg"
    }
  }
}
