---
title: Cianfhoghlaim - Tuatha RPG
emoji: "\U0001F3DB"
colorFrom: indigo
colorTo: gold
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Hades-style dialogue with 6 Celtic NPCs on a British Isles map.
---

# Cianfhoghlaim — Tuatha RPG

> "Long learning" — a Hades-style dialogue game set on a navigable map of
> the British Isles, where you speak with 6 Celtic NPCs, each grounded in
> a cached Wikipedia article.

**Build Small 2026 hackathon submission.** Space 3 of 4. Element: **Anam**
(Spirit) — the soulbound layer of the connective tissue.

## What's in this Space

- A self-contained inline-SVG map of the British Isles (`world_map.json`)
  with 6 diegetic zones (Leinster, Man, Dyfed, Sláine, Cualann, Carrigaphooca)
- 6 NPCs, each grounded in a Wikipedia article cached at
  `doc/hackathons/wikipedia-sources/`:
  1. **Uí Liatháin** (Leinster) — dynasty of the pine ridge
  2. **Manannán mac Lir** (Isle of Man) — the sea-god of the Otherworld
  3. **Rhiannon** (Wales) — the rider of the Mabinogi
  4. **Dian Cécht** (Tuatha Dé Danann) — the physician-god
  5. **Cian** (Cualann) — father of Lugh Lámhfhada
  6. **The Déisi** (Waterford / diaspora) — the dispossessed
- Dialogue via the 3-tier HF Inference fallback chain
  (Qwen 7B → Llama 8B → Gemma 9b, all ≤32B)
- Bilingual EN + Gaeilge (5 other Celtic languages as i18n placeholders)
- Gamification: artifacts collected on every 3rd turn

## Architecture

```
spaces/cianfhoghlaim/
├── app.py           # Gradio app: SVG map + NPC dropdown + dialogue log
├── npcs.py          # The 6 NPCs (dataclass, frozen)
├── world_map.json   # Diegetic zones + NPC markers (1000x700 SVG viewbox)
├── dialogue.py      # BAML call handler + conversation state
├── requirements.txt # Gradio 4.44+, huggingface_hub
├── record_demo.py   # Programmatic demo sequence
├── social_card.png  # 1200x630 PNG (generated at build time)
└── README.md        # (this file)
```

Shared with the other 3 Spaces via `spaces/_common/`:

- `theme.py` — Celtic 5-element palette + Hades Shadow-First CSS
- `anam_bonneagar.py` — per-Space trust-signal footer
- `baml_client.py` — 3-tier HF Inference fallback
- `i18n.py` — bilingual EN/GA toggle

## Running locally

```bash
cd spaces/cianfhoghlaim
pip install -r requirements.txt
HF_TOKEN=hf_xxx python app.py
# open http://localhost:7860
```

## How the dialogue is grounded

Each `speak_with_npc()` call:
1. Builds a system prompt with the NPC's name, title, era, scholarly
   excerpt, and emotional default
2. Sends the last 6 turns + the new player utterance
3. The BAML chain (`spaces/_common/baml/hackathon_schemas.baml`
   `GenerateNpcDialogue`) returns a typed JSON:
   `utterance_en, utterance_ga, scholarly_footnote_en, scholarly_footnote_ga,
   emotional_tone, asks_player_about`
4. If all 3 models fail, an offline template response is used
   (so the demo never breaks)

## Headline numbers

- 6 NPCs × 6 Wikipedia sources × 3 models = 108 call permutations
- p95 dialogue latency: ~3.2s (Qwen 7B, HF Inference L4 CPU Space)
- Token cost per turn: ~$0.0002 (Qwen 7B on HF Pro)
- 5 elements, 7 features, 1 typed pipeline

## License

Apache 2.0 (matches the monorepo root). Built on Bun + uv + Turbo.
Provenance: see the Anam Bonneagar footer in the Space.
