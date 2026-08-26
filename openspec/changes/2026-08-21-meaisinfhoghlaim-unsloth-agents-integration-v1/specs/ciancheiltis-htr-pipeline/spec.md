## ADDED Requirements

### Requirement: Duchas IIIF manuscript page + transcription loader

The ciancheiltis sister repo SHALL provide a Duchas IIIF manuscript page + transcription loader at `dlt_sources/cultural_heritage/duchas_images_htr.py`. The loader downloads page images (via IIIF) + TEI-XML transcriptions from the Dúchas.ie National Folklore Collection API (cbes collection, transcribed-only).

#### Scenario: Duchas IIIF loader downloads page images + transcriptions

- **GIVEN** a Dúchas.ie volume URL
- **WHEN** the operator runs `python3 -c "from dlt_sources.cultural_heritage.duchas_images_htr import source; pipeline.run(source(volume='XXXX'))"`
- **THEN** the loader downloads all page images (IIIF size=1024) + TEI-XML transcriptions + Meitheal corrections
- **AND** the result lands in the `oideachais.cultural_heritage` DuckLake schema

### Requirement: HTR fine-tune via Unsloth + Modal H100

The ciancheiltis sister repo SHALL provide a Gemma 4 4B fine-tune script (`dlt_sources/cultural_heritage/htr_finetune.py`) that uses Unsloth + Modal H100 to fine-tune on the Dúchas transcription dataset.

#### Scenario: Gemma 4 4B fine-tunes on Dúchas cbes

- **GIVEN** the Dúchas transcription dataset is loaded into DuckLake
- **WHEN** the operator runs `python3 dlt_sources/cultural_heritage/htr_finetune.py --base-model unsloth/gemma-4-E2B-it-GGUF --dataset-path oideachais.cultural_heritage.cbes --lora-r 8 --epochs 3`
- **THEN** a QLoRA r=8 adapter is fine-tuned on Modal H100
- **AND** the adapter is pushed to HuggingFace as `meaisinfhoghlaim/gemma-4-e2b-gaeilge-htr-v1`
- **AND** the adapter can be loaded by Unsloth Studio for inference
- **AND** the training metrics (loss, CER, WER) are logged to Langfuse + MLflow

### Requirement: Qwen3-VL-8B fine-tune for handwriting recognition

The ciancheiltis sister repo SHALL provide a Qwen3-VL-8B fine-tune script for handwriting recognition on the Dúchas manuscript images dataset.

#### Scenario: Qwen3-VL-8B fine-tunes on Dúchas manuscript images

- **GIVEN** the Dúchas manuscript images + transcriptions dataset
- **WHEN** the operator runs the fine-tune script with `base-model=unsloth/Qwen3-VL-8B-Instruct-GGUF`
- **THEN** a QLoRA r=8 adapter is fine-tuned on Modal H100
- **AND** the adapter is pushed to HuggingFace as `meaisinfhoghlaim/qwen3-vl-8b-gaeilge-htr-v1`
