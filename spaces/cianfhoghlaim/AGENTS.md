# Cianfhoghlaim (cianfhoghlaim/) — Tuatha RPG

## Priority quick reference

The 3 priority skills, the 3 priority commands, the 1 BAML
function this Space uses, and the 1 openspec spec. **Read this
first**.

### Priority skills (3 of 108)

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | The `GenerateNpcDialogue` BAML function (promoted from this Space in 2026-06) |
| [`babylonjs`](../.agents/skills/babylonjs/SKILL.md) | Babylon.js 7 + WebGPU (the MMO client renderer for the British Isles map) |
| [`tuatha-mmo`](../.agents/skills/tuatha-mmo/SKILL.md) | The 4-agent formative assessment pattern (Celtic Tutor / Mythology Narrator / Quest Guide / Research Assistant) |

### ccc + openspec commands

```bash
bun run ccc:search "GenerateNpcDialogue BAML function"     # find prior art
openspec list --specs                                      # 32 specs total
openspec validate <change-id> --strict                     # MUST pass before commit
```

### BAML functions used

| Function | Source |
|:--|:--|
| `GenerateNpcDialogue(npc_name, npc_title, nation_code, era, player_utterance, conversation_history, scholarly_source) -> NpcDialogueExchange` | `sruth/tuatha/baml_src/mythology_extraction.baml` (canonical, promoted from this Space in 2026-06) |

### Priority openspec spec for cianfhoghlaim

| Spec | One-liner |
|:--|:--|
| `tuatha-platform` | The Celtic MMO + crypteolas crypto platform (this Space is the demo surface) |

## What this Space does

A Hades-style dialogue game set on a navigable map of the British Isles.
The player speaks with 6 Celtic NPCs, each grounded in a cached Wikipedia
article:

1. **Ui Liathain** (IE) — Leinster cycle
2. **Manannan mac Lir** (IM) — Sea god of the Otherworld
3. **Rhiannon** (WLS) — Mabinogion, the Otherworld rider
4. **Dian Cecht** (IE/GOD) — Physician god
5. **Cian** (IE) — Father of Lugh Lámhfhada
6. **The Deisi** (IE diaspora) — The Expulsion of the Deisi

## Architecture

```
spaces/cianfhoghlaim/
├── app.py        # Gradio app: British Isles map + 6 NPC buttons
├── dialogue.py   # BAML GenerateNpcDialogue handler + templated fallback
├── npcs.py       # The 6 NPC profiles (with cached Wikipedia sources)
├── record_demo.py # Programmatic demo sequence
├── requirements.txt # Gradio 5.x
├── social_card.png  # 1200x630 PNG
├── README.md     # HF Space README
└── AGENTS.md     # (this file)
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../_common/AGENTS.md`](../_common/AGENTS.md) — the shared bundle
- [`../../tuatha/AGENTS.md`](../../tuatha/AGENTS.md) — the tuatha quadrant
- [`../../tuatha/baml_src/mythology_extraction.baml`](../../tuatha/baml_src/mythology_extraction.baml) — the canonical BAML
