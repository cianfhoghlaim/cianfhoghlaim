---
title: 'NLLB-200 — 200-Language Neural Machine Translation'
domain: 'ai_ml'
status: 'stable'
description: 'NLLB-200 (No Language Left Behind) is Meta AI''''s neural machine translation model supporting 200 languages — including all 6 living Celtic languages (Irish, Scottish Gaelic, Manx, Welsh, Cornish, Breton). The distilled 600M parameter variant provides fast, resource-efficient trans'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/nllb-200.md
ccc_query_hints:
  - nllb-200 — 200-language neural machine t
truth: partial

---

# NLLB-200 — 200-Language Neural Machine Translation

## Overview

NLLB-200 (No Language Left Behind) is Meta AI's neural machine translation model supporting 200 languages — including all 6 living Celtic languages (Irish, Scottish Gaelic, Manx, Welsh, Cornish, Breton). The distilled 600M parameter variant provides fast, resource-efficient translation suitable for self-hosted deployment.

## Why This Matters for Kings' College Galway

The curriculum platform is fundamentally bilingual (Irish/English), but the Celtic language ecosystem extends to 6 living languages across Ireland, Scotland, Wales, Cornwall, Brittany, and the Isle of Man. Supporting all 6 Celtic languages means content created in Irish can be translated to Welsh for Welsh-medium schools, or Breton-language resources can be brought into the Irish curriculum. NLLB-200 is the only translation model covering all 6 Celtic languages in a single model, making it the backbone of the cross-Celtic translation pipeline.

## Key Features

- **200 languages** — The widest language coverage of any open translation model
- **All 6 Celtic languages** — Irish, Scottish Gaelic, Manx, Welsh, Cornish, Breton
- **Distilled variant** — 600M parameters, fast inference, low memory
- **Sentence-level** — Translates complete sentences with context
- **Open-source** — MIT-licensed model weights

## Installation

```bash
uv add transformers
# Model: facebook/nllb-200-distilled-600M
```

## Integration with Our Stack

NLLB-200 is served via HuggingFace passthrough in the LiteLLM gateway's `translation` alias. The model is cached in `stedding/huggingface/hub/` (~2.3 GB). BAML extraction functions use it for cross-language curriculum alignment.

## Upstream

- **Model**: <https://huggingface.co/facebook/nllb-200-distilled-600M>
- **Paper**: <https://arxiv.org/abs/2207.04672>
- **Latest**: NLLB-200 (2022) — Meta AI's flagship multilingual translation model

## Screenshot

NLLB-200 is a model accessed via HuggingFace Transformers. Translation quality is evaluated on the FLORES-200 benchmark. The model card shows per-language BLEU scores. Usage: `model.generate(**tokenizer("Irish text", return_tensors="pt", src_lang="gle_Latn"), forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"])`.
