// video_kg.baml — Phase 1 of `2026-07-14-multimodal-code-and-media-intel-v1`.
//
// BAML schema for the YouTube video knowledge-graph extraction pipeline.
// Powers the `cianfhoghlaim.cocoindex.youtube_kg_embedding` CocoIndex v1
// App, which ingests curated YouTube videos (via
// `dlt.api_sources.youtube_videos`) and emits 3 typed knowledge layers:
//
// 1. `video_segments`       — per-30-second audio transcript segments
//                             (WhisperX-aligned) + frame-level captions
// 2. `video_frame_captions` — per-frame visual captions (qwen3-vl-8b)
//                             + diagram pointing (molmo2-8b)
// 3. `video_triples`        — typed knowledge triples extracted by BAML
//
// The 3 BAML functions here each take the per-video context and return
// a typed list:
//
//   ExtractVideoKnowledgeTriple  — Concept | Definition | Example |
//                                   Formula | VisualSequence triples
//   ExtractConceptChain           — ordered prerequisite chain across
//                                   triples, with summary text
//   ExtractFrameSequence          — VisualSequence timeline across the
//                                   sampled frames
//
// Backbone routing (per the canonical 24-entry
// `ocianfhoghlaim.meaisinfhoghlaim.ocr.models.registry.VISION_MODELS`):
//   * qwen3-vl-8b  (llama-swap) — visual caption leg
//   * molmo2-8b   (transformers) — diagram pointing
//   * qwen3.6-27b-mtp (llama-swap) — text leg (post-processing)
//
// No HuggingFace IDs are hardcoded — they all resolve through the
// registry. The BAML clients below reference named client aliases from
// `clients_llama_swap.baml` / `clients.baml`; those aliases map to the
// LiteLLM routing layer that wraps the registry.

enum KnowledgeTripleKind {
  Concept
  Definition
  Example
  Formula
  VisualSequence
}

class KnowledgeTriple {
  subject string  @description("The subject of the triple (e.g. 'matrix multiplication', 'Baye's theorem', 'the Python `asyncio.gather` function').")
  verb string     @description("The relationship verb (e.g. 'is defined as', 'has property', 'is a prerequisite for', 'is visualised by').")
  object string   @description("The object of the triple (e.g. 'a linear transformation over a vector space', 'P(A|B) = P(B|A)P(A)/P(B)', 'a coroutine scheduler').")
  triple_kind KnowledgeTripleKind  @description("Which typed category the triple belongs to.")
  confidence float                 @description("Confidence score in [0, 1]; the model's self-reported certainty.")
  source_frame_idx int?            @description("If extracted from a frame caption, the frame index (1-based). Null if from transcript.")
  source_segment_idx int?          @description("If extracted from a transcript segment, the segment index (1-based). Null if from frame.")
}

class ConceptChain {
  triples KnowledgeTriple[]  @description("The ordered chain of triples; the first triple is the most foundational concept.")
  chain_summary string       @description("A 1-2 sentence summary of the prerequisite chain.")
  prerequisites string[]     @description("Topical prerequisites the viewer is assumed to know (e.g. 'vector spaces', 'conditional probability').")
  target_audience string     @description("Inferred audience (e.g. 'high-school students', 'graduate ML researchers', 'developers building async pipelines').")
}

class VisualScene {
  frame_idx int               @description("The frame index (1-based).")
  t_start_s float             @description("Wall-clock time in seconds since the start of the video.")
  t_end_s float               @description("End of the frame window (typically `t_start_s + 1` for a 1-fps sample).")
  caption string              @description("The caption emitted by qwen3-vl-8b (256-token frame absorption).")
  has_diagram bool            @description("True if the frame contains a diagram / whiteboard drawing / slide with figures.")
  has_formula bool            @description("True if the frame contains a mathematical formula.")
  has_code bool               @description("True if the frame contains source code.")
  diagram_points string[] @description("If `has_diagram` is true, the bounding-box or pointing targets extracted by molmo2-8b.")
}

class VisualSequence {
  video_id string          @description("The YouTube video ID this VisualSequence belongs to.")
  fps_sampled float        @description("The actual frames-per-second the App sampled (typically 1/10 = 0.1).")
  scenes VisualScene[]     @description("Ordered list of scenes; sorted by `t_start_s` ascending.")
  sequence_summary string  @description("A 1-2 sentence summary of the visual progression of the video.")
}


function ExtractVideoKnowledgeTriple(
  video_id: string,
  transcript: string,
  frame_captions: string[]
) -> KnowledgeTriple[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}


function ExtractConceptChain(
  triples: KnowledgeTriple[],
  video_id: string
) -> ConceptChain {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}


function ExtractFrameSequence(
  video_id: string,
  frame_paths: string[],
  fps_sampled: float
) -> VisualSequence {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}