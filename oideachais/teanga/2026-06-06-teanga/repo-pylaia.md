# KCG_SUMMARY: PyLaia — Deep Learning Handwritten Text Recognition

## What It Is
PyLaia is a device-agnostic, PyTorch-based deep learning toolkit for handwritten document analysis (HTR/OCR). It is the successor to the Laia system and provides VGG+BLSTM models for text-line recognition using CTC decoding, with tools for model creation, training, and inference. Developed by Teklia and the PRHLT Research Center, it is a core component of the eScriptorium transcription pipeline.

## Why This Matters for Kings' College Galway
Ireland's historical manuscripts — from medieval Irish annals to 19th-century school copybooks — require specialised OCR for the Irish language and Gaelic script (an cló Gaelach). PyLaia represents one of the few open-source HTR toolkits capable of being fine-tuned for Irish-language manuscript recognition. For Kings' College Galway's **teanga** platform, this provides the technical foundation for a student project pipeline: digitise local historical documents, train custom Irish-language OCR models, and build searchable text corpora from handwritten sources — connecting students directly with primary historical materials in the Irish language.

## Key Patterns Preserved
- `README.md` — Full project overview, installation, model architecture (VGG+BLSTM+CTC), CLI tools reference, BibTeX citations
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.0
- `CONTRIBUTING.md` — Contribution guide with bug reporting, enhancement suggestions, and development setup
- `benchmarks/README.md` — Benchmark information

## Source Files
Full source code was removed on 2026-06-06. The original repository is available at gitlab.teklia.com/atr/pylaia and github.com/jpuigcerver/PyLaia. This skeleton preserves the technical documentation and research context.

## What Was Removed
- Python source code (laia/ package with model definitions, training scripts, CTC decoder)
- Pre-trained model weights and checkpoints
- Test suites and CI pipeline configuration
- Training configuration files
- Sphinx documentation source
- Pre-commit hooks and development tooling
