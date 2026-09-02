// BAML schema: 7 Vernacular Language Pipelines (Step 9)
//
// Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1 change
// (Step 9 of the cianfhoghlaim-nua v6 era plan). The 7 vernacular
// languages of the British Isles that need BAML extraction support
// for the sister-repo lift pattern.
//
// The 7 languages (in operator-approved priority):
//  1. Welsh (cy)           — Wales; sister repo: ciancheiltis
//  2. Scottish Gaelic (gd) — Scotland; sister repo: gemini_hackathon
//  3. Breton (br)          — sister repo: ciancheiltis (future)
//  4. Cornish (kw)         — sister repo: ciancheiltis (future)
//  5. Manx (gv)            — Isle of Man; sister repo: ciancheiltis
//  6. Channel Islands French (fr-je / fr-gg) — Jersey + Guernsey
//  7. Ulster Scots (sco)   — Northern Ireland
//
// All extractions are bilingual by default (per operator direction):
// the source document is in the vernacular + English, and the
// output has both `text_vernacular` + `text_en` + `text_ga` fields.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

// ============================================================================
// Canonical enums
// ============================================================================

enum VernacularLanguage {
  CY  @description("Welsh (Cymraeg)")
  GD  @description("Scottish Gaelic (Gàidhlig)")
  BR  @description("Breton (Brezhoneg)")
  KW  @description("Cornish (Kernewek)")
  GV  @description("Manx (Gaelg)")
  FR_JE @description("Channel Islands French (Jèrriais) — Jersey")
  FR_GG @description("Channel Islands French (Guernésiais) — Guernsey")
  SCO @description("Ulster Scots")
}

// ============================================================================
// Output classes (always bilingual EN + GA + vernacular)
// ============================================================================

class VernacularSubjectSpec {
  language VernacularLanguage
  jurisdiction_code string @description("WL/SC/IM/JE/GG/NI")
  subject_slug string
  stage string
  display_name string @description("Subject name in the vernacular language")
  display_name_en string @description("English translation")
  display_name_ga string @description("Irish (Gaeilge) translation")
  award_descriptor string
  source_pdf string
  source_url string
  page int
  year int
}

// ============================================================================
// 7 per-vernacular extraction functions
// ============================================================================

function ExtractWelshSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Welsh-medium (Cymraeg) subject specification from the PDF text. The source is the official WJEC/CBAC document at {{ source_url }}. Return the canonical VernacularSubjectSpec with display_name in Welsh + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractScottishGaelicSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Scottish Gaelic (Gàidhlig) CfE subject specification from the PDF text. The source is the official SQA document at {{ source_url }}. Return the canonical VernacularSubjectSpec with display_name in Scottish Gaelic + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractBretonSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Breton (Brezhoneg) subject specification from the PDF text. Return the canonical VernacularSubjectSpec with display_name in Breton + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractCornishSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Cornish (Kernewek) subject specification from the PDF text. Return the canonical VernacularSubjectSpec with display_name in Cornish + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractManxSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Manx (Gaelg) subject specification from the PDF text. The source is the official Isle of Man Government document at {{ source_url }}. Return the canonical VernacularSubjectSpec with display_name in Manx + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractJerseyFrenchSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Jersey French (Jèrriais) subject specification from the PDF text. The source is the official States of Jersey document at {{ source_url }}. Return the canonical VernacularSubjectSpec with display_name in Jèrriais + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractGuernseyFrenchSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Guernsey French (Guernésiais) subject specification from the PDF text. The source is the official States of Guernsey document at {{ source_url }}. Return the canonical VernacularSubjectSpec with display_name in Guernésiais + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

function ExtractUlsterScotsSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: string,
  source_url: string
) -> VernacularSubjectSpec {
  client Primary
  prompt #"Extract the Ulster Scots subject specification from the PDF text. The source is the official DENI (NI) document at {{ source_url }}. Return the canonical VernacularSubjectSpec with display_name in Ulster Scots + display_name_en + display_name_ga. {{ ctx.output_format }}"#
}

// ============================================================================
// BAML test blocks
// ============================================================================

test welsh_subject_spec_sanity {
  functions [ExtractWelshSubjectSpec]
  args {
    pdf_text "Sample Welsh (Cymraeg) WJEC Mathematics spec text..."
    subject_slug "mathematics"
    stage "gcse"
    source_url "https://www.wjec.co.uk/qualifications/mathematics-gcse"
  }
}

test scottish_gaelic_subject_spec_sanity {
  functions [ExtractScottishGaelicSubjectSpec]
  args {
    pdf_text "Sample Scottish Gaelic CfE Mathematics text..."
    subject_slug "mathematics"
    stage "higher"
    source_url "https://www.sqa.org.uk/sqa/56992.html"
  }
}
