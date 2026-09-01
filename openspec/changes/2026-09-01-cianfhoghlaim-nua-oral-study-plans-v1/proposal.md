# Change: Cianfhoghlaim-Nua Oral Study Plans v1 — Pipecat + Chatterbox + mms-tts-gle wiring

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Phase 6 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means Phases 0-5 are already
> shipped.

## Why

The Phase 1 chat-with-syllabus → study-plan surface shipped a Phase
1 stub for the oral-delivery companion: `voice_agent.process_audio()`
was a wired Pipecat client stub that returned a 1-second silent WAV;
`b.GenerateOralStudyPlan` returned an empty `audio_segments[]`.

Phase 6 wires the real TTS round-trip:

- **Pipecat HTTP client** (`agents/api/_oideachais_api/services/pipecat_client.py`)
  replaces the `pass # TODO: Pipecat SDK integration` body with a
  real HTTP round-trip to the canonical Pipecat service at
  `PIPECAT_URL` (default `http://pipecat:8765/v1`).
- **Dialect-aware TTS router** (`agents/api/_oideachais_api/services/tts_router.py`)
  routes per-dialect TTS requests to the canonical provider:
  - `standard` → Chatterbox
  - `connacht`/`munster`/`ulster` → facebook-mms-tts-gle (canonical
    Irish voice model)
  - Mock fallback when neither provider is installed
- **OralStudyPlayer A2UI component** (`web/packages/a2ui/src/components/OralStudyPlayer.tsx`)
  renders the per-week audio segments with `<audio>` controls.
- **Pluggable fallback**: when the Pipecat service is unreachable,
  the voice_agent falls back to the Phase 1 silent-WAV stub (so the
  agent works in lightweight container builds).

## What was shipped

### §1 — Author the canonical Pipecat HTTP client (1 file, ~140 LOC)

- **§1.1** `agents/api/_oideachais_api/services/pipecat_client.py`
  - `PipecatAudioRequest` dataclass (audio_b64 + session_id +
    language + agent)
  - `PipecatAudioResponse` dataclass (transcript_in + agent_text +
    audio_out_b64 + tts_provider + voice_id)
  - `PipecatUnreachable` exception (raised when Pipecat is down or
    httpx is not installed)
  - `call_pipecat_roundtrip(request)` async function
  - `b64_audio_from_bytes(audio_bytes)` helper

### §2 — Author the dialect-aware TTS router (1 file, ~160 LOC)

- **§2.1** `agents/api/_oideachais_api/services/tts_router.py`
  - `IrishDialect` type alias (`standard` / `connacht` / `munster` / `ulster`)
  - `TTSProvider` type alias (`chatterbox` / `orpheus-tts-3b-ft` / `facebook-mms-tts-gle` / `mock_chatterbox`)
  - `TTSRequest` + `TTSResponse` dataclasses
  - `_PROVIDER_FOR_DIALECT` routing table
  - `_synthesize_with_chatterbox(request)` async function (English +
    Irish standard)
  - `_synthesize_with_mms_tts_gle(request)` async function (Connacht /
    Munster / Ulster Irish)
  - `synthesize_oral_study_segment(request)` — the canonical
    router (falls back to mock if provider unavailable)
  - `synthesize_oral_study_plan_segments(segments, dialect)` —
    batched version for per-week plan synthesis

### §3 — Wire the real Pipecat HTTP round-trip into voice_agent (1 file modified)

- **§3.1** `agents/adk/voice_agent.py` `process_audio()` now:
  - Encodes audio as base64 + calls `call_pipecat_roundtrip()` from
    the new Pipecat client
  - Returns the canonical `PipecatAudioResponse` shape (transcript_in
    + agent_text + audio_out_b64)
  - Falls back to the Phase 1 silent-WAV stub on `PipecatUnreachable`
  - Phase marker is now `PHASE_6_WIRED` or `PHASE_6_UNREACHABLE`

### §4 — Add the OralStudyPlayer A2UI component (1 file, ~120 LOC)

- **§4.1** `web/packages/a2ui/src/components/OralStudyPlayer.tsx`
  - `OralStudySegmentData` interface (week_number + text_en + text_ga +
    estimated_duration_sec + tts_provider + voice_id + audio_b64)
  - `OralStudyPlayerData` interface (subject + dialect +
    total_duration_min + segments + phase)
  - Renders per-week segments with `<audio>` controls (base64
    data URI)
  - Shows the phase marker (phase1_stub = silent WAV,
    phase6_wired = real TTS)
- **§4.2** Updated `web/packages/a2ui/src/components/index.ts` barrel
  to export `OralStudyPlayer` + 3 new types

### §5 — Updated Phase 1 regression test (1 file)

- **§5.1** `tests/test_adk_subject_actions.py`
  `test_phase1_voice_agent_process_audio_not_a_pass` — accepts the
  new phase markers (`phase1_stub` / `phase6_wired` /
  `phase6_unreachable`) per the Phase 6 voice_agent rewrite.

### §6 — Spec delta to `agentic-frontend-frameworks` (1 file)

- **§6.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/specs/agentic-frontend-frameworks/spec.md`
  — adds 2 new Requirements:
    - "Pipecat HTTP client MUST gracefully fall back to silent WAV"
    - "Dialect-aware TTS router MUST route per Irish dialect"

## Impact

- **Audience:** every Cianfhoghlaim user (especially Irish-language
  students via the LC Gaeilge surface).
- **Scope:** 4 new files (~400 LOC) + 2 modified files.
- **LOC delta:** +~400.
- **Risk:** LOW — additive; the Pipecat client + TTS router are
  isolated services.
- **Reversibility:** full — the voice_agent can be reverted to the
  Phase 1 stub via `git revert`.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-baml-regeneration-blocker-v1/` — Phase 0.5
  (BAML regeneration) shipped earlier today. Required for the
  Phase 6 wired `b.GenerateOralStudyPlan` to compile.

`Blocked by (hard):` none.

`Extends:`

- [`openspec/specs/agentic-frontend-frameworks/spec.md`](../../specs/agentic-frontend-frameworks/spec.md)
  — adds 2 Requirements to the canonical agent UI spec.

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale copy of `gemini_hackathon/gemini_hackathon_backend/`
  (the GCP-first Pipecat service) — lifted selectively per the
  operator's earlier directive (deeply-per-sister-repo customisation,
  NOT wholesale copies).
- Real TTS round-trip via a managed service — Phase 6 uses the
  canonical self-hosted Pipecat + Chatterbox + mms-tts-gle stack
  (per the OSS-first posture). GCP-first Pipecat Cloud stays in
  the sister repo.
- Wholesale rewrite of the BAML contracts — Phase 1's
  `GenerateOralStudyPlan` stub schema is reused.

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1 --strict  ✅
uv run pytest tests/test_adk_subject_actions.py -v                                ✅ 11 passed
uv run python -c "from agents.api._oideachais_api.services.pipecat_client import call_pipecat_roundtrip"  ✅
uv run python -c "from agents.api._oideachais_api.services.tts_router import synthesize_oral_study_segment"  ✅
```

---

*Last updated by build subagent at 2026-09-01.*