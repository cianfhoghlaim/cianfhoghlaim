## ADDED Requirements

### Requirement: Pipecat HTTP client MUST gracefully fall back to silent WAV

The Cianfhoghlaim agentic-frontend-frameworks capability MUST expose
a Pipecat HTTP client (`agents/api/_oideachais_api/services/pipecat_client.py`)
that sends audio to the canonical Pipecat service at `PIPECAT_URL`
(default `http://pipecat:8765/v1`) + receives the agent response
+ TTS audio back.

The client MUST raise `PipecatUnreachable` when:
- The service is down (`httpx.ConnectError`, `httpx.HTTPStatusError`, etc.)
- `httpx` is not installed (lightweight container builds)

The `voice_agent.process_audio()` body MUST catch `PipecatUnreachable`
and fall back to the Phase 1 silent-WAV stub so the agent works
in lightweight container builds.

#### Scenario: A user sends audio to the voice agent

- **WHEN** a user sends audio bytes to `voice_agent.process_audio(audio_bytes, session_id)`
- **THEN** the agent POSTs the audio (base64-encoded) to `PIPECAT_URL/audio/roundtrip`
- **AND** returns the canonical `PipecatAudioResponse` shape (transcript_in + agent_text + audio_out_b64 + tts_provider + voice_id)
- **AND** the phase marker is `PHASE_6_WIRED`

#### Scenario: Pipecat is unreachable

- **WHEN** `PIPECAT_URL` is unreachable (the Pipecat service is down)
- **THEN** the agent catches `PipecatUnreachable` and falls back to a 1-second silent WAV
- **AND** the phase marker is `PHASE_6_UNREACHABLE`

### Requirement: Dialect-aware TTS router MUST route per Irish dialect

The Cianfhoghlaim agentic-frontend-frameworks capability MUST expose
a dialect-aware TTS router (`agents/api/_oideachais_api/services/tts_router.py`)
that routes TTS requests per Irish dialect:

| Dialect | TTS Provider | Notes |
|---------|--------------|-------|
| `standard` | Chatterbox | English / Irish standard fallback |
| `connacht` | facebook-mms-tts-gle | Connacht Irish (Galway, Mayo, Roscommon) |
| `munster` | facebook-mms-tts-gle | Munster Irish (Kerry, Cork, Waterford) |
| `ulster` | facebook-mms-tts-gle | Ulster Irish (Donegal) |

The router MUST try the canonical provider first and fall back to
the mock service when the canonical provider is unavailable.

#### Scenario: A Gaeilge student requests an oral study plan

- **WHEN** a student requests `synthesize_oral_study_segment(text="Bain triail as!", dialect="connacht")`
- **THEN** the router dispatches to `facebook-mms-tts-gle` (per the dialect routing table)
- **AND** the response `voice_id` is `gle-connacht`
- **AND** if the provider is unavailable, the router falls back to the mock service (Phase 6 graceful degradation)