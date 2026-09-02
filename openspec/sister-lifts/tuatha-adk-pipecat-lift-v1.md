# Sister-Repo Lift: `tuatha-adk-pipecat-lift-v1`

> **One-line summary:** Lift the wired Pipecat + TTS router +
> LC planner + 4-step per-subject ADK pattern from cianfhoghlaim
> into tuatha (the British Isles Formative Assessment MMO). The
> Babylon.js 3D + SpacetimeDB legacy theming is hard-archived per
> the 2026-08-25 consolidation; the ADK 2-stage coordinators are
> the new tuatha ops surface.

## Source files (cianfhoghlaim)

| # | Source path | Bytes | Description |
|--:|---|--:|---|
| T.1 | `agents/adk/voice_agent.py` | ~18 KB | The wired Pipecat + ChatterboxTTS dispatch + 5 voice_profile overrides. |
| T.2 | `agents/api/_oideachais_api/services/pipecat_client.py` | ~6 KB | The Pipecat WS + RTTS client bridge. |
| T.3 | `agents/api/_oideachais_api/services/tts_router.py` | ~4 KB | The TTS router with voice_id mapping. |
| T.4 | `agents/adk/subjects/lc/planner.py` | ~10 KB | The canonical LC study-plan planner. |
| T.5 | `agents/adk/subjects/lc/chemistry.py` | ~5 KB | The canonical 4-step per-subject ADK pattern (extract → plan → render → dispatch). |

## Destination files (tuatha)

| # | Destination path | Bytes | Source |
|--:|---|--:|---|
| T.1.dest | `~/dev/tuatha/agents/adk/voice_agent.py` | ~16 KB | T.1 (drop the Lingala + French (CA) voice_profiles — tuatha is LC + JC only) |
| T.2.dest | `~/dev/tuatha/agents/api/_oideachais_api/services/pipecat_client.py` | ~6 KB | T.2 (lift as-is — the Pipecat client is identical across both repos) |
| T.3.dest | `~/dev/tuatha/agents/api/_oideachais_api/services/tts_router.py` | ~3 KB | T.3 (rewrite the voice_id mapping to use tuatha's 5 voice profiles) |
| T.4.dest | `~/dev/tuatha/agents/adk/subjects/lc/planner.py` | ~10 KB | T.4 (lift as-is) |
| T.5.dest | `~/dev/tuatha/agents/adk/subjects/lc/chemistry.py` | ~5 KB | T.5 (lift as-is; tuatha replicates the 4-step pattern across its 14 subjects per `2026-08-26-extend-educational-mmo-to-14-subjects-v1/`) |

## Transformation rules

### T.1 — voice_agent.py

| Rule | Before | After |
|---|---|---|
| **voice_profiles** | `voice_profiles = {"lc_mathematics": "...", "lc_gaeilge_ga": "...", "lc_gaeilge_ga_connemara": "...", "lingala_lc": "...", "french_ca_lc": "...", "jc_mathematics": "...", "jc_english": "..."}` | Tuatha uses LC + JC only — drop `lingala_lc` + `french_ca_lc`; keep the 5 LC + 2 JC voice profiles |
| **dispatch_table** | Maps to BIEP + JC + LC + Lingala + French (CA) | Tuatha uses LC + JC only — drop the Lingala + French (CA) entries |
| **Class names** | `PipecatVoiceAgent` | `TuathaVoiceAgent` (rename to align with `TuathaRootAgent` + `TuathaCaptureAgent` naming pattern) |

### T.3 — tts_router.py

| Rule | Before | After |
|---|---|---|
| **voice_id mapping** | 7 voice_ids mapped to BIEP BAML functions + LC + JC + Lingala + French (CA) | 5 voice_ids mapped to LC + JC BAML functions only |
| **BAML function refs** | `b.GenerateStudyPlanAssets` + `b.GenerateLingalaStudyPlan` + `b.GenerateFrenchCAStudyPlan` | `b.GenerateLCStudyPlan` + `b.GenerateJCStudyPlan` (the canonical tuatha functions) |
| **Default voice_id** | `"lc_gaeilge_ga"` | `"lc_english"` (tuatha's default subject) |

### T.2, T.4, T.5 — No transformation

- T.2 — The Pipecat client bridge is identical (Hono + ws bridge; not subject-specific).
- T.4 — The LC planner is identical (canonical study-plan surface per Phase 1).
- T.5 — The 4-step per-subject pattern is identical (extract → plan → render → dispatch).

## Per-PR step-by-step checklist

### PR #1 — Lift the wired voice agent (3 items)

- [ ] **1.1** Copy `agents/adk/voice_agent.py` → `~/dev/tuatha/agents/adk/voice_agent.py`
- [ ] **1.2** Apply the 3 transformation rules above (voice_profiles + dispatch_table + class names)
- [ ] **1.3** Run `cd ~/dev/tuatha && uv run pytest agents/adk/tests/test_voice_agent.py -v`

### PR #2 — Lift the Pipecat client + TTS router (4 items)

- [ ] **2.1** Copy `agents/api/_oideachais_api/services/pipecat_client.py` → `~/dev/tuatha/agents/api/_oideachais_api/services/pipecat_client.py` (no transformation)
- [ ] **2.2** Copy `agents/api/_oideachais_api/services/tts_router.py` → `~/dev/tuatha/agents/api/_oideachais_api/services/tts_router.py` (apply the 3 voice_id mapping rules)
- [ ] **2.3** Wire `voice_agent.py` → `pipecat_client.py` → `tts_router.py` in `tuatha/agents/api/_oideachais_api/routes/audio.py`
- [ ] **2.4** Run `cd ~/dev/tuatha && uv run pytest agents/api/_oideachais_api/tests/test_audio_routes.py -v`

### PR #3 — Lift the LC planner + apply the 4-step pattern to 14 subjects (5 items)

- [ ] **3.1** Copy `agents/adk/subjects/lc/planner.py` → `~/dev/tuatha/agents/adk/subjects/lc/planner.py` (no transformation)
- [ ] **3.2** Copy `agents/adk/subjects/lc/chemistry.py` → `~/dev/tuatha/agents/adk/subjects/lc/chemistry.py` (no transformation; the 4-step pattern is canonical)
- [ ] **3.3** Apply the 4-step pattern to the remaining 13 LC subjects in tuatha (per `2026-08-26-extend-educational-mmo-to-14-subjects-v1/`)
- [ ] **3.4** Author `tuatha/agents/adk/subjects/lc/_pattern.py` with the shared 4-step base class so the 14 subjects share the pattern
- [ ] **3.5** Run `cd ~/dev/tuatha && uv run pytest agents/adk/subjects/lc/tests/ -v`

## What stays behind (explicit)

- **The Babylon.js 3D + SpacetimeDB v2 + Pent-Elemental Cosmology
  + Crypteolas + Anam Cara + Brown Ajah legacy theming** — the
  tuatha consolidation plan hard-archives these to
  `tuatha/old/legacy_theming/` per the 2026-08-25 change. The ADK
  2-stage coordinators are the new tuatha ops surface.
- **The Lingala + French (CA) voice_profile additions** — tuatha
  is LC + JC only; the BIEP-JC subject extension to Lingala +
  French (CA) stays in cianfhoghlaim.

## Sister-repo hand-off

- Tuatha maintainer receives this lift patch + openspec change
  `2026-09-XX-tuatha-lift-v1.md` (authored in
  `~/dev/tuatha/openspec/changes/`).
- Approximate LOC delta: 720 LOC (~16 KB voice_agent + ~6 KB
  pipecat + ~3 KB tts_router + ~10 KB planner + ~5 KB chemistry
  + ~40 KB of 14-subject wire-up).
