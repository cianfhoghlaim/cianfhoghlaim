# Anam: Tuatha na nGaelscoil (anam_sruth/tuatha/) — Integration Space

## Priority quick reference

The 3 priority skills, the 3 priority commands, the 1 BAML
function this Space uses, and the 1 openspec spec. **Read this
first**.

### Priority skills (3 of 108)

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | The `GenerateExitCardQuestions` BAML function (promoted from this Space in 2026-06) |
| [`british-isles-formative-assessment`](../.agents/skills/british-isles-formative-assessment/SKILL.md) | The 4-feedback-channel pattern (Celtic Tutor / Mythology Narrator / Quest Guide / Research Assistant) |
| [`celtic-language-ai`](../.agents/skills/celtic-language-ai/SKILL.md) | The bilingual EN/GA toggle + the fada/tironian/punctum metrics |

### ccc + openspec commands

```bash
bun run ccc:search "GenerateExitCardQuestions BAML function"     # find prior art
openspec list --specs                                          # 32 specs total
openspec validate <change-id> --strict                         # MUST pass before commit
```

### BAML functions used

| Function | Source |
|:--|:--|
| `GenerateExitCardQuestions(lesson_topic, subject, level, num_questions, curriculum_extract) -> ExitCardSet` | `sruth/tuatha/baml_src/player_assessment.baml` (canonical, promoted from this Space in 2026-06) |

### Priority openspec spec for anam_tuatha

| Spec | One-liner |
|:--|:--|
| `tuatha-platform` | The 4 sub-modules + the BAML Celtic content extraction + the croilar consumer integration (this Space is the integration layer) |

## What this Space does

The integration Space. 5 Celtic elements + 2 cross-cutting features
= 7 panels, all in one Gradio app:

| # | Feature | Element | What it does |
|:-:|:--|:--|:--|
| 1 | Curriculum Map | **Talamh** | Lifted from Space 1 (summary) |
| 2 | Chemistry Visual | **Uisce** | 8 molecule SVGs (CPK colours) |
| 3 | OCR Gaelscríbhneoir | **Tine** | Fada/eclipsis/punctum metrics |
| 4 | Languages | **Aer** | Lifted from Space 2 (Foclóir) |
| 5 | Soulbound Token | **Anam** | 3-stage Anvil sidecar mock |
| 6 | Mac Léinn | (formative) | BAML exit-card generator |
| 7 | Fiosraigh | (classroom) | Bilingual EN/GA switcher |

## Architecture

```
spaces/anam_sruth/tuatha/
├── app.py               # Gradio: 7-tab integration app
├── chemistry_visual.py  # 8-molecule CPK-coloured SVG renderer
├── gaelscribhneoir.py   # Fada/eclipsis/punctum Irish-text quality checker
├── soulbound_local.py   # 3-stage Anvil sidecar mock (no on-chain tx)
├── mac_leinn.py         # BAML GenerateExitCardQuestions + template bank
├── fiosraigh.py         # Bilingual EN/GA classroom-action switcher
├── record_demo.py       # Programmatic demo sequence
├── requirements.txt     # Gradio 5.x
├── social_card.png      # 1200x630 PNG
├── README.md            # HF Space README
└── AGENTS.md            # (this file)
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../_common/AGENTS.md`](../_common/AGENTS.md) — the shared bundle
- [`../../tuatha/AGENTS.md`](../../tuatha/AGENTS.md) — the tuatha quadrant
- [`../../tuatha/baml_src/player_assessment.baml`](../../tuatha/baml_src/player_assessment.baml) — the canonical BAML
