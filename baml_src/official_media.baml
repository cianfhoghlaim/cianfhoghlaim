// baml_src/official_media.baml
//
// BAML extraction functions for the ``official-media-pipeline``
// openspec change. Used by ``oideachais/dlt_sources/official_media/
// classifier.py`` as the Stage-2 fallback for the two-stage filter
// (deterministic allowlist + BAML-gated heuristic).
//
// Phase 3 of the change. The single function exported here:
//
//   ClassifyOfficialMedia(ig_username, ig_bio, ig_external_url)
//     -> OfficialMediaDecision
//
// is invoked only when (a) the username is not in any of the 4
// allowlist YAMLs AND (b) the cheap heuristic matches (verified
// badge, .gov/.ie/.uk/.ac in external URL, presence of words like
// "official", "department", "ministry", "police", "army", "agency"
// in the bio). This makes the BAML cost a tiny fraction of the
// raw filter pipeline.
//
// All clients route through the canonical LiteLLM gateway client
// ``LiteLLM`` with the model alias ``extract`` (gemini-2.5-pro ->
// glm-4.6 -> gemini-2.5-flash -> local GGUF). See
// ``baml_src/clients.baml`` for the full client registry.

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

enum OfficialMediaCategory {
  Intelligence
  University
  Party
  Jurisdiction
  Agency
  EmergencyService
  Military
  Government
  Other
}

class OfficialMediaDecision {
  is_official_media bool
  confidence float          // 0-1; the allowlist filter rejects below 0.7
  category OfficialMediaCategory
  reason string             // one-sentence justification, surfaced in the marimo dashboard
}

// ---------------------------------------------------------------------------
// Function
// ---------------------------------------------------------------------------

function ClassifyOfficialMedia(
  ig_username: string,
  ig_bio: string,
  ig_external_url: string?
) -> OfficialMediaDecision {
  client LiteLLM            // LiteLLM gateway with `extract` model alias
  prompt #"
    Decide if the Instagram profile {{ ig_username }} is an official
    British Isles government / political / public-service / university /
    emergency-services / intelligence-agency account.

    Username: {{ ig_username }}
    Bio: {{ ig_bio }}
    External URL: {{ ig_external_url }}

    Mark ``is_official_media=true`` ONLY for public bodies, elected
    offices, emergency services, universities, intelligence agencies,
    or other public-service organisations. Do NOT mark personal
    accounts, fan pages, parody accounts, or commercial businesses.

    Return:
      - ``is_official_media``: true or false
      - ``confidence``: 0.0 to 1.0 (your certainty)
      - ``category``: one of { Intelligence, University, Party,
        Jurisdiction, Agency, EmergencyService, Military, Government,
        Other }
      - ``reason``: a one-sentence justification that will be shown
        to the user in the marimo dashboard

    Be conservative: when in doubt, mark ``is_official_media=false``.
  "#
}
