// BAML Client Configuration for the 5 image_gen MODEL_REGISTRY entries
//
// Per the 2026-08-15 centralized-model-registry openspec change:
// model strings are sourced from `meaisinfhoghlaim.models.model_registry`
// at runtime via the `model_for(family, role)` helper. The 5 clients
// below map to the 5 image_gen roles:
//
//   - role="default"   → flux2-dev       (subject illustrations)
//   - role="fast"      → z-image-turbo   (fast iteration)
//   - role="bilingual" → qwen-image      (bilingual EN/GA)
//   - role="legacy"    → sdxl            (legacy SDXL)
//   - role="diagrams"   → fibo            (diagrams + textures)
//
// When the image_gen stack is deployed (InvokeAI / ComfyUI / llama.cpp),
// replace the `InvokeAILocalImageGen` endpoint with the production
// server. The 5 client blocks below remain unchanged.
//
// Reference:
//   openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
//   specs/image-generation-agent/spec.md

// ====== Image-gen stack endpoint (default; replace when deployed) ======
//
// Routes all 5 image_gen roles through the local InvokeAI instance.
// In dev (no GPU), InvokeAI returns a stub image; in production it
// dispatches to the configured model based on the request payload's
// `model` field.
//
// When deployed, the InvokeAI URL comes from the openchamber-infra
// stack's `InvokeAILocalImageGen` container (per openspec/changes/
// 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
// Phase L).

client<llm> InvokeAILocalImageGen {
  provider "openai-generic"
  options {
    base_url env.INVOKEAI_BASE_URL
    api_key env.INVOKEAI_API_KEY
    // MODEL_REGISTRY: family="image_gen", role="default" → "local/image/flux2-dev"
    // The model parameter is overridden at runtime by the agent via
    // model_for(family='image_gen', role). Each invocation sets the
    // model explicitly via the litellm_alias field.
    model "local/image/flux2-dev"
  }
}

// ====== Per-role client aliases (active) ======
//
// MODEL_REGISTRY: family="image_gen", role="default" → "local/image/flux2-dev"
// Used for subject illustrations (canonical 2D assets)

client<llm> ImageGenDefault {
  provider "openai-generic"
  options {
    base_url env.INVOKEAI_BASE_URL
    api_key env.INVOKEAI_API_KEY
    model "local/image/flux2-dev"
  }
}

// MODEL_REGISTRY: family="image_gen", role="fast" → "local/image/z-image-turbo"
// Used for fast-iteration 2D assets

client<llm> ImageGenFast {
  provider "openai-generic"
  options {
    base_url env.INVOKEAI_BASE_URL
    api_key env.INVOKEAI_API_KEY
    model "local/image/z-image-turbo"
  }
}

// MODEL_REGISTRY: family="image_gen", role="bilingual" → "local/image/qwen-image"
// Used for bilingual EN/GA illustrations

client<llm> ImageGenBilingual {
  provider "openai-generic"
  options {
    base_url env.INVOKEAI_BASE_URL
    api_key env.INVOKEAI_API_KEY
    model "local/image/qwen-image"
  }
}

// MODEL_REGISTRY: family="image_gen", role="legacy" → "local/image/sdxl"
// Used for legacy SDXL generation (backward compatibility)

client<llm> ImageGenLegacy {
  provider "openai-generic"
  options {
    base_url env.INVOKEAI_BASE_URL
    api_key env.INVOKEAI_API_KEY
    model "local/image/sdxl"
  }
}

// MODEL_REGISTRY: family="image_gen", role="diagrams" → "local/image/fibo"
// Used for diagrams + charts + Babylon.js textures

client<llm> ImageGenDiagrams {
  provider "openai-generic"
  options {
    base_url env.INVOKEAI_BASE_URL
    api_key env.INVOKEAI_API_KEY
    model "local/image/fibo"
  }
}

// ====== BAML extraction function for image asset metadata ======
//
// The agent calls this function to extract structured metadata from
// raw user prompts (e.g. "Celtic round tower at sunset, oil painting").
// Returns the canonical asset metadata that gets registered in CocoIndex.

class ImageAssetMetadata {
  subject string
  style string?
  palette string[]?
  width int
  height int
  language "en" | "ga" | "both"
  baml_routing_role string  // one of: default, fast, bilingual, legacy, diagrams
  cocoindex_record_id string
  created_at string
}

function ExtractImageAssetMetadata(prompt: string, language: string?) -> ImageAssetMetadata {
  client ImageGenDefault
  prompt #"
    {{ _.role("user") }}
    Extract structured image-asset metadata from the user's prompt below.

    Return JSON with:
    - subject: the canonical subject name (e.g. "irish_round_tower", "celtic_knotwork", "tuatha_filigree")
    - style: the artistic style (e.g. "oil-painting", "pixel-art", "cel-shaded", "ukiyo-e", "watercolor")
    - palette: the colour palette as an array of hex codes (if the prompt mentions specific colours)
    - width: the canonical width in pixels (1024 for square, 1536 for landscape, 768 for portrait)
    - height: the canonical height in pixels (matching the width/aspect ratio)
    - language: "en" for English, "ga" for Irish/Gaeilge, "both" for bilingual
    - baml_routing_role: which image_gen role to use ("default" for subject illustrations, "fast" for iteration, "bilingual" for EN/GA, "legacy" for SDXL, "diagrams" for charts)

    {{ ctx.output_format }}

    PROMPT: {{ prompt }}
  "#

  catch_all (err) {
    ImageAssetMetadata {
      subject "",
      style null,
      palette null,
      width 0,
      height 0,
      baml_routing_role "",
      cocoindex_record_id "",
      created_at "",
    }
  }
}

// ====== Style-match function (for the style_match tool) ======
//
// Returns N style-preserved variant prompts for the style_match tool.

class StyleMatchVariants {
  reference_prompt string
  target_prompt string
  variants StyleMatchVariant[]
}

class StyleMatchVariant {
  index int
  prompt string
  rationale string
}

function ExtractStyleMatchVariants(reference_prompt: string, target_prompt: string, count: int) -> StyleMatchVariants {
  client ImageGenBilingual
  prompt #"
    {{ _.role("user") }}
    Given a reference style description and a target subject to render,
    generate {{ count }} distinct style-preserving variant prompts.

    Each variant should:
    - Preserve the reference style's key visual elements (colour palette, line work, era)
    - Render the target subject with a slightly different framing or composition
    - Be unambiguous enough for the image_gen model to render distinct images

    Return JSON:
    - variants: array of {index, prompt, rationale}

    {{ ctx.output_format }}

    REFERENCE STYLE: {{ reference_prompt }}
    TARGET SUBJECT: {{ target_prompt }}
  "#

  catch_all (err) {
    StyleMatchVariants {
      reference_prompt "",
      target_prompt "",
      variants null,
    }
  }
}
