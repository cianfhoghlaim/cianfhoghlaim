# Tasks — Cianfhoghlaim-Nua Oral Study Plans v1

> 6 sections, 9 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1 --strict` exits 0

## Phase B — Author the canonical Pipecat HTTP client (§1, 1 task)

- [x] **B.1** `agents/api/_oideachais_api/services/pipecat_client.py` (~140 LOC)
  - `PipecatAudioRequest` + `PipecatAudioResponse` dataclasses
  - `PipecatUnreachable` exception
  - `call_pipecat_roundtrip(request)` async function
  - `b64_audio_from_bytes(audio_bytes)` helper

## Phase C — Author the dialect-aware TTS router (§2, 1 task)

- [x] **C.1** `agents/api/_oideachais_api/services/tts_router.py` (~160 LOC)
  - `IrishDialect` + `TTSProvider` type aliases
  - `TTSRequest` + `TTSResponse` dataclasses
  - `_PROVIDER_FOR_DIALECT` routing table
  - `_synthesize_with_chatterbox` + `_synthesize_with_mms_tts_gle`
  - `synthesize_oral_study_segment` + `synthesize_oral_study_plan_segments`

## Phase D — Wire the real Pipecat HTTP round-trip into voice_agent (§3, 1 task)

- [x] **D.1** `agents/adk/voice_agent.py` `process_audio()` rewired to use the new Pipecat client + fallback to silent WAV

## Phase E — Add the OralStudyPlayer A2UI component (§4, 2 tasks)

- [x] **E.1** `web/packages/a2ui/src/components/OralStudyPlayer.tsx` (~120 LOC)
- [x] **E.2** `web/packages/a2ui/src/components/index.ts` updated to export `OralStudyPlayer`

## Phase F — Updated Phase 1 regression test + spec delta (§5-§6, 2 tasks)

- [x] **F.1** `tests/test_adk_subject_actions.py` — accepts the new phase markers
- [x] **F.2** Spec delta to `agentic-frontend-frameworks` — 2 ADDED Requirements

---

*Last updated by build subagent at 2026-09-01.*