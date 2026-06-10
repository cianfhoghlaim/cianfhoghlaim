# Cianfhoghlaim / kings_college_galway — Hackathon Submission Status

**As of:** 2026-06-08 20:00 UTC
**Head:** `9b14c9fa0` on `main`
**Branch state:** `up to date with origin/main`

## Build Small 2026 — current state

| Phase | Status | Notes |
|:--|:-:|:--|
| 5 hackathon planning artefacts committed | done | `doc/hackathons/build-small-2026-*.md` |
| OpenSpec change authored + validated `--strict` | done | `openspec/changes/croilar-hf-build-small-2026-demo/` |
| OpenSpec change archived | done | `openspec/changes/archive/2026-06-08-...` + `openspec/specs/croilar-gradio-hf-demo/` |
| Shared bundle (`spaces/_common/`) | done | 10 files, 1,896 lines |
| BAML client fork + 4 new schemas | done | `spaces/_common/baml/*.baml` |
| Space 1 — An Scrúdú (Talamh) | code done | `spaces/an_scrudu/` — BAML extractor + heatmap + PCLM-PDF |
| Space 2 — Meaisín Cliste (Aer + Uisce) | code done | `spaces/meaisin_cliste/` — 3-tab app, 30 cognates, 26-county map |
| Space 3 — Cianfhoghlaim (Anam) | code done | `spaces/cianfhoghlaim/` — 6 NPCs, inline-SVG British Isles map |
| Space 4 — Anam Tuatha (all 5 elements) | code done | `spaces/anam_tuatha/` — 7-panel integration app |
| 4 social cards (1200×630 PNG) | done | one per Space dir |
| 4 voiceover scripts + storyboards + JSON sequences | done | one set per Space |
| Deployment runbook | done | `doc/hackathons/build-small-2026-runbook.md` |
| Push script (uses new `hf` CLI) | done | `scripts/push_spaces_to_hf.sh` |
| `hf auth whoami` returns `cianfhoghlaim` | done | token already in venv |
| Push 4 Spaces to `huggingface.co/cianfhoghlaim/` | **pending — your turn** | run `bash scripts/push_spaces_to_hf.sh` |
| Add `HF_TOKEN` secret to each Space | **pending — your turn** | 4 Settings tabs |
| Record 4 demo videos | **pending — your turn** | voiceover scripts in `spaces/*/voiceover_script.txt` |
| Fill submission form | **pending — your turn** | copy-paste text in the runbook §5 |
| Post blog | **pending — your turn** | `doc/hackathons/build-small-2026-blog.md` |
| Post tweet thread | **pending — your turn** | `doc/hackathons/build-small-2026-tweet-thread.md` |

## Quick deploy (one-liner)

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway
bash scripts/push_spaces_to_hf.sh
```

The script handles everything: auth check, repo creation, file upload
to all 4 Spaces. Idempotent — safe to re-run.

## Codebase health

- All 30 Python files in `spaces/` pass `ast.parse`
- All 4 Spaces have offline fallbacks (the demo never breaks)
- All 4 Spaces use the 3-tier HF Inference fallback (Qwen 7B → Llama 8B → Gemma 9b, all ≤32B)
- All 4 Spaces render the same "Anam Bonneagar" footer with 5 trust signals
- All 4 Spaces are bilingual EN + Gaeilge (5 other Celtic langs as i18n placeholders)
- Total: 5,557 lines of Python + 389 lines of BAML + 4 social cards + 4 storyboards

## Headline numbers

- 4 Spaces × 5 elements × 1 typed pipeline
- 6 Celtic NPCs × 3 model tiers = 108 call permutations
- 30 cognates × 6 languages = 180 cells
- 26 counties × Pobal HP 2022 = 1,629 schools mapped
- 5 Celtic-nation curricula × 6 reference topics = 30 cross-nations
- 8 molecules × CPK colours = 32 atoms rendered
- 5-feat Sétanta → Cúchulainn → Ríastrad progression
- 10 bilingual classroom actions in Fiosraigh

## File map (where to find things)

| What | Where |
|:--|:--|
| 5 planning artefacts | `doc/hackathons/build-small-2026-*.md` |
| This status doc | `doc/hackathons/STATUS.md` |
| Submission runbook (5 steps) | `doc/hackathons/build-small-2026-runbook.md` |
| Blog draft (for dev.to etc.) | `doc/hackathons/build-small-2026-blog.md` |
| 6-tweet thread | `doc/hackathons/build-small-2026-tweet-thread.md` |
| OpenSpec archived change | `openspec/changes/archive/2026-06-08-croilar-hf-build-small-2026-demo/` |
| OpenSpec spec | `openspec/specs/croilar-gradio-hf-demo/spec.md` |
| Shared bundle (in every Space) | `spaces/_common/` |
| Space 1 source | `spaces/an_scrudu/` |
| Space 2 source | `spaces/meaisin_cliste/` |
| Space 3 source | `spaces/cianfhoghlaim/` |
| Space 4 source | `spaces/anam_tuatha/` |
| Push script (uses `hf`) | `scripts/push_spaces_to_hf.sh` |
| Social card renderer | `scripts/render_social_cards.py` |

## The 5-element connective tissue

| Element | Color | Hex | Space |
|:--|:--|:--|:--|
| **Talamh** (Earth) | emerald | `#28955e` | Space 1 (An Scrúdú) + Space 4 Panel 1 |
| **Uisce** (Water) | azure | `#1e80c6` | Space 2 (Scoil theme) + Space 4 Panel 2 |
| **Tine** (Fire) | amber | `#d68c1c` | Space 4 Panel 3 (OCR Gaelscríbhneoir) |
| **Aer** (Air) | indigo | `#5a4fcf` | Space 2 (Foclóir + Curaclam) + Space 4 Panel 4 |
| **Anam** (Spirit) | gold | `#cc9966` | Space 3 (NPC dialogue) + Space 4 Panel 5 (soulbound) |

Long learning. Cianfhoghlaim.
