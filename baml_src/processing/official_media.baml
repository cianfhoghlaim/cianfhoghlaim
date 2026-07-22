// oideachais/baml_src/official_media.baml
//
// Stage-2 BAML fallback for the official-media Instagram export pipeline.
// Invoked by `oideachais.dlt_sources.official_media.classifier.classify_with_baml`
// when the cheap heuristic matches but the username is not in any allowlist YAML.
//
// The function returns a structured classification that the allowlist
// filter maps to the canonical category enum:
//   Intelligence / University / Party / Jurisdiction / Agency /
//   EmergencyService / Military / Government / Other
//
// See `oideachais/AGENTS.md` (official-media-pipeline spec) and
// `oideachais/dlt_sources/official_media/classifier.py` for the
// Python-side consumer.

class OfficialMediaCategory {
  // The category enum mirrors the BAML-side category strings.
  // Python `classify_with_baml` maps these to lowercase strings
  // ('intelligence', 'university', 'party', 'jurisdiction',
  // 'agency', 'emergency_service', 'military', 'government', 'other').
  // When the function returns "Other", the Python wrapper falls
  // back to "other" (catch-all bucket).
  is_official_media bool @description("True if the profile is an official-media account.")
  confidence float @description("0.0 (not official) to 1.0 (definitively official).")
  category string @description("One of: Intelligence, University, Party, Jurisdiction, Agency, EmergencyService, Military, Government, Other.")
  reason string @description("One-paragraph explanation of the classification decision.")
}

function ClassifyOfficialMedia(
  ig_username: string,
  ig_bio: string,
  ig_external_url: string?
) -> OfficialMediaCategory {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// =============================================================================
// Merged from /baml_src/official_media.baml (root) on 2026-06-25
// Skipped: enum OfficialMediaCategory (collision — sruth class OfficialMediaCategory wins)
// Skipped: function ClassifyOfficialMedia (collision — sruth function ClassifyOfficialMedia wins)
// =============================================================================
// (class OfficialMediaDecision removed by openspec change 2026-07-14 - was a stray class with no schema)
