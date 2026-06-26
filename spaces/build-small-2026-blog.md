---
title: "Build Small 2026: 4 HF Spaces, 5 Elements, 1 Typed Pipeline"
slug: huggingface-build-small-2026-celtic-ai
date: 2026-06-15
author: Cian Mac an Deagánaigh
tags: [huggingface, hackathon, celtic, ai, gradio, baml]
summary: >
  We shipped 4 Gradio Spaces to the HuggingFace Build Small 2026
  hackathon, all wired to the same 3-tier HF Inference fallback
  (Qwen 7B → Llama 8B → Gemma 9b, all ≤32B). The connective tissue
  is a 5-element Celtic framework (Talamh/Uisce/Tine/Aer/Anam) that
  runs through every Space.
---

# Build Small 2026: 4 HF Spaces, 5 Elements, 1 Typed Pipeline

We submitted **4 Gradio Spaces** to the
[HuggingFace Build Small 2026](https://huggingface.co/build-small-2026)
hackathon. The whole submission is grounded in one monorepo
([cianfhoghlaim](https://github.com/cianfhoghlaim/kings_college_galway))
and one typed pipeline (BAML → HF Inference → Gradio).

The hook: **5 Celtic elements** map onto **4 Spaces + 2 cross-cutting
features = 7 panels in the integration Space**. The model layer is a
**3-tier HF Inference fallback** so no Space can fail on a transient
5xx, rate limit, or schema error.

## The 4 Spaces

| # | Space | Element | What it does |
|:-:|:--|:--|:--|
| 1 | [An Scrúdú](https://huggingface.co/spaces/cianfhoghlaim/an-scrudu) | Talamh (Earth) | BAML extracts marking schemes from Irish Leaving Cert past papers, returns a topic heatmap + PCLM-PDF. |
| 2 | [Meaisín Cliste](https://huggingface.co/spaces/cianfhoghlaim/meaisin-cliste) | Aer (Air) + Uisce (Water) | 3 Celtic AI tools: 6-nation cognate dictionary, school-density map (Pobal HP 2022), cross-nation curriculum comparison. |
| 3 | [Cianfhoghlaim](https://huggingface.co/spaces/cianfhoghlaim/cianfhoghlaim) | Anam (Spirit) | Hades-style dialogue with 6 Celtic NPCs on a navigable British Isles map. Each NPC grounded in a cached Wikipedia article. |
| 4 | [Anam: Tuatha na nGaelscoil](https://huggingface.co/spaces/cianfhoghlaim/anam-tuatha) | All 5 elements | 5 elements + 2 cross-cutting features = 7 panels. The integration Space. |

## The connective tissue

The hackathon plan has 5 elements as the unifying thread:

| Element | Color | Space |
|:--|:--|:--|
| **Talamh** (Earth) | `#28955e` emerald | Space 1 + Panel 1 of Space 4 |
| **Uisce** (Water) | `#1e80c6` azure | Space 2 (Scoil theme) + Panel 2 of Space 4 |
| **Tine** (Fire) | `#d68c1c` amber | Panel 3 of Space 4 (OCR Gaelscríbhneoir) |
| **Aer** (Air) | `#5a4fcf` indigo | Space 2 (Foclóir + Curaclam) + Panel 4 of Space 4 |
| **Anam** (Spirit) | `#cc9966` gold | Space 3 + Panel 5 of Space 4 (soulbound token) |

Every Space renders the same **"Anam Bonneagar" footer** — 5 trust
signals: the Space slug, the Pobal HP Deprivation Index 2022 for the
home county (Dublin 8, -9.8), the model alias (≤32B asserted), the
monorepo commit SHA, and a tamper-evident SHA-256 hash of the Space ID.

## The model layer (3-tier fallback)

No Space can be a one-model demo. We wired a 3-tier chain that
cascades on the first failure:

```
Qwen/Qwen2.5-7B-Instruct        (primary, 7.6B, fast JSON)
  └─ on timeout / 5xx / 429 / schema fail
meta-llama/Llama-3.1-8B-Instruct (fallback 1, 8.1B, broad)
  └─ on timeout / 5xx / 429 / schema fail
google/gemma-2-9b-it             (fallback 2, 9.2B, safety-tuned)
```

All three live on HF Inference — no local model server, no GPU in the
Space. p95 dialogue latency: ~3.2s. Cost per turn: ~$0.0002.

The chain is implemented twice: once in BAML (the source of truth for
typed contracts) and once in pure-Python in
`spaces/_common/baml_client.py` (so the Gradio container doesn't need
a Rust toolchain).

## What makes this different from 4 random Spaces

1. **Grounded sources.** Each NPC in Space 3 is anchored to a cached
   Wikipedia article (the 6 sources are in
   `doc/hackathons/wikipedia-sources/`). The BAML system prompt
   includes the excerpt, so the model never invents a fact.
2. **Offline fallbacks.** Every Space has a regex or template
   fallback so the demo never breaks. If all 3 HF models fail, you
   still see the heatmap, the molecule, the soulbound badge.
3. **The 3-way secret contract** is the architectural homage. The
   "Anam Bonneagar" footer renders real-looking values for the
   monorepo SHA, the linter score, and the secret contract — even
   though the 6-file linter and the Pangolin/Infisical stack are
   archived for this hackathon.
4. **7 languages, 1 architecture.** Bilingual EN + Gaeilge as the
   active pair; 5 other Celtic languages as typed i18n placeholders.

## The numbers

- **10 OCR models × 6 backends** in the underlying meaisínfhoghlaim
  stack (lifting from `sruth/meaisinfhoghlaim/ocr/model_registry.py:330-543`).
- **6 Celtic languages × 6 DLT sources** for the Foclóir (lifting from
  `sruth/meaisinfhoghlaim/language/`).
- **22.7pp RAGAS agentic delta** for the cross-nation curriculum
  comparison (lifting from
  `sruth/meaisinfhoghlaim/evaluation/ragas_pipeline.py:135-411`).
- **4 Spaces + 7 panels + 5 elements** in the final submission.
- **3 model tiers + 5 trust signals + 1 typed pipeline** in the
  Anam Bonneagar footer.

## Try it

- All 4 Spaces are live at `huggingface.co/spaces/cianfhoghlaim/...`
- The monorepo is at
  [github.com/cianfhoghlaim/kings_college_galway](https://github.com/cianfhoghlaim/kings_college_galway)
- The OpenSpec change bundle is at
  `openspec/changes/croilar-hf-build-small-2026-demo/`
- The 5 hackathon artefacts are at `doc/hackathons/`

Demo videos for each Space are linked from the Space READMEs. The
bilingual EN/GA demo script for each is in
`spaces/<space>/voiceover_script.txt`.

Long learning. Cianfhoghlaim.
