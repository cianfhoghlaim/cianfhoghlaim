# docs/teanga — Celtic Language AI Reference Library

This directory holds skeletonised documentation from cloned Celtic language AI tools, applications, and training repositories. Full source code has been removed (2026-06-06); each subdirectory retains only its markdown documentation and a `KCG_SUMMARY.md` explaining why the tool matters for Kings' College Galway's **teanga** (language) curriculum platform.

All subdirectories below are skeletons — documentation-only snapshots of larger source repositories.

---

## Subdirectories

### [kscanne/](kscanne/KCG_SUMMARY.md)
Kevin Scannell's comprehensive Irish NLP tools and datasets — grammar checking, machine translation, dependency parsing, POS tagging, sentiment analysis, OCR correction, and 25+ benchmark tasks for Irish language AI. **81M → 268K**

### [escriptorium/](escriptorium/KCG_SUMMARY.md)
Django-based collaborative platform for historical document transcription, annotation, and publishing. Integrates Kraken OCR, used by EU-funded Scripta/RESILIENCE projects. **45M → 24K**

### [gaois/](gaois/KCG_SUMMARY.md)
DCU's Gaois research group — Ireland's national digital language infrastructure. Includes téarma.ie (National Terminology Database), logainm.ie API, Dúchas folklore API, Irish surname databases with grammatical inflection, and Terminologue terminology management. **30M → 1.2M**

### [pylaia/](pylaia/KCG_SUMMARY.md)
PyTorch-based deep learning toolkit for handwritten text recognition (HTR). VGG+BLSTM models with CTC decoding, used as the OCR engine behind eScriptorium. **812K → 32K**

### [genizah_search/](genizah_search/KCG_SUMMARY.md)
React + Python web application for semantic search of the Cairo Genizah manuscript collection. Uses Elasticsearch, Neo4j graph database, and Mirador IIIF viewer. **740K → 8K**

### [historical-document-analysis/](historical-document-analysis/KCG_SUMMARY.md)
Multi-modal deep learning pipeline for historical document analysis — OCR (Cloud Vision, Doctr), embeddings (NOMIC, CLIP), Elasticsearch indexing, and Neo4j graph storage. Built for Cairo Genizah research. **620K → 24K**

### [chatterbox-finetuning/](chatterbox-finetuning/KCG_SUMMARY.md)
Modular TTS fine-tuning infrastructure supporting new languages via custom tokenizers. VE + T3 Transformer + S3Gen vocoder pipeline with offline preprocessing for GPU-optimised training. **116K → 20K**

### [IRLBench/](IRLBench/KCG_SUMMARY.md)
Parallel Irish-English benchmark for LLM reasoning evaluation, based on 12 subjects from the 2024 Irish Leaving Certificate exams. Uses long-form generation and official marking schemes. **68K → 8K**

### [tts-dataset-generator/](tts-dataset-generator/KCG_SUMMARY.md)
Automated TTS dataset creation tool — silence-based audio segmentation + Whisper transcription → LJSpeech format. Compatible with VITS, Tacotron, Coqui TTS, and XTTS frameworks. **52K → 16K**

---

*All subdirectories skeletonised on 2026-06-06. Source code removed; documentation preserved for architectural reference. See each KCG_SUMMARY.md for original repository links.*
