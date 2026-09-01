// BAML template: Oral Study Plan Generator (Phase 1 stub; Phase 6 wired)
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1 of the cianfhoghlaim-nua v6 era plan).
//
// This file ships a Phase 1 stub callable that returns an empty
// `audio_segments[]` with the dialect echoed from the input. Phase 6
// replaces the stub with a real Pipecat + Chatterbox dispatch wired to
// the canonical `agents/api/_oideachais_api/services/chatterbox.py`
// TTS service (and `orpheus-tts-3b-ft` for the LC Gaeilge subject
//
// The dialect routing table:
//
//   dialect == STANDARD   -> TTS provider: "chatterbox" (English)
//   dialect == CONNACHT  -> TTS provider: "facebook-mms-tts-gle" (Irish)
//   dialect == MUNSTER   -> TTS provider: "facebook-mms-tts-gle" (Irish)
//   dialect == ULSTER    -> TTS provider: "facebook-mms-tts-gle" (Irish)
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src
//
// Reference:
//   openspec/changes/2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/
//   baml_src/british_isles/_shared/study_plan.baml (the text-plan input)
//   agents/api/_oideachais_api/services/chatterbox.py (the TTS service)
//   baml_src/celtic/sources.baml (the canonical IrishDialect enum;
//     duplicated here as a string alias to keep the template self-contained)

// ============================================================================
// Canonical enums
// ============================================================================

enum OralStudyPlanTTSProvider {
  CHATTERBOX           @description("Chatterbox TTS (English; the canonical Irish-standard fallback)")
  ORPHEUS_TTS_3B_FT    @description("Orpheus TTS 3B fine-tune (Gaeilge voice)")
  FACEBOOK_MMS_TTS_GLE @description("Facebook MMS-TTS-GLE (Connacht / Munster / Ulster Irish)")
}

enum OralStudyPlanPhase {
  PHASE_1_STUB @description("Phase 1: returns empty audio_segments (this file ships now)")
  PHASE_6_WIRED @description("Phase 6: real Pipecat + Chatterbox dispatch (delivered in Phase 6)")
}

// ============================================================================
// Output classes
// ============================================================================

class OralStudySegment {
  week_number             int    @description("Mirrors the StudyPlanWeek.week_number this segment covers")
  text_en                 string @description("Spoken English text")
  text_ga                 string? @description("Spoken Irish text (null for EN-only subjects)")
  estimated_duration_sec  float  @description("Estimated segment duration in seconds")
  tts_provider            OralStudyPlanTTSProvider @description("Which TTS provider to call")
  voice_id                string @description("Provider-specific voice id (empty in Phase 1 stub)")
}

class OralStudyPlan {
  study_plan_id     string  @description("Foreign key to the parent StudyPlan row in the Convex study_plans table")
  dialect           string  @description("Irish dialect echoed from the input (connacht / munster / ulster / standard)")
  duration_min      float   @description("Total estimated oral duration in minutes (0.0 in Phase 1 stub)")
  voice_id          string  @description("Provider-specific voice id (empty in Phase 1 stub)")
  audio_segments    OralStudySegment[] @description("Per-week spoken segments; empty in Phase 1 stub")
  phase             OralStudyPlanPhase @description("The implementation phase marker")
  trace_id          string? @description("Langfuse trace id (populated by the @trace decorator)")
}

// ============================================================================
// Phase 1 stub: returns an empty audio_segments[] with the dialect echoed.
// Phase 6 will replace the prompt body with the real Pipecat + Chatterbox dispatch.
// ============================================================================

function GenerateOralStudyPlan(
  text_plan_id: string,
  subject: string,
  dialect: string,
  total_weeks: string
) -> OralStudyPlan {
  client Primary
  prompt #"
    {{ _.role("user") }}
    Phase 1 STUB — return an OralStudyPlan with `audio_segments=[]`,
    `duration_min=0.0`, `voice_id=""`, `phase=PHASE_1_STUB`, and
    `dialect` echoed from the input `{{ dialect }}`. The parent
    StudyPlan has id is `{{ text_plan_id }}` for the `{{ subject }}`
    subject over `{{ total_weeks }}` weeks. Phase 6 (forthcoming) will
    fill the real Pipecat + Chatterbox dispatch here.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML test blocks (per the canonical @assert requirement)
// ============================================================================

test oral_study_plan_gaeilge_connacht_16w {
  functions [GenerateOralStudyPlan]
  args {
    text_plan_id "plan_test_connacht_16w"
    subject "gaeilge"
    dialect "connacht"
    total_weeks "16"
  }
}

test oral_study_plan_chemistry_standard_12w {
  functions [GenerateOralStudyPlan]
  args {
    text_plan_id "plan_test_chemistry_12w"
    subject "chemistry"
    dialect "standard"
    total_weeks "12"
  }
}
