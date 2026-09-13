// BAML extraction schemas for the YouTube cross-source knowledge graph.
//
// NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1).
//
// Two extraction functions drive the cross-source view across the
// HuggingFace Post-training Agents playlist + the Google Cloud AI
// Agent Crash Course playlist:
//
//   ExtractCrossSourceConcept — finds agentic-AI concepts shared
//                                between the 2 playlists (one row per
//                                concept, with hf_video_ids[] +
//                                gc_video_ids[] + confidence +
//                                source_evidence[])
//   CompareCrossSourcePerspectives — compares how the 2 playlists
//                                     discuss a single shared concept
//                                     (one row per comparison)
//
// The 3 classes are:
//   CrossSourceConcept   — a concept mentioned across both playlists
//   SnippetEvidence      — one transcript snippet citing the concept
//   CrossSourceComparison — perspective-difference row for 2 videos
//
// All routes through the canonical `ExtractEn` client from
// `baml_src/clients.baml` (line 243-251), which uses the LiteLLM
// gateway alias `extract-en` → gemini-2.5-flash → glm-4.6 →
// gemini-1.5-flash. No new LLM clients added — the existing 24-entry
// `VISION_MODELS` registry covers all extraction needs.
//
// Re-gen after edits: `cd baml_src && baml-cli generate`

enum ConceptKind {
  TRAINING_METHOD
  DEPLOYMENT_PATTERN
  TOOL_PROTOCOL
  EVAL_METHOD
  DESIGN_PATTERN
  WORKFLOW_PATTERN
  MEMORY_PATTERN
  FRAMEWORK
  METRIC
  OTHER
}

// One row per shared concept across the 2 playlists. The BAML
// extraction reads descriptions from the N HF videos + the M GC
// videos and emits a deduplicated concept list with cross-source
// references.
class CrossSourceConcept {
  concept_name string @description("The canonical concept name (e.g. 'agent evaluation', 'MCP server', 'ADK').")
  concept_kind ConceptKind @description("The taxonomy bucket for this concept.")
  hf_video_ids string[] @description("HuggingFace video_ids that mention this concept.")
  gc_video_ids string[] @description("Google Cloud video_ids that mention this concept.")
  confidence float @description("BAML confidence score in [0.0, 1.0].")
  source_evidence SnippetEvidence[] @description("Up to 5 transcript snippets citing this concept.")
}

// One transcript snippet citing a concept. BAML emits multiple per
// concept; the user can drill into a specific video + timestamp.
class SnippetEvidence {
  video_id string @description("The video_id (YouTube 11-char ID).")
  timestamp_s float @description("Approximate timestamp within the video (seconds from start).")
  snippet string @description("50-200 character snippet of the transcript around the mention.")
}

// One row per (HF video, GC video, shared concept) tuple. The user
// picks 1 concept from the CrossSourceConcept list + 1 HF video +
// 1 GC video + asks for the perspective diff.
class CrossSourceComparison {
  concept_name string @description("The shared concept being compared.")
  hf_video_id string @description("The HF video_id representing HuggingFace's perspective.")
  gc_video_id string @description("The GC video_id representing Google Cloud's perspective.")
  hf_perspective string @description("1-3 sentences summarising HuggingFace's view of the concept.")
  gc_perspective string @description("1-3 sentences summarising Google Cloud's view of the concept.")
  agreement_pct float @description("BAML confidence in alignment, [0.0, 100.0].")
  differences string[] @description("1-3 specific points of disagreement or nuance.")
}

// Find concepts shared between N HuggingFace videos + M Google Cloud
// videos. Emits a deduplicated list with the video_ids from each
// playlist that mention each concept.
function ExtractCrossSourceConcept(
  hf_video_descriptions: string[],
  gc_video_descriptions: string[]
) -> CrossSourceConcept[] {
  client "ExtractEn"
  prompt #"
    You are an expert AI agentics researcher comparing two curricula
    on building, training, and evaluating AI agents.

    # HuggingFace playlist videos (Post-training Agents, 6 videos):
    {% for desc in hf_video_descriptions %}
    - {{ desc }}
    {% endfor %}

    # Google Cloud playlist videos (AI Agent Crash Course, 11 videos):
    {% for desc in gc_video_descriptions %}
    - {{ desc }}
    {% endfor %}

    Find all concepts that are mentioned in BOTH playlists (i.e. at
    least one HuggingFace video AND at least one Google Cloud video
    discuss the same concept). Examples of concepts that should
    appear in both:
    - agent evaluation (RLHF, evals, agent-as-judge)
    - MCP server / Model Context Protocol
    - ADK (Agent Development Kit)
    - memory (short-term + long-term)
    - multi-agent systems
    - agent design patterns (ReAct, reflection, planning)
    - workflow agents / SequentialAgent / ParallelAgent
    - continual learning / fine-tuning / distillation

    For each shared concept, emit one CrossSourceConcept row with:
    - the canonical concept name
    - the concept_kind (TRAINING_METHOD / DEPLOYMENT_PATTERN / TOOL_PROTOCOL / EVAL_METHOD / DESIGN_PATTERN / WORKFLOW_PATTERN / MEMORY_PATTERN / FRAMEWORK / METRIC / OTHER)
    - hf_video_ids: the YouTube video_ids from the HF playlist that mention the concept
    - gc_video_ids: the YouTube video_ids from the GC playlist that mention the concept
    - confidence: how confident you are that both playlists genuinely cover the same concept (0.0-1.0)
    - source_evidence: 2-5 SnippetEvidence rows with the actual quote

    Only emit concepts with confidence >= 0.6. Return [] if no shared
    concepts found.

    {{ ctx.output_format }}
  "%
}

// Compare how the 2 playlists discuss a single shared concept.
// Used by the marimo notebook's "concept deep-dive" tab.
function CompareCrossSourcePerspectives(
  hf_video_id: string,
  gc_video_id: string,
  shared_concept: string,
  hf_video_description: string,
  gc_video_description: string
) -> CrossSourceComparison {
  client "ExtractEn"
  prompt #"
    You are an expert AI agentics researcher comparing how two
    different video courses discuss the same shared concept.

    Shared concept: {{ shared_concept }}

    # HuggingFace video (Post-training Agents playlist):
    video_id: {{ hf_video_id }}
    description: {{ hf_video_description }}

    # Google Cloud video (AI Agent Crash Course playlist):
    video_id: {{ gc_video_id }}
    description: {{ gc_video_description }}

    Write a 1-3 sentence summary of each video's perspective on the
    shared concept. Then estimate how aligned they are (0-100, where
    100 = identical views and 0 = opposite views). List 1-3 specific
    points of disagreement or nuance.

    {{ ctx.output_format }}
  "%
}
