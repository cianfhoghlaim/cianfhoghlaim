// Celtic Text Standardization BAML wrappers.
// Phase 1.3 (2026-09-25 5-phase Celtic overhaul) — wraps the
// `cocoindex_flows/_shared/caighdean_standardize.py` module so the
// pre-extraction standardisation is callable from any BAML function.
//
// The 3 BAML functions mirror the 3 concrete `TextTransform` subclasses:
//   - CaighdeanTransform     → StandardizeIrish  (pure-Python, default)
//   - CaighdeanCLITransform  → (kept for future use, not wrapped yet)
//   - the GD/GV stdlib       → StandardizeScottishGaelic + StandardizeManx
//                              via caighdean's `ok-gd.txt` + `ok-gv.txt`
//
// These functions are designed to be called PRE-extraction in the
// LC/JC stage templates (Phase 1.4 + Phase 1.5) and POST-load in the
// CocoIndex gaeilge_embedding.py App (Phase 1.6).

// ============================================================================
// INPUT / OUTPUT CLASSES
// ============================================================================

// The kind of pre-extraction cleanup to apply.
enum StandardizationMode {
  WIKITEXT @description("Strip wikitext markup (ref/TN6/strikethrough/etc.)")
  TN6_HYPERLINKS @description("Strip external/internal hyperlinks per the Téamaí Náisiúnta 6 standard")
  TEANGLANN_AUDIO @description("Capture Teanglann.ie audio link anchors")
  FULL_CLEAN @description("Apply all 3 in sequence")
}

class StandardizationConfig {
  mode StandardizationMode @description("Which cleanup mode to apply")
  preserve_audio_links bool @description("If true, keep Teanglann audio links instead of stripping them (default: false)")
  language CelticLanguage @description("Which Celtic language to standardise (affects which word lists are loaded)")
}

class StandardizationDiff {
  segment_id string @description("Identifier for the diff segment (e.g. 'paragraph_3_sentence_1')")
  original string @description("The original text before standardisation")
  standardised string @description("The text after standardisation")
  changes int @description("Number of word-level changes applied")
  audio_links string[] @description("Captured Teanglann audio links (only populated in TEANGLANN_AUDIO / FULL_CLEAN mode)")
}

class StandardizationResult {
  original_text string @description("The full input text")
  standardised_text string @description("The full text after standardisation")
  language CelticLanguage
  diffs StandardizationDiff[] @description("Per-segment standardisation diffs")
  total_changes int @description("Total word-level changes across all diffs")
  confidence float @description("0.5-1.0 — inverse-proportional to total_changes/length(original)")
}

// ============================================================================
// WIKITEXT EXTRACTION (Mode 1)
// ============================================================================

// Strip the standard MediaWiki + Irish-language wiki markup:
//   - [[link|alias]] → alias
//   - {{template|arg}} → empty (templates are usually metadata)
//   - <ref>...</ref> → empty (or capture if preserve_audio_links)
//   - [[File:...]] / [[Íomhá:...]] → empty (images)
//   - {| ... |} (tables) → keep cells, drop alignment markup
//   - ''italic'' → italic (mark but don't transform)
//   - '''bold''' → bold (mark but don't transform)
function StripWikitext(text: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are a wikitext-cleanup specialist for Irish (Gaeilge) + Scottish Gaelic
    + Welsh + Manx + Cornish + Breton.

    Strip the following markup from the input text:
      - [[link|alias]]        → keep alias (drop the [[...]])
      - [[link]]              → keep link text
      - {{template|arg}}      → drop entirely (templates are metadata)
      - <ref>...</ref>        → drop entirely (citation references)
      - <ref name="..."/>     → drop entirely
      - [[File:...]] / [[Íomhá:...]] / [[Image:...]] → drop entirely (image markup)
      - {| ... |}             → keep cell content, drop alignment markup
      - ''italic''            → keep as-is (mark with leading/trailing underscores if you wish)
      - '''bold'''            → keep as-is
      - <br> / <br/>          → drop (line break)
      - <span>...</span>      → drop (formatting wrapper)
      - <ref name="X" />      → drop

    Preserve:
      - All Irish / Scottish-Gaelic / Welsh / Manx characters (including fada, séimhiú, urú, etc.)
      - All diacritics
      - Hyphens, apostrophes, Irish punctuation (e.g. « »)
      - Newlines (one blank line max)

    Return ONLY the cleaned text, no commentary.

    {{ ctx.output_format(render_null_as="-1") }}

    INPUT TEXT:
    {{ text }}
  "#
}

// ============================================================================
// TN6 HYPERLINK STRIPPING (Mode 2)
// ============================================================================

// Strip hyperlinks per the Téamaí Náisiúnta 6 (TN6) standard:
//   - [http://...](text) → text
//   - <a href="...">text</a> → text
//   - [text](http://...) → text (markdown)
//   - [link][ref] → link
function StripTn6Hyperlinks(text: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are a hyperlink-stripping specialist for the Téamaí Náisiúnta 6 (TN6) standard.

    Strip the following hyperlink formats from the input text:
      - [anchor text](http://...)  → keep anchor text only
      - [anchor text](https://...) → keep anchor text only
      - <a href='http://...'>text</a>  → keep text only
      - <a href='https://...'>text</a> → keep text only
      - [anchor text][ref]  → keep anchor text only
      - Bare URLs (http://... or https://...) → drop entirely

    Preserve:
      - All Celtic characters
      - TN6-specific markup (e.g. <ref name='tn6'>...</ref>)

    Return ONLY the cleaned text, no commentary.

    {{ ctx.output_format(render_null_as="-1") }}

    INPUT TEXT:
    {{ text }}
  "#
}

// ============================================================================
// TEANGLANN AUDIO LINK CAPTURE (Mode 3)
// ============================================================================

// Capture Teanglann.ie audio link anchors (the canonical Irish-language
// pronunciation dictionary at https://www.teanglann.ie/) and return them
// alongside the cleaned text. The audio URLs follow the pattern
// `https://www.teanglann.ie/CanAinm/<word>.mp3` or similar.
//
// Use case: the gaeilge_embedding.py CocoIndex App can attach audio
// pronunciation data to each chunk for the operator-facing marimo notebook.
function CaptureTeanglannAudioLinks(text: string) -> string[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are a URL extractor for the Teanglann.ie pronunciation dictionary.

    Extract ALL Teanglann.ie audio link URLs from the input text. The URLs
    follow these patterns:
      - https://www.teanglann.ie/CanAinm/<word>.mp3
      - https://www.teanglann.ie/fuaim/<word>.mp3
      - https://www.teanglann.ie/<word>/<pronunciation>.mp3
      - Any URL containing 'teanglann.ie' that ends in .mp3 or .ogg

    Return a JSON array of strings. Example:
    ['https://www.teanglann.ie/CanAinm/cat.mp3',
     'https://www.teanglann.ie/fuaim/bád.mp3']

    If no Teanglann audio links are found, return an empty array.

    {{ ctx.output_format(render_null_as="-1") }}

    INPUT TEXT:
    {{ text }}
  "#
}

// ============================================================================
// TOP-LEVEL WRAPPER: StandardizeIrish (Phase 1.4 / Phase 1.5)
// ============================================================================

// The canonical pre-extraction standardisation for Irish (Gaeilge) text.
// Wraps the CocoIndex `CaighdeanTransform` class. Used by the LC + JC
// stage templates (Phase 1.4 + Phase 1.5) to standardise dialectal
// variations + pre-1936 spellings before BAML extraction.
function StandardizeIrish(text: string) -> StandardizationResult {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an Irish-language text standardisation specialist. Your job is
    to apply the Caighdean Oifigiúil standardisation (the canonical Irish
    language standard) to the input text.

    Specifically:
      1. Strip wikitext markup (use the StripWikitext function logic)
      2. Strip hyperlinks per TN6 standard (use the StripTn6Hyperlinks logic)
      3. Capture Teanglann audio links (use the CaptureTeanglannAudioLinks logic)
      4. Apply the CaighdeanTransform (modern → standard) — map pre-1936
         spellings to modern standard Irish:
           - bhéadh → bheadh
           - aoinne → aon duine
           - dochtuir → dochtúir
           - etc.
      5. Track the per-segment diff (original → standardised)
      6. Compute the confidence (1.0 - changes/length)

    Return a StandardizationResult with:
      - original_text: the input
      - standardised_text: the fully standardised version
      - language: 'ga'
      - diffs: list of StandardizationDiff with per-segment changes
      - total_changes: sum of all changes
      - confidence: 0.5-1.0

    {{ ctx.output_format(render_null_as="-1") }}

    INPUT TEXT:
    {{ text }}
  "#
}

// ============================================================================
// TOP-LEVEL WRAPPER: StandardizeScottishGaelic (Phase 4.5 — Manx + cross-Celtic)
// ============================================================================

function StandardizeScottishGaelic(text: string) -> StandardizationResult {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are a Scottish Gaelic (Gàidhlig) text standardisation specialist.

    Apply:
      1. Strip wikitext + TN6 hyperlinks
      2. Apply the Scottish Gaelic word list (caighdean's `ok-gd.txt`)
      3. Track diffs + compute confidence

    Return a StandardizationResult with language='gd'.

    {{ ctx.output_format(render_null_as='-1') }}

    INPUT TEXT:
    {{ text }}
  "#
}

// ============================================================================
// TOP-LEVEL WRAPPER: StandardizeManx (Phase 4.5)
// ============================================================================

function StandardizeManx(text: string) -> StandardizationResult {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are a Manx (Gaelg) text standardisation specialist. Note: Manx is a
    critically endangered Celtic language (~2000 L1+L2 speakers).

    Apply:
      1. Strip wikitext + TN6 hyperlinks
      2. Apply the Manx word list (caighdean's `ok-gv.txt`)
      3. Track diffs + compute confidence

    Return a StandardizationResult with language='gv'.

    {{ ctx.output_format(render_null_as='-1') }}

    INPUT TEXT:
    {{ text }}
  "#
}
