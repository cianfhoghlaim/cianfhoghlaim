# Change: Welsh + Manx + Celtic Siblings HF Integration (Phase 4)

## Why

This is **Phase 4** of the 5-phase × 10-stage Celtic pipeline overhaul.

The 5 lesser-resourced Celtic languages (Welsh/cy, Scottish Gaelic/gd, Manx/gv, Cornish/kw, Breton/br) currently have BAML extractors + CocoIndex Apps + Dagster assets via Phase 14 vernacular — but **only the Phase 14 BAML/DLT surfaces are populated**. None of the 200+ HuggingFace datasets for these languages are integrated:

### Welsh (Cymraeg / cy) — 60+ HF datasets
- **techiaith/** — the canonical Welsh-language HF org (Bangor University):
  - `techiaith/banc-trawsgrifiadau-bangor` (65h natural speech, 50+ speakers, CC0)
  - `techiaith/commonvoice_16_1_cy` + `commonvoice_18_0_cy` (CV Welsh)
  - `techiaith/bu-tts-cy-en` (BU TTS)
  - `techiaith/YouTube-Subtitles` (Welsh subtitles)
  - `techiaith/cofnodycynulliad_en-cy` (Welsh Parliament)
  - `techiaith/llyw-cymru-en-cy-ogl` (Welsh Government)
  - `techiaith/legislation-gov-uk_en-cy` (UK Legislation EN-CY)
  - `techiaith/bydtermcymru-tm-en-cy` (TermCymru TM)
  - `techiaith/cardiff-university-tm-en-cy` (Cardiff University TM)
  - `techiaith/macsen_intent_parsing` (Macsen assistant)
  - `techiaith/mgsm_cy` (Welsh math GSM8K)
  - `techiaith/COPA-cy` (Welsh COPA causal reasoning)
  - `techiaith/wnli-cy` (Welsh NLI)
- **UniversalCEFR/learn_welsh_cy** (LearnWelsh coursebooks)
- **cardiffnlp/welsh-cefr** (CEFR text classification)
- **locailabs/** — open Welsh parallel: `opensubtitles_welsh`, `eubookshop_welsh`, `welsh_parallel_corpora`, `tatoeba_welsh`, `wikimedia_welsh`, `nemotron-chat-welsh`
- **BangorAI/** — alpaca + Hysbysiadau + Wiki calibration sets
- **BethanAmy123/** — North + South Welsh CEFR variants
- **britllm/** — truthfulqa_welsh, arc_welsh, piqa_welsh, xnli_brit

### Scottish Gaelic (Gàidhlig / gd) — 12+ HF datasets
- `universal-dependencies/universal_dependencies` (config: `gd_arcosg`) — UD_Scottish_Gaelic-ARCOSG
- `britllm/truthfulqa_scottish_gaelic`, `arc_scottish_gaelic`, `piqa_scottish_gaelic`
- `saillab/alpaca_scottishgaelic_taco` + `saillab/alpaca-scottishgaelic-cleaned`
- `JayJayThrowThrow/scottish-gaelic-wiki` + `celtic-wiki-mix` + `celtic-wiki-mix-clean`
- GaelEval benchmark (Scottish Gaelic LLM benchmark, arxiv 2604.02135v1)

### Manx (Gaelg / gv) — 2 HF datasets
- `k-mktr/manx_gaelic_nt_gv` (Bible portions: Esther, Jonah, Gospels)
- `manxaneletso/Chats_Memory` (chat memory)
- `universal-dependencies/universal_dependencies` (config: `gv_cadhan`) — UD_Manx-Cadhan

### Cornish (Kernewek / kw) — 3 HF datasets
- `CK0607/CORNISH2ENGLISH-ALPACA`
- `Jendersen/cornish_english_translation`
- `Jendersen/welsh-breton-cornish-filtered-n-readied`
- Mozilla Common Voice Cornish 27.0 (11,269 clips, 12.9h, 11 speakers)

### Breton (Brezhoneg / br) — 60+ HF datasets from Bretagne org
- `Bretagne/Banque_Sonore_Dialectes_Bretons` (1K-10K multi-dialect recordings)
- `Bretagne/UD_Breton-KEB` (POS treebank)
- `Bretagne/Prosody_Breton` (Kerne + Treger dialects)
- `Bretagne/fineweb-2_raw_breton` (1M-10M)
- `Bretagne/archive_sonores_en_breton_1..30` (30 splits)
- `Bretagne/PDF_en_breton`, `Bretagne/dictionnaire_breton_phonetique`, `Bretagne/Lexique_etymologique_du_breton_moderne`
- `mozilla-foundation/common_voice_17_0` (config: br)

### Cross-Celtic
- `Jendersen/welsh-breton-cornish-filtered-n-readied` (3-way Celtic)
- `JayJayThrowThrow/celtic-wiki-mix` + `celtic-wiki-mix-clean`

## What changes (10 stages)

### Stage 4.1 — Welsh HF (techiaith ASR/TTS) → `dlt_sources/education/wales/british_isles/welsh_hf.py`
### Stage 4.2 — Welsh eval (techiaith mgsm/COPA/wnli/macsen + UniversalCEFR) → extend `baml_src/british_isles/_cross/vernacular_languages.baml`
### Stage 4.3 — Welsh CEFR + institutions (cardiffnlp + BethanAmy123 + CorCenCC + Bangor Siarad + Welsh Gov) → `dlt_sources/education/wales/british_isles/welsh_cefr.py` + `welsh_institutional.py`
### Stage 4.4 — Welsh parallel (10 techiaith + locailabs) → `dlt_sources/education/wales/british_isles/welsh_parallel.py`
### Stage 4.5 — Manx + cross-Celtic → `dlt_sources/education/isle_of_man/british_isles/manx_hf.py` + `dlt_sources/celtic_cross/cross_celtic_pretrain.py`
### Stage 4.6 — Cornish + Breton → `dlt_sources/breton_cornish/british_isles/{cornish_hf,breton_hf}.py`
### Stage 4.7 — CocoIndex: strengthen `welsh_embedding.py` + `manx_embedding.py` + add `celtic_wiki_mix_embedding.py`
### Stage 4.8 — DLT: 7 new sources registered
### Stage 4.9 — Dagster: 21 assets in `vernacular/hf_vernacular_assets.py`
### Stage 4.10 — Per-phase verify + archive

## Impact

- **Affected code**: ~15 new files (7 DLT sources + 1 CocoIndex App + 1 Dagster asset file + 1 wholesale-copied bilingual module + 5 strengthen records)
- **Affected specs**: NEW `celtic-language-pipeline` (added by the umbrella change)

## Out of scope

- HuggingFace dataset integration for Irish (Phase 2 — already done)
- Tuatha sister-repo wholesale-copy
