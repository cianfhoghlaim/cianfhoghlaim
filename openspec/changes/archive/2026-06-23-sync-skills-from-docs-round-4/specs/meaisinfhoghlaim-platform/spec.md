# Spec Delta: meaisinfhoghlaim-platform

## ADDED Requirements

### Requirement: TTS pipeline (text-to-speech)

The system SHALL support Irish-language TTS via Chatterbox
(9.7 GB Resemble AI model) for pronunciation guides, audio
study notes, and AI tutor speech, with a BAML→TTS pipeline
that converts BAML-extracted curriculum text to audio files
stored in Garage S3.

#### Scenario: BAML→TTS audio generation

- **GIVEN** a BAML-extracted curriculum passage (e.g. a
  NCCA Irish Leaving Cert grammar explanation)
- **WHEN** the `sruth/meaisinfhoghlaim/tts/` service is invoked with
  the passage + voice ID
- **THEN** Chatterbox SHALL render the passage to a 16-bit
  PCM WAV file
- **AND** the WAV SHALL be uploaded to `garage://kcg-tts/`
  with a deterministic key (sha256 of the text + voice)
- **AND** the FastAPI route `POST /api/tts/synthesize` SHALL
  return the signed URL

### Requirement: ASR routing (speech recognition)

The system SHALL use the canonical ASR routing rule:
`wav2vec2-XLSR-Irish` for accuracy-critical Irish (séimhiú,
urú, dialectal variation, oral exam recordings), Whisper
large-v3 (via faster-whisper) for general multilingual
transcription, MMS-1B-fl102 as a fallback for low-resource
languages.

#### Scenario: Irish oral exam transcription

- **GIVEN** an audio recording of an Irish Leaving Cert oral
  exam (Irish + English mixed)
- **WHEN** the `sruth/meaisinfhoghlaim/asr/` service is invoked
- **THEN** the service SHALL route to
  `cpierse/wav2vec2-large-xlsr-53-irish` for the Irish
  segments (auto-detected by language ID)
- **AND** to `openai/whisper-large-v3` (faster-whisper) for
  the English segments
- **AND** return a single transcript with per-segment
  language tags

### Requirement: TRL training (preference optimization)

The system SHALL support HuggingFace TRL SFTTrainer, DPOTrainer,
GRPOTrainer, and RewardTrainer for alignment training, with
the RAGAS-as-DPO-preference-signal pattern wired in via a
Dagster asset.

#### Scenario: RAGAS-driven DPO training run

- **GIVEN** a BAML extraction with 1000 examples, each
  scored by RAGAS (faithfulness, answer-relevancy, etc.)
- **WHEN** the `trl_dpo_training` Dagster asset runs
- **THEN** examples with RAGAS faithfulness ≥ 0.8 SHALL be
  used as the "chosen" examples
- **AND** examples with RAGAS faithfulness < 0.5 SHALL be
  used as the "rejected" examples
- **AND** the DPOTrainer SHALL produce a LoRA adapter
  (via PEFT) on the base model
- **AND** the adapter SHALL be logged to MLflow + Langfuse
- **AND** the trained adapter SHALL be served via llama-swap

### Requirement: PEFT parameter-efficient fine-tuning

The system SHALL use HuggingFace PEFT (LoRA, QLoRA,
IA³) for parameter-efficient fine-tuning on MacBook M4
48 GB unified memory, with bitsandbytes 4-bit quantisation
for the base model.

#### Scenario: QLoRA fine-tune on M4 Mac

- **GIVEN** a 7B parameter base model (e.g.
  `ReliableAI/UCCIX-Llama3.1-8B-Instruct`) + a 1k-example
  Irish curriculum dataset
- **WHEN** the `peft_qlora_finetune` Dagster asset runs
  via Unsloth
- **THEN** the base model SHALL be quantised to 4-bit via
  bitsandbytes
- **AND** a 64-rank LoRA adapter SHALL be trained on the
  quantised base
- **AND** the adapter SHALL be < 100 MB on disk
- **AND** the adapter SHALL be saved to
  `stedding/huggingface/hub/ReliableAI-UCCIX-Llama3.1-8B-Instruct/`

## REMOVED Requirements

(None.)
