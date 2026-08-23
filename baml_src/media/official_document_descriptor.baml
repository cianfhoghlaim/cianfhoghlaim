// official_document_descriptor.baml
// Class E (NCCA + SEC / examinations.ie + DfE + SQA + WJEC
// + DESC + Met Éireann + OSi + Met Office + Wikipedia + CELT
// + Dúchas) extractor function.
//
// Class E is the official-document surface: PDFs + HTML. The
// per-medium extractor reads the page + the metadata block
// (issuer, date, version) and emits the descriptor.
//
// Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
//             design.md § 1.3 (the PDF + metadata input shape)
//             spec.md § media-intel-acquisition-plan Requirement 5

class OfficialDocumentType {
  syllabus                // NCCA / SEC / SQA / WJEC / DESC curriculum spec
  exam_paper              // SEC / examinations.ie / Pearson / AQA / OCR
  marking_scheme          // NCCA / SEC / SQA / WJEC / DESC marking scheme
  research_pdf            // NCCA / DES research PDFs (formative assessment, certificate, online learning)
  census                  // CSO / NISRA / ONS census tables
  boundary                 // OSi / Tailte Éireann / Ordnance Survey / Met Éireann / Met Office boundary files
  wiki                    // Wikipedia article
  celt_text               // CELT (UCC) Corpus of Electronic Texts
  duchas_text             // Dúchas / Gaois (Goidelic + Brythonic surface)
}

class OfficialPowerEvent {
  actor string?            // e.g. "The State" (in the Irish Constitution)
  element "earth" | "air" | "water" | "fire" | "spirit" | "none"
  power_source string?     // e.g. "the Constitution", "the syllabus"
  trigger string?          // e.g. "the certification event"
  scale_tier "personal" | "local" | "regional" | "continental" | "planetary" | "cosmic"
  cost string?             // e.g. "the examination fee", "the hours of study"
  consequence string?
  counter string?
}

class OfficialVisualGrammar {
  composition string?       // The page layout descriptor
  panel_or_shot_type string? // e.g. "single-column", "two-column", "table", "figure"
  motion_lines string?      // n/a for official documents
  camera string?            // n/a for official documents
  silhouette string?        // n/a for official documents
  focal_hierarchy string?   // The page-level focal hierarchy (heading + subheading + body)
}

class OfficialPalette {
  dominant_hex string[]     // empty for official documents (no visual)
  accent_hex string[]       // empty
  emissive_hex string[]     // empty
  per_element_palette map<string, string[]>  // n/a for official documents
  contrast_strategy string?  // n/a
}

class OfficialVfxVocabulary {
  particle_class "dust" | "ember" | "mist" | "spark" | "lattice" | "ash" | "ink" | "glyph" | "none"
  density "sparse" | "moderate" | "dense" | "overwhelming"
  trail_behavior string?    // n/a for official documents
  dissipation string?       // n/a for official documents
  light_interaction string?  // n/a for official documents
}

class OfficialNarrativeBeat {
  arc_position string?      // e.g. "NCCA LC Geography syllabus 2026 § 1.2"
  beat_significance string?
}

class OfficialTransferability {
  in_game_mechanic string?  // e.g. "syllabus_completion_event", "certification_event"
  anam_cost int?            // 0 for official documents
  palette_token string?     // null for v1
  particle_effect string?   // null for v1
}

class OfficialProvenance {
  rights_holder string       // e.g. "NCCA" (Ireland) / "SEC" (examinations.ie) / "DfE" (England) / "SQA" (Scotland) / "WJEC" (Wales) / "DESC" (Isle of Man) / "CSO" / "NISRA" / "OSi" / "Met Éireann" / "Met Office" / "Wikipedia Foundation" / "CELT" / "Dúchas"
  licence string             // e.g. "CC-BY-SA-4.0" (Wikipedia + CELT + Dúchas) / "CC0" (CSO + NISRA + OSi open data) / "fair-use-description" (NCCA / SEC / SQA / WJEC / DESC)
  derivation_class "description_only" | "derivative" | "fair_use_quote"
  shippable false
  shippable_art_path string?
}

class OfficialDocumentMediaDescriptor {
  work string                // e.g. "NCCA LC Geography syllabus 2026" / "SEC Mathematics Higher 2024 Paper 2" / "Wikipedia: Tuatha Dé Danann"
  medium "official"
  language string            // "en" or "ga" (the Leaving Certificate is published in both)
  source_url string
  source_timestamp string

  power_event OfficialPowerEvent
  visual_grammar OfficialVisualGrammar
  palette OfficialPalette
  vfx_vocabulary OfficialVfxVocabulary
  narrative_beat OfficialNarrativeBeat
  transferability OfficialTransferability
  provenance OfficialProvenance
}

// Class E — Official (NCCA + SEC + DfE + SQA + WJEC + DESC + Met Éireann + OSi + Wikipedia + CELT + Dúchas)
// Default VLM: olmocr-2-7b (resolved via MODEL_REGISTRY
// family=ocr_vision, role=official_document_descriptor).
// No hardcoded model strings.

function ExtractOfficialDocumentDescriptor(
  pdf_page: image,
  metadata: string,
  source_url: string,
  source_timestamp: string,
  work: string,
  language: string,
  evidence: string,
) -> OfficialDocumentMediaDescriptor {
  client MediaIntelPrimary
  prompt #"
    You are a medium-agnostic official-document analyst for
    the Cianfhoghlaim reference-corpus. You are reading a
    page from {{ work }} (an official document from NCCA,
    SEC, DfE, SQA, WJEC, DESC, Met Éireann, OSi, Met Office,
    Wikipedia, CELT, or Dúchas).

    The page image + the metadata block (issuer, date,
    version) feed the per-medium descriptor. The descriptor
    is a structured summary of the page — NEVER a verbatim
    copy of the full page.

    Extract the 7-axis OfficialDocumentMediaDescriptor from
    this page:

    1. power_event — the actor (e.g. "The State" in the
       Irish Constitution), the element (usually "none" for
       official documents; "spirit" for the World of Dreams
       analogue in Celtic-mythology Wikipedia pages), the
       power source (e.g. "the Constitution", "the
       syllabus"), the trigger, the scale tier, the cost,
       the consequence, the counter.
    2. visual_grammar — the composition is the page layout
       descriptor; the panel/shot type is the page format
       (e.g. "single-column", "two-column", "table", "figure");
       the other fields are n/a for official documents.
    3. palette — all fields are n/a for official documents
       (no visual).
    4. vfx_vocabulary — the particle_class is "ink"; the
       other fields are n/a for official documents.
    5. narrative_beat — the arc_position is the document
       reference (e.g. "NCCA LC Geography syllabus 2026
       § 1.2"); the beat_significance is the significance of
       the page.
    6. transferability — the in_game_mechanic is set to
       something like "syllabus_completion_event" or
       "certification_event" or "wikipedia_lore_lookup"; the
       anam cost (0 for official documents), the palette
       token + particle effect (null for v1).
    7. provenance — the rights holder is the issuing body
       (e.g. "NCCA" for Ireland, "SEC" for examinations.ie,
       "DfE" for England, "SQA" for Scotland, "WJEC" for
       Wales, "DESC" for Isle of Man, "CSO" / "NISRA" for
       census, "OSi" for boundaries, "Met Éireann" / "Met
       Office" for weather, "Wikipedia Foundation" for
       Wikipedia, "CELT" for CELT, "Dúchas" for Dúchas); the
       licence is "CC-BY-SA-4.0" for Wikipedia + CELT +
       Dúchas, "CC0" for CSO + NISRA + OSi open data,
       "fair-use-description" for the syllabus PDFs; the
       derivation class is "fair_use_quote" (we are
       summarising a short excerpt); the shippable field is
       always false; the shippable_art_path is always null.

    The metadata block is:
    {{ metadata }}

    The source URL is:
    {{ source_url }}

    The source timestamp is:
    {{ source_timestamp }}

    The language is:
    {{ language }}

    The verbatim evidence excerpt is:
    {{ evidence }}

    Return the typed OfficialDocumentMediaDescriptor.
  "#
}
