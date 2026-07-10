// =============================================================================
// Docs Skills Extraction BAML
//
// Source-agnostic extraction functions for the docs-skills-consolidation
// CocoIndex v1 App (see `cianfhoghlaim/cocoindex/docs_skills_consolidation.py`).
// Re-creates the 2 functions + 2 classes that the CocoIndex flow imports
// from `_baml()` (lines 247, 273, 293 in docs_skills_consolidation.py).
//
// Call sites (verified 2026-07-11):
//   - _baml().ExtractDocSkillTag(content, path) -> DocSkillTag
//       result.category  : string (e.g. "tutorial", "api-reference", "guide")
//       result.quadrant  : string (e.g. "oideachais", "meaisinfhoghlaim")
//       result.confidence: float in [0.0, 1.0]
//       result.short_label: string
//       result.is_canonical: bool
//   - _baml().ExtractTriples(content, path) -> TriplesResult
//       result.triples: Triple[] where each Triple has
//         (subject: string, predicate: string, object: string)
//
// Canonical BAML 0.223.0 syntax (per the
// `2026-07-10-fix-baml-codegen-v4-syntax-v1` Wave 2 migration):
//   - field-name and type are whitespace-separated, NOT `field: type`
//   - `@description("...")` immediately follows the type
//   - `?` marks optional fields (optional[T] in the codegen)
//   - `@stream.done` / `@stream.not_null` / `@stream.with_state` are
//     the optional 0.212+ semantic-attr primitives
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum DocCategory {
  TUTORIAL        @description("Step-by-step tutorial that walks the reader through a feature or workflow")
  API_REFERENCE   @description("Reference documentation for an API endpoint, type, or function")
  GUIDE           @description("Concept or how-to guide that explains a topic at a higher level than a tutorial")
  CHANGELOG       @description("Release notes / changelog entry")
  BLOG_POST       @description("Long-form blog post or announcement")
  SKILL           @description("A skill file (e.g. AGENTS.md-style skill definition)")
  OTHER           @description("Anything that doesn't fit the above categories")
}

enum Quadrant {
  OIDEACHAIS       @description("Education / curriculum / BAML extraction quadrant")
  MEAISINFHOGHLAIM @description("Agents / OCR / HTR / agent fleet quadrant")
  TUATHA           @description("Educational MMO / Babylon.js / 3D quadrant")
  CROILAR          @description("Portfolio / Croilar / multi-persona quadrant")
  SHARED           @description("Cross-quadrant shared capabilities")
  INFRA            @description("Infrastructure stacks / IaC / Komodo / Pangolin / Infisical")
  TOOLING          @description("Tooling (CCC, Cognee, skills)")
  TEAM             @description("Team workflow (n8n, Vikunja, cal-diy)")
  OTHER            @description("Anything that doesn't fit the above quadrants")
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class DocSkillTag {
  category      DocCategory @description("Coarse document category; OTHER if uncertain")
  quadrant      Quadrant    @description("Which Cianfhoghlaim quadrant this doc supports; OTHER if cross-cutting or unclear")
  confidence    float       @description("Calibrated 0-1 confidence in the category+quadrant assignment")
  short_label   string      @description("<= 80-char human label summarising the doc's primary topic")
  is_canonical  bool        @description("True if this doc is the canonical reference for its category+quadrant; False otherwise")
  @@stream.done
}

class Triple {
  subject    string @description("Subject of the (s, p, o) triple — typically a class name, skill name, or noun phrase")
  predicate  string @description("Predicate — typically a verb phrase like 'uses', 'extends', 'depends-on'")
  object     string @description("Object — typically a class name, skill name, or noun phrase the subject relates to")
}

class TriplesResult {
  triples    Triple[] @description("All (subject, predicate, object) triples extracted from the document")
  @@stream.done
}

// -----------------------------------------------------------------------------
// Functions
// -----------------------------------------------------------------------------

function ExtractDocSkillTag(content: string, path: string) -> DocSkillTag {
  client default
  prompt #"
    You are a doc-skill tagger. Given a single documentation file's
    contents ({{ content }}) and its on-disk path ({{ path }}), return
    ONE DocSkillTag with the category, quadrant, confidence, short
    label, and is_canonical flag.

    Constraints:
      - category MUST be a DocCategory enum value (TUTORIAL,
        API_REFERENCE, GUIDE, CHANGELOG, BLOG_POST, SKILL, OTHER).
      - quadrant MUST be a Quadrant enum value
        (OIDEACHAIS, MEAISINFHOGHLAIM, TUATHA, CROILAR, SHARED,
        INFRA, TOOLING, TEAM, OTHER).
      - confidence MUST be in [0.0, 1.0].
      - short_label MUST be <= 80 chars and human-readable.
      - is_canonical MUST be True only if the doc is THE
        single source-of-truth for its category+quadrant (e.g.
        `openspec/AGENTS.md` is canonical for Quadrant.SHARED,
        but a tutorial that references it is NOT canonical).

    {{ ctx.output_format }}
  "#
}

function ExtractTriples(content: string, path: string) -> TriplesResult {
  client default
  prompt #"
    You are a knowledge-graph triple extractor. Given a single
    documentation file's contents ({{ content }}) and its on-disk
    path ({{ path }}), return a TriplesResult with the `triples`
    field populated by the (subject, predicate, object) triples
    that describe the relationships in the doc.

    Constraints:
      - triples MUST be a list of Triple objects.
      - subject, predicate, object MUST all be non-empty strings.
      - subject and object SHOULD be noun phrases (class / skill /
        system names). predicate SHOULD be a verb phrase.
      - Return at most 32 triples per call to avoid context bloat.

    {{ ctx.output_format }}
  "#
}

// -----------------------------------------------------------------------------
// Test block (exercised by `mise run baml:test` once the CI gate lands)
// -----------------------------------------------------------------------------

test ExtractDocSkillTagSmokeTest {
  functions [ExtractDocSkillTag]
  input {
    content "Step-by-step tutorial that walks the user through deploying a BAML project locally."
    path "docs/03_quadrants/04_baml/01_tutorials/01_baml_post_v4_syntax.md"
  }
  output {
    category "TUTORIAL"
    quadrant "OIDEACHAIS"
    confidence 0.92
    short_label "BAML post-v4 syntax tutorial"
    is_canonical false
  }
}
