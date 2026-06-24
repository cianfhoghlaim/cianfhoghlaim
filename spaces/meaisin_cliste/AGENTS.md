# Meaisín Cliste (meaisin_cliste/) — Celtic AI Tools

## Priority quick reference

The 3 priority skills, the 3 priority commands, the 1 BAML
function this Space uses, and the 1 openspec spec. **Read this
first**.

### Priority skills (3 of 108)

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | The `CompareCelticNations` BAML function (promoted from this Space in 2026-06) |
| [`motherduck-connections`](../.agents/skills/motherduck-connections/SKILL.md) | Wire to the production cognate table in DuckLake (replaces the 30 hand-picked seeds) |
| [`falkordb`](../.agents/skills/falkordb/SKILL.md) | The school-density map (Pobal HP scoring + 26 counties) |

### ccc + openspec commands

```bash
bun run ccc:search "CompareCelticNations BAML function"     # find prior art
openspec list --specs                                       # 32 specs total
openspec validate <change-id> --strict                      # MUST pass before commit
```

### BAML functions used

| Function | Source |
|:--|:--|
| `CompareCelticNations(topic_query, scope) -> CrossNationComparison` | `tuatha/baml_src/celtic_curriculum.baml` (canonical, promoted from this Space in 2026-06) |

### Priority openspec spec for meaisin_cliste

| Spec | One-liner |
|:--|:--|
| `meaisinfhoghlaim-platform` | The AI/ML quadrant (the Space is the consumer) |

## What this Space does

3 themes for Celtic AI in one Gradio Space:

- **Theme 1: Foclóir na Sé Náisiún** (Aer) — a 6-nation Celtic cognate dictionary
  (~30 hand-picked seeds; production reads from `oideachais/language/dlt_sources/cognates.py` ~1,800 rows)
- **Theme 2: Scoil ar an Léarscáil** (Uisce) — a 26-county school-density SVG
  map (1,629 schools; coloured by the Pobal HP Deprivation Index 2022)
- **Theme 3: Curaclam Trasteorann** (Aer) — a cross-nation curriculum
  comparison (NCCA / CCEA / WJEC / DESC / SQA)

## Architecture

```
spaces/meaisin_cliste/
├── app.py           # Gradio app: 3 tabs (Foclóir + Scoil + Curaclam)
├── cognates.py      # 30 hand-picked cognate seeds (proto-Celtic + 6 langs)
├── scoil_map.py     # 26-county school-density SVG + Pobal HP scoring
├── curaclam.py      # CompareCelticNations handler + offline reference
├── record_demo.py   # Programmatic demo sequence
├── requirements.txt # Gradio 5.x
├── social_card.png  # 1200x630 PNG (generated at build time)
├── README.md        # HF Space README
└── AGENTS.md        # (this file)
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../_common/AGENTS.md`](../_common/AGENTS.md) — the shared bundle
- [`../../meaisinfhoghlaim/AGENTS.md`](../../meaisinfhoghlaim/AGENTS.md) — the AI/ML quadrant
- [`../../tuatha/baml_src/celtic_curriculum.baml`](../../tuatha/baml_src/celtic_curriculum.baml) — the canonical BAML
