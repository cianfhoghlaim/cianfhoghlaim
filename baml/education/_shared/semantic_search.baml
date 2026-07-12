// =============================================================================
// Semantic Search BAML Function (per oideachais-semantic-search v1)
//
// The agent-callable entrypoint for cross-corpus semantic search.
// Backs onto `oideachais.cognify_rules.semantic_search` (Python).
//
// Reference: openspec/changes/2026-07-14-oideachais-semantic-search-v1/
//             + openspec/specs/oideachais-semantic-search/spec.md
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


function SemanticSearch(query: string, filters: string) -> SearchResult[] {
  client Default
  prompt #"You are the cross-corpus semantic search assistant for the
Oideachais (Cianfhoghlaim) platform. Given the user's natural-language
query and a JSON-serialised `SearchFilter` envelope, return the top-10
closest chunks across the BIEP v1 Leaving Cert corpora (Mathematics,
Chemistry, Geography, Gaeilge, English, Computer Science) and the
leabharlann corpus (books, zotero, takeout).

QUERY: {{ query }}

FILTERS (JSON): {{ filters }}

The filter envelope supports:
- `corpora`: array of corpus keys
- `subjects`: array of subject keys
- `levels`: array of education levels
- `languages`: array of language codes (en/ga/both)
- `years`: array of years (1990..2026)

For each result, produce a `SearchResult` row with:
- `chunk_id`: stable hash of the source path + line offset
- `text`: the matched chunk text (truncate to ~200 chars)
- `source_url`: the canonical URL or path
- `corpus`: one of `chemistry` / `computer_science` / `english` / `gaeilge` / `geography` / `mathematics` / `leabharlann`
- `subject`: optional, the parent subject
- `level`: optional, the parent education level
- `year`: optional, the publication year
- `language`: `en` / `ga` / `both`
- `score`: relevance score in [0..1] (higher is better)
- `highlight_en`: optional, the matched English snippet
- `highlight_ga`: optional, the matched Irish snippet
- `model_name`: `BAAI/bge-m3` (multilingual) or `BAAI/bge-large-en-v1.5` (English-only)

{{ ctx.output_format(prefix="Return a JSON array of SearchResult. Example:\n") }}

{{ _.role("user") }}
    QUERY: {{ query }}
    FILTERS: {{ filters }}
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
) -> SearchTelemetry {
  client Default
  prompt #"Build a `SearchTelemetry` record for a single search call.

This is a deterministic pass-through (no LLM reasoning). Return the
record verbatim.

QUERY: {{ query }}
EMBEDDER: {{ embedder }}
TOP_K: {{ top_k }}
LATENCY_MS: {{ latency_ms }}
RESULT_COUNT: {{ result_count }}
CACHE_HIT: {{ cache_hit }}
SEARCH_ID: {{ search_id }}
"#
}