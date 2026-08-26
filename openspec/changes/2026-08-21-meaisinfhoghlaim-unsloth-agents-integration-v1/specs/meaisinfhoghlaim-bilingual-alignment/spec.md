## ADDED Requirements

### Requirement: Bilingual EU Irish-English alignment via fast_align + eflomal

The ciancheiltis sister repo SHALL provide a bilingual EU Irish-English alignment pipeline at `dlt_sources/language/bilingual_alignment.py`. The pipeline uses fast_align + eflomal to align parallel Irish-English text from the EUR-Lex corpus + the NCCA Leaving Certificate syllabus.

#### Scenario: EUR-Lex alignment pipeline produces word-level alignments

- **GIVEN** the EUR-Lex Irish-English parallel corpus is available
- **WHEN** the operator runs the alignment pipeline
- **THEN** fast_align produces word-level alignments
- **AND** eflomal validates them with HMM-based re-alignment
- **AND** the result lands in the `ciancheiltis.language.bilingual_alignment` DuckLake schema

### Requirement: NCCA Leaving Certificate syllabus loader

The ciancheiltis sister repo SHALL provide a NCCA Leaving Certificate syllabus loader at `dlt_sources/language/ndcc_syllabus.py`. The loader fetches the bilingual EN + GA syllabus from the official NCCA source.

#### Scenario: NCCA syllabus loader fetches bilingual EN + GA LOs

- **GIVEN** an NCCA syllabus URL
- **WHEN** the operator runs the loader
- **THEN** it fetches the bilingual EN + GA syllabus + all learning outcomes (LOs)
- **AND** the result lands in the `ciancheiltis.language.ncca_syllabus` DuckLake schema

### Requirement: Gemma 4 4B fine-tune for EN-GA alignment

The system SHALL provide a Gemma 4 4B fine-tune script that produces an EN-GA alignment adapter, trained on the EUR-Lex + NCCA bilingual pairs.

#### Scenario: Gemma 4 4B alignment fine-tune

- **GIVEN** the EUR-Lex + NCCA bilingual pairs are in DuckLake
- **WHEN** the operator runs `python3 dlt_sources/language/alignment_finetune.py --base-model unsloth/gemma-4-E4B-it-GGUF --lora-r 16 --epochs 5`
- **THEN** a LoRA r=16 adapter is fine-tuned on Modal H100
- **AND** the adapter is pushed to HuggingFace as `meaisinfhoghlaim/gemma-4-e4b-ga-en-align-v1`
- **AND** the adapter can be loaded by Unsloth Studio for inference

### Requirement: Bilingual alignment eval via RAGAS

The system SHALL provide a bilingual alignment eval that uses RAGAS faithfulness + chrF metrics to compare the fine-tuned alignment adapter against the baseline.

#### Scenario: RAGAS eval shows alignment adapter is better than baseline

- **GIVEN** the Gemma 4 4B alignment adapter is loaded
- **WHEN** the operator runs the alignment eval
- **THEN** RAGAS computes faithfulness + chrF scores
- **AND** the result lands in the `ciancheiltis.language.alignment_eval` DuckLake schema
- **AND** the result is compared against the baseline (no fine-tune) to show improvement
