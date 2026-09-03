// =============================================================================
// Semantic Search BAML Function (per cianfhoghlaim-semantic-search v1)
//
// The agent-callable entrypoint for cross-corpus semantic search.
// Backs onto `cianfhoghlaim.cognify_rules.semantic_search` (Python).
//
// Reference: openspec/changes/2026-07-14-cianfhoghlaim-semantic-search-v1/
//             + openspec/specs/cianfhoghlaim-semantic-search/spec.md
// =============================================================================


class SearchResult {
  chunk_id string
  text string
  source_url string
  corpus string           @description("chemistry / computer_science / english / gaeilge / geography / mathematics / leabharlann")
  subject string?
  level string?
  year int?
  language string         @description("en / ga / both")
  score float             @description("0..1; higher is better")
  highlight_en string?
  highlight_ga string?
  model_name string       @description("BAAI/bge-m3 / BAAI/bge-large-en-v1.5")
  parent_chunk_id string? @description("For windowed RAG (requirement #6)")
  lat float?
  lon float?
}


class SearchFilter {
  corpora string[]   @description("Restrict to these corpora (chemistry, gaeilge, ..., leabharlann)")
  subjects string[]  @description("Restrict to these subjects")
  levels string[]    @description("primary / junior_cycle / senior_cycle / university")
  languages string[] @description("en / ga / both")
  years int[]        @description("1990..2026")
}


class SearchTelemetry {
  query string
  embedder string         @description("BAAI/bge-m3 / BAAI/bge-large-en-v1.5 / hybrid / bm25")
  top_k int
  latency_ms float
  result_count int
  cache_hit bool
  search_id string
  timestamp float
}


function SemanticSearch(query: string, filters: string) -> SearchResult[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}


function SemanticSearchTelemetry(
  query: string,
  embedder: string,
  top_k: int,
  latency_ms: float,
  result_count: int,
  cache_hit: bool,
  search_id: string,
) -> SearchTelemetry {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}