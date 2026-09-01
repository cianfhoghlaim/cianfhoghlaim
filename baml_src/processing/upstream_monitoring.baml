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
  pkg Package
  blog_post_type BlogPostType
  summary string
  affected_capabilities string[]
  code_examples string[]
  api_changes string[]
}

class ApiChange {
  symbol string
  pkg Package
  severity ChangeSeverity
  old_signature string
  new_signature string
  migration_steps string[]
  example_code string?
  changelog_url string
  detected_at string // ISO 8601
  v1_app_affected string? // e.g. "upstream_blog_monitor", matched by symbol
}

class PackageRelease {
  pkg Package
  version string // semver
  release_date string // ISO 8601
  breaking_changes string[]
  new_features string[]
  deprecations string[]
  release_notes_url string
}

function ExtractBlogPostMetadata(
  content: string,
  url: string
) -> BlogPostMetadata {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    {{ ctx.output_format }}

    You are extracting metadata from an upstream data-platform blog post
    or documentation page (one of: MotherDuck blog, dltHub blog, LanceDB
    blog, or CocoIndex docs/blog).

    Source URL: {{ url }}

    Source content (markdown, may be truncated):
    ---
    {{ content }}
    ---

    Extract:
    - title: the page title (h1 or og:title if present)
    - author: the author name (from byline or metadata) if present
    - published_at: ISO 8601 publication date if discoverable, else the
      last-modified date
    - pkg: which of MOTHERDUCK / DLTHUB / LANCEDB / COCOINDEX the page
      belongs to (use the URL hostname as the primary signal)
    - blog_post_type: classify as ANNOUNCEMENT (new release/feature),
      TUTORIAL (how-to), BENCHMARK (performance numbers), CASE_STUDY
      (customer story), RELEASE_NOTES (per-version changelog), or API_DOC
    - summary: 2-3 sentence executive summary
    - affected_capabilities: list of capability names this post touches
      (e.g. ["motherduck_byob", "ducklake_lakehouse_hydration"])
    - code_examples: list of code snippets shown in the post
    - api_changes: list of API surface changes (method signatures, new
      endpoints) if any

    Return ONLY the structured BlogPostMetadata. No prose, no markdown.
  "#

}

function ExtractCocoIndexApiChange(
  content: string,
  url: string
) -> ApiChange {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    {{ ctx.output_format }}

    You are extracting an API surface change from an upstream changelog
    page (CocoIndex docs, LanceDB release notes, dltHub migration guide,
    or MotherDuck breaking-change notice).

    Source URL: {{ url }}

    Source content (markdown, may be truncated):
    ---
    {{ content }}
    ---

    Extract:
    - symbol: the class / function / method / enum name that changed
    - pkg: which of MOTHERDUCK / DLTHUB / LANCEDB / COCOINDEX
    - severity: BREAKING (API removed / signature incompatible),
      MAJOR (new required arg / new behavior), MINOR (new optional
      arg / new method), PATCH (internal-only)
    - old_signature: the pre-change signature (literal text)
    - new_signature: the post-change signature (literal text)
    - migration_steps: ordered list of steps a downstream caller must
      take to adapt to the change
    - example_code: a single code snippet showing the new usage if
      present in the source content, else null
    - detected_at: ISO 8601 timestamp (use today's date if the page
      doesn't specify)
    - v1_app_affected: the name of the v1 CocoIndex App in our tree
      (e.g. "upstream_blog_monitor", "upstream_api_surface") if the
      symbol matches one we watch, else null

    Return ONLY the structured ApiChange. No prose, no markdown.
  "#

}

function ExtractPackageRelease(
  content: string,
  url: string
) -> PackageRelease {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    {{ ctx.output_format }}

    You are extracting a package release entry from an upstream
    changelog (CocoIndex PyPI changelog, LanceDB RELEASE.md, dltHub
    release notes, or MotherDuck feature announcements).

    Source URL: {{ url }}

    Source content (markdown, may be truncated):
    ---
    {{ content }}
    ---

    Extract:
    - pkg: which of MOTHERDUCK / DLTHUB / LANCEDB / COCOINDEX
    - version: the semver version string (e.g. "1.0.20")
    - release_date: ISO 8601 release date if present, else the
      detected_at timestamp
    - breaking_changes: list of breaking-change descriptions
      (empty list if none)
    - new_features: list of new-feature descriptions
    - deprecations: list of deprecation descriptions (empty list
      if none)
    - release_notes_url: the canonical URL for this release entry
      (may differ from the source URL)

    Return ONLY the structured PackageRelease. No prose, no markdown.
  "#

}
