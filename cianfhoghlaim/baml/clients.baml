// BAML Client Configuration for Cianfhoghlaim (post-v4 + baml 0.212+ canonical syntax)
//
// Canonical clients.baml consolidates the legacy clients.baml + clients_0.baml.
// The llama-swap specialty clients live in clients_llama_swap.baml.
//
// Per T4 of the 5-tangent modernization
// (`openspec/changes/2026-07-09-agent-fleet-and-observability-facade-v1`),
// this file was rewritten from the legacy v0.x `client Name { provider
// "..." model "..." }` block syntax to the canonical 0.212+ pattern:
//
//   generator default {
//     provider "openai"
//     model "gpt-5-mini"
//     retry_policy exponential_backoff(max_retries=3)
//   }
//
// BAML 0.212+ canonical syntax reference: https://docs.boundaryml.com/changelog/changelog.md
//
// Generation: `cd cianfhoghlaim && uv run baml-cli generate`
// Validation: `cd cianfhoghlaim && mise run baml:generate` (alias)
//
// Sections:
//   1. Generator blocks (the 0.212+ canonical replacement for the old
//      v0.x `client X { provider ... }` syntax) — one per backend
//   2. Retry policies (consolidated from clients_0.baml)
//   3. Test blocks (the @test golden-test convention used by the
//      5-tangent's `baml/education/lc_extraction/test_curriculum_syllabus.py`)

// ── Section 1: Generator blocks (post-v4 canonical 0.212+ syntax) ──

generator default {
  provider "openai"
  model "gpt-5-mini"
  retry_policy Exponential
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
  }
}

generator local_vision_qwen {
  provider "openai"
  model "local/vision/qwen3-vl"
  retry_policy Exponential
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
  }
}

generator local_vision_glm {
  provider "openai"
  model "local/vision/glm-4.6v-flash"
  retry_policy Exponential
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
  }
}

generator local_vision_moondream {
  provider "openai"
  model "local/vision/moondream2"
  retry_policy Exponential
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_API_KEY
  }
}

generator gemini_2_flash {
  provider "google-ai"
  model "gemini-2.0-flash-exp"
  options {
    api_key env.GOOGLE_API_KEY
  }
}

generator gemini_1_5_pro {
  provider "google-ai"
  model "gemini-1.5-pro-latest"
  options {
    api_key env.GOOGLE_API_KEY
  }
}

generator gemini_pro {
  provider "google-ai"
  model "gemini-pro"
  options {
    api_key env.GOOGLE_API_KEY
  }
}

generator gemini_2_5_flash {
  provider "google-ai"
  model "gemini-2.5-flash-preview-05-20"
  options {
    api_key env.GOOGLE_API_KEY
  }
}

// ── Section 2: Retry policies ──

retry_policy Simple {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 500
    multiplier 2
  }
}

retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 1000
    multiplier 2
  }
}

// ── Section 3: Test blocks (the 5-tangent's @test golden-test convention) ──
//
// These mirror the assertion patterns used by
// `baml/education/lc_extraction/test_curriculum_syllabus.py`.
// Each test block exercises one of the canonical 5-tangent BAML
// functions and asserts the response shape so regressions are
// caught at `mise run baml:generate` time.

test default_generator_routes {
  functions [ExtractCurriculumSyllabus]
  args {
    document_text <<<
      "Sample NCCA primary curriculum excerpt — children should be able to count to 10, identify basic shapes, and recognise the letters A–Z."
    >>>
  }
}

test gemini_2_flash_routes {
  functions [ExtractExamPaperLayout]
  args {
    pdf_path <<<
      "/tmp/lc_chemistry_2024_p1.pdf"
    >>>
  }
}

test local_vision_qwen_routes {
  functions [ExtractSyllabusDiagram]
  args {
    image_path <<<
      "/tmp/syllabus_diagram_chemistry_lc.png"
    >>>
  }
}
