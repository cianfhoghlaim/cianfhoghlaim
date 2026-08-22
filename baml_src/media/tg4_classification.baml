// BAML file: tg4_classification.baml
//
// Per the `2026-08-25-tg4-foghlaim-corpus-v1` openspec change.
//
// 4 BAML functions that power the TG4 + Foghlaim multimodal embedding
// pipeline:
//
//   1. ClassifyTg4Episode    — per-episode metadata → BIEP subject join
//                              + dialect + Irish-purity scoring
//   2. ExtractSpeakerLineup  — VTT cues → speaker diarization (with
//                              Irish dialect + fluency tagging)
//   3. ExtractWorksheetAnswers — worksheet PNG → structured questions
//                              + Bloom levels + mark allocations
//   4. AuditTranscriptQuality — VTT (canonical) vs WhisperX (audio
//                              audit) → coverage + disagreement metrics
//
// Routing: per the proposal's cost-ordering
//   - ClassifyTg4Episode       : every episode
//   - ExtractSpeakerLineup     : every episode
//   - ExtractWorksheetAnswers  : only when has_worksheet=true
//   - AuditTranscriptQuality   : 5% sample + every NCCA-tagged lesson
//
// Clients: routes through the canonical baml_src/clients.baml.
// Per the `centralized-model-registry` contract, no literal HuggingFace
// IDs — every client<llm> block is keyed off MODEL_REGISTRY.
//
// Re-gen: `mise run baml:generate`
// Re-validate: `mise run baml:test`

// ---------------------------------------------------------------------------
// Class 1: Per-episode metadata classification
// ---------------------------------------------------------------------------

class Tg4EpisodeClassification {
  biep_subject string  @description("One of the BIEP v3 subject slugs: mathematics | chemistry | geography | gaeilge | english | computer_science | history | gaeilge_oral | gaeilge_literature | gaeilge_poetry | gaeilge_current_affairs | gaeilge_children | science | music | music_songs | art | physical_education | wellbeing | business | geography_climate | non_curriculum")
  biep_stage string  @description("One of: bunscoil | junior_cycle | senior_cycle | adult")
  dialect string  @description("Primary Irish dialect: connacht | munster | ulster | mixed | unknown")
  irish_purity_score float  @description("0.0-1.0 — fraction of dialogue in Irish (vs English/other). Use 0.5 for mixed-language shows.")
  educational_use bool  @description("True if the episode has explicit educational framing (curriculum alignment, learning outcomes, age rating <18). False for pure entertainment (drama, music videos).")
  age_appropriate bool  @description("True if the episode is suitable for the level(s) inferred from the Foghlaim context. False if it contains explicit adult content.")
  confidence float  @description("0.0-1.0 — model's own confidence in the classification. Use this as a BAML runtime quality signal.")
  rationale string  @description("One-sentence rationale for the classification, useful for the marimo notebook's audit panel.")
}

function ClassifyTg4Episode(
  title: string,
  description: string,
  genre: string,
  series: string,
  duration_s: int,
  foghlaim_metadata: string?
) -> Tg4EpisodeClassification {
  client ExtractEnStrong
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish-language media classifier. Given the
    episode metadata + optional Foghlaim educational metadata, classify
    the episode into the BIEP v3 subject taxonomy + the Irish dialect
    distribution.

    BIEP v3 subjects (canonical):
    - 6 LC subjects: mathematics, chemistry, geography, gaeilge, english, computer_science
    - 18 JC subjects (use the closest slug): history, gaeilge_oral,
      gaeilge_literature, gaeilge_poetry, gaeilge_current_affairs,
      gaeilge_children, science, music, music_songs, art,
      physical_education, wellbeing, business, geography_climate
    - Sentinel: non_curriculum (entertainment, music videos, sport, drama)

    Irish dialects: connacht (Western), munster (Southern), ulster (Northern), mixed (pan-dialect), unknown.

    Irish-purity score: ratio of dialogue in Irish vs English. Nuacht TG4 is ~0.95. Béalbhinn interviews are ~0.5. English-only programmes are 0.0.

    Educational use: True if the show has explicit curriculum framing
    or learning outcomes; False for pure entertainment.

    Episode metadata:
      Title: {{ title }}
      Description: {{ description }}
      Genre: {{ genre }}
      Series: {{ series }}
      Duration (seconds): {{ duration_s }}
      Foghlaim educational metadata (optional): {{ foghlaim_metadata }}

    {{ ctx.output_format }}
  "#
}

// ---------------------------------------------------------------------------
// Class 2: Speaker diarization from VTT cues
// ---------------------------------------------------------------------------

class SpeakerTurn {
  speaker string  @description("Speaker label (e.g. 'presenter_1', 'interviewee_2'). Use 'presenter', 'interviewee', 'child', 'expert', 'narrator' as defaults if no diarization hint is available.")
  t_start_s float
  t_end_s float
  transcript string  @description("Verbatim VTT cue text")
  irish_fluency string  @description("native | L2 | mixed")
}

class Speaker {
  label string
  gender string  @description("male | female | nonbinary | unknown")
  dialect string  @description("connacht | munster | ulster | mixed | unknown")
  role string  @description("presenter | interviewee | child | expert | narrator")
  irish_fluency string  @description("native | L2 | mixed")
}

class SpeakerLineup {
  speakers Speaker[]
  turns SpeakerTurn[]
  total_speakers int
  total_duration_s float
}

function ExtractSpeakerLineup(
  vtt_cues_json: string,
  duration_s: int,
  show_context: string?
) -> SpeakerLineup {
  client ExtractEnStrong
  prompt #"
    {{ _.role("user") }}
    You are an expert at Irish-language speaker diarization. Given the
    JSON-encoded VTT cues from a TG4 episode, extract the speaker
    lineup + speaker-tagged turn list.

    VTT cues JSON:
      {{ vtt_cues_json }}
    Episode duration (seconds): {{ duration_s }}
    Show context (optional): {{ show_context }}

    Rules:
    - Infer speakers from speaker tags in the VTT (e.g. <v Speaker 1>)
      when available.
    - When no speaker tags are present, infer from context:
      - The first speaker is usually the presenter / news anchor.
      - Subsequent speakers are interviewees / guests / voice-over.
    - Each turn MUST have t_start_s < t_end_s and the transcript must
      match the corresponding VTT cue verbatim.
    - irish_fluency: 'native' for native Irish speakers, 'L2' for
      learners, 'mixed' for code-switchers.
    - dialect: per the canonical Connacht / Munster / Ulster tags. Use
      'mixed' for pan-dialect shows.

    {{ ctx.output_format }}
  "#
}

// ---------------------------------------------------------------------------
// Class 3: Worksheet answer extraction (only when has_worksheet=true)
// ---------------------------------------------------------------------------

class WorksheetQuestion {
  q_number int
  irish_text string  @description("The question in Irish (verbatim from the worksheet).")
  english_translation string?  @description("English translation of the question, if unambiguous.")
  mark_allocation int  @description("Mark allocation for this question, as printed on the worksheet. Use 0 if not specified.")
  difficulty string  @description("Bloom's taxonomy level: remember | understand | apply | analyse | evaluate | create")
}

class WorksheetAnswers {
  questions WorksheetQuestion[]
  total_marks int
  subject_foghlaim string  @description("The Foghlaim subject tag as printed on the worksheet header.")
  level_foghlaim string  @description("The educational level as printed on the worksheet header: Bunscoil | Sraith Shóisearach | Ardteist | ... | Adult")
  learning_outcomes string[]  @description("The 'Spriocanna Foghlama' learning outcomes printed at the top of the worksheet.")
}

function ExtractWorksheetAnswers(
  worksheet_image_url: string,
  page_title: string,
  page_description: string?
) -> WorksheetAnswers {
  client ExtractEnStrong
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting worksheet answers from TG4 Foghlaim
    educational worksheets. Given a worksheet image URL + the page
    title, extract the structured questions + Bloom-level difficulty +
    mark allocations.

    Worksheet image URL: {{ worksheet_image_url }}
    Page title: {{ page_title }}
    Page description (optional): {{ page_description }}

    Rules:
    - Each question MUST have a question number, the verbatim Irish
      text, an English translation if unambiguous, a mark allocation,
      and a Bloom's taxonomy level.
    - total_marks MUST equal the sum of per-question mark_allocation.
    - learning_outcomes MUST be the verbatim 'Spriocanna Foghlama'
      printed at the top of the worksheet, in Irish.
    - subject_foghlaim + level_foghlaim MUST match the worksheet
      header text exactly.

    If the image is unreadable, return an empty questions array with
    rationale in the page_description.

    {{ ctx.output_format }}
  "#
}

// ---------------------------------------------------------------------------
// Class 4: Subtitle–audio alignment audit (5% sample + every NCCA-tagged)
// ---------------------------------------------------------------------------

class TranscriptQualityAudit {
  coverage float  @description("0.0-1.0 — fraction of canonical VTT cues that have a corresponding WhisperX segment. 1.0 = perfect VTT coverage; 0.5 = half the cues are unmatched.")
  disagreement_rate float  @description("0.0-1.0 — fraction of matched cues where WhisperX transcript text disagrees with the VTT text (after whitespace + punctuation normalisation). 0.0 = perfect text agreement; 0.3 = heavy disagreement.")
  insertion_rate float  @description("0.0-1.0 — fraction of WhisperX segments that have no corresponding VTT cue. 0.05 = expected baseline (interjections, breaths); 0.30 = serious divergence.")
  missing_cues_count int  @description("Count of VTT cues that have NO corresponding WhisperX segment within ±2s.")
  total_vtt_cues int
  total_whisperx_segments int
  matched_pairs int
  assessment string  @description("One of: 'high_quality' (coverage >= 0.95, disagreement <= 0.10), 'medium_quality' (coverage >= 0.80, disagreement <= 0.20), 'low_quality' (anything below).")
  notes string  @description("Free-form notes explaining the divergence (e.g. 'strong Múscraí accent in 70% of cues, likely ASR difficulty', 'speaker 2 is a learner, expected lower accuracy').")
}

function AuditTranscriptQuality(
  vtt_cues_json: string,
  whisperx_segments_json: string,
  show_context: string?
) -> TranscriptQualityAudit {
  client ExtractEnStrong
  prompt #"
    {{ _.role("user") }}
    You are an expert at evaluating transcript quality. Given the
    JSON-encoded canonical Brightcove VTT cues (treated as ground truth)
    + the audio-derived WhisperX segments, compute alignment metrics.

    Canonical VTT cues JSON:
      {{ vtt_cues_json }}

    Audio-derived WhisperX segments JSON:
      {{ whisperx_segments_json }}

    Show context (optional): {{ show_context }}

    Rules:
    - A VTT cue and a WhisperX segment are 'matched' when their
      t_start_s overlap is within ±2s AND the (whitespace + case-folded)
      text similarity is >= 0.5.
    - coverage = matched_pairs / total_vtt_cues
    - disagreement_rate = matched_pairs_with_text_disagreement / matched_pairs
    - insertion_rate = (total_whisperx_segments - matched_pairs) / total_whisperx_segments
    - assessment: high_quality when coverage >= 0.95 AND disagreement <= 0.10,
      medium_quality when coverage >= 0.80 AND disagreement <= 0.20,
      otherwise low_quality.

    This audit provides proof-of-alignment for the canonical VTT used
    in the multimodal embedding pipeline. High coverage + low
    disagreement = VTT can be trusted as the canonical transcript.

    {{ ctx.output_format }}
  "#
}