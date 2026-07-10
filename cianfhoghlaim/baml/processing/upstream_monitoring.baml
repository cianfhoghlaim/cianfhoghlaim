// BAML extraction schemas for the upstream-package-monitoring pipeline.
//
// Three extraction functions cover the four upstream packages
// (motherduck / dlthub / lancedb / cocoindex):
//
//   ExtractBlogPostMetadata  — for Firecrawl `monitor.page` payloads
//                              from motherduck/dlthub/lancedb blog
//                              posts + cocoindex docs pages
//   ExtractCocoIndexApiChange — for the upstream_api_surface v1 App
//                                that watches cocoindex docs URLs
//                                + llms-full.txt
//   ExtractPackageRelease    — for the changelog pages that publish
//                              per-version release notes (LanceDB
//                              `lance/python/RELEASE.md`, CocoIndex
//                              PyPI changelog, etc.)
//
// All three route through the canonical `ExtractEn` client from
// `baml_src/clients.baml` (line 243-251), which uses the LiteLLM
// gateway alias `extract-en` → gemini-2.5-flash → glm-4.6 →
// gemini-1.5-flash.
//
// Enum types are defined inline here (rather than importing from
// Python) because BAML enum syntax requires `MOTHERDUCK` etc. to be
// declared as BAML enum values. The canonical home for the Python
// enum is `sruth/oideachais/core/types.py` — both must stay in sync
// (see openspec/changes/upstream-package-monitoring/specs/schema-type-standardization/spec.md
// for the conformance scenarios).
//
// Post-archive update: 2026-06-25-upstream-package-monitoring
// Re-gen after edits: `cd sruth/oideachais && uv run baml-cli generate`

enum Package {
  MOTHERDUCK
  DLTHUB
  LANCEDB
  COCOINDEX
}

enum BlogPostType {
  ANNOUNCEMENT
  TUTORIAL
  BENCHMARK
  CASE_STUDY
  RELEASE_NOTES
  API_DOC
}

enum ChangeSeverity {
  BREAKING
  MAJOR
  MINOR
  PATCH
}

class BlogPostMetadata {
  title string
  url string
  author string?
  published_at string // ISO 8601
  package Package
  blog_post_type BlogPostType
  summary string
  affected_capabilities string[]
  code_examples string[]
  api_changes string[]
  @@stream.done
}

class ApiChange {
  symbol string
  package Package
  severity ChangeSeverity
  old_signature string
  new_signature string
  migration_steps string[]
  example_code string?
  changelog_url string
  detected_at string // ISO 8601
  v1_app_affected string? // e.g. "upstream_blog_monitor", matched by symbol
  @@stream.done
}

class PackageRelease {
  package Package
  version string // semver
  release_date string // ISO 8601
  breaking_changes string[]
  new_features string[]
  deprecations string[]
  release_notes_url string
  @@stream.done
}

function ExtractBlogPostMetadata(content: string, url: string) -> BlogPostMetadata {
  client ExtractEn
  prompt #"
    Extract structured metadata from this blog post or docs page.

    URL: {{ url }}

    Content (markdown):
    ---
    {{ content }}
    ---

    Return a BlogPostMetadata object with:
    - title: the post's headline
    - url: the source URL ({{ url }})
    - author: the author byline, or null if not stated
    - published_at: ISO 8601 timestamp from the post metadata, or the
      URL's date if no explicit timestamp
    - package: which of MOTHERDUCK / DLTHUB / LANCEDB / COCOINDEX this
      post is about (infer from the URL and the content)
    - blog_post_type: ANNOUNCEMENT (new product capability), TUTORIAL
      (how-to / guide), BENCHMARK (performance numbers), CASE_STUDY
      (customer / open-source user story), RELEASE_NOTES (per-version
      changelog), or API_DOC (technical reference)
    - summary: 1-3 sentence executive summary
    - affected_capabilities: list of capability names from the post
      (e.g. ["DuckLake 1.0", "data inlining", "bucket partitioning"])
    - code_examples: any code snippets, as raw text strings
    - api_changes: any API symbol renames, deprecations, or new exports
      mentioned in the post

    Strict: every field is required except author, code_examples, and
    api_changes (which default to empty lists / null).
  "#
}

function ExtractCocoIndexApiChange(content: string, url: string) -> ApiChange {
  client ExtractEn
  prompt #"
    Extract a single API-surface change from this CocoIndex docs page
    or `llms-full.txt` excerpt.

    URL: {{ url }}

    Content (markdown):
    ---
    {{ content }}
    ---

    Return an ApiChange object describing one specific API symbol change:
    - symbol: the qualified name (e.g. `coco.App`, `coco.ContextKey`,
      `SentenceTransformerEmbedder`, `lancedb.mount_table_target`)
    - package: COCOINDEX (this function is always about cocoindex)
    - severity: BREAKING (removed/renamed signature, no fallback),
      MAJOR (new required argument, behaviour change), MINOR (new
      optional argument, additive), or PATCH (doc / typing fix)
    - old_signature: the previous signature verbatim, or "" if
      this is a brand-new symbol
    - new_signature: the new signature verbatim
    - migration_steps: ordered list of code changes a developer
      needs to make to migrate from old to new (each step is a
      1-line imperative sentence)
    - example_code: a minimal usage example for the new signature,
      or null
    - changelog_url: the URL this change was detected at ({{ url }})
    - detected_at: ISO 8601 timestamp at the top of the content if
      present, else the current UTC time
    - v1_app_affected: which of the KCG v1 CocoIndex Apps this change
      is most likely to affect (matched by symbol), e.g.
      "upstream_blog_monitor" or "codebase_indexing". Null if
      uncategorised.
  "#
}

function ExtractPackageRelease(content: string, url: string) -> PackageRelease {
  client ExtractEn
  prompt #"
    Extract structured release-notes metadata from this package
    release page or changelog entry.

    URL: {{ url }}

    Content (markdown):
    ---
    {{ content }}
    ---

    Return a PackageRelease object with:
    - package: which of MOTHERDUCK / DLTHUB / LANCEDB / COCOINDEX this
      release is for (infer from the URL and the content)
    - version: semver string (e.g. "1.0.7", "2.4.0")
    - release_date: ISO 8601 timestamp
    - breaking_changes: list of breaking-change descriptions
    - new_features: list of new-feature descriptions
    - deprecations: list of deprecation descriptions
    - release_notes_url: the source URL ({{ url }})

    If the page mentions multiple versions, return only the most
    recent release. If no clear semver is identifiable, use "0.0.0".
  "#
}