# Helsinki OPUS-MT — Celtic Language Pair Translation

## Overview

Helsinki OPUS-MT is a collection of neural machine translation models from the University of Helsinki's Language Technology group, trained on the OPUS parallel corpus. It includes dedicated models for Celtic language pairs: English↔Irish (en-ga, ga-en), English↔Welsh (en-cy, cy-en), and other pairs. These specialised models provide higher accuracy for specific Celtic language pairs than general-purpose multilingual models.

## Why This Matters for Kings' College Galway

While NLLB-200 covers all Celtic languages in one model, its accuracy for low-resource language pairs (especially Irish↔English) is lower than a dedicated bilingual model. Helsinki OPUS-MT models are trained specifically on Irish-English and Welsh-English parallel corpora, producing more idiomatic translations for these pairs. The platform uses OPUS-MT for high-quality Irish↔English translation of curriculum content, and NLLB-200 as the fallback for other Celtic language pairs.

## Key Features

- **Dedicated pairs** — Trained specifically on en↔ga and en↔cy
- **Higher accuracy** — Outperforms multilingual models on their target pairs
- **Lightweight** — ~566 MB per model pair
- **OPUS corpus** — Trained on the largest open parallel corpus collection
- **Marian NMT** — Built on the efficient Marian neural MT framework

## Installation

```bash
uv add transformers
# Models:
# Helsinki-NLP/opus-mt-en-ga  (English → Irish)
# Helsinki-NLP/opus-mt-ga-en  (Irish → English)
# Helsinki-NLP/opus-mt-en-cy  (English → Welsh)
# Helsinki-NLP/opus-mt-cy-en  (Welsh → English)
```

## Integration with Our Stack

OPUS-MT models are served via HuggingFace passthrough. The LiteLLM gateway exposes them as translation routes for Celtic language pairs. The models are cached in `stedding/huggingface/hub/`. BAML extraction functions use OPUS-MT for high-quality Irish↔English curriculum translation.

## Upstream

- **HuggingFace**: <https://huggingface.co/Helsinki-NLP>
- **OPUS corpus**: <https://opus.nlpl.eu>
- **Latest**: OPUS-MT models continuously updated as OPUS corpus grows

## Screenshot

OPUS-MT models are accessed via HuggingFace Transformers. Translation quality is evaluated on Celtic language test sets. The HuggingFace model cards show BLEU and chrF scores per language pair. Usage is standard MarianMT: `MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-ga")`.
