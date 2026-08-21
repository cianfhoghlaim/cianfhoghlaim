# An Scrúdú (an_scrudu/) — Past Paper Heatmap

## Priority quick reference

The 3 priority skills, the 3 priority commands, the 1 BAML
function this Space uses, and the 1 openspec spec. **Read this
first**.

### Priority skills (3 of 108)

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | The `ExtractCircularMeta` BAML function (promoted from this Space in 2026-06) |
| [`marimo`](../.agents/skills/marimo/SKILL.md) | Replace the hand-rolled heatmap with a marimo notebook |
| [`oideachais-pipeline`](../.agents/skills/oideachais-pipeline/SKILL.md) | The canonical lakehouse pipeline (this Space is the consumer) |

### ccc + openspec commands

```bash
bun run ccc:search "ExtractCircularMeta BAML function"     # find prior art
openspec list --specs                                       # 32 specs total
openspec validate <change-id> --strict                      # MUST pass before commit
```

### BAML functions used

| Function | Source |
|:--|:--|
| `ExtractCircularMeta(pdf_text, filename) -> CircularExtraction` | `sruth/oideachais/baml_src/circular_extraction.baml` (canonical, promoted from this Space in 2026-06) |

### Priority openspec spec for an_scrudu

| Spec | One-liner |
|:--|:--|
| `oideachais-pipeline` | The canonical lakehouse pipeline (this Space is the consumer) |

## What this Space does

- Upload a Leaving Cert past paper (PDF or text) or use the built-in sample
- BAML `ExtractCircularMeta` extracts the circular metadata (number, year,
  issuing body, title EN + GA, subject, level) + the marking scheme summary
  (total marking points, topics, duration, has orale, has coursework)
- The HTML heatmap renders the topic distribution with the Talamh gradient
- The PCLM preview + download emits the result as PCLM-XML or a minimal PDF

## Architecture

```
spaces/an_scrudu/
├── app.py           # Gradio app: file upload + heatmap + PCLM preview/download
├── extraction.py    # BAML ExtractCircularMeta handler + offline regex fallback
├── heatmap.py       # HTML/CSS heatmap renderer (Talamh → Anam gradient)
├── pclm.py          # PCLM-XML + minimal-PDF emitter
├── record_demo.py   # Programmatic demo sequence
├── requirements.txt # Gradio 5.x
├── social_card.png  # 1200x630 PNG (generated at build time)
├── README.md        # HF Space README
└── AGENTS.md        # (this file)
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../_common/AGENTS.md`](../_common/AGENTS.md) — the shared bundle
- [`../../oideachais/AGENTS.md`](../../oideachais/AGENTS.md) — the oideachais quadrant
- [`../../oideachais/baml_src/circular_extraction.baml`](../../oideachais/baml_src/circular_extraction.baml) — the canonical BAML
