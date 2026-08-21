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
  @@stream.done
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

function ExtractStyleFeatures(artwork: image) -> StyleFeatures {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function CreateStyleTransferSpec(
  content_prompt: string,
  style_reference: image
) -> StyleTransferSpec {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function BlendStyles(
  style_a: image,
  style_b: image,
  blend_ratio: float,
  content: string
) -> StyleBlend {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function GenerateSeriesPrompts(
  base_style: image,
  count: int,
  variation_axis: string
) -> string[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function AnalyzeForIPAdapter(artwork: image) -> StyleEmbedding {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Album-specific functions

function GenerateAlbumCoverSpec(
  album_title: string,
  artist_name: string,
  track_list: string[],
  style_reference: image?,
  genre: string
) -> StyleTransferSpec {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function GenerateSingleCoverVariation(
  original_album_cover: image,
  single_title: string
) -> string {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// test style_extraction {
//   functions [ExtractStyleFeatures]
//   args {
//     artwork {
//       file "../test_images/sample_artwork.jpg"
//     }
//   }
// }

// test style_transfer {
//   functions [CreateStyleTransferSpec]
//   args {
//     content_prompt "abstract ocean waves at sunset"
//     style_reference {
//       file "../test_images/sample_artwork.jpg"
//     }
//   }
// }
