# ColPali — KCG Summary

## What It Is
ColPali (Column-Paligemma) is a vision-language model for efficient document retrieval using visual embeddings. Instead of OCR → text → embedding pipelines, ColPali directly embeds document page images, capturing visual layout, tables, and formatting alongside text. Each document page produces a grid of patch-level embeddings (128-d per patch) enabling fine-grained visual search across document collections.

## Why This Matters for Kings' College Galway
ColPali is the chosen embedding backbone for the Leaving Certificate exam paper archive. Historical Irish exam papers contain complex mixed layouts (tables, formulae, diagrams, Irish/English bilingual sections) where traditional OCR-to-text pipelines lose critical visual context. ColPali's visual-first embedding preserves mathematical notation layout, graph structures, and bilingual text positioning — essential for accurate retrieval of past exam questions by topic. The patch-level embeddings enable finding specific diagrams or formula arrangements within dense exam pages. Combined with GaBERT for Irish text and BGE-M3 for multilingual, ColPali completes the multi-modal retrieval stack for the Celtic curriculum knowledge base.

## Key Patterns Preserved
- `README.md` — Redirect to document-processing-reference.md (content merged into main docs)
- `CHANGELOG.md` — Redirect to document-processing-reference.md (content merged into main docs)

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/illuin-tech/colpali

## What Was Removed
Python source code (.py), model configuration files (.json, .yaml), Jupyter notebooks, test files, package dependencies (pyproject.toml), Dockerfiles, CI/CD configs, Git metadata, data samples.
