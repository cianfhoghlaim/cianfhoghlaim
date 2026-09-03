---
title: An Scrudu - Past Paper Heatmap
emoji: "\U0001F4CA"
colorFrom: green
colorTo: emerald
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: BAML extracts marking schemes from Irish Leaving Cert past papers, returns a topic heatmap and PCLM-PDF.
---

# An Scrúdú — Past Paper Heatmap

> "The Examination" — a BAML-powered extractor that turns Irish Leaving
> Cert past papers into topic-distribution heatmaps and PCLM-XML/PDF
> downloads.

**Build Small 2026 hackathon submission.** Space 1 of 4. Element: **Talamh**
(Earth) — the curriculum map.

## What's in this Space

- Upload a past paper (`.txt` / `.md`) or use the built-in sample
  (LC Chemistry 2024 Higher Level, 300 marks across 8 topics)
- BAML `ExtractCircularMeta` extracts the marking scheme structure
  (circular number, year, issuing body, subject, level, topics, sections)
- A self-contained HTML heatmap renders the topic distribution on a
  Talamh → Anam gradient (emerald → gold)
- Download the result as **PCLM-XML** (the Department-of-Education-flavoured
  scheme) or a minimal **PDF** (1-page, Helvetica, no external deps)
- 3-tier HF Inference fallback (Qwen 7B → Llama 8B → Gemma 9b, all ≤32B)
- Offline regex fallback if all 3 models fail (the heatmap always renders)

## Architecture

```
spaces/an_scrudu/
├── app.py           # Gradio app: file upload + heatmap + PCLM preview/download
├── extraction.py    # BAML ExtractCircularMeta handler + offline regex fallback
├── heatmap.py       # HTML/CSS heatmap renderer (Talamh -> Anam gradient)
├── pclm.py          # PCLM-XML + minimal-PDF emitter
├── record_demo.py   # Programmatic demo sequence
├── requirements.txt # Gradio 4.44+
├── social_card.png  # 1200x630 PNG (generated at build time)
└── README.md        # (this file)
```

Shared with the other 3 Spaces via `spaces/_common/`:

- `theme.py` — Celtic 5-element palette + Hades Shadow-First CSS
- `baml_client.py` — 3-tier HF Inference fallback
- `anam_bonneagar.py` — per-Space trust-signal footer
- `i18n.py` — bilingual EN/GA toggle

## The 4-element (Talamh) theme

| Color | Use |
|:--|:--|
| `#28955e` emerald | Section headers, button border, heatmap high values |
| `#1a3a2a` darkest | Heatmap zero value |
| `#a8924d` bronze | Heatmap mid values |
| `#cc9966` gold | Heatmap max value (Anam) |

## Sample output

For the built-in LC Chemistry 2024 sample:

- 6 topics (CH3-CH8), each 50 marks
- Total 300 marks, 3-hour paper
- Source model: `offline-regex` (in demo) or `Qwen/Qwen2.5-7B-Instruct` (in production)
- Confidence: 0.40 (offline) or 0.85+ (Qwen)

## Running locally

```bash
cd spaces/an_scrudu
pip install -r requirements.txt
HF_TOKEN=hf_xxx python app.py
# open http://localhost:7860
```

## License

Apache 2.0. Built on Bun + uv + Turbo.
