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
  @@stream.done
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
  @@stream.done
}

class PackageRelease {
  pkg Package
  version string // semver
  release_date string // ISO 8601
  breaking_changes string[]
  new_features string[]
  deprecations string[]
  release_notes_url string
  @@stream.done
}

function ExtractBlogPostMetadata(content: string, url: string) -> BlogPostMetadata {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractCocoIndexApiChange(content: string, url: string) -> ApiChange {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractPackageRelease(content: string, url: string) -> PackageRelease {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}