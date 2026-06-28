---
truth: superseded
---

# Docs/ Inventory Report — Consolidation Discovery Audit

**Generated:** 2026-06-06
**Scope:** 8 subtrees, 1036 files, 49.7 MiB total

## Executive Summary

This inventory covers 1036 files across 8 directories totalling 49.7 MiB. The largest subtrees by file count are **docs/teanga** (295 files) and **docs/tuatha** (232 files). **docs/tuatha** has a nested `sruth/tuatha/sruth/tuatha/` directory containing 116 near-exact duplicates of its parent. There are 203 files with YAML frontmatter (none use `domain:` or `status:` fields), and 82 files flagged as predominantly Irish/Gaelic content.

## 1. Global Statistics

### 1.1 By Subtree

| Subtree | Files | Bytes |
|---|---:|:---:|
| docs/agents | 39 | 939.3 KiB |
| docs/bonneagar | 163 | 6.8 MiB |
| docs/context | 108 | 23.5 MiB |
| docs/data_engineering | 28 | 4.3 MiB |
| docs/meaisínfhoghlaim | 103 | 3.8 MiB |
| docs/teanga | 295 | 3.5 MiB |
| docs/web | 68 | 1.1 MiB |
| docs/tuatha | 232 | 5.7 MiB |
| **TOTAL** | **1036** | **49.7 MiB** |

### 1.2 Extension Breakdown

| Extension | Count |
|---|---:|
| .md | 998 |
| .py | 24 |
| .pdf | 7 |
| .yaml | 5 |
| .toml | 1 |
| .docx | 1 |

### 1.3 Extension × Subtree Matrix

| Subtree | .docx | .md | .pdf | .py | .toml | .yaml |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| docs/agents | 0 | 39 | 0 | 0 | 0 | 0 |
| docs/bonneagar | 0 | 150 | 0 | 11 | 0 | 2 |
| docs/context | 0 | 90 | 5 | 10 | 1 | 2 |
| docs/data_engineering | 1 | 27 | 0 | 0 | 0 | 0 |
| docs/meaisínfhoghlaim | 0 | 99 | 0 | 3 | 0 | 1 |
| docs/teanga | 0 | 295 | 0 | 0 | 0 | 0 |
| docs/web | 0 | 68 | 0 | 0 | 0 | 0 |
| docs/tuatha | 0 | 230 | 2 | 0 | 0 | 0 |

## 2. Frontmatter Audit

- **Files with YAML frontmatter (`---`):** 203 / 1036 (19%)
- **Files with `title:` field:** 176
- **Files with `domain:` field:** 0
- **Files with `status:` field:** 0

**Finding:** Frontmatter usage is sparse and inconsistent. Only `name:` and `description:` are used in the context/07-skills/ and data_engineering/ assistant files. No `domain:` or `status:` taxonomies exist. Strong recommendation: standardize on a common frontmatter schema for the consolidated structure.

## 3. Language Mix (Irish vs English)

**82 files flagged as predominantly Irish/Gaelic (score > 3.0)**

| Score | File |
|---|---|
| 98.6 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-cosaint-sonrai.ga.md |
| 96.4 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-brabhsail.ga.md |
| 94.5 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-abhar.ga.md |
| 94.5 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cad-is-tearma.ga.md |
| 91.6 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-casta.ga.md |
| 89.8 | docs/teanga/kscanne-cadhan.com-README.md |
| 84.9 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-tapa.ga.md |
| 81.7 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-coiste.ga.md |
| 79.1 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-conas-usaid.ga.md |
| 77.9 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-corpus.ga.md |
| 72.2 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-gan-toradh.ga.md |
| 70.5 | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-data.ga.md |
| 65.5 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-torthai-a-thuiscint.ga.md |
| 65.3 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-stair.ga.md |
| 64.3 | docs/teanga/gaois-terminologue-website-docs-intro.ga.md |
| 64.1 | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-tionscadal.ga.md |
| 60.1 | docs/teanga/gaois-Nationalist-README.md |
| 55.6 | docs/teanga/gaois-documental-docs-software-documental-editors.ga.md |
| 53.6 | docs/teanga/gaois-terminologue-website-docs-info.ga.md |
| 53.3 | docs/teanga/gaois-documental-docs-software-geonames2sql-index.ga.md |
| 52.0 | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-configuration.ga.md |
| 51.9 | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-faulttolerance.ga.md |
| 49.9 | docs/teanga/gaois-documental-docs-software-documental-developers.ga.md |
| 49.6 | docs/teanga/gaois-documental-docs-software-documental-deployment.ga.md |
| 48.4 | docs/teanga/gaois-documental-docs-software-terminologue-txt-export.ga.md |
| 47.7 | docs/teanga/kscanne-ogham-README.md |
| 45.6 | docs/teanga/gaois-documental-docs-software-localizer-index.ga.md |
| 43.1 | docs/teanga/gaois-documental-docs-software-documental-intro.ga.md |
| 40.1 | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-intro.ga.md |
| 40.0 | docs/teanga/gaois-Tearma-README.md |
| ... | *(52 more)* |

The majority of Irish-language files are in `docs/teanga/` (gaois documentation, kscanne repositories) and `docs/meaisínfhoghlaim/`. The `.ga.md` suffixed files under `docs/teanga/gaois-*/` are deliberate Irish-language versions of their `.en.md` counterparts.

## 4. Duplicate Topic Map

### 4.1 Exact Name Duplicates (same filename in multiple locations)

Found **152** filenames appearing in multiple locations.

| Filename | Locations |
|---|---|
| `2510.17652v1.pdf` | docs/sruth/tuatha/2510.17652v1.pdf<br>docs/sruth/tuatha/sruth/tuatha/2510.17652v1.pdf |
| `adding_agents.md` | docs/sruth/tuatha/ADDING_AGENTS.md<br>docs/sruth/tuatha/sruth/tuatha/ADDING_AGENTS.md |
| `adding_data_sources.md` | docs/sruth/tuatha/ADDING_DATA_SOURCES.md<br>docs/sruth/tuatha/sruth/tuatha/ADDING_DATA_SOURCES.md |
| `adding_tools.md` | docs/sruth/tuatha/ADDING_TOOLS.md<br>docs/sruth/tuatha/sruth/tuatha/ADDING_TOOLS.md |
| `adding_zones.md` | docs/sruth/tuatha/ADDING_ZONES.md<br>docs/sruth/tuatha/sruth/tuatha/ADDING_ZONES.md |
| `ag-ui and a2ui_ understanding the differences _ copilotkit.md` | docs/web/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md<br>docs/sruth/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md<br>docs/sruth/tuatha/sruth/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md |
| `agentic education platform development.md` | docs/agents/Agentic Education Platform Development.md<br>docs/teanga/Agentic Education Platform Development.md<br>docs/sruth/tuatha/Agentic Education Platform Development.md<br>docs/sruth/tuatha/sruth/tuatha/Agentic Education Platform Development.md |
| `agentic translation workflow technologies.md` | docs/agents/Agentic Translation Workflow Technologies.md<br>docs/teanga/Agentic Translation Workflow Technologies.md |
| `agentic web scraping pipeline.md` | docs/agents/Agentic Web Scraping Pipeline.md<br>docs/teanga/Agentic Web Scraping Pipeline.md<br>docs/sruth/tuatha/Agentic Web Scraping Pipeline.md<br>docs/sruth/tuatha/sruth/tuatha/Agentic Web Scraping Pipeline.md |
| `agents.md` | docs/context/01-patterns/AGENTS.md<br>docs/meaisínfhoghlaim/AGENTS.md<br>docs/sruth/tuatha/AGENTS.md<br>docs/sruth/tuatha/sruth/tuatha/AGENTS.md |
| `agno.md` | docs/context/package-ecosystem/ai-frameworks/agno.md<br>docs/context/07-skills/agno.md |
| `ai agents for irish language resources.md` | docs/agents/AI Agents for Irish Language Resources.md<br>docs/teanga/AI Agents for Irish Language Resources.md |
| `ai chemistry education image generation.md` | docs/meaisínfhoghlaim/AI Chemistry Education Image Generation.md<br>docs/teanga/AI Chemistry Education Image Generation.md<br>docs/sruth/tuatha/AI Chemistry Education Image Generation.md<br>docs/sruth/tuatha/sruth/tuatha/AI Chemistry Education Image Generation.md |
| `analysis.md` | docs/sruth/tuatha/ANALYSIS.md<br>docs/sruth/tuatha/sruth/tuatha/ANALYSIS.md |
| `api-readme.md` | docs/sruth/tuatha/api-README.md<br>docs/sruth/tuatha/sruth/tuatha/api-README.md |
| `api.md` | docs/bonneagar/api.md<br>docs/sruth/tuatha/API.md<br>docs/sruth/tuatha/sruth/tuatha/API.md |
| `apple_ml-fastvlm_ this repository contains the official implementation of _fastvlm_ efficient vision encoding for vision language models_ - cvpr 2025.md` | docs/meaisínfhoghlaim/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md<br>docs/sruth/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md<br>docs/sruth/tuatha/sruth/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md |
| `architecture.md` | docs/bonneagar/ARCHITECTURE.md<br>docs/data_engineering/ARCHITECTURE.md |
| `asset management for full-stack app.md` | docs/teanga/Asset Management for Full-Stack App.md<br>docs/web/Asset Management for Full-Stack App.md<br>docs/sruth/tuatha/Asset Management for Full-Stack App.md<br>docs/sruth/tuatha/sruth/tuatha/Asset Management for Full-Stack App.md |
| `auto-optimize pydantic models for structured information extraction_ a complete guide to dspydantic.md` | docs/meaisínfhoghlaim/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md<br>docs/teanga/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md |
| `backend strategy for educational tutoring system.md` | docs/bonneagar/Backend Strategy For Educational Tutoring System.md<br>docs/teanga/Backend Strategy For Educational Tutoring System.md |
| `baml for syllabus-driven data extraction.md` | docs/agents/BAML for Syllabus-Driven Data Extraction.md<br>docs/teanga/BAML for Syllabus-Driven Data Extraction.md |
| `baml schemas for irish education.md` | docs/agents/BAML Schemas for Irish Education.md<br>docs/teanga/BAML Schemas for Irish Education.md |
| `baml, dlt, and ai workflow integration.md` | docs/meaisínfhoghlaim/BAML, DLT, and AI Workflow Integration.md<br>docs/teanga/BAML, DLT, and AI Workflow Integration.md |
| `baml, graphiti, tanstack ai pipeline.md` | docs/teanga/BAML, Graphiti, Tanstack AI Pipeline.md<br>docs/web/BAML, Graphiti, Tanstack AI Pipeline.md |
| `baml.md` | docs/context/01-patterns/BAML.md<br>docs/context/package-ecosystem/ai-frameworks/baml.md<br>docs/context/07-skills/baml.md |
| `british isles education map.md` | docs/teanga/British Isles Education Map.md<br>docs/sruth/tuatha/British Isles Education Map.md<br>docs/sruth/tuatha/sruth/tuatha/British Isles Education Map.md |
| `british isles game dev data pipeline.md` | docs/sruth/tuatha/British Isles Game Dev Data Pipeline.md<br>docs/sruth/tuatha/sruth/tuatha/British Isles Game Dev Data Pipeline.md |
| `british isles mythology mmo research.md` | docs/sruth/tuatha/British Isles Mythology MMO Research.md<br>docs/sruth/tuatha/sruth/tuatha/British Isles Mythology MMO Research.md |
| `building an educational agent's knowledge base.md` | docs/sruth/tuatha/Building an Educational Agent's Knowledge Base.md<br>docs/sruth/tuatha/sruth/tuatha/Building an Educational Agent's Knowledge Base.md |
| `celtic etymology for game names.md` | docs/sruth/tuatha/Celtic Etymology for Game Names.md<br>docs/sruth/tuatha/sruth/tuatha/Celtic Etymology for Game Names.md |
| `celtic language data aggregation & analysis.md` | docs/teanga/Celtic Language Data Aggregation & Analysis.md<br>docs/sruth/tuatha/Celtic Language Data Aggregation & Analysis.md<br>docs/sruth/tuatha/sruth/tuatha/Celtic Language Data Aggregation & Analysis.md |
| `celtic mmo web3 concept integration.md` | docs/sruth/tuatha/Celtic MMO Web3 Concept Integration.md<br>docs/sruth/tuatha/sruth/tuatha/Celtic MMO Web3 Concept Integration.md |
| `celtic-language-ai.md` | docs/context/07-skills/celtic-language-ai.md<br>docs/meaisínfhoghlaim/celtic-language-ai.md |
| `celtic-ocr.md` | docs/sruth/tuatha/celtic-ocr.md<br>docs/sruth/tuatha/sruth/tuatha/celtic-ocr.md |
| `celtic_languages.md` | docs/sruth/tuatha/CELTIC_LANGUAGES.md<br>docs/sruth/tuatha/sruth/tuatha/CELTIC_LANGUAGES.md |
| `celtic_mmo.md` | docs/sruth/tuatha/celtic_mmo.md<br>docs/sruth/tuatha/sruth/tuatha/celtic_mmo.md |
| `chemistry education asset generation.md` | docs/meaisínfhoghlaim/Chemistry Education Asset Generation.md<br>docs/teanga/Chemistry Education Asset Generation.md<br>docs/sruth/tuatha/Chemistry Education Asset Generation.md<br>docs/sruth/tuatha/sruth/tuatha/Chemistry Education Asset Generation.md |
| `chromedevtools_chrome-devtools-mcp_ chrome devtools for coding agents.md` | docs/teanga/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md<br>docs/web/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md |
| `cocoindex.md` | docs/context/package-ecosystem/orchestration/cocoindex.md<br>docs/context/07-skills/cocoindex.md |
| `comparing the top 6 agent-native rails for the agentic internet_ mcp, a2a, ap2, acp, x402, and kite.md` | docs/sruth/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md<br>docs/sruth/tuatha/sruth/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md |
| `compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md` | docs/sruth/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md<br>docs/sruth/tuatha/sruth/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md |
| `cross_platform_guide.md` | docs/sruth/tuatha/CROSS_PLATFORM_GUIDE.md<br>docs/sruth/tuatha/sruth/tuatha/CROSS_PLATFORM_GUIDE.md |
| `crypteolas_ federated learning & crypto payments.md` | docs/sruth/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md<br>docs/sruth/tuatha/sruth/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md |
| `crypteolas_integration_guide.md` | docs/sruth/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md<br>docs/sruth/tuatha/sruth/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md |
| `crypto analysis ai agent system architecture.md` | docs/sruth/tuatha/Crypto Analysis AI Agent System Architecture.md<br>docs/sruth/tuatha/sruth/tuatha/Crypto Analysis AI Agent System Architecture.md |
| `crypto_integration_summary.md` | docs/sruth/tuatha/CRYPTO_INTEGRATION_SUMMARY.md<br>docs/sruth/tuatha/sruth/tuatha/CRYPTO_INTEGRATION_SUMMARY.md |
| `deployment.md` | docs/sruth/tuatha/DEPLOYMENT.md<br>docs/sruth/tuatha/sruth/tuatha/DEPLOYMENT.md |
| `dlt.md` | docs/context/package-ecosystem/orchestration/dlt.md<br>docs/context/07-skills/dlt.md |
| `dlt_crawl4ai_lancedb.md` | docs/sruth/tuatha/dlt_crawl4ai_lancedb.md<br>docs/sruth/tuatha/sruth/tuatha/dlt_crawl4ai_lancedb.md |
| `duckdb.md` | docs/context/package-ecosystem/storage/duckdb.md<br>docs/context/07-skills/duckdb.md |
| `educational game dev pipeline.md` | docs/teanga/Educational Game Dev Pipeline.md<br>docs/sruth/tuatha/Educational Game Dev Pipeline.md<br>docs/sruth/tuatha/sruth/tuatha/Educational Game Dev Pipeline.md |
| `educational website tech stack.md` | docs/teanga/Educational Website Tech Stack.md<br>docs/web/Educational Website Tech Stack.md |
| `educational-game-development.md` | docs/sruth/tuatha/educational-game-development.md<br>docs/sruth/tuatha/sruth/tuatha/educational-game-development.md |
| `engine-selection.md` | docs/sruth/tuatha/engine-selection.md<br>docs/sruth/tuatha/sruth/tuatha/engine-selection.md |
| `erc-4361_ sign-in with ethereum.md` | docs/sruth/tuatha/ERC-4361_ Sign-In with Ethereum.md<br>docs/sruth/tuatha/sruth/tuatha/ERC-4361_ Sign-In with Ethereum.md |
| `federated ai marketplace on iphone.md` | docs/meaisínfhoghlaim/Federated AI Marketplace on iPhone.md<br>docs/sruth/tuatha/Federated AI Marketplace on iPhone.md<br>docs/sruth/tuatha/sruth/tuatha/Federated AI Marketplace on iPhone.md |
| `federated-marketplace.md` | docs/sruth/tuatha/federated-marketplace.md<br>docs/sruth/tuatha/sruth/tuatha/federated-marketplace.md |
| `fine-tuning vlms for ios htr.md` | docs/meaisínfhoghlaim/Fine-tuning VLMs for iOS HTR.md<br>docs/teanga/Fine-tuning VLMs for iOS HTR.md<br>docs/sruth/tuatha/Fine-tuning VLMs for iOS HTR.md<br>docs/sruth/tuatha/sruth/tuatha/Fine-tuning VLMs for iOS HTR.md |
| `finetuning qwen3-vl for gaelic ocr.md` | docs/meaisínfhoghlaim/Finetuning Qwen3-VL for Gaelic OCR.md<br>docs/teanga/Finetuning Qwen3-VL for Gaelic OCR.md |
| `from bi to ai_ a modern lakehouse stack with lance and iceberg.md` | docs/bonneagar/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md<br>docs/teanga/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md |
| `frontend idea catalog development.md` | docs/teanga/Frontend Idea Catalog Development.md<br>docs/web/Frontend Idea Catalog Development.md<br>docs/sruth/tuatha/Frontend Idea Catalog Development.md<br>docs/sruth/tuatha/sruth/tuatha/Frontend Idea Catalog Development.md |
| `frontend.md` | docs/sruth/tuatha/FRONTEND.md<br>docs/sruth/tuatha/sruth/tuatha/FRONTEND.md |
| `gaelic in the digital age_ inside the èist project – gaelic algorithmic research group.md` | docs/meaisínfhoghlaim/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md<br>docs/teanga/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md |
| `game dev pipeline research & plan.md` | docs/teanga/Game Dev Pipeline Research & Plan.md<br>docs/sruth/tuatha/Game Dev Pipeline Research & Plan.md<br>docs/sruth/tuatha/sruth/tuatha/Game Dev Pipeline Research & Plan.md |
| `game development research & ai integration.md` | docs/teanga/Game Development Research & AI Integration.md<br>docs/sruth/tuatha/Game Development Research & AI Integration.md<br>docs/sruth/tuatha/sruth/tuatha/Game Development Research & AI Integration.md |
| `game particle effects research(2).md` | docs/sruth/tuatha/Game Particle Effects Research(2).md<br>docs/sruth/tuatha/sruth/tuatha/Game Particle Effects Research(2).md |
| `game particle effects research.md` | docs/sruth/tuatha/Game Particle Effects Research.md<br>docs/sruth/tuatha/sruth/tuatha/Game Particle Effects Research.md |
| `game reverse engineering workflow design.md` | docs/sruth/tuatha/Game Reverse Engineering Workflow Design.md<br>docs/sruth/tuatha/sruth/tuatha/Game Reverse Engineering Workflow Design.md |
| `game-design-readme.md` | docs/sruth/tuatha/game-design-README.md<br>docs/sruth/tuatha/sruth/tuatha/game-design-README.md |
| `game_client.md` | docs/sruth/tuatha/GAME_CLIENT.md<br>docs/sruth/tuatha/sruth/tuatha/GAME_CLIENT.md |
| `game_contributing.md` | docs/sruth/tuatha/game_CONTRIBUTING.md<br>docs/sruth/tuatha/sruth/tuatha/game_CONTRIBUTING.md |
| `game_development.md` | docs/sruth/tuatha/game_DEVELOPMENT.md<br>docs/sruth/tuatha/sruth/tuatha/game_DEVELOPMENT.md |
| `game_siwe-auth.md` | docs/sruth/tuatha/game_siwe-auth.md<br>docs/sruth/tuatha/sruth/tuatha/game_siwe-auth.md |
| `gdext-readme.md` | docs/sruth/tuatha/gdext-ReadMe.md<br>docs/sruth/tuatha/sruth/tuatha/gdext-ReadMe.md |
| `generative ai art workflow integration.md` | docs/data_engineering/Generative AI Art Workflow Integration.md<br>docs/sruth/tuatha/Generative AI Art Workflow Integration.md<br>docs/sruth/tuatha/sruth/tuatha/Generative AI Art Workflow Integration.md |
| `geoai.md` | docs/sruth/tuatha/GeoAI.md<br>docs/sruth/tuatha/sruth/tuatha/GeoAI.md |
| `geospatial workflow & particle effects.md` | docs/sruth/tuatha/Geospatial Workflow & Particle Effects.md<br>docs/sruth/tuatha/sruth/tuatha/Geospatial Workflow & Particle Effects.md |
| `godot_rust_guide.md` | docs/sruth/tuatha/GODOT_RUST_GUIDE.md<br>docs/sruth/tuatha/sruth/tuatha/GODOT_RUST_GUIDE.md |
| `google adk with litellm _ litellm.md` | docs/meaisínfhoghlaim/Google ADK with LiteLLM _ liteLLM.md<br>docs/teanga/Google ADK with LiteLLM _ liteLLM.md |
| `graphics_index.md` | docs/sruth/tuatha/GRAPHICS_INDEX.md<br>docs/sruth/tuatha/sruth/tuatha/GRAPHICS_INDEX.md |
| `implementation_guide.md` | docs/bonneagar/IMPLEMENTATION_GUIDE.md<br>docs/context/08-examples/IMPLEMENTATION_GUIDE.md<br>docs/meaisínfhoghlaim/IMPLEMENTATION_GUIDE.md |
| `index.md` | 9 copies across subtrees |
| `infrastructure-readme.md` | docs/sruth/tuatha/infrastructure-README.md<br>docs/sruth/tuatha/sruth/tuatha/infrastructure-README.md |
| `integrating rust, duckdb, tanstack, copilotkit.md` | docs/teanga/Integrating Rust, DuckDB, TanStack, CopilotKit.md<br>docs/sruth/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md<br>docs/sruth/tuatha/sruth/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md |
| `integrating tanstack ai with litellm.md` | docs/teanga/Integrating TanStack AI with LiteLLM.md<br>docs/web/Integrating TanStack AI with LiteLLM.md |
| `interactive ai pipeline development.md` | docs/meaisínfhoghlaim/Interactive AI Pipeline Development.md<br>docs/sruth/tuatha/Interactive AI Pipeline Development.md<br>docs/sruth/tuatha/sruth/tuatha/Interactive AI Pipeline Development.md |
| `interactive map & ai agents.md` | docs/teanga/Interactive Map & AI Agents.md<br>docs/sruth/tuatha/Interactive Map & AI Agents.md<br>docs/sruth/tuatha/sruth/tuatha/Interactive Map & AI Agents.md |
| `introducing anylanguagemodel_ one api for local and remote llms on apple platforms.md` | docs/meaisínfhoghlaim/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md<br>docs/sruth/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md<br>docs/sruth/tuatha/sruth/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md |
| `ios app development ecosystem strategy.md` | docs/meaisínfhoghlaim/iOS App Development Ecosystem Strategy.md<br>docs/sruth/tuatha/iOS App Development Ecosystem Strategy.md<br>docs/sruth/tuatha/sruth/tuatha/iOS App Development Ecosystem Strategy.md |
| `irish handwriting app development.md` | docs/teanga/Irish Handwriting App Development.md<br>docs/sruth/tuatha/Irish Handwriting App Development.md<br>docs/sruth/tuatha/sruth/tuatha/Irish Handwriting App Development.md |
| `irish llm for iphone development.md` | docs/meaisínfhoghlaim/Irish LLM for iPhone Development.md<br>docs/teanga/Irish LLM for iPhone Development.md<br>docs/sruth/tuatha/Irish LLM for iPhone Development.md<br>docs/sruth/tuatha/sruth/tuatha/Irish LLM for iPhone Development.md |
| `kotlin multiplatform vs. react native_ a cross-platform comparison _ kotlin multiplatform.md` | docs/sruth/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md<br>docs/sruth/tuatha/sruth/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md |
| `learn-to-earn blockchain and ai.md` | docs/sruth/tuatha/Learn-to-Earn Blockchain and AI.md<br>docs/sruth/tuatha/sruth/tuatha/Learn-to-Earn Blockchain and AI.md |
| `learn-to-earn-model.md` | docs/sruth/tuatha/learn-to-earn-model.md<br>docs/sruth/tuatha/sruth/tuatha/learn-to-earn-model.md |
| `llm serving with mlflow & langfuse.md` | docs/sruth/tuatha/LLM Serving with MLflow & Langfuse.md<br>docs/sruth/tuatha/sruth/tuatha/LLM Serving with MLflow & Langfuse.md |
| `mcp-ui.md` | docs/agents/MCP-UI.md<br>docs/sruth/tuatha/MCP-UI.md<br>docs/sruth/tuatha/sruth/tuatha/MCP-UI.md |
| `mcp_research.md` | docs/agents/MCP_RESEARCH.md<br>docs/context/04-agents/MCP_RESEARCH.md |
| `ml-models-readme.md` | docs/sruth/tuatha/ml-models-README.md<br>docs/sruth/tuatha/sruth/tuatha/ml-models-README.md |
| `mmo geospatial data & visual rag.md` | docs/sruth/tuatha/MMO Geospatial Data & Visual RAG.md<br>docs/sruth/tuatha/sruth/tuatha/MMO Geospatial Data & Visual RAG.md |
| `model_training.md` | docs/context/05-celtic-language/MODEL_TRAINING.md<br>docs/teanga/model_training.md |
| `motherduck_mcp.md` | docs/meaisínfhoghlaim/motherduck_mcp.md<br>docs/teanga/motherduck_mcp.md |
| `multimodal irish handwriting generation model.md` | docs/meaisínfhoghlaim/Multimodal Irish Handwriting Generation Model.md<br>docs/teanga/Multimodal Irish Handwriting Generation Model.md |
| `multimodal video knowledge graph pipeline.md` | docs/sruth/tuatha/Multimodal Video Knowledge Graph Pipeline.md<br>docs/sruth/tuatha/sruth/tuatha/Multimodal Video Knowledge Graph Pipeline.md |
| `mythology-framework.md` | docs/sruth/tuatha/mythology-framework.md<br>docs/sruth/tuatha/sruth/tuatha/mythology-framework.md |
| `neuro-symbolic translation model training.md` | docs/meaisínfhoghlaim/Neuro-Symbolic Translation Model Training.md<br>docs/teanga/Neuro-Symbolic Translation Model Training.md |
| `new in llama.cpp_ model management.md` | docs/bonneagar/New in llama.cpp_ Model Management.md<br>docs/meaisínfhoghlaim/New in llama.cpp_ Model Management.md |
| `notebooklm_1.md` | docs/meaisínfhoghlaim/notebooklm_1.md<br>docs/teanga/notebooklm_1.md |
| `ogham crypto mmo research.md` | docs/sruth/tuatha/Ogham Crypto MMO Research.md<br>docs/sruth/tuatha/sruth/tuatha/Ogham Crypto MMO Research.md |
| `payment_guide.md` | docs/sruth/tuatha/PAYMENT_GUIDE.md<br>docs/sruth/tuatha/sruth/tuatha/PAYMENT_GUIDE.md |
| `performance_tuning.md` | docs/sruth/tuatha/PERFORMANCE_TUNING.md<br>docs/sruth/tuatha/sruth/tuatha/PERFORMANCE_TUNING.md |
| `pipelines.md` | docs/sruth/tuatha/PIPELINES.md<br>docs/sruth/tuatha/sruth/tuatha/PIPELINES.md |
| `productionalize ai workloads with lance namespace, lancedb, and ray.md` | docs/meaisínfhoghlaim/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md<br>docs/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md |
| `react drag-and-drop for exam builder.md` | docs/meaisínfhoghlaim/React Drag-and-Drop for Exam Builder.md<br>docs/web/React Drag-and-Drop for Exam Builder.md |
| `readme.md` | docs/bonneagar/README.md<br>docs/meaisínfhoghlaim/README.md<br>docs/web/README.md<br>docs/sruth/tuatha/README.md<br>docs/sruth/tuatha/sruth/tuatha/README.md |
| `release v28.0.0 - mesh shaders, immediates, and more! · gfx-rs_wgpu.md` | docs/web/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md<br>docs/sruth/tuatha/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md<br>docs/sruth/tuatha/sruth/tuatha/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md |
| `repo-agui_kotlin.md` | docs/sruth/tuatha/repo-agui_kotlin.md<br>docs/sruth/tuatha/sruth/tuatha/repo-agui_kotlin.md |
| `repo-anylanguagemodel.md` | docs/sruth/tuatha/repo-AnyLanguageModel.md<br>docs/sruth/tuatha/sruth/tuatha/repo-AnyLanguageModel.md |
| `repo-hophacks-spacetimedb-workshop.md` | docs/sruth/tuatha/repo-hophacks-spacetimedb-workshop.md<br>docs/sruth/tuatha/sruth/tuatha/repo-hophacks-spacetimedb-workshop.md |
| `repo-ireland.md` | docs/sruth/tuatha/repo-ireland.md<br>docs/sruth/tuatha/sruth/tuatha/repo-ireland.md |
| `repo-react-native-godot.md` | docs/sruth/tuatha/repo-react-native-godot.md<br>docs/sruth/tuatha/sruth/tuatha/repo-react-native-godot.md |
| `repo-react-native-reusables.md` | docs/sruth/tuatha/repo-react-native-reusables.md<br>docs/sruth/tuatha/sruth/tuatha/repo-react-native-reusables.md |
| `repo-spacetimedb-cookbook.md` | docs/sruth/tuatha/repo-spacetimedb-cookbook.md<br>docs/sruth/tuatha/sruth/tuatha/repo-spacetimedb-cookbook.md |
| `repo-spacetimedb-typescript-sdk.md` | docs/sruth/tuatha/repo-spacetimedb-typescript-sdk.md<br>docs/sruth/tuatha/sruth/tuatha/repo-spacetimedb-typescript-sdk.md |
| `repo-spacetimedb.md` | docs/sruth/tuatha/repo-SpacetimeDB.md<br>docs/sruth/tuatha/sruth/tuatha/repo-SpacetimeDB.md |
| `repo-wgpu.md` | docs/sruth/tuatha/repo-wgpu.md<br>docs/sruth/tuatha/sruth/tuatha/repo-wgpu.md |
| `repo-x402.md` | docs/sruth/tuatha/repo-x402.md<br>docs/sruth/tuatha/sruth/tuatha/repo-x402.md |
| `resource maximization and project planning.md` | docs/bonneagar/Resource Maximization and Project Planning.md<br>docs/meaisínfhoghlaim/Resource Maximization and Project Planning.md |
| `rust client.md` | docs/bonneagar/Rust Client.md<br>docs/sruth/tuatha/Rust Client.md<br>docs/sruth/tuatha/sruth/tuatha/Rust Client.md |
| `rust full-stack gaming environment.md` | docs/bonneagar/Rust Full-Stack Gaming Environment.md<br>docs/sruth/tuatha/Rust Full-Stack Gaming Environment.md<br>docs/sruth/tuatha/sruth/tuatha/Rust Full-Stack Gaming Environment.md |
| `sign in with ethereum (siwe) _ better auth.md` | docs/agents/Sign In With Ethereum (SIWE) _ Better Auth.md<br>docs/web/Sign In With Ethereum (SIWE) _ Better Auth.md<br>docs/sruth/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md<br>docs/sruth/tuatha/sruth/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md |
| `spacetimedb blockchain integration strategy.md` | docs/sruth/tuatha/Spacetimedb Blockchain Integration Strategy.md<br>docs/sruth/tuatha/sruth/tuatha/Spacetimedb Blockchain Integration Strategy.md |
| `spacetimedb ogham stone game integration.md` | docs/sruth/tuatha/SpacetimeDB Ogham Stone Game Integration.md<br>docs/sruth/tuatha/sruth/tuatha/SpacetimeDB Ogham Stone Game Integration.md |
| `spacetimedb.md` | docs/sruth/tuatha/SpacetimeDB.md<br>docs/sruth/tuatha/sruth/tuatha/SpacetimeDB.md |
| `spacetimedb_guide.md` | docs/sruth/tuatha/SPACETIMEDB_GUIDE.md<br>docs/sruth/tuatha/sruth/tuatha/SPACETIMEDB_GUIDE.md |
| `swift transformers reaches 1.0 – and looks to the future.md` | docs/meaisínfhoghlaim/Swift Transformers Reaches 1.0 – and Looks to the Future.md<br>docs/sruth/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md<br>docs/sruth/tuatha/sruth/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md |
| `syft-flwr_notebooks_fedrag_readme.md at main · openmined_syft-flwr.md` | docs/meaisínfhoghlaim/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md<br>docs/sruth/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md<br>docs/sruth/tuatha/sruth/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md |
| `tanstack db integration and comparison.md` | docs/web/TanStack DB Integration and Comparison.md<br>docs/sruth/tuatha/TanStack DB Integration and Comparison.md<br>docs/sruth/tuatha/sruth/tuatha/TanStack DB Integration and Comparison.md |
| `tanstack-start.md` | docs/context/package-ecosystem/frontend/tanstack-start.md<br>docs/context/07-skills/tanstack-start.md |
| `tech_stack.md` | docs/bonneagar/TECH_STACK.md<br>docs/context/04-agents/TECH_STACK.md |
| `technical integration plan_ dagster + dlt + cocoindex + feast + mlflow (with duckdb & dragonfly).md` | docs/sruth/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md<br>docs/sruth/tuatha/sruth/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md |
| `the expulsion of the déisi - wikipedia.md` | docs/sruth/tuatha/The Expulsion of the Déisi - Wikipedia.md<br>docs/sruth/tuatha/sruth/tuatha/The Expulsion of the Déisi - Wikipedia.md |
| `tokenomics-readme.md` | docs/sruth/tuatha/tokenomics-README.md<br>docs/sruth/tuatha/sruth/tuatha/tokenomics-README.md |
| `transformers.md` | docs/data_engineering/transformers.md<br>docs/meaisínfhoghlaim/transformers.md |
| `unsloth model catalog _ unsloth documentation.md` | docs/meaisínfhoghlaim/Unsloth Model Catalog _ Unsloth Documentation.md<br>docs/sruth/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md<br>docs/sruth/tuatha/sruth/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md |
| `unsloth-catalog.md` | docs/sruth/tuatha/unsloth-catalog.md<br>docs/sruth/tuatha/sruth/tuatha/unsloth-catalog.md |
| `useagent hook.md` | docs/teanga/useAgent Hook.md<br>docs/sruth/tuatha/useAgent Hook.md<br>docs/sruth/tuatha/sruth/tuatha/useAgent Hook.md |
| `web3 classroom response system design.md` | docs/sruth/tuatha/Web3 Classroom Response System Design.md<br>docs/sruth/tuatha/sruth/tuatha/Web3 Classroom Response System Design.md |
| `web3 gamified education & asset generation.md` | docs/sruth/tuatha/Web3 Gamified Education & Asset Generation.md<br>docs/sruth/tuatha/sruth/tuatha/Web3 Gamified Education & Asset Generation.md |
| `wgpu_guide.md` | docs/sruth/tuatha/WGPU_GUIDE.md<br>docs/sruth/tuatha/sruth/tuatha/WGPU_GUIDE.md |
| `world-map.md` | docs/sruth/tuatha/world-map.md<br>docs/sruth/tuatha/sruth/tuatha/world-map.md |
| `x402-payments.md` | docs/sruth/tuatha/x402-payments.md<br>docs/sruth/tuatha/sruth/tuatha/x402-payments.md |

### 4.2 Topical Overlaps (same topics across subtrees)

The following table lists the number of files in each topic cluster per subtree:

| Topic | agents | bonneagar | context | data_engineering | meaisínfhoghlaim | teanga | web | tuatha |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Agents/MCP | 39 | 8 | 21 | 3 | 12 | 16 | 8 | 54 |
| BAML | 6 | 1 | 4 | 3 | 5 | 7 | 2 | 6 |
| Browser/Scraping | 2 | 18 | 1 | 0 | 1 | 3 | 0 | 6 |
| Celtic/Education | 5 | 27 | 30 | 2 | 21 | 89 | 5 | 90 |
| Cloudflare | 0 | 11 | 1 | 1 | 0 | 0 | 4 | 0 |
| CocoIndex | 0 | 1 | 4 | 2 | 0 | 1 | 0 | 2 |
| Cognee/Graphiti | 0 | 8 | 6 | 3 | 1 | 4 | 1 | 6 |
| Convex | 1 | 1 | 0 | 0 | 0 | 0 | 8 | 2 |
| Crypto/Web3 | 3 | 6 | 3 | 0 | 2 | 0 | 1 | 42 |
| DLT | 0 | 1 | 4 | 3 | 1 | 4 | 0 | 4 |
| Dagster | 0 | 11 | 17 | 3 | 3 | 1 | 0 | 8 |
| Docker | 0 | 15 | 2 | 1 | 0 | 0 | 0 | 0 |
| DuckDB | 1 | 2 | 3 | 2 | 1 | 9 | 1 | 10 |
| Effect-TS | 0 | 0 | 0 | 0 | 0 | 4 | 3 | 8 |
| Game/MMO | 0 | 1 | 2 | 1 | 0 | 5 | 1 | 98 |
| Hono | 1 | 1 | 1 | 0 | 0 | 0 | 2 | 0 |
| Komodo/Pangolin | 0 | 30 | 0 | 0 | 0 | 0 | 0 | 0 |
| LanceDB | 0 | 3 | 4 | 4 | 2 | 4 | 0 | 2 |
| LiteLLM | 0 | 1 | 1 | 1 | 6 | 2 | 1 | 0 |
| MLflow/Langfuse | 0 | 0 | 1 | 0 | 7 | 2 | 0 | 4 |
| OCR | 0 | 1 | 1 | 0 | 11 | 15 | 0 | 4 |
| Pulumi | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| TanStack | 0 | 1 | 3 | 0 | 1 | 4 | 20 | 6 |
| Unsloth/HF | 0 | 1 | 6 | 0 | 25 | 16 | 0 | 8 |

### 4.3 Key Duplicate/Overlap Findings

1. **docs/sruth/tuatha/sruth/tuatha/ is a near-exact mirror of docs/sruth/tuatha/** (116 files) — immediate pruning target.
2. **`Prompt Optimization (Beta).md`** appears 3× identically in `docs/meaisínfhoghlaim/` — exact byte-for-byte copies.
3. **Celtic/Education** topics span 6 of 8 subtrees — the most cross-cutting concern.
4. **Agents/MCP** topics span 5 subtrees (agents, bonneagar, context, meaisínfhoghlaim, teanga).
5. **KCG_SUMMARY.md** exists in both `docs/teanga/gaois-KCG_SUMMARY.md` and `docs/teanga/kscanne-KCG_SUMMARY.md`.
6. **Same research articles** (`Resource Maximization`, `Productionalize AI`, `British Isles Education Map`, etc.) duplicated between `docs/teanga/` and `docs/sruth/tuatha/`.
7. **Same research articles** duplicated between `docs/meaisínfhoghlaim/` and `docs/teanga/` (e.g., `Notebooklm`, `Neuro-Symbolic Translation`, `Google ADK with LiteLLM`).

## 5. Per-File Inventory

Each file listed with: size, extension, frontmatter flag, Irish score, and 1-line summary.

### 5.1 docs/agents

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 25.5 KiB | .md |  |  | Agent-Related Implementations Analysis | docs/agents/AGENT_IMPLEMENTATIONS_SUMMARY.md |
| 10.8 KiB | .md |  |  | Agno Framework: Comprehensive Architecture Reference | docs/agents/AGNO_COMPREHENSIVE_REFERENCE.md |
| 135 B | .md |  |  | MERGED INTO IRISH_EDUCATION_PLATFORM_BLUEPRINT.md | docs/agents/AI Agents for Irish Language Resources.md |
| 3.7 KiB | .md | Y |  | Agent UI Ecosystem   A2UI | docs/agents/Agent UI Ecosystem - A2UI.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/Agent _ Firecrawl.md |
| 135 B | .md |  |  | MERGED INTO IRISH_EDUCATION_PLATFORM_BLUEPRINT.md | docs/agents/Agentic Education Platform Development.md |
| 135 B | .md |  |  | MERGED INTO IRISH_EDUCATION_PLATFORM_BLUEPRINT.md | docs/agents/Agentic Translation Workflow Technologies.md |
| 209 B | .md |  |  | MERGED INTO BAML_COMPREHENSIVE_GUIDE.md | docs/agents/Agentic Web Scraping Pipeline.md |
| 115 B | .md |  |  | MERGED INTO BAML_COMPREHENSIVE_GUIDE.md | docs/agents/BAML Schemas for Irish Education.md |
| 115 B | .md |  |  | MERGED INTO BAML_COMPREHENSIVE_GUIDE.md | docs/agents/BAML for Syllabus-Driven Data Extraction.md |
| 33.5 KiB | .md |  |  | BAML Comprehensive Guide: Patterns, Architecture, and Production Applications | docs/agents/BAML_COMPREHENSIVE_GUIDE.md |
| 115 B | .md |  |  | MERGED INTO BAML_COMPREHENSIVE_GUIDE.md | docs/agents/BAML_DUCKDB_DRAGONFLY_ANALYSIS.md |
| 4.2 KiB | .md |  |  | Browser Automation Platform Reference | docs/agents/BROWSER_AUTOMATION_PLATFORM.md |
| 1.9 KiB | .md |  |  | Convex Agent Platform Reference | docs/agents/CONVEX_AGENT_PLATFORM.md |
| 5.7 KiB | .md |  |  | Durable Execution: Restate & DBOS — Comprehensive Reference | docs/agents/DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md |
| 4.9 KiB | .md |  |  | Google Agent Development Kit (ADK) — Comprehensive Reference | docs/agents/GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md |
| 2.8 KiB | .md |  |  | Agent Documentation Index | docs/agents/INDEX.md |
| 12.3 KiB | .md |  |  | Irish Education Platform Blueprint: Agentic Systems for Celtic Education | docs/agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/MCP Server with x402.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/MCP Server.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/MCP Toolbox.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/MCP _ Better Auth.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/MCP-UI.md |
| 20.5 KiB | .md |  |  | MCP Comprehensive Research: Protocol, Integration, and Applications | docs/agents/MCP_COMPREHENSIVE_RESEARCH.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/MCP_RESEARCH.md |
| 2.5 KiB | .md |  |  | Pydantic AI Reference | docs/agents/PYDIANTIC_AI_REFERENCE.md |
| 6.4 KiB | .md |  |  | Stagehand Comprehensive Reference: Browser Automation with AI | docs/agents/STAGEHAND_COMPREHENSIVE_REFERENCE.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/Sign In With Ethereum (SIWE) _ Better Auth.md |
| 363.3 KiB | .md |  |  | agent frameworks | docs/agents/agent-frameworks.md |
| 123 B | .md |  |  | MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md | docs/agents/agno-architecture-guide.md |
| 123 B | .md |  |  | MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md | docs/agents/agno-openapi-specification-research.md |
| 123 B | .md |  |  | MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md | docs/agents/agno_architecure_z_ai.md |
| 47.4 KiB | .md |  |  | ai sdk tools | docs/agents/ai-sdk-tools.md |
| 192.7 KiB | .md |  |  | uackend platforms | docs/agents/backend-platforms.md |
| 115 B | .md |  |  | MERGED INTO BAML_COMPREHENSIVE_GUIDE.md | docs/agents/baml-patterns-and-best-practices.md |
| 198.3 KiB | .md |  |  | urowser automation | docs/agents/browser-automation.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/mcp-research-report.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/mcp-ui-gradio-evidence-integration-analysis.md |
| 119 B | .md |  |  | MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md | docs/agents/x402_examples_typescript_servers_hono at main · coinbase_x402.md |

### 5.2 docs/bonneagar

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 1.6 KiB | .md |  |  | Monorepo Management Best Practices Research | docs/bonneagar/.!31103!monorepo-best-practices-2025.md |
| 9.9 KiB | .md | Y |  | AI Partner Catalyst  Accelerate Innovation(1) | docs/bonneagar/AI Partner Catalyst_ Accelerate Innovation(1).md |
| 20.0 KiB | .md |  |  | Infrastructure Architecture Reference | docs/bonneagar/ARCHITECTURE.md |
| 35.7 KiB | .md |  |  | **Backend Architecture Strategy for a Bilingual Temporal Knowledge Graph in Mathematics Education** | docs/bonneagar/Backend Strategy For Educational Tutoring System.md |
| 12.2 KiB | .md | Y |  | Building preconfigured OS images with HashiCorp Packer | docs/bonneagar/Building preconfigured OS images with HashiCorp Packer.md |
| 13.2 KiB | .md | Y |  | Configuration File | docs/bonneagar/Configuration File.md |
| 31.2 KiB | .md |  |  | **Architectural Blueprint for Autonomous Web Reconnaissance and High-Value Asset Extraction: Integrating Stagehand and C | docs/bonneagar/Crawl4ai Scraping and Site Analysis.md |
| 6.7 KiB | .md |  |  | Dagger CI/CD - Complete Guide Index | docs/bonneagar/DAGGER_GUIDE_INDEX.md |
| 49.5 KiB | .md |  |  | Comprehensive Analysis of Dagger Examples | docs/bonneagar/DAGGER_PATTERNS_ANALYSIS.md |
| 10.2 KiB | .md |  |  | Dagger Patterns Quick Reference | docs/bonneagar/DAGGER_QUICK_REFERENCE.md |
| 10.2 KiB | .md |  |  | Infrastructure Decision Matrices | docs/bonneagar/DECISION_MATRICES.md |
| 31.2 KiB | .md |  |  | Docker Compose Architecture Overview | docs/bonneagar/DOCKER_COMPOSE_ARCHITECTURE.md |
| 10.7 KiB | .md |  |  | Docker Compose Analysis - Complete Documentation Index | docs/bonneagar/DOCKER_COMPOSE_QUICKSTART.md |
| 33.0 KiB | .md |  |  | Docker Compose Stacks Analysis - Hackathon Project | docs/bonneagar/DOCKER_COMPOSE_REFERENCE.md |
| 38.2 KiB | .md |  |  | **Architectural Blueprint for Mathematical Knowledge Extraction: A Modular Orchestration Strategy Using Dagster, Cocoind | docs/bonneagar/Dagster Orchestration for Cocoindex, Graphiti.md |
| 3.4 KiB | .md | Y |  | Deploying Dagster to Google Cloud Platform   Dagster Docs | docs/bonneagar/Deploying Dagster to Google Cloud Platform _ Dagster Docs.md |
| 34.9 KiB | .md |  |  | **Architecting the Composable Data Fabric: A Definitive Implementation Guide for Local-First Lakehouse Environments** | docs/bonneagar/Docker Compose Setup for Data Tools.md |
| 11.0 KiB | .md | Y |  | Docker Provider | docs/bonneagar/Docker Provider.md |
| 33.2 KiB | .md |  |  | **Architecting the Modern Platform: Integrating Ansible into High-Performance Monorepo Ecosystems** | docs/bonneagar/Enhancing Monorepo Ansible Workflow.md |
| 19.2 KiB | .md | Y |  | From BI to AI  A Modern Lakehouse Stack with Lance and Iceberg | docs/bonneagar/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md |
| 2.5 KiB | .md | Y |  | Get started with a 1Password Connect server   1Password Developer | docs/bonneagar/Get started with a 1Password Connect server _ 1Password Developer.md |
| 11.5 KiB | .md | Y |  | High Availability Kubernetes on Hetzner with Talos 1.11 | docs/bonneagar/High-Availability Kubernetes on Hetzner with Talos 1.11.md |
| 8.5 KiB | .md |  |  | Infrastructure Implementation Guide | docs/bonneagar/IMPLEMENTATION_GUIDE.md |
| 4.3 KiB | .md |  |  | Bonneagar — Infrastructure Research Index | docs/bonneagar/INDEX.md |
| 2.1 KiB | .md |  |  | Infrastructure Research - Consolidated Index | docs/bonneagar/INDEX1.md |
| 10.7 KiB | .md |  |  | Komodo — Complete Deployment Orchestration Guide | docs/bonneagar/KOMODO_COMPLETE_GUIDE.md |
| 29.1 KiB | .md |  |  | **Comprehensive Architectural Strategy for the Pan-Curricular Expansion of the Irish Leaving Certificate AI Tutoring Sys | docs/bonneagar/Leaving Certificate Subject Analysis Plan.md |
| 11.8 KiB | .md | Y |  | MCP Server Transports  STDIO, Streamable HTTP & SSE | docs/bonneagar/MCP Server Transports_ STDIO, Streamable HTTP & SSE.md |
| 31.1 KiB | .md |  |  | **Orchestrating the Polyglot Monorepo: A Comparative Architectural Analysis of Mise-en-place, Taskipy, and Dagger for Hy | docs/bonneagar/Monorepo Toolchain_ Mise, Dagger, Taskipy.md |
| 5.6 KiB | .md | Y |  | New in llama.cpp  Model Management | docs/bonneagar/New in llama.cpp_ Model Management.md |
| 12.8 KiB | .md |  |  | OpenAPI Specifications Research Summary | docs/bonneagar/OPENAPI_SPECS_SUMMARY.md |
| 21.3 KiB | .md |  |  | OpenSpec Analysis Report: Comprehensive Structure and Guidelines | docs/bonneagar/OPENSPEC_ANALYSIS.md |
| 8.7 KiB | .md |  |  | OpenSpec Documentation Index | docs/bonneagar/OPENSPEC_README.md |
| 34.9 KiB | .md |  |  | **Architectural Paradigms for Self-Hosted Autonomous Web Scraping: A Deep Technical Analysis of Cloudflare Turnstile Eva | docs/bonneagar/Open-Source Crawl4ai Anti-Bot Stack.md |
| 36.4 KiB | .md |  |  | **Strategic Architecture for Autonomous Educational Data Acquisition: Integrating Skyvern, Crawl4AI, and Stagehand in th | docs/bonneagar/Open-Source Web Scraping Architecture Analysis.md |
| 11.9 KiB | .md |  |  | Pangolin — Complete Zero-Trust Networking Guide | docs/bonneagar/PANGOLIN_COMPLETE_GUIDE.md |
| 26.6 KiB | .md |  |  | **Architectural Blueprint for the Unified Deployment of Pigsty and Mathesar: A Simplified Komodo-Ansible Integration** | docs/bonneagar/Pigsty, Mathesar, Komodo Deployment Outline.md |
| 31.2 KiB | .md |  |  | **Architecting the Polymath Studio: A Full-Stack Blueprint for Game Development and Audio Production Portfolios** | docs/bonneagar/Portfolio Tech Stack & Cloudflare R2.md |
| 15.3 KiB | .md | Y |  | Provision Resources on Hetzner Cloud with Pulumi | docs/bonneagar/Provision Resources on Hetzner Cloud with Pulumi.md |
| 11.1 KiB | .md |  |  | Celtic Education Scraping Agent | docs/bonneagar/README.md |
| 2.3 KiB | .md | Y |  | Register a GCP Instance | docs/bonneagar/Register a GCP Instance.md |
| 1.6 KiB | .md | Y |  | Register a Hetzner Server | docs/bonneagar/Register a Hetzner Server.md |
| 4.7 KiB | .md | Y |  | Release Komodo v2.0.0 dev 102 · moghtech komodo | docs/bonneagar/Release Komodo v2.0.0-dev-102 · moghtech_komodo.md |
| 32.3 KiB | .md |  |  | **Strategic Resource Maximization: Architecting the Celtic Heritage Intelligence Platform (CHIP)** | docs/bonneagar/Resource Maximization and Project Planning(1).md |
| 32.3 KiB | .md |  |  | **Strategic Resource Maximization: Architecting the Celtic Heritage Intelligence Platform (CHIP)** | docs/bonneagar/Resource Maximization and Project Planning.md |
| 3.5 KiB | .md | Y |  | Rust Client | docs/bonneagar/Rust Client.md |
| 39.2 KiB | .md |  |  | **Architectural Analysis and Implementation Strategy for a Rust-Based Full-Stack Gaming Ecosystem** | docs/bonneagar/Rust Full-Stack Gaming Environment.md |
| 14.3 KiB | .md |  |  | Secrets Management — Locket + Infisical Complete Guide | docs/bonneagar/SECRETS_MANAGEMENT_GUIDE.md |
| 12.8 KiB | .md |  |  | Automation Setup Guide | docs/bonneagar/SETUP.md |
| 35.9 KiB | .md |  |  | **Architectural Convergence in Modern Self-Hosted Infrastructure: A Comprehensive Analysis of Visualization, Centralizat | docs/bonneagar/Self-Hosted Stack Visualization & Management.md |
| 1.2 KiB | .md |  |  | TECH STACK | docs/bonneagar/TECH_STACK.md |
| 37.7 KiB | .md |  |  | **Architectural Synthesis of a Unified Scraping Swarm: Optimizing Skyvern, Crawl4AI, and Stagehand via Model Context Pro | docs/bonneagar/Unified Scraping Swarm Stack Optimization.md |
| 24.5 KiB | .md | Y |  | Using MCP in Roo Code   Roo Code Documentation | docs/bonneagar/Using MCP in Roo Code _ Roo Code Documentation.md |
| 16.5 KiB | .md |  |  | Data Acquisition Pipeline Implementation | docs/bonneagar/acquisition-pipeline.md |
| 9.8 KiB | .md |  |  | Agentic Scraping Architecture: Hunter-Gatherer-Operator Pattern | docs/bonneagar/agentic-scraping-architecture.md |
| 13.8 KiB | .md |  |  | AI/ML Pipeline for Irish Education Platform | docs/bonneagar/ai-ml-pipeline.md |
| 110.4 KiB | .md |  |  | AI-Native Data Pipelines | docs/bonneagar/ai-pipelines.md |
| 11.8 KiB | .md |  |  | Text Alignment Tools for Irish-English | docs/bonneagar/alignment-tools.md |
| 26.8 KiB | .md | Y |  | ansible role komodo examples at komodo v2 · bpbradley ansible role komodo | docs/bonneagar/ansible-role-komodo_examples at komodo_v2 · bpbradley_ansible-role-komodo.md |
| 16.4 KiB | .md | Y |  | Pangolin API Development Assistant | docs/bonneagar/api.md |
| 11.2 KiB | .md |  |  | Apple Silicon LLM Deployment | docs/bonneagar/apple-silicon-deployment.md |
| 15.0 KiB | .md |  |  | Apple Silicon Deployment for Document Intelligence | docs/bonneagar/apple-silicon-deployment_1.md |
| 14.8 KiB | .md |  |  | Pangolin Project: Architecture Patterns & Best Practices | docs/bonneagar/architecture-patterns.md |
| 25.8 KiB | .md |  |  | Automating Deployment with Komodo and Docker | docs/bonneagar/automation_readme.md |
| 7.2 KiB | .md | Y |  | Ibis Backend Selection Assistant | docs/bonneagar/backend.md |
| 84.5 KiB | .md |  |  | Bilingual Irish Educational Resources Scraper | docs/bonneagar/bilingual-scraper-implementation.md |
| 10.4 KiB | .md |  |  | Bunchloch Infrastructure Stack | docs/bonneagar/bunchloch.md |
| 170.4 KiB | .md |  |  | Celtic Language Platform | docs/bonneagar/celtic-platform.md |
| 35.8 KiB | .md |  |  | Cloudflare Full-Stack Repository Summary | docs/bonneagar/cloudflare-backpine-summary.md |
| 35.9 KiB | .md |  |  | Cloudflare Containers: Comprehensive Research Report | docs/bonneagar/cloudflare-containers-research.md |
| 40.3 KiB | .md |  |  | Cloudflare D1 - Comprehensive Research Report | docs/bonneagar/cloudflare-d1-research.md |
| 14.7 KiB | .md |  |  | Cloudflare API OpenAPI Specification Research | docs/bonneagar/cloudflare-openapi-specification-research.md |
| 40.9 KiB | .md |  |  | Cloudflare Tunnel: Comprehensive Research Report | docs/bonneagar/cloudflare-tunnel-research.md |
| 47.2 KiB | .md |  |  | Cloudflare Workers: Comprehensive Research Report | docs/bonneagar/cloudflare-workers-research.md |
| 11.5 KiB | .md |  |  | Cloudflare Developer Platform Expert | docs/bonneagar/cloudflare.md |
| 13.2 KiB | .md |  |  | Cognee: Entity Resolution and Knowledge Structuring | docs/bonneagar/cognee-entity-resolution.md |
| 31.3 KiB | .md |  |  | comparing approaches pangolin registration komodo deployment | docs/bonneagar/comparing-approaches-pangolin-registration-komodo-deployment.md |
| 667 B | .yaml | Y |  | compose | docs/bonneagar/compose.yaml |
| 2.7 KiB | .py |  |  | append the path to the root of the project | docs/bonneagar/crawlai_vs_firecrawl.py |
| 18.9 KiB | .py |  |  | crypto analysis example | docs/bonneagar/crypto_analysis_example.py |
| 22.7 KiB | .md |  |  | dagger docker compose workflow komodo periphery pangolin newt olm | docs/bonneagar/dagger-docker-compose-workflow-komodo-periphery-pangolin-newt-olm.md |
| 12.3 KiB | .md |  |  | Dagger Pipeline Implementation Checklist | docs/bonneagar/dagger-implementation-checklist.md |
| 26.9 KiB | .md |  |  | dagger pipeline orchestration komodo pangolin fullstack deployment | docs/bonneagar/dagger-pipeline-orchestration-komodo-pangolin-fullstack-deployment.md |
| 72.3 KiB | .md |  |  | Comprehensive Dagger Pipeline Orchestration | docs/bonneagar/dagger-unified-pipeline-architecture.md |
| 377.0 KiB | .md |  |  | Data Acquisition & Integrations | docs/bonneagar/data-acquisition.md |
| 13.8 KiB | .md | Y |  | Pangolin Debugging Assistant | docs/bonneagar/debug.md |
| 11.0 KiB | .py |  |  | demo multi config clean | docs/bonneagar/demo_multi_config_clean.py |
| 8.0 KiB | .md | Y |  | Pangolin Deployment Assistant | docs/bonneagar/deploy.md |
| 22.8 KiB | .md |  |  | deploying komodo periphery pangolin private access lancedb stack | docs/bonneagar/deploying-komodo-periphery-pangolin-private-access-lancedb-stack.md |
| 2.1 MiB | .md |  |  | Development Tools | docs/bonneagar/development-tools.md |
| 490 B | .yaml |  |  | docker compose(1) | docs/bonneagar/docker-compose(1).yaml |
| 16.1 KiB | .md |  |  | Docker Compose Patterns for AI Infrastructure | docs/bonneagar/docker-compose-patterns.md |
| 21.7 KiB | .py |  |  | docker hooks examples | docs/bonneagar/docker_hooks_examples.py |
| 1.2 KiB | .py |  |  | If jwt is enabled, authenticate first | docs/bonneagar/docker_python_sdk.py |
| 15.8 KiB | .py |  |  | docker webhook example | docs/bonneagar/docker_webhook_example.py |
| 18.2 KiB | .md |  |  | Document Processing Pipeline for Cryptocurrency Analytics | docs/bonneagar/document-processing-pipeline.md |
| 80.4 KiB | .md |  |  | Education Knowledge Graph | docs/bonneagar/education-kg.md |
| 13.0 KiB | .md |  |  | Irish Education Subject Data Inventory | docs/bonneagar/education-subject-inventory.md |
| 6.5 KiB | .py |  |  | embedding vs statistical | docs/bonneagar/embedding_vs_statistical.py |
| 113.4 KiB | .md |  |  | Platform Engineering | docs/bonneagar/engineering.md |
| 6.8 KiB | .md |  |  | Celtic Language Education Enrollment Statistics | docs/bonneagar/enrollment-statistics.md |
| 25.3 KiB | .md |  |  | extending komodo pr deploy pangolin integration komodo actions | docs/bonneagar/extending-komodo-pr-deploy-pangolin-integration-komodo-actions.md |
| 10.8 KiB | .md |  |  | Firecrawl OpenAPI Specification Research Report | docs/bonneagar/firecrawl-openapi-research.md |
| 20.2 KiB | .md |  |  | Frontend Integration for Crypto Analytics Platform | docs/bonneagar/frontend-integration.md |
| 10.7 KiB | .md |  |  | Frontend Stack for Irish Education Platform | docs/bonneagar/frontend-stack.md |
| 17.2 KiB | .md |  |  | Gaelic Heritage Digitization Pipeline | docs/bonneagar/gaelic-heritage-pipeline.md |
| 11.3 KiB | .md |  |  | Gaois API Reference | docs/bonneagar/gaois-api-reference.md |
| 29.0 KiB | .md |  |  | generating typescript client pangolin api openapi spec | docs/bonneagar/generating-typescript-client-pangolin-api-openapi-spec.md |
| 15.8 KiB | .md |  |  | Graph Visualization Tools and Patterns | docs/bonneagar/graph-visualization.md |
| 10.4 KiB | .md |  |  | Graphiti Adaptation for Cryptocurrency Analytics | docs/bonneagar/graphiti-crypto-adaptation.md |
| 13.8 KiB | .md |  |  | hosting lancedb docker compose | docs/bonneagar/hosting-lancedb-docker-compose.md |
| 15.4 KiB | .md |  |  | hosting litellm pangolin public vs private access models | docs/bonneagar/hosting-litellm-pangolin-public-vs-private-access-models.md |
| 7.9 KiB | .md | Y |  | Infisical Development Assistant | docs/bonneagar/infisical.md |
| 23.4 KiB | .md |  |  | Infrastructure & DevOps | docs/bonneagar/infrastructure-devops.md |
| 2.6 KiB | .md |  |  | Theme: Knowledge Graph Infrastructure & EdTech Backend | docs/bonneagar/infrastructure-knowledge-graph.md |
| 549.8 KiB | .md |  |  | Infrastructure Tools | docs/bonneagar/infrastructure-tools.md |
| 35.9 KiB | .md |  |  | integrating 1password cli connect komodo ansible deployment | docs/bonneagar/integrating-1password-cli-connect-komodo-ansible-deployment.md |
| 10.1 KiB | .md |  |  | integrating 1password cli komodo ansible deployment | docs/bonneagar/integrating-1password-cli-komodo-ansible-deployment.md |
| 40.2 KiB | .md |  |  | integrating dagger polyglot monorepo ci cd workflow | docs/bonneagar/integrating-dagger-polyglot-monorepo-ci-cd-workflow.md |
| 17.5 KiB | .md |  |  | Irish Educational Archives Workflow | docs/bonneagar/irish-archives-workflow.md |
| 8.2 KiB | .md |  |  | Irish (Gaeilge) Language AI Resources | docs/bonneagar/irish-nlp-resources.md |
| 33.4 KiB | .md |  |  | Knowledge Graph Infrastructure: Unified Architecture Guide | docs/bonneagar/knowledge-graph-infrastructure.md |
| 11.6 KiB | .md |  |  | Cryptocurrency Knowledge Graph Schema | docs/bonneagar/knowledge-graph-schema.md |
| 4.7 KiB | .md |  |  | Komodo (komo.do) API Summary | docs/bonneagar/komodo-api-summary.md |
| 14.5 KiB | .md |  |  | Komodo Deployment and Orchestration | docs/bonneagar/komodo-deployment.md |
| 13.4 KiB | .md |  |  | Komodo (komo.do) OpenAPI Research Report | docs/bonneagar/komodo-openapi-research.md |
| 23.9 KiB | .md |  |  | Komodo Infrastructure Management Skill | docs/bonneagar/komodo.md |
| 11.9 KiB | .md |  |  | Real-Time Open Data Lakehouse Architecture | docs/bonneagar/lakehouse-architecture.md |
| 5.3 KiB | .py |  |  | llm config example | docs/bonneagar/llm_config_example.py |
| 2.1 KiB | .py |  |  | llm extraction openai pricing | docs/bonneagar/llm_extraction_openai_pricing.py |
| 12.6 KiB | .md |  |  | MapLibre Visualization for Celtic Language Data | docs/bonneagar/maplibre-visualization.md |
| 14.9 KiB | .md |  |  | Metadata Control Plane: DuckDB-Backed Dynamic Source Management | docs/bonneagar/metadata-control-plane.md |
| 19.7 KiB | .md |  |  | Model Fine-Tuning Strategy for Cryptocurrency Domain | docs/bonneagar/model-finetuning-strategy.md |
| 35.9 KiB | .md |  |  | Monorepo Management Best Practices Research | docs/bonneagar/monorepo-best-practices-2025.md |
| 17.4 KiB | .md |  |  | Model Orchestration & Infrastructure | docs/bonneagar/orchestration-infrastructure.md |
| 331.2 KiB | .md |  |  | Cianfhoghlaim Platform Overview | docs/bonneagar/overview.md |
| 11.6 KiB | .md |  |  | Pan-Celtic Web Scraping Strategy | docs/bonneagar/pan-celtic-scraping.md |
| 10.9 KiB | .md |  |  | Pangolin OpenAPI Specification Research Report | docs/bonneagar/pangolin-openapi-specification-research.md |
| 25.1 KiB | .md |  |  | Pangolin Project: Patterns and Ontologies Deep Dive | docs/bonneagar/pangolin-patterns.md |
| 10.0 KiB | .md | Y |  | Pangolin Development Assistant | docs/bonneagar/pangolin.md |
| 7.5 KiB | .md |  |  | Parallel Corpus Sources for Irish-English | docs/bonneagar/parallel-corpus-sources.md |
| 8.3 KiB | .md |  |  | Celtic Language Education Policy Frameworks | docs/bonneagar/policy-frameworks.md |
| 62.1 KiB | .md |  |  | Pulumi Infrastructure as Code: Comprehensive Guide for LLMs | docs/bonneagar/pulumi-infrastructure-as-code.md |
| 18.3 KiB | .md |  |  | pulumi typescript guide provisioning cloudflare d1 r2 1password integration | docs/bonneagar/pulumi-typescript-guide-provisioning-cloudflare-d1-r2-1password-integration.md |
| 3.5 KiB | .md |  |  | Pulumi Infrastructure as Code | docs/bonneagar/pulumi.md |
| 11.6 KiB | .md | Y |  | Pulumi Infrastructure as Code Expert Skill | docs/bonneagar/pulumi_1.md |
| 9.4 KiB | .md |  |  | Scottish Gaelic AI Resources | docs/bonneagar/scottish-gaelic-resources.md |
| 4.7 KiB | .py |  |  | WebScrapingStrategy is now an alias for LXMLWebScrapingStrategy | docs/bonneagar/scraping_strategies_performance.py |
| 83.7 KiB | .md |  |  | Specialized Pipelines | docs/bonneagar/specialized-pipelines.md |
| 12.5 KiB | .md |  |  | Stealth Browser Infrastructure | docs/bonneagar/stealth-browser-stack.md |
| 12.4 KiB | .md |  |  | Subject-Specific Implementations | docs/bonneagar/subject-implementations.md |
| 1.7 KiB | .py |  |  | summarize page | docs/bonneagar/summarize_page.py |
| 8.4 KiB | .md |  |  | Celtic Language Teacher Supply Crisis | docs/bonneagar/teacher-supply.md |
| 79.5 KiB | .md |  |  | Technical Implementation | docs/bonneagar/technical-implementation.md |
| 7.1 KiB | .md | Y |  | Termix Development Assistant | docs/bonneagar/termix.md |
| 12.9 KiB | .md |  |  | TMX File Processing | docs/bonneagar/tmx-processing.md |
| 10.2 KiB | .md |  |  | Celtic Language AI - Unified Model Comparison | docs/bonneagar/unified-model-comparison.md |
| 525 B | .md |  |  | Update Specs | docs/bonneagar/update-specs.md |
| 10.4 KiB | .md |  |  | Vision-Language Models & OCR Systems Comparison | docs/bonneagar/vlm-ocr-comparison.md |
| 17.6 KiB | .md |  |  | Web Scraping & Automation | docs/bonneagar/web-scraping-automation.md |
| 45.7 KiB | .md |  |  | **The 2025 Composable SaaS Stack: An Expert Analysis of TanStack Start, Hono, Polar.sh, and Better-Auth** | docs/bonneagar/web-tech-tutorials-and-examples.md |
| 10.5 KiB | .md |  |  | Welsh (Cymraeg) AI Resources | docs/bonneagar/welsh-resources.md |
| 7.9 KiB | .md |  |  | where to install 1password cli op | docs/bonneagar/where-to-install-1password-cli-op.md |

### 5.3 docs/context

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 6.2 MiB | .pdf |  |  | 2602.15763v2 | docs/context/2602.15763v2.pdf |
| 351.5 KiB | .pdf |  |  | Apple Education and AI Goals | docs/context/Apple Education and AI Goals.pdf |
| 7.6 KiB | .md |  |  | Cianfhoghlaim Context Library | docs/context/INDEX.md |
| 289.9 KiB | .pdf |  |  | Irish Language Copyright and Education | docs/context/Irish Language Copyright and Education.pdf |
| 421.3 KiB | .pdf |  |  | Licensing and Government Opportunities | docs/context/Licensing and Government Opportunities.pdf |
| 15.2 MiB | .pdf |  |  | james hardiman library | docs/context/james_hardiman_library.pdf |
| 13.6 KiB | .md |  |  | Taisce - Modular Docker Stacks | docs/context/06-infrastructure/BONNEAGAR_OVERVIEW.md |
| 2.4 KiB | .md |  | G (5) | Meaisínfhoghlaim - ML Models | docs/context/06-infrastructure/ML_MODELS_REGISTRY.md |
| 2.1 KiB | .md |  |  | ML STACK | docs/context/06-infrastructure/ML_STACK.md |
| 37.8 KiB | .toml |  |  | auto deploy stacks | docs/context/06-infrastructure/auto-deploy-stacks.toml |
| 11.0 KiB | .yaml |  |  | Celtic Language ML Models Registry | docs/context/06-infrastructure/celtic_ml_models.yaml |
| 54.8 KiB | .yaml |  |  | =========================================================================== | docs/context/06-infrastructure/models_registry.yaml |
| 2.2 KiB | .md |  |  | Beads - AI-Native Issue Tracking | docs/context/08-examples/BEADS_TRACKER.md |
| 10.4 KiB | .md |  |  | Data Architecture for Irish Education Platform | docs/context/08-examples/DATA_ARCHITECTURE.md |
| 10.7 KiB | .md |  |  | Frontend Stack for Irish Education Platform | docs/context/08-examples/FRONTEND_STACK.md |
| 24.7 KiB | .md |  |  | Implementation Guide & Best Practices | docs/context/08-examples/IMPLEMENTATION_GUIDE.md |
| 19.7 KiB | .md |  |  | Model Fine-Tuning Strategy for Cryptocurrency Domain | docs/context/08-examples/MODEL_FINETUNING.md |
| 3.6 KiB | .md |  |  | Oideachais Pipeline Capability | docs/context/08-examples/OIDEACHAIS_SPEC.md |
| 2.5 KiB | .md |  |  | OpenSpec Instructions for Cianfhoghlaim | docs/context/08-examples/OPENSPEC_AGENTS.md |
| 12.4 KiB | .md |  |  | Subject-Specific Implementations | docs/context/08-examples/SUBJECT_IMPLEMENTATIONS.md |
| 29.6 KiB | .md |  |  | **Architectural Blueprint for a Bilingual EdTech Platform: Leveraging Edge Computing and WebAssembly for the Irish Leavi | docs/context/05-celtic-language/BILINGUAL_EDTECH.md |
| 29.0 KiB | .md |  |  | Celtic Languages AI Resources on HuggingFace | docs/context/05-celtic-language/CELTIC_AI_RESOURCES.md |
| 17.7 KiB | .md |  |  | Technical Architecture for a Bilingual Irish/English Mathematics Education System | docs/context/05-celtic-language/IRISH_ENGLISH_EDUCATION.md |
| 15.0 KiB | .md |  |  | Irish (Gaeilge) Language AI Resources on HuggingFace | docs/context/05-celtic-language/IRISH_HUGGINGFACE.md |
| 26.2 KiB | .md |  |  | DuckLake Unified Platform - Architecture Analysis | docs/context/05-celtic-language/LANGUAGE_ARCHITECTURE.md |
| 5.0 KiB | .md |  | G (3) | MODEL TRAINING | docs/context/05-celtic-language/MODEL_TRAINING.md |
| 25.5 KiB | .md |  |  | Agent-Related Implementations Analysis | docs/context/02-architecture/AGENT_IMPLEMENTATIONS.md |
| 9.0 KiB | .md |  |  | Aleyum Portfolio | docs/context/02-architecture/ALEYUM_PORTFOLIO.md |
| 18.2 KiB | .md |  |  | Document Processing Pipeline for Cryptocurrency Analytics | docs/context/02-architecture/DOCUMENT_PROCESSING.md |
| 35.8 KiB | .md |  |  | Data Stack Architecture Reference | docs/context/02-architecture/EDUCATION_ARCHITECTURE.md |
| 3.5 KiB | .md |  |  | Irish EdTech Platform Architecture | docs/context/02-architecture/IRISH_EDTECH.md |
| 51.7 KiB | .md |  |  | Comprehensive AI/ML Systems Architecture & Integration Guide | docs/context/02-architecture/ML_SYSTEMS.md |
| 47.4 KiB | .md |  |  | Building Production Multi-Agent Systems: Complete Implementation Guide | docs/context/02-architecture/MULTI_AGENT_PRODUCTION.md |
| 16.9 KiB | .md |  | G (6) | oideachais - Unified Celtic Education Platform | docs/context/02-architecture/OIDEACHAIS_PIPELINE.md |
| 3.9 KiB | .md |  |  | Sruth - Data Flows | docs/context/02-architecture/SRUTH_OVERVIEW.md |
| 34.1 KiB | .md |  |  | Tuath System Architecture | docs/context/02-architecture/TUATH_MMO.md |
| 8.7 KiB | .md |  |  | Pattern: Agent Design | docs/context/01-patterns/AGENTS.md |
| 13.1 KiB | .md |  |  | Pattern: BAML (Type-Safe LLM Extraction) | docs/context/01-patterns/BAML.md |
| 14.8 KiB | .md |  |  | Pattern: Data Pipeline (DLT → Dagster → CocoIndex) | docs/context/01-patterns/DATA_PIPELINE.md |
| 18.4 KiB | .md |  |  | Pattern: Embeddings (Batching, Models, Indexes) | docs/context/01-patterns/EMBEDDINGS.md |
| 15.7 KiB | .md |  |  | Pattern: Observability (Datadog, MLflow, Langfuse, Ragas) | docs/context/01-patterns/OBSERVABILITY.md |
| 15.2 KiB | .md |  |  | Pattern: Storage (DuckDB, LanceDB, DuckLake) | docs/context/01-patterns/STORAGE.md |
| 16.0 KiB | .md |  |  | Pattern: Web Frameworks (TanStack, AG-UI, MCP-UI) | docs/context/01-patterns/WEB.md |
| 13.8 KiB | .md |  |  | AI/ML Pipeline for Irish Education Platform | docs/context/03-pipelines/AI_ML_PIPELINE.md |
| 17.3 KiB | .py |  |  | ag ui protocol | docs/context/03-pipelines/ag_ui_protocol.py |
| 7.9 KiB | .py |  |  | api main | docs/context/03-pipelines/api_main.py |
| 20.5 KiB | .py |  |  | curriculum embedding | docs/context/03-pipelines/curriculum_embedding.py |
| 17.9 KiB | .py |  | G (7) | dagster definitions | docs/context/03-pipelines/dagster_definitions.py |
| 16.6 KiB | .py |  |  | dagster factories | docs/context/03-pipelines/dagster_factories.py |
| 7.5 KiB | .py |  |  | observability init | docs/context/03-pipelines/observability_init.py |
| 2.5 KiB | .py |  |  | storage init | docs/context/03-pipelines/storage_init.py |
| 2.2 KiB | .md |  |  | AG-UI — Agent-User Interaction Protocol (SSE) | docs/context/package-ecosystem/frontend/ag-ui.md |
| 2.4 KiB | .md |  |  | Babylon.js — 3D Web Rendering Engine | docs/context/package-ecosystem/frontend/babylonjs.md |
| 2.4 KiB | .md |  |  | CopilotKit — AI Agent UI Components | docs/context/package-ecosystem/frontend/copilotkit.md |
| 2.3 KiB | .md |  |  | Hono — Lightweight Web API Framework | docs/context/package-ecosystem/frontend/hono.md |
| 2.2 KiB | .md |  |  | TanStack Start — React Full-Stack Framework | docs/context/package-ecosystem/frontend/tanstack-start.md |
| 2.5 KiB | .md |  |  | Helsinki OPUS-MT — Celtic Language Pair Translation | docs/context/package-ecosystem/translation/helsinki-opus-mt.md |
| 2.3 KiB | .md |  |  | M2M-100 — Many-to-Many Multilingual Translation | docs/context/package-ecosystem/translation/m2m-100.md |
| 2.3 KiB | .md |  |  | NLLB-200 — 200-Language Neural Machine Translation | docs/context/package-ecosystem/translation/nllb-200.md |
| 2.4 KiB | .md |  |  | BGE-M3 — Multilingual Embedding Model | docs/context/package-ecosystem/embedding/bge-m3.md |
| 2.5 KiB | .md |  |  | ColPali — Visual Late-Interaction Document Retrieval | docs/context/package-ecosystem/embedding/colpali.md |
| 2.4 KiB | .md |  |  | GaBERT — Irish Language BERT Embedding Model | docs/context/package-ecosystem/embedding/gabert.md |
| 2.1 KiB | .md |  |  | Chatterbox — Text-to-Speech (TTS) | docs/context/package-ecosystem/speech/chatterbox.md |
| 2.3 KiB | .md |  |  | wav2vec2-XLSR-Irish — Irish Speech Recognition | docs/context/package-ecosystem/speech/wav2vec2-xlsr-irish.md |
| 2.3 KiB | .md |  |  | Whisper / faster-whisper — Speech Recognition (ASR) | docs/context/package-ecosystem/speech/whisper-faster-whisper.md |
| 2.1 KiB | .md |  |  | Cloudflare R2 — Zero-Egress Object Storage SDK | docs/context/package-ecosystem/storage/cloudflare-r2.md |
| 2.2 KiB | .md |  |  | DuckDB — Embedded Analytical Database | docs/context/package-ecosystem/storage/duckdb.md |
| 2.1 KiB | .md |  |  | DuckLake — Lightweight Data Lakehouse on Object Storage | docs/context/package-ecosystem/storage/ducklake.md |
| 2.1 KiB | .md |  |  | Neo4j Python Driver — Graph Database SDK | docs/context/package-ecosystem/storage/neo4j.md |
| 2.3 KiB | .md |  |  | LoRA / QLoRA — Parameter-Efficient Fine-Tuning | docs/context/package-ecosystem/fine-tuning/lora-qlora.md |
| 2.0 KiB | .md |  |  | Modal — Serverless GPU Cloud | docs/context/package-ecosystem/fine-tuning/modal.md |
| 2.3 KiB | .md |  |  | TRL — Transformer Reinforcement Learning (HuggingFace) | docs/context/package-ecosystem/fine-tuning/trl.md |
| 2.1 KiB | .md |  |  | Unsloth — Efficient LLM Fine-Tuning | docs/context/package-ecosystem/fine-tuning/unsloth.md |
| 2.3 KiB | .md |  |  | Crawl4AI — AI-Powered Web Crawling SDK | docs/context/package-ecosystem/browser/crawl4ai-sdk.md |
| 2.3 KiB | .md |  |  | Patchright — Stealth Browser Automation | docs/context/package-ecosystem/browser/patchright.md |
| 2.5 KiB | .md |  |  | Stagehand — AI Browser Operator (Python SDK) | docs/context/package-ecosystem/browser/stagehand.md |
| 2.2 KiB | .md |  |  | CocoIndex — Data Transformation Pipeline SDK | docs/context/package-ecosystem/orchestration/cocoindex.md |
| 2.4 KiB | .md |  |  | Dagster Python SDK — Data Orchestration Framework | docs/context/package-ecosystem/orchestration/dagster-sdk.md |
| 2.3 KiB | .md |  |  | dlt — Data Load Tool (Python SDK) | docs/context/package-ecosystem/orchestration/dlt.md |
| 2.3 KiB | .md |  |  | SQLMesh — Data Transformation Framework | docs/context/package-ecosystem/orchestration/sqlmesh.md |
| 2.3 KiB | .md |  |  | Cognee Python SDK — GraphRAG Memory System | docs/context/package-ecosystem/memory-kg/cognee-sdk.md |
| 2.3 KiB | .md |  |  | Graphiti Python SDK — Temporal Knowledge Graph | docs/context/package-ecosystem/memory-kg/graphiti-sdk.md |
| 2.2 KiB | .md |  |  | Agno — Multi-Agent Orchestration Framework | docs/context/package-ecosystem/ai-frameworks/agno.md |
| 2.4 KiB | .md |  |  | BAML — Type-Safe LLM Extraction DSL | docs/context/package-ecosystem/ai-frameworks/baml.md |
| 2.1 KiB | .md |  |  | Google ADK — Agent Development Kit | docs/context/package-ecosystem/ai-frameworks/google-adk.md |
| 2.3 KiB | .md |  |  | Pydantic AI — Agent Framework with Structured Validation | docs/context/package-ecosystem/ai-frameworks/pydantic-ai.md |
| 2.3 KiB | .md |  |  | RAGAS — RAG Evaluation Framework | docs/context/package-ecosystem/ai-frameworks/ragas.md |
| 11.0 KiB | .md |  |  | Cianfhoghlaim - AI Agent Instructions | docs/context/00-core/CLAUDE.md |
| 7.4 KiB | .md |  |  | Critical Constraints | docs/context/00-core/CONSTRAINTS.md |
| 2.9 KiB | .md |  |  | Cianfhoghlaim Project Conventions | docs/context/00-core/PROJECT_SPEC.md |
| 49.0 KiB | .md |  |  | Model Context Protocol (MCP) - Comprehensive Research Report | docs/context/04-agents/MCP_RESEARCH.md |
| 25.0 KiB | .md |  |  | **Technical Blueprint for a Next-Generation Leaving Certificate Education Platform: Architecture, Pedagogy, and Implemen | docs/context/04-agents/TECH_STACK.md |
| 3.2 KiB | .md |  |  | Tuath Celtic Educational MMO - Quick Start | docs/context/04-agents/TUATH_QUICKSTART.md |
| 7.5 KiB | .py |  |  | browser orchestrator | docs/context/04-agents/browser_orchestrator.py |
| 11.1 KiB | .py |  |  | browser session | docs/context/04-agents/browser_session.py |
| 15.7 KiB | .py |  |  | durable orchestrator | docs/context/04-agents/durable_orchestrator.py |
| 11.2 KiB | .md | Y |  | Agno - AI Agent Framework | docs/context/07-skills/agno.md |
| 16.3 KiB | .md | Y |  | BAML - Type-Safe LLM Development | docs/context/07-skills/baml.md |
| 6.5 KiB | .md | Y |  | Celtic Language AI/ML Resources | docs/context/07-skills/celtic-language-ai.md |
| 25.7 KiB | .md | Y |  | CocoIndex | docs/context/07-skills/cocoindex.md |
| 13.2 KiB | .md | Y |  | Dagster - Modern Data Orchestration | docs/context/07-skills/dagster.md |
| 11.2 KiB | .md | Y |  | dlt - Data Load Tool | docs/context/07-skills/dlt.md |
| 8.7 KiB | .md | Y |  | DuckDB - In-Process Analytical Database | docs/context/07-skills/duckdb.md |
| 4.5 KiB | .md | Y |  | Graphiti | docs/context/07-skills/graphiti.md |
| 8.5 KiB | .md | Y |  | LanceDB - Embedded Vector Database | docs/context/07-skills/lancedb.md |
| 9.2 KiB | .md | Y |  | Memgraph - High-Performance Graph Database | docs/context/07-skills/memgraph.md |
| 4.5 KiB | .md | Y | G (6) | Oideachas Pipeline | docs/context/07-skills/oideachas-pipeline.md |
| 10.8 KiB | .md | Y |  | TanStack Start - Full-Stack React Framework | docs/context/07-skills/tanstack-start.md |

### 5.4 docs/data_engineering

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 40.0 KiB | .docx |  |  | 21109422 universal junior cycle short course scoping document ga | docs/data_engineering/21109422_universal-junior-cycle-short-course-scoping-document_ga.docx |
| 35.8 KiB | .md |  |  | Data Stack Architecture Reference | docs/data_engineering/ARCHITECTURE.md |
| 18.7 KiB | .md |  |  | DLT (Data Load Tool) — Complete Reference Guide | docs/data_engineering/DLT_COMPLETE_GUIDE.md |
| 8.1 KiB | .md | Y |  | FIBO Hackathon | docs/data_engineering/FIBO Hackathon.md |
| 26.8 KiB | .md |  |  | **Architecting Agentic Creative Workflows: Deep Research into Generative AI Integration for React Ecosystems** | docs/data_engineering/Generative AI Art Workflow Integration.md |
| 4.1 KiB | .md |  |  | Data Engineering — Research Index | docs/data_engineering/INDEX.md |
| 31.5 KiB | .md |  |  | **Architectural Convergence: BAML, CocoIndex, Cognee, and Graphiti in Temporal Ontology Engineering** | docs/data_engineering/Ontology and Temporal Graphs Research.md |
| 10.4 KiB | .md | Y |  | Feast Expert Assistant | docs/data_engineering/assistant.md |
| 643.4 KiB | .md |  |  | CocoIndex Comprehensive Guide | docs/data_engineering/cocoindex-comprehensive.md |
| 492.7 KiB | .md |  |  | Dagster Comprehensive Guide | docs/data_engineering/dagster-comprehensive.md |
| 504.8 KiB | .md |  |  | Data Architecture Reference | docs/data_engineering/data-architecture.md |
| 18.5 KiB | .md |  |  | Data Pipeline Architecture | docs/data_engineering/data-pipeline-architecture.md |
| 8.4 KiB | .md |  |  | Geospatial Data Sources for Celtic Language Mapping | docs/data_engineering/data-sources.md |
| 268.8 KiB | .md |  |  | Data Versioning Reference | docs/data_engineering/data-versioning.md |
| 270.2 KiB | .md |  |  | dlt (Data Load Tool) Comprehensive Guide | docs/data_engineering/dlt-comprehensive.md |
| 129.9 KiB | .md |  |  | DuckDB Reference | docs/data_engineering/duckdb-reference.md |
| 167.5 KiB | .md |  |  | GeoAI Reference | docs/data_engineering/geoai-reference.md |
| 8.5 KiB | .md | Y |  | Initialize LanceDB in Project | docs/data_engineering/init.md |
| 204.0 KiB | .md |  |  | Knowledge Systems Reference | docs/data_engineering/knowledge-systems.md |
| 113.8 KiB | .md |  |  | LanceDB Reference | docs/data_engineering/lancedb-reference.md |
| 56.5 KiB | .md |  |  | Marimo Reference | docs/data_engineering/marimo-reference.md |
| 8.4 KiB | .md | Y |  | pandas to Ibis Migration Assistant | docs/data_engineering/migrate.md |
| 6.1 KiB | .md | Y |  | Ibis Query Builder Assistant | docs/data_engineering/query.md |
| 6.9 KiB | .md | Y |  | LanceDB Quick Reference | docs/data_engineering/quickref.md |
| 266.1 KiB | .md |  |  | Semantic Layer Reference | docs/data_engineering/semantic-layer-reference.md |
| 47.4 KiB | .md |  |  | Building Production Multi-Agent Systems: Complete Implementation Guide | docs/data_engineering/stage-3-production-multi-agent-systems.md |
| 824.1 KiB | .md |  |  | Tool Ecosystem Reference | docs/data_engineering/tool-ecosystem.md |
| 90.3 KiB | .md |  |  | Transformers.js | docs/data_engineering/transformers.md |

### 5.5 docs/meaisínfhoghlaim

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 7.8 KiB | .md |  | G (6) | Meaisínfhoghlaim (Machine Learning) - AI Agent Instructions | docs/meaisínfhoghlaim/AGENTS.md |
| 28.6 KiB | .md |  |  | **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Structured Extraction wi | docs/meaisínfhoghlaim/AI Chemistry Education Image Generation.md |
| 36.3 KiB | .md |  |  | **Bria Fibo and the Hugging Face Ecosystem: Architecting Educational Visualization Pipelines via Structured JSON Synthes | docs/meaisínfhoghlaim/AI Syllabus to JSON Schema.md |
| 33.1 KiB | .md |  |  | AI Memory, Agents & Knowledge Management | docs/meaisínfhoghlaim/AI_MEMORY.md |
| 20.9 KiB | .md |  |  | Comprehensive Analysis of HuggingFace Examples Directory | docs/meaisínfhoghlaim/ANALYSIS_SUMMARY.md |
| 36.8 KiB | .md |  |  | **Architectural Due Diligence: Scaling the Crypteolas Agentic PaaS** | docs/meaisínfhoghlaim/Agentic Crypto Platform Scaling Research.md |
| 15.5 KiB | .md | Y |  | Auto Optimize Pydantic Models for Structured Information Extraction  A Complete Guide to DSPydantic | docs/meaisínfhoghlaim/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md |
| 32.2 KiB | .md |  |  | **Unified Schema Architecture for Agentic AI Systems: Integrating BAML, dlt, and TanStack AI across Multi-Modal Data Lay | docs/meaisínfhoghlaim/BAML, DLT, and AI Workflow Integration.md |
| 14.3 KiB | .md | Y |  | Blaizzy mlx vlm  MLX VLM is a package for inference and fine tuning of Vision Language Models (VLMs) on your Mac using M | docs/meaisínfhoghlaim/Blaizzy_mlx-vlm_ MLX-VLM is a package for inference and fine-tuning of Vision Language Models (VLMs) on your Mac using MLX..md |
| 32.4 KiB | .md |  |  | **Architectural Blueprint for Autonomous Agentic Tutoring Systems: Integrating Hybrid Knowledge Graphs, Temporal Reasoni | docs/meaisínfhoghlaim/Building an Agentic Tutor.md |
| 3.6 KiB | .md | Y | G (5) | Call for papers  A special edition of TEANGA on corpus linguistics in an Irish language context | docs/meaisínfhoghlaim/Call for papers_ A special edition of TEANGA on corpus linguistics in an Irish-language context.md |
| 37.8 KiB | .md |  |  | **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architecture for Next-Generatio | docs/meaisínfhoghlaim/Chemistry Education Asset Generation.md |
| 26.5 KiB | .md | Y |  | Datasets Guide   Unsloth Documentation | docs/meaisínfhoghlaim/Datasets Guide _ Unsloth Documentation.md |
| 33.1 KiB | .md |  |  | **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device | docs/meaisínfhoghlaim/Federated AI Marketplace on iPhone.md |
| 26.3 KiB | .md | Y |  | Federated RAG Tutorial  Build Privacy Preserving LLM Systems in Python ⬩OpenMined | docs/meaisínfhoghlaim/Federated RAG Tutorial_ Build Privacy-Preserving LLM Systems in Python ⬩OpenMined.md |
| 15.2 KiB | .md | Y |  | Fine tuning LLMs Guide   Unsloth Documentation | docs/meaisínfhoghlaim/Fine-tuning LLMs Guide _ Unsloth Documentation.md |
| 32.2 KiB | .md |  |  | **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supe | docs/meaisínfhoghlaim/Fine-tuning VLMs for iOS HTR.md |
| 25.0 KiB | .md |  |  | **Deep Research Report: End-to-End Fine-Tuning of Qwen3-VL for Historic Manuscript Transcription using Unsloth, MLflow,  | docs/meaisínfhoghlaim/Finetuning Qwen3-VL for Gaelic OCR.md |
| 8.4 KiB | .md | Y |  | Gaelic in the Digital Age  Inside the ÈIST Project – Gaelic Algorithmic Research Group | docs/meaisínfhoghlaim/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md |
| 10.4 KiB | .md | Y |  | Google ADK with LiteLLM   liteLLM | docs/meaisínfhoghlaim/Google ADK with LiteLLM _ liteLLM.md |
| 26.8 KiB | .md | Y |  | How to Run and Deploy LLMs on your iOS or Android Phone   Unsloth Documentation | docs/meaisínfhoghlaim/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md |
| 24.7 KiB | .md |  |  | Implementation Guide & Best Practices | docs/meaisínfhoghlaim/IMPLEMENTATION_GUIDE.md |
| 5.2 KiB | .md |  |  | Meaisínfhoghlaim — Machine Learning Research Index | docs/meaisínfhoghlaim/INDEX.md |
| 39.2 KiB | .md |  |  | **Architectural Convergence: Orchestrating Skyvern, Crawl4AI, and Stagehand for Semantic Web Mapping and Data Extraction | docs/meaisínfhoghlaim/Integrating Skyvern with Crawl4AI_Stagehand.md |
| 52.3 KiB | .md | Y |  | Interactions API   Gemini API   Google AI for Developers | docs/meaisínfhoghlaim/Interactions API _ Gemini API _ Google AI for Developers.md |
| 30.7 KiB | .md |  |  | **Architectural Convergence: The Agentic Pipeline for Structured Generative AI** | docs/meaisínfhoghlaim/Interactive AI Pipeline Development.md |
| 10.3 KiB | .md | Y |  | Introducing AnyLanguageModel  One API for Local and Remote LLMs on Apple Platforms | docs/meaisínfhoghlaim/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md |
| 9.6 KiB | .md | Y |  | Introducing Bolmo  Byteifying the next generation of language models   Ai2 | docs/meaisínfhoghlaim/Introducing Bolmo_ Byteifying the next generation of language models _ Ai2.md |
| 33.2 KiB | .md |  |  | **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework for Deploying Irish | docs/meaisínfhoghlaim/Irish LLM for iPhone Development.md |
| 32.7 KiB | .md |  |  | **Advanced Architectures for Document Intelligence on Apple Silicon: A Comprehensive Analysis of PaddleOCR v3, Docling,  | docs/meaisínfhoghlaim/LLM and OCR Deployment Research.md |
| 6.2 KiB | .md | Y |  | LLM based TTS models | docs/meaisínfhoghlaim/LLM based TTS models.md |
| 1.9 KiB | .md | Y |  | LiteLLM   Pydantic Logfire Documentation | docs/meaisínfhoghlaim/LiteLLM - Pydantic Logfire Documentation.md |
| 20.2 KiB | .md | Y |  | LoRA Hyperparameters Guide   Unsloth Documentation | docs/meaisínfhoghlaim/LoRA Hyperparameters Guide _ Unsloth Documentation.md |
| 26.9 KiB | .md |  |  | **Convergent Local Intelligence: Architecting High-Fidelity Multi-Modal Document Workflows on Apple Silicon** | docs/meaisínfhoghlaim/Local macOS MLX_MPS LLM Workflow.md |
| 11.8 KiB | .md | Y |  | Ministral 3   How to Run Guide   Unsloth Documentation | docs/meaisínfhoghlaim/Ministral 3 - How to Run Guide _ Unsloth Documentation.md |
| 32.4 KiB | .md |  |  | **Architecting a Sovereign Multimodal Neuro-Symbolic System for the Preservation and Generative Synthesis of Irish Cultu | docs/meaisínfhoghlaim/Multimodal Irish Handwriting Generation Model.md |
| 34.3 KiB | .md |  |  | **Architectural Blueprint for the Neuro-Symbolic Gaeilge Engine: Integrating InkSpire Diffusion Architectures with Sover | docs/meaisínfhoghlaim/Neuro-Symbolic Translation Model Training.md |
| 5.6 KiB | .md | Y |  | New in llama.cpp  Model Management | docs/meaisínfhoghlaim/New in llama.cpp_ Model Management.md |
| 25.2 KiB | .md |  |  | **The Semantic Frontier: A Comprehensive Architectural Analysis of Provider-Agnostic Document Intelligence Pipelines for | docs/meaisínfhoghlaim/Open-Source VLMs For PDF Extraction.md |
| 13.2 KiB | .md | Y |  | Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray | docs/meaisínfhoghlaim/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md |
| 11.2 KiB | .md | Y |  | Prompt Optimization (Beta)(2) | docs/meaisínfhoghlaim/Prompt Optimization (Beta)(2).md |
| 11.2 KiB | .md | Y |  | Prompt Optimization (Beta)(3) | docs/meaisínfhoghlaim/Prompt Optimization (Beta)(3).md |
| 11.2 KiB | .md | Y |  | Prompt Optimization (Beta) | docs/meaisínfhoghlaim/Prompt Optimization (Beta).md |
| 9.9 KiB | .md | Y |  | Pydantic AI Gateway   Pydantic AI | docs/meaisínfhoghlaim/Pydantic AI Gateway - Pydantic AI.md |
| 8.4 KiB | .md |  |  | Quick Reference Guide: OCR Models & Integration | docs/meaisínfhoghlaim/QUICK_REFERENCE.md |
| 9.0 KiB | .md | Y |  | Quantization Aware Training (QAT)   Unsloth Documentation | docs/meaisínfhoghlaim/Quantization-Aware Training (QAT) _ Unsloth Documentation.md |
| 2.4 KiB | .md |  | G (5) | Meaisínfhoghlaim - ML Models | docs/meaisínfhoghlaim/README.md |
| 9.2 KiB | .md |  |  | Gaeilge Research - Organized Collection | docs/meaisínfhoghlaim/README_1.md |
| 10.1 KiB | .md |  |  | HuggingFace OCR & Vision-Language Models - Complete Analysis | docs/meaisínfhoghlaim/README_ANALYSIS.md |
| 2.0 KiB | .md |  |  | Research Analysis & Centralization Plan | docs/meaisínfhoghlaim/RESEARCH_CONSOLIDATION_PLAN.md |
| 35.9 KiB | .md |  |  | **Architectural Blueprint for an Intelligent, British Curriculum-Aligned Interactive Exam Builder** | docs/meaisínfhoghlaim/React Drag-and-Drop for Exam Builder.md |
| 32.3 KiB | .md |  |  | **Strategic Resource Maximization: Architecting the Celtic Heritage Intelligence Platform (CHIP)** | docs/meaisínfhoghlaim/Resource Maximization and Project Planning.md |
| 34.0 KiB | .md |  |  | **Architecting the Sovereign AI Stack: A Comprehensive Analysis of Integrating Llama.cpp, MLX-VLM, Docling, Llama-Swap,  | docs/meaisínfhoghlaim/Setting Up Local LLM Services on Mac.md |
| 12.6 KiB | .md | Y |  | Streaming datasets  100x More Efficient | docs/meaisínfhoghlaim/Streaming datasets_ 100x More Efficient.md |
| 32.0 KiB | .md | Y |  | Supercharge your OCR Pipelines with Open Models | docs/meaisínfhoghlaim/Supercharge your OCR Pipelines with Open Models.md |
| 10.4 KiB | .md | Y |  | Swift Transformers Reaches 1.0 – and Looks to the Future | docs/meaisínfhoghlaim/Swift Transformers Reaches 1.0 – and Looks to the Future.md |
| 27.8 KiB | .md | Y |  | Tokenization in Transformers v5  Simpler, Clearer, and More Modular | docs/meaisínfhoghlaim/Tokenization in Transformers v5_ Simpler, Clearer, and More Modular.md |
| 7.3 KiB | .md | Y |  | Train a tiny model to generate 3D files (v2) through example diversification | docs/meaisínfhoghlaim/Train a tiny model to generate 3D files (v2) through example diversification.md |
| 7.1 KiB | .md | Y |  | Unsloth Model Catalog   Unsloth Documentation(1) | docs/meaisínfhoghlaim/Unsloth Model Catalog _ Unsloth Documentation(1).md |
| 7.1 KiB | .md | Y |  | Unsloth Model Catalog   Unsloth Documentation | docs/meaisínfhoghlaim/Unsloth Model Catalog _ Unsloth Documentation.md |
| 34.8 KiB | .md |  |  | **Optimizing Open-Weights Large Language Models for Celtic Linguistics, Educational Analytics, and Multimodal Asset Gene | docs/meaisínfhoghlaim/Unsloth Models for Celtic Datasets.md |
| 17.1 KiB | .md | Y |  | We Got Claude to Fine Tune an Open Source LLM | docs/meaisínfhoghlaim/We Got Claude to Fine-Tune an Open Source LLM.md |
| 4.5 KiB | .md | Y |  | What Model Should I Use for Fine tuning    Unsloth Documentation | docs/meaisínfhoghlaim/What Model Should I Use for Fine-tuning_ _ Unsloth Documentation.md |
| 9.5 KiB | .md | Y |  | ag ui sdks community kotlin at main · ag ui protocol ag ui | docs/meaisínfhoghlaim/ag-ui_sdks_community_kotlin at main · ag-ui-protocol_ag-ui.md |
| 12.1 KiB | .md |  |  | Agent Patterns, MCP, and Autonomous Systems | docs/meaisínfhoghlaim/agent-patterns-reference.md |
| 3.4 KiB | .md |  | G (6) | agent patterns | docs/meaisínfhoghlaim/agent-patterns.md |
| 60.3 KiB | .md |  |  | **A Strategic Blueprint for a Polyglot AI & Data Platform** | docs/meaisínfhoghlaim/ai-compute-allocation-strategy.md |
| 51.7 KiB | .md |  |  | Comprehensive AI/ML Systems Architecture & Integration Guide | docs/meaisínfhoghlaim/ai-ml-systems-consolidated.md |
| 6.9 KiB | .md | Y |  | apple ml fastvlm  This repository contains the official implementation of  FastVLM  Efficient Vision Encoding for Vision | docs/meaisínfhoghlaim/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md |
| 636.4 KiB | .md |  | G (4) | celtic language ai | docs/meaisínfhoghlaim/celtic-language-ai.md |
| 29.2 KiB | .py |  |  | -*- coding: utf-8 -*- | docs/meaisínfhoghlaim/deepseek_ocr_(3b)_eval.py |
| 12.3 KiB | .md |  |  | Document Processing & OCR: VLM, OCR, and Heritage Digitization | docs/meaisínfhoghlaim/document-processing-reference.md |
| 11.8 KiB | .md |  |  | Dual-Engine Graph + Complementary LLM Serving Integration | docs/meaisínfhoghlaim/dual-engine-graph-llm-serving-integration.md |
| 7.6 KiB | .py |  |  | Local development | docs/meaisínfhoghlaim/ducklake_explorer.py |
| 4.2 KiB | .md |  | G (5) | fine tuning guide | docs/meaisínfhoghlaim/fine-tuning-guide.md |
| 20.7 KiB | .md |  |  | Comprehensive LLM Fine-Tuning Reference | docs/meaisínfhoghlaim/fine-tuning-reference.md |
| 2.1 KiB | .md |  |  | GGUF | docs/meaisínfhoghlaim/gguf.md |
| 12.5 KiB | .md |  |  | GPU Experiment Guide: Reproducing & Improving Celtic Language Models | docs/meaisínfhoghlaim/gpu_experiment_guide.md |
| 68.6 KiB | .md |  |  | Hugging Face Design Patterns and Best Practices: Comprehensive Analysis | docs/meaisínfhoghlaim/huggingface-design-patterns-analysis.md |
| 23.4 KiB | .md |  |  | Hugging Face Ontologies, Taxonomies, and Data Structures | docs/meaisínfhoghlaim/huggingface-ontologies-research.md |
| 11.6 KiB | .md |  |  | Hugging Face Expert | docs/meaisínfhoghlaim/huggingface.md |
| 32.0 KiB | .md |  |  | **Strategic Architecture for Converged Agentic Ecosystems: Integrating iOS Vision Intelligence with Cross-Platform Devel | docs/meaisínfhoghlaim/iOS App Development Ecosystem Strategy.md |
| 12.3 KiB | .py |  |  | irish tts finetune | docs/meaisínfhoghlaim/irish_tts_finetune.py |
| 119.3 KiB | .md |  |  | Langfuse LLM Observability Platform - Comprehensive Research | docs/meaisínfhoghlaim/langfuse-guide.md |
| 14.3 KiB | .md | Y |  | langfuse ragas | docs/meaisínfhoghlaim/langfuse_ragas.md |
| 103.3 KiB | .md |  |  | LiteLLM API Patterns and Usage Conventions - Comprehensive Research | docs/meaisínfhoghlaim/litellm-comprehensive-guide.md |
| 15.8 KiB | .md |  |  | LiteLLM Proxy - Deployment & Operations Guide | docs/meaisínfhoghlaim/litellm-deployment-guide.md |
| 16.9 KiB | .yaml |  |  | LiteLLM Configuration File | docs/meaisínfhoghlaim/litellm_config.yaml |
| 28.7 KiB | .md | Y |  | madroidmaq mlx omni server | docs/meaisínfhoghlaim/madroidmaq_mlx-omni-server.md |
| 2.5 KiB | .md | Y |  | mlflow (dagster mlflow)   Dagster Docs | docs/meaisínfhoghlaim/mlflow (dagster-mlflow) _ Dagster Docs.md |
| 58.1 KiB | .md |  |  | MLflow LLM Features Reference Documentation | docs/meaisínfhoghlaim/mlflow-llm-guide.md |
| 36.0 KiB | .md |  |  | MLflow Model Registry and Deployment Reference | docs/meaisínfhoghlaim/mlflow-model-registry-deployment-reference.md |
| 20.4 KiB | .md | Y |  | mlflow ragas | docs/meaisínfhoghlaim/mlflow_ragas.md |
| 278.4 KiB | .md |  | G (6) | model ecosystem | docs/meaisínfhoghlaim/model-ecosystem.md |
| 9.7 KiB | .md |  |  | Model Serving & Inference on Apple Silicon & Local Hardware | docs/meaisínfhoghlaim/model-serving-guide.md |
| 4.5 KiB | .md |  | G (7) | model serving | docs/meaisínfhoghlaim/model-serving.md |
| 19.0 KiB | .md |  |  | MotherDuck's DuckDB MCP Server | docs/meaisínfhoghlaim/motherduck_mcp.md |
| 310.0 KiB | .md |  | G (5) | noteuook catalog | docs/meaisínfhoghlaim/notebook-catalog.md |
| 4.3 KiB | .md |  |  | notebooklm 1 | docs/meaisínfhoghlaim/notebooklm_1.md |
| 3.0 KiB | .md |  | G (6) | ocr reference | docs/meaisínfhoghlaim/ocr-reference.md |
| 3.4 KiB | .md | Y |  | syft flwr notebooks fedrag README.md at main · OpenMined syft flwr | docs/meaisínfhoghlaim/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md |
| 359.3 KiB | .md |  | G (6) | training pipeline | docs/meaisínfhoghlaim/training-pipeline.md |
| 90.3 KiB | .md |  |  | Transformers.js | docs/meaisínfhoghlaim/transformers.md |

### 5.6 docs/teanga

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 29.3 KiB | .md |  |  | **Architecting the Neuro-Symbolic Gaeilge Engine: A Technical Blueprint for Agentic Knowledge Extraction and Preservatio | docs/teanga/AI Agents for Irish Language Resources.md |
| 28.6 KiB | .md |  |  | **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Structured Extraction wi | docs/teanga/AI Chemistry Education Image Generation.md |
| 7.6 KiB | .md | Y |  | AI Partner Catalyst  Accelerate Innovation | docs/teanga/AI Partner Catalyst_ Accelerate Innovation.md |
| 26.2 KiB | .md |  |  | DuckLake Unified Platform - Architecture Analysis | docs/teanga/ARCHITECTURE_ANALYSIS.md |
| 32.6 KiB | .md |  |  | **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Educational Hub** | docs/teanga/Agentic Education Platform Development.md |
| 31.4 KiB | .md |  |  | **The Neuro-Symbolic Agentic Translation Architecture: A Comprehensive Blueprint Leveraging T5Gemma-2, Gemini 3, Google  | docs/teanga/Agentic Translation Workflow Technologies.md |
| 31.9 KiB | .md |  |  | **Autonomous Web Intelligence Architecture: A Comprehensive Implementation Framework for Agentic Scraping and Reconstruc | docs/teanga/Agentic Web Scraping Pipeline.md |
| 30.3 KiB | .md |  |  | **Automated Weakly-Supervised Alignment of Historical Gaelic Manuscripts: A Pipeline for Fine-Tuning Qwen2-VL using ColP | docs/teanga/Aligning Gaelic Script for QwenVL Finetuning.md |
| 37.4 KiB | .md |  |  | **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms** | docs/teanga/Asset Management for Full-Stack App.md |
| 15.5 KiB | .md | Y |  | Auto Optimize Pydantic Models for Structured Information Extraction  A Complete Guide to DSPydantic | docs/teanga/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md |
| 30.5 KiB | .md |  |  | **Semantic Indexing and Knowledge Graph Architecture for the Irish Education System: A Comprehensive Technical Implement | docs/teanga/BAML Schemas for Irish Education.md |
| 30.1 KiB | .md |  |  | **Architecting the Adaptive Classroom: A Technical Blueprint for Agentic Educational Systems Using Agno, Restate, and BA | docs/teanga/BAML for Syllabus-Driven Data Extraction.md |
| 32.2 KiB | .md |  |  | **Unified Schema Architecture for Agentic AI Systems: Integrating BAML, dlt, and TanStack AI across Multi-Modal Data Lay | docs/teanga/BAML, DLT, and AI Workflow Integration.md |
| 30.3 KiB | .md |  |  | **ARCHITECTURAL CONVERGENCE FOR DETERMINISTIC AGENTIC SYSTEMS: INTEGRATING BAML, GRAPHITI, AND TANSTACK AI WITHIN THE IR | docs/teanga/BAML, Graphiti, Tanstack AI Pipeline.md |
| 35.7 KiB | .md |  |  | **Backend Architecture Strategy for a Bilingual Temporal Knowledge Graph in Mathematics Education** | docs/teanga/Backend Strategy For Educational Tutoring System.md |
| 9.0 KiB | .md | Y |  | BritLLM | docs/teanga/BritLLM.md |
| 47.5 KiB | .md |  |  | **The State of Education and Celtic Language Revitalisation in the British Isles: Demographic Shifts, Fiscal Realities,  | docs/teanga/British Isles Celtic Language Education Data.md |
| 33.2 KiB | .md |  |  | **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report** | docs/teanga/British Isles Education Map.md |
| 29.6 KiB | .md |  |  | **Architectural Blueprint for a Bilingual EdTech Platform: Leveraging Edge Computing and WebAssembly for the Irish Leavi | docs/teanga/Building Bilingual EdTech Platform.md |
| 29.0 KiB | .md |  |  | Celtic Languages AI Resources on HuggingFace | docs/teanga/CELTIC_LANGUAGES_AI_RESOURCES.md |
| 40.5 KiB | .md |  |  | **Computational Archiving of Celtic Digital Heritage: An Exhaustive Analysis of Skyvern Integration and Pan-Celtic Resou | docs/teanga/Celtic Data Scraping and Integration Plan.md |
| 41.0 KiB | .md |  |  | **Unified Computational Infrastructure for Celtic Languages: Data Integration, Educational Analytics, and Strategic Mode | docs/teanga/Celtic Language Data Aggregation & Analysis.md |
| 40.0 KiB | .md |  |  | **Celtic-Bench: A Comprehensive Technical and Linguistic Analysis of Educational Data Architectures for the Construction | docs/teanga/Celtic Language Educational Data Scrape.md |
| 34.6 KiB | .md |  |  | **Automated Paleography and Visual Document Understanding for the Celtic Languages: A Comprehensive Framework for Fine-T | docs/teanga/Celtic Language OCR Resource Analysis.md |
| 37.8 KiB | .md |  |  | **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architecture for Next-Generatio | docs/teanga/Chemistry Education Asset Generation.md |
| 28.4 KiB | .md | Y |  | ChromeDevTools chrome devtools mcp  Chrome DevTools for coding agents | docs/teanga/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md |
| 18.6 KiB | .md | Y |  | Digital Resources for the Languages in Ireland and Britain(1) | docs/teanga/Digital Resources for the Languages in Ireland and Britain(1).md |
| 18.6 KiB | .md | Y |  | Digital Resources for the Languages in Ireland and Britain | docs/teanga/Digital Resources for the Languages in Ireland and Britain.md |
| 37.9 KiB | .md |  |  | **High-Fidelity Pedagogical Simulation: A Comprehensive Framework for Automating Scientifically Accurate Educational Vis | docs/teanga/Educational Game Dev Pipeline.md |
| 25.0 KiB | .md |  |  | **Technical Blueprint for a Next-Generation Leaving Certificate Education Platform: Architecture, Pedagogy, and Implemen | docs/teanga/Educational Website Tech Stack.md |
| 41.5 KiB | .md |  |  | **The Convergence of Diffusion Generative Models and Agentic Workflows: A Paradigm Shift for Low-Resource Neural Machine | docs/teanga/Enhancing English-Irish Translation with Diffusion Models.md |
| 5.1 KiB | .md | Y |  | Explore data with marimo   dlt Docs | docs/teanga/Explore data with marimo _ dlt Docs.md |
| 32.2 KiB | .md |  |  | **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supe | docs/teanga/Fine-tuning VLMs for iOS HTR.md |
| 25.0 KiB | .md |  |  | **Deep Research Report: End-to-End Fine-Tuning of Qwen3-VL for Historic Manuscript Transcription using Unsloth, MLflow,  | docs/teanga/Finetuning Qwen3-VL for Gaelic OCR.md |
| 19.2 KiB | .md | Y |  | From BI to AI  A Modern Lakehouse Stack with Lance and Iceberg | docs/teanga/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md |
| 34.3 KiB | .md |  |  | **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction** | docs/teanga/Frontend Idea Catalog Development.md |
| 8.4 KiB | .md | Y |  | Gaelic in the Digital Age  Inside the ÈIST Project – Gaelic Algorithmic Research Group | docs/teanga/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md |
| 33.1 KiB | .md |  |  | **Converging High-Fidelity Pre-Rendering and Database-Driven State: A Comprehensive Technical Blueprint for Next-Generat | docs/teanga/Game Dev Pipeline Research & Plan.md |
| 38.5 KiB | .md |  |  | **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem** | docs/teanga/Game Development Research & AI Integration.md |
| 31.2 KiB | .md |  | G (5) | **Convergence of Spatial Analytics and Digital Folkloristics: A Technical and Theoretical Examination of *Hidden Heritag | docs/teanga/Geospatial Data Analysis and DuckDB.md |
| 25.9 KiB | .md |  |  | **Modernizing Educational Geospatial Intelligence: A Comprehensive Architectural Analysis of Ibis, DuckDB, GeoParquet, a | docs/teanga/Geospatial Data Visualization with Ibis.md |
| 29.8 KiB | .md |  |  | **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP and WebGPU Rendering f | docs/teanga/Geospatial Workflow & Particle Effects(1).md |
| 10.4 KiB | .md | Y |  | Google ADK with LiteLLM   liteLLM | docs/teanga/Google ADK with LiteLLM _ liteLLM.md |
| 35.7 KiB | .md |  |  | **Architectural Unification of Agentic Memory: Synthesizing Cognee, Cocoindex, and Graphiti within High-Performance Grap | docs/teanga/Graph Tech Integration and Recommendation.md |
| 25.7 KiB | .md |  |  | **Advanced Architectures for Bilingual Heritage Archiving and Mathematical Document Intelligence: A Deep Research Report | docs/teanga/Handwriting Recognition and Dataset Creation.md |
| 3.1 KiB | .md |  |  | docs/teanga — Celtic Language AI Reference Library | docs/teanga/INDEX.md |
| 27.2 KiB | .md |  |  | **The Converged Lakehouse: Architecting a Multimodal Data Environment with Lance Namespace and the Composable Stack** | docs/teanga/Ibis, LanceDB, and Data Stack Integration.md |
| 8.4 KiB | .md | Y | G (4) | Iceberg in the Browser | docs/teanga/Iceberg in the Browser.md |
| 36.6 KiB | .md |  |  | **Architecting the Real-Time Open Data Lakehouse: A Comprehensive Technical Analysis of Integrating OLake, Lakekeeper, a | docs/teanga/Integrating Olake, Lakekeeper, RisingWave.md |
| 33.1 KiB | .md |  |  | **Architectural Synthesis of Sovereign Game State: Integrating SpacetimeDB, DuckDB WASM, TanStack Start, and CopilotKit* | docs/teanga/Integrating Rust, DuckDB, TanStack, CopilotKit.md |
| 28.7 KiB | .md |  |  | **Architecting the Isomorphic AI Tutor: A Comprehensive Research Report on Integrating TanStack AI, BAML, and LiteLLM** | docs/teanga/Integrating TanStack AI with LiteLLM.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the British Isles** | docs/teanga/Interactive Map & AI Agents.md |
| 32.9 KiB | .md |  |  | **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analysis of MLX, Llama.cp | docs/teanga/Irish Handwriting App Development.md |
| 33.2 KiB | .md |  |  | **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework for Deploying Irish | docs/teanga/Irish LLM for iPhone Development.md |
| 27.2 KiB | .md |  |  | **Architectural & Curricular Analysis: Digital Transformation of Leaving Certificate Prescribed Materials** | docs/teanga/Leaving Certificate Material App.md |
| 32.4 KiB | .md |  |  | **Architecting a Sovereign Multimodal Neuro-Symbolic System for the Preservation and Generative Synthesis of Irish Cultu | docs/teanga/Multimodal Irish Handwriting Generation Model.md |
| 34.3 KiB | .md |  |  | **Architectural Blueprint for the Neuro-Symbolic Gaeilge Engine: Integrating InkSpire Diffusion Architectures with Sover | docs/teanga/Neuro-Symbolic Translation Model Training.md |
| 7.0 KiB | .md | Y |  | PlanetScale   MotherDuck Docs | docs/teanga/PlanetScale _ MotherDuck Docs.md |
| 13.2 KiB | .md | Y |  | Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1) | docs/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1).md |
| 13.2 KiB | .md | Y |  | Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray | docs/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md |
| 29.0 KiB | .md |  |  | Celtic Languages AI Resources on HuggingFace | docs/teanga/RESOURCES.md |
| 33.1 KiB | .md |  |  | **Technical Feasibility Study: Archival and Organization of Irish Language Audio Corpora (Teanglann.ie & Canuint.ie)** | docs/teanga/Scraping Irish Audio Files.md |
| 3.3 KiB | .md | Y |  | Using MotherDuck with PlanetScale — PlanetScale | docs/teanga/Using MotherDuck with PlanetScale — PlanetScale.md |
| 10.1 KiB | .md |  |  | Parallel Education Data Sources for the British Isles | docs/teanga/british_isles_parallel_data_sources.md |
| 9.0 KiB | .md | Y |  | datasets BritLLM | docs/teanga/datasets-BritLLM.md |
| 10.1 KiB | .md |  |  | Parallel Education Data Sources for the British Isles | docs/teanga/datasets-british_isles_parallel_data_sources.md |
| 36.1 KiB | .md |  |  | Irish-English Bilingual Dataset Creation: Technical Research Outline | docs/teanga/datasets-irish_bilingual_dataset_research.md |
| 47.0 KiB | .md |  |  | gaeilge | docs/teanga/gaeilge.md |
| 1.2 KiB | .md |  |  | Changelog | docs/teanga/gaois-DuchasAPI-docs-CHANGELOG.md |
| 54.7 KiB | .md |  | G (6) | Dúchas Application Programming Interface (Version 0.5): Data dictionary | docs/teanga/gaois-DuchasAPI-docs-DATADICT.md |
| 27.6 KiB | .md |  | G (6) | Dúchas Application Programming Interface (Version 0.5): Developer documentation | docs/teanga/gaois-DuchasAPI-docs-README.md |
| 1.5 KiB | .md |  |  | Issues to be addressed | docs/teanga/gaois-DuchasAPI-docs-TODO.md |
| 1.2 KiB | .md |  |  | Gaois.Localizer | docs/teanga/gaois-Gaois.Localizer-README.md |
| 2.7 KiB | .md |  |  | Gaois.QueryLogger | docs/teanga/gaois-Gaois.QueryLogger-README.md |
| 1.1 KiB | .md |  |  | gaois GeoNames2Sql LICENSE | docs/teanga/gaois-GeoNames2Sql-LICENSE.md |
| 441 B | .md |  |  | GeoNames2Sql | docs/teanga/gaois-GeoNames2Sql-README.md |
| 672 B | .md |  |  | IrishSurnameIndex | docs/teanga/gaois-IrishSurnameIndex-README.md |
| 4.0 KiB | .md |  |  | KCG_SUMMARY: Gaois — Irish Language Digital Infrastructure (DCU) | docs/teanga/gaois-KCG_SUMMARY.md |
| 606 B | .md |  |  | Changelog | docs/teanga/gaois-LogainmAPI-docs-CHANGELOG.md |
| 23.3 KiB | .md |  |  | Logainm Application Programming Interface (Version 0.9): Data dictionary | docs/teanga/gaois-LogainmAPI-docs-DATADICT.md |
| 2.4 KiB | .md |  |  | API Design Decisions | docs/teanga/gaois-LogainmAPI-docs-DECISIONS.md |
| 15.8 KiB | .md |  |  | Logainm Application Programming Interface (Version 0.9): Developer documentation | docs/teanga/gaois-LogainmAPI-docs-README.md |
| 595 B | .md |  | G (60) | Nationalist | docs/teanga/gaois-Nationalist-README.md |
| 12 B | .md |  |  | PublicDocs | docs/teanga/gaois-PublicDocs-README.md |
| 31.0 KiB | .md |  |  | The Data Structure of the National Folklore Collection *Main Manuscript Collection* | docs/teanga/gaois-PublicDocs-cbe-xml-documentation.md |
| 204 B | .md |  | G (40) | téarma.ie | docs/teanga/gaois-Tearma-README.md |
| 978 B | .md |  |  | Browse | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-brabhsail.en.md |
| 1.0 KiB | .md |  | G (96) | Brabhsáil | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-brabhsail.ga.md |
| 1.1 KiB | .md |  |  | What is a term? | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cad-is-tearma.en.md |
| 1.3 KiB | .md |  | G (94) | Cad is téarma ann? | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cad-is-tearma.ga.md |
| 481 B | .md |  |  | How to use the site | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-conas-usaid.en.md |
| 532 B | .md |  | G (79) | Conas an suíomh a úsáid | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-conas-usaid.ga.md |
| 2.8 KiB | .md |  | G (3) | How to use Advanced Search | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-casta.en.md |
| 3.4 KiB | .md |  | G (92) | Conas an Cuardach Casta a úsáid | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-casta.ga.md |
| 2.7 KiB | .md |  |  | Quick Search | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-tapa.en.md |
| 3.0 KiB | .md |  | G (85) | An Cuardach Tapa | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-tapa.ga.md |
| 796 B | .md |  |  | I didn’t find what I was looking for | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-gan-toradh.en.md |
| 832 B | .md |  | G (72) | Níor aimsigh mé a raibh uaim | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-gan-toradh.ga.md |
| 4.9 KiB | .md |  |  | Understanding search results | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-torthai-a-thuiscint.en.md |
| 5.5 KiB | .md |  | G (66) | Conas na torthaí cuardaigh a thuiscint | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-torthai-a-thuiscint.ga.md |
| 7.3 KiB | .md |  |  | About the Content | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-abhar.en.md |
| 7.5 KiB | .md |  | G (94) | Eolas Faoin Ábhar | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-abhar.ga.md |
| 1.8 KiB | .md |  |  | The Terminology Committee | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-coiste.en.md |
| 2.0 KiB | .md |  | G (82) | An Coiste Téarmaíochta | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-coiste.ga.md |
| 6.3 KiB | .md |  |  | Link between téarma.ie and the New Corpus for Ireland | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-corpus.en.md |
| 7.0 KiB | .md |  | G (78) | An ceangal idir téarma.ie agus Nua-Chorpas na hÉireann | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-corpus.ga.md |
| 2.9 KiB | .md |  |  | Data protection information | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-cosaint-sonrai.en.md |
| 3.6 KiB | .md |  | G (99) | Eolas cosanta sonraí | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-cosaint-sonrai.ga.md |
| 3.0 KiB | .md |  | G (8) | The History of focal.ie/téarma.ie | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-stair.en.md |
| 3.1 KiB | .md |  | G (65) | Stair focal.ie/téarma.ie | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-stair.ga.md |
| 1.8 KiB | .md |  |  | The téarma.ie project | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-tionscadal.en.md |
| 1.9 KiB | .md |  | G (64) | Tionscadal téarma.ie | docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-tionscadal.ga.md |
| 594 B | .md |  | G (25) | Documental | docs/teanga/gaois-documental-README.md |
| 4.2 KiB | .md | Y |  | gaois documental docs software documental deployment.en | docs/teanga/gaois-documental-docs-software-documental-deployment.en.md |
| 4.6 KiB | .md | Y | G (50) | gaois documental docs software documental deployment.ga | docs/teanga/gaois-documental-docs-software-documental-deployment.ga.md |
| 10.9 KiB | .md | Y |  | gaois documental docs software documental developers.en | docs/teanga/gaois-documental-docs-software-documental-developers.en.md |
| 12.6 KiB | .md | Y | G (50) | gaois documental docs software documental developers.ga | docs/teanga/gaois-documental-docs-software-documental-developers.ga.md |
| 9.1 KiB | .md | Y |  | gaois documental docs software documental editors.en | docs/teanga/gaois-documental-docs-software-documental-editors.en.md |
| 10.4 KiB | .md | Y | G (56) | gaois documental docs software documental editors.ga | docs/teanga/gaois-documental-docs-software-documental-editors.ga.md |
| 1.2 KiB | .md | Y |  | gaois documental docs software documental intro.en | docs/teanga/gaois-documental-docs-software-documental-intro.en.md |
| 1.5 KiB | .md | Y | G (43) | gaois documental docs software documental intro.ga | docs/teanga/gaois-documental-docs-software-documental-intro.ga.md |
| 7.4 KiB | .md | Y |  | gaois documental docs software geonames2sql index.en | docs/teanga/gaois-documental-docs-software-geonames2sql-index.en.md |
| 8.3 KiB | .md | Y | G (53) | gaois documental docs software geonames2sql index.ga | docs/teanga/gaois-documental-docs-software-geonames2sql-index.ga.md |
| 20.5 KiB | .md | Y |  | gaois documental docs software localizer index.en | docs/teanga/gaois-documental-docs-software-localizer-index.en.md |
| 23.3 KiB | .md | Y | G (46) | gaois documental docs software localizer index.ga | docs/teanga/gaois-documental-docs-software-localizer-index.ga.md |
| 5.3 KiB | .md | Y |  | gaois documental docs software querylogger v0.7 configuration.en | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-configuration.en.md |
| 6.2 KiB | .md | Y | G (52) | gaois documental docs software querylogger v0.7 configuration.ga | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-configuration.ga.md |
| 2.6 KiB | .md | Y |  | gaois documental docs software querylogger v0.7 data.en | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-data.en.md |
| 2.9 KiB | .md | Y | G (71) | gaois documental docs software querylogger v0.7 data.ga | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-data.ga.md |
| 2.2 KiB | .md | Y |  | gaois documental docs software querylogger v0.7 faulttolerance.en | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-faulttolerance.en.md |
| 2.5 KiB | .md | Y | G (52) | gaois documental docs software querylogger v0.7 faulttolerance.ga | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-faulttolerance.ga.md |
| 3.4 KiB | .md | Y |  | gaois documental docs software querylogger v0.7 intro.en | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-intro.en.md |
| 3.9 KiB | .md | Y | G (40) | gaois documental docs software querylogger v0.7 intro.ga | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-intro.ga.md |
| 7.2 KiB | .md | Y |  | gaois documental docs software querylogger v0.7 net461.en | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-net461.en.md |
| 8.1 KiB | .md | Y | G (22) | gaois documental docs software querylogger v0.7 net461.ga | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-net461.ga.md |
| 8.3 KiB | .md | Y |  | gaois documental docs software querylogger v0.7 netcore.en | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-netcore.en.md |
| 9.2 KiB | .md | Y | G (22) | gaois documental docs software querylogger v0.7 netcore.ga | docs/teanga/gaois-documental-docs-software-querylogger-v0.7-netcore.ga.md |
| 6.2 KiB | .md | Y |  | gaois documental docs software terminologue configuration.en | docs/teanga/gaois-documental-docs-software-terminologue-configuration.en.md |
| 7.2 KiB | .md | Y | G (21) | gaois documental docs software terminologue configuration.ga | docs/teanga/gaois-documental-docs-software-terminologue-configuration.ga.md |
| 3.8 KiB | .md | Y |  | gaois documental docs software terminologue installation.en | docs/teanga/gaois-documental-docs-software-terminologue-installation.en.md |
| 4.5 KiB | .md | Y | G (38) | gaois documental docs software terminologue installation.ga | docs/teanga/gaois-documental-docs-software-terminologue-installation.ga.md |
| 1.3 KiB | .md | Y |  | gaois documental docs software terminologue intro.en | docs/teanga/gaois-documental-docs-software-terminologue-intro.en.md |
| 2.0 KiB | .md | Y | G (23) | gaois documental docs software terminologue intro.ga | docs/teanga/gaois-documental-docs-software-terminologue-intro.ga.md |
| 13.1 KiB | .md | Y |  | gaois documental docs software terminologue source code.en | docs/teanga/gaois-documental-docs-software-terminologue-source-code.en.md |
| 16.2 KiB | .md | Y | G (21) | gaois documental docs software terminologue source code.ga | docs/teanga/gaois-documental-docs-software-terminologue-source-code.ga.md |
| 14.1 KiB | .md | Y | G (36) | gaois documental docs software terminologue tbx export.ga | docs/teanga/gaois-documental-docs-software-terminologue-tbx-export.ga.md |
| 2.4 KiB | .md | Y | G (34) | gaois documental docs software terminologue tbx import.ga | docs/teanga/gaois-documental-docs-software-terminologue-tbx-import.ga.md |
| 2.4 KiB | .md | Y | G (48) | gaois documental docs software terminologue txt export.ga | docs/teanga/gaois-documental-docs-software-terminologue-txt-export.ga.md |
| 64 B | .md |  |  | gaoisalign | docs/teanga/gaois-gaoisalign-README.md |
| 1.5 KiB | .md |  |  | Screenful | docs/teanga/gaois-screenful-README.md |
| 6.0 KiB | .md |  | G (3) | Database of Irish-Language Surnames | docs/teanga/gaois-sloinnte-README.md |
| 533 B | .md |  |  | Terminologue | docs/teanga/gaois-terminologue-README.md |
| 160 B | .md |  |  | gaois terminologue docs configuring | docs/teanga/gaois-terminologue-docs-configuring.md |
| 144 B | .md |  |  | gaois terminologue docs index | docs/teanga/gaois-terminologue-docs-index.md |
| 3.8 KiB | .md |  |  | Om *Terminologue* | docs/teanga/gaois-terminologue-docs-info.nb.md |
| 158 B | .md |  |  | gaois terminologue docs installation | docs/teanga/gaois-terminologue-docs-installation.md |
| 13.6 KiB | .md |  |  | Kjapp innføring i Terminologue | docs/teanga/gaois-terminologue-docs-intro.nb.md |
| 156 B | .md |  |  | gaois terminologue docs sourcecode | docs/teanga/gaois-terminologue-docs-sourcecode.md |
| 129 B | .md |  |  | gaois terminologue shared README | docs/teanga/gaois-terminologue-shared-README.md |
| 5.1 KiB | .md |  |  | حول Terminologue | docs/teanga/gaois-terminologue-website-docs-info.ar.md |
| 4.3 KiB | .md |  | G (6) | Sobre *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.ca.md |
| 4.0 KiB | .md |  |  | Ynghylch *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.cy.md |
| 4.2 KiB | .md |  |  | Über *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.de.md |
| 6.0 KiB | .md |  |  | Σχετικά με το *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.el.md |
| 4.8 KiB | .md |  |  | About *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.en.md |
| 4.3 KiB | .md |  | G (11) | Acerca de *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.es.md |
| 3.4 KiB | .md |  | G (4) | *Terminologue*-ri buruz | docs/teanga/gaois-terminologue-website-docs-info.eu.md |
| 4.1 KiB | .md |  |  | Tietoa *Terminologuesta* | docs/teanga/gaois-terminologue-website-docs-info.fi.md |
| 4.6 KiB | .md |  | G (12) | À propos de Terminologue | docs/teanga/gaois-terminologue-website-docs-info.fr.md |
| 5.6 KiB | .md |  | G (54) | Maidir le *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.ga.md |
| 3.9 KiB | .md |  |  | O *Terminologueu* | docs/teanga/gaois-terminologue-website-docs-info.hr.md |
| 4.2 KiB | .md |  |  | Apie *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.lt.md |
| 4.1 KiB | .md |  |  | Om *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.nb.md |
| 4.1 KiB | .md |  |  | Over *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.nl.md |
| 5.6 KiB | .md |  |  | О *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.ru.md |
| 4.0 KiB | .md |  |  | Om *Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.sv.md |
| 4.3 KiB | .md |  |  | *Terminologue* Hakkında | docs/teanga/gaois-terminologue-website-docs-info.tr.md |
| 4.3 KiB | .md |  |  | 關於*Terminologue* | docs/teanga/gaois-terminologue-website-docs-info.zh.md |
| 21.5 KiB | .md |  |  | مقدمة لطيفة لـبرنامج Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.ar.md |
| 15.9 KiB | .md |  | G (10) | Introducció senzilla a Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.ca.md |
| 13.6 KiB | .md |  |  | Cyflwyniad cryno i Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.cy.md |
| 15.7 KiB | .md |  |  | Behutsame Einführung in Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.de.md |
| 28.3 KiB | .md |  |  | Ευγενική εισαγωγή στο Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.el.md |
| 13.8 KiB | .md |  |  | Gentle introduction to Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.en.md |
| 15.6 KiB | .md |  | G (30) | Sencilla iniciación a Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.es.md |
| 15.0 KiB | .md |  |  | Terminologuerako sarrera arina | docs/teanga/gaois-terminologue-website-docs-intro.eu.md |
| 13.5 KiB | .md |  |  | Terminologuen lyhyt esittely | docs/teanga/gaois-terminologue-website-docs-intro.fi.md |
| 19.7 KiB | .md |  | G (8) | Brève introduction à Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.fr.md |
| 17.3 KiB | .md |  | G (64) | Treoir úsáideora Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.ga.md |
| 13.9 KiB | .md |  |  | Uvod u Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.hr.md |
| 14.4 KiB | .md |  |  | Trumpas įvadas į *Terminologue* | docs/teanga/gaois-terminologue-website-docs-intro.lt.md |
| 13.6 KiB | .md |  |  | Kjapp innføring i Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.nb.md |
| 14.5 KiB | .md |  |  | Korte inleiding tot Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.nl.md |
| 25.0 KiB | .md |  |  | Знакомство с Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.ru.md |
| 14.1 KiB | .md |  |  | Kort introduktion till Terminologue | docs/teanga/gaois-terminologue-website-docs-intro.sv.md |
| 16.1 KiB | .md |  |  | Terminologue'a kısa bir giriş | docs/teanga/gaois-terminologue-website-docs-intro.tr.md |
| 12.3 KiB | .md |  |  | Terminologue簡介 | docs/teanga/gaois-terminologue-website-docs-intro.zh.md |
| 4.4 KiB | .md |  |  | Terminologue Offline Processor | docs/teanga/gaois-terminologue-website-docs-top.en.md |
| 1.5 KiB | .md |  |  | Screenful | docs/teanga/gaois-terminologue-website-libs-screenful-README.md |
| 267 B | .md |  |  | Xonomy | docs/teanga/gaois-terminologue-website-libs-xonomy-README.md |
| 47.5 KiB | .md |  |  | **The State of Education and Celtic Language Revitalisation in the British Isles: Demographic Shifts, Fiscal Realities,  | docs/teanga/geoai-British Isles Celtic Language Education Data.md |
| 33.2 KiB | .md |  |  | **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report** | docs/teanga/geoai-British Isles Education Map.md |
| 31.2 KiB | .md |  | G (5) | **Convergence of Spatial Analytics and Digital Folkloristics: A Technical and Theoretical Examination of *Hidden Heritag | docs/teanga/geoai-Geospatial Data Analysis and DuckDB.md |
| 25.9 KiB | .md |  |  | **Modernizing Educational Geospatial Intelligence: A Comprehensive Architectural Analysis of Ibis, DuckDB, GeoParquet, a | docs/teanga/geoai-Geospatial Data Visualization with Ibis.md |
| 29.8 KiB | .md |  |  | **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP and WebGPU Rendering f | docs/teanga/geoai-Geospatial Workflow & Particle Effects(1).md |
| 25.7 KiB | .md |  |  | **Advanced Architectures for Bilingual Heritage Archiving and Mathematical Document Intelligence: A Deep Research Report | docs/teanga/handwriting-Handwriting Recognition and Dataset Creation.md |
| 32.9 KiB | .md |  |  | **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analysis of MLX, Llama.cp | docs/teanga/handwriting-Irish Handwriting App Development.md |
| 32.4 KiB | .md |  |  | **Architecting a Sovereign Multimodal Neuro-Symbolic System for the Preservation and Generative Synthesis of Irish Cultu | docs/teanga/handwriting-Multimodal Irish Handwriting Generation Model.md |
| 17.7 KiB | .md |  |  | Technical Architecture for a Bilingual Irish/English Mathematics Education System | docs/teanga/irish-english-education.md |
| 47.0 KiB | .md |  |  | irish gaeilge | docs/teanga/irish-gaeilge.md |
| 15.0 KiB | .md |  |  | Irish (Gaeilge) Language AI Resources on HuggingFace | docs/teanga/irish-irish_gaeilge_huggingface_resources.md |
| 36.1 KiB | .md |  |  | Irish-English Bilingual Dataset Creation: Technical Research Outline | docs/teanga/irish_bilingual_dataset_research.md |
| 15.0 KiB | .md |  |  | Irish (Gaeilge) Language AI Resources on HuggingFace | docs/teanga/irish_gaeilge_huggingface_resources.md |
| 710 B | .md |  |  | kscanne 1070 README | docs/teanga/kscanne-1070-README.md |
| 632 B | .md |  |  | kscanne 2100 README | docs/teanga/kscanne-2100-README.md |
| 297 B | .md |  |  | 2300 | docs/teanga/kscanne-2300-README.md |
| 87 B | .md |  |  | 5750 | docs/teanga/kscanne-5750-README.md |
| 567 B | .md |  |  | kscanne 5755 README | docs/teanga/kscanne-5755-README.md |
| 5.2 KiB | .md |  |  | Hyphenator.js | docs/teanga/kscanne-Hyphenator-README.md |
| 603 B | .md |  |  | kscanne Irish Dependency Treebank README | docs/teanga/kscanne-Irish-Dependency-Treebank-README.md |
| 317 B | .md |  |  | kscanne Irish Universal Dependency Treebank README | docs/teanga/kscanne-Irish-Universal-Dependency-Treebank-README.md |
| 2.9 KiB | .md |  |  | KCG_SUMMARY: kscanne — Irish NLP Tools Repository | docs/teanga/kscanne-KCG_SUMMARY.md |
| 368 B | .md |  |  | Contributing | docs/teanga/kscanne-UD_Irish-IDT-CONTRIBUTING.md |
| 1.1 KiB | .md |  |  | kscanne beach README | docs/teanga/kscanne-beach-README.md |
| 43 B | .md |  | G (90) | cadhan.com | docs/teanga/kscanne-cadhan.com-README.md |
| 1.4 KiB | .md |  |  | kscanne chichewa README | docs/teanga/kscanne-chichewa-README.md |
| 1.0 KiB | .md |  |  | kscanne crubadan transliterate README | docs/teanga/kscanne-crubadan-transliterate-README.md |
| 2.0 KiB | .md |  | G (12) | An Crúbadán - Web | docs/teanga/kscanne-crubadan.web-README.md |
| 4.2 KiB | .md |  | G (14) | An Crúbadán - clld | docs/teanga/kscanne-crubadan_clld-README.md |
| 376 B | .md |  |  | fst | docs/teanga/kscanne-fst-README.md |
| 1.5 KiB | .md |  |  | fulah-wordlist | docs/teanga/kscanne-fulah-wordlist-README.md |
| 2.0 KiB | .md |  | G (7) | kscanne gbb README | docs/teanga/kscanne-gbb-README.md |
| 78 B | .md |  |  | kscanne gbb classification author README | docs/teanga/kscanne-gbb-classification-author-README.md |
| 79 B | .md |  |  | kscanne gbb classification dialect README | docs/teanga/kscanne-gbb-classification-dialect-README.md |
| 78 B | .md |  |  | kscanne gbb classification gender README | docs/teanga/kscanne-gbb-classification-gender-README.md |
| 98 B | .md |  |  | kscanne gbb classification native README | docs/teanga/kscanne-gbb-classification-native-README.md |
| 75 B | .md |  |  | kscanne gbb classification sentiment README | docs/teanga/kscanne-gbb-classification-sentiment-README.md |
| 87 B | .md |  |  | kscanne gbb classification topic README | docs/teanga/kscanne-gbb-classification-topic-README.md |
| 1.5 KiB | .md |  |  | kscanne gbb datasets bli README | docs/teanga/kscanne-gbb-datasets-bli-README.md |
| 1.8 KiB | .md |  |  | kscanne gbb datasets blogspot README | docs/teanga/kscanne-gbb-datasets-blogspot-README.md |
| 3.2 KiB | .md |  |  | kscanne gbb datasets charles README | docs/teanga/kscanne-gbb-datasets-charles-README.md |
| 3.6 KiB | .md |  |  | kscanne gbb datasets errors README | docs/teanga/kscanne-gbb-datasets-errors-README.md |
| 3.6 KiB | .md |  | G (10) | kscanne gbb datasets inscne README | docs/teanga/kscanne-gbb-datasets-inscne-README.md |
| 1.7 KiB | .md |  |  | kscanne gbb datasets iudt README | docs/teanga/kscanne-gbb-datasets-iudt-README.md |
| 4.3 KiB | .md |  |  | kscanne gbb datasets sentiment README | docs/teanga/kscanne-gbb-datasets-sentiment-README.md |
| 2.8 KiB | .md |  |  | kscanne gbb datasets topaic README | docs/teanga/kscanne-gbb-datasets-topaic-README.md |
| 3.1 KiB | .md |  |  | kscanne gbb datasets tuairisc README | docs/teanga/kscanne-gbb-datasets-tuairisc-README.md |
| 2.0 KiB | .md |  |  | kscanne gbb datasets twittirish README | docs/teanga/kscanne-gbb-datasets-twittirish-README.md |
| 78 B | .md |  |  | kscanne gbb generation conversation README | docs/teanga/kscanne-gbb-generation-conversation-README.md |
| 74 B | .md |  |  | kscanne gbb generation lm README | docs/teanga/kscanne-gbb-generation-lm-README.md |
| 75 B | .md |  |  | kscanne gbb generation qa README | docs/teanga/kscanne-gbb-generation-qa-README.md |
| 3.8 KiB | .md |  |  | kscanne gbb proofing diacritics README | docs/teanga/kscanne-gbb-proofing-diacritics-README.md |
| 73 B | .md |  |  | kscanne gbb proofing grammar README | docs/teanga/kscanne-gbb-proofing-grammar-README.md |
| 88 B | .md |  |  | kscanne gbb proofing mutations README | docs/teanga/kscanne-gbb-proofing-mutations-README.md |
| 71 B | .md |  |  | kscanne gbb proofing ocr README | docs/teanga/kscanne-gbb-proofing-ocr-README.md |
| 78 B | .md |  |  | kscanne gbb proofing standardization README | docs/teanga/kscanne-gbb-proofing-standardization-README.md |
| 65 B | .md |  |  | kscanne gbb syntax chunking README | docs/teanga/kscanne-gbb-syntax-chunking-README.md |
| 77 B | .md |  |  | kscanne gbb syntax constituency README | docs/teanga/kscanne-gbb-syntax-constituency-README.md |
| 75 B | .md |  |  | kscanne gbb syntax dependency README | docs/teanga/kscanne-gbb-syntax-dependency-README.md |
| 81 B | .md |  |  | kscanne gbb tagging codeswitch README | docs/teanga/kscanne-gbb-tagging-codeswitch-README.md |
| 70 B | .md |  |  | kscanne gbb tagging lemmatization README | docs/teanga/kscanne-gbb-tagging-lemmatization-README.md |
| 81 B | .md |  |  | kscanne gbb tagging ner README | docs/teanga/kscanne-gbb-tagging-ner-README.md |
| 728 B | .md |  |  | kscanne gbb tagging pos README | docs/teanga/kscanne-gbb-tagging-pos-README.md |
| 90 B | .md |  |  | kscanne gbb translation en README | docs/teanga/kscanne-gbb-translation-en-README.md |
| 98 B | .md |  |  | kscanne gbb translation gd README | docs/teanga/kscanne-gbb-translation-gd-README.md |
| 95 B | .md |  |  | kscanne gbb translation gv README | docs/teanga/kscanne-gbb-translation-gv-README.md |
| 84 B | .md |  |  | kscanne gbb translation lexicon README | docs/teanga/kscanne-gbb-translation-lexicon-README.md |
| 4.1 KiB | .md |  | G (7) | kscanne gramadoir API | docs/teanga/kscanne-gramadoir-API.md |
| 481 B | .md |  | G (26) | kscanne grammatach README | docs/teanga/kscanne-grammatach-README.md |
| 795 B | .md |  |  | hunspell-rw | docs/teanga/kscanne-hunspell-rw-README.md |
| 64 B | .md |  |  | kscanne itweets geodata README | docs/teanga/kscanne-itweets-geodata-README.md |
| 1.3 KiB | .md |  |  | NishAnimate | docs/teanga/kscanne-nishanimate-README.md |
| 3.3 KiB | .md |  | G (48) | kscanne ogham README | docs/teanga/kscanne-ogham-README.md |
| 738 B | .md |  |  | spelling-errors-GA | docs/teanga/kscanne-spelling-errors-GA-README.md |
| 5.3 KiB | .md |  |  | kscanne treocht API | docs/teanga/kscanne-treocht-API.md |
| 112 B | .md |  |  | kscanne unicorn README | docs/teanga/kscanne-unicorn-README.md |
| 5.0 KiB | .md |  | G (3) | model training | docs/teanga/model_training.md |
| 19.0 KiB | .md |  |  | MotherDuck's DuckDB MCP Server | docs/teanga/motherduck_mcp.md |
| 4.3 KiB | .md |  |  | notebooklm 1 | docs/teanga/notebooklm_1.md |
| 30.3 KiB | .md |  |  | **Automated Weakly-Supervised Alignment of Historical Gaelic Manuscripts: A Pipeline for Fine-Tuning Qwen2-VL using ColP | docs/teanga/ocr-Aligning Gaelic Script for QwenVL Finetuning.md |
| 34.6 KiB | .md |  |  | **Automated Paleography and Visual Document Understanding for the Celtic Languages: A Comprehensive Framework for Fine-T | docs/teanga/ocr-Celtic Language OCR Resource Analysis.md |
| 25.0 KiB | .md |  |  | **Deep Research Report: End-to-End Fine-Tuning of Qwen3-VL for Historic Manuscript Transcription using Unsloth, MLflow,  | docs/teanga/ocr-Finetuning Qwen3-VL for Gaelic OCR.md |
| 2.2 KiB | .md |  |  | KCG_SUMMARY: IRLBench — Irish-English Bilingual LLM Benchmark | docs/teanga/repo-IRLBench.md |
| 2.2 KiB | .md |  | G (3) | KCG_SUMMARY: Chatterbox TTS — Fine-Tuning & Inference Kit | docs/teanga/repo-chatterbox-finetuning.md |
| 2.2 KiB | .md |  |  | KCG_SUMMARY: eScriptorium — Historical Document Transcription Platform | docs/teanga/repo-escriptorium.md |
| 1.8 KiB | .md |  |  | KCG_SUMMARY: Genizah Search — Cairo Genizah AI Semantic Search Application | docs/teanga/repo-genizah_search.md |
| 2.4 KiB | .md |  |  | KCG_SUMMARY: Historical Document Analysis — Multi-Modal Deep Learning Pipeline | docs/teanga/repo-historical-document-analysis.md |
| 2.1 KiB | .md |  |  | KCG_SUMMARY: PyLaia — Deep Learning Handwritten Text Recognition | docs/teanga/repo-pylaia.md |
| 2.0 KiB | .md |  |  | KCG_SUMMARY: TTS Dataset Generator — Automated Speech Dataset Creation | docs/teanga/repo-tts-dataset-generator.md |
| 19.2 KiB | .md |  |  | Scottish Gaelic AI Resources on HuggingFace | docs/teanga/scottish-scottish_gaelic_huggingface_resources.md |
| 19.2 KiB | .md |  |  | Scottish Gaelic AI Resources on HuggingFace | docs/teanga/scottish_gaelic_huggingface_resources.md |
| 9.8 KiB | .md | Y |  | useAgent Hook | docs/teanga/useAgent Hook.md |
| 8.0 KiB | .md | Y |  | utter project EuroLLM 22B Instruct 2512 · Hugging Face | docs/teanga/utter-project_EuroLLM-22B-Instruct-2512 · Hugging Face.md |
| 19.0 KiB | .md |  |  | Welsh (Cymraeg) Language AI Resources on HuggingFace | docs/teanga/welsh-huggingface-resources.md |
| 19.0 KiB | .md |  |  | Welsh (Cymraeg) Language AI Resources on HuggingFace | docs/teanga/welsh-welsh-huggingface-resources.md |

### 5.7 docs/web

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 16.7 KiB | .md | Y |  | AG UI   Pydantic AI | docs/web/AG-UI - Pydantic AI.md |
| 3.4 KiB | .md | Y |  | AG UI Goes Mobile  The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM | docs/web/AG-UI Goes Mobile_ The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM.md |
| 6.0 KiB | .md | Y |  | AG UI Overview | docs/web/AG-UI Overview.md |
| 3.7 KiB | .md | Y |  | AG UI and A2UI  Understanding the Differences   CopilotKit | docs/web/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md |
| 37.4 KiB | .md |  |  | **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms** | docs/web/Asset Management for Full-Stack App.md |
| 30.3 KiB | .md |  |  | **ARCHITECTURAL CONVERGENCE FOR DETERMINISTIC AGENTIC SYSTEMS: INTEGRATING BAML, GRAPHITI, AND TANSTACK AI WITHIN THE IR | docs/web/BAML, Graphiti, Tanstack AI Pipeline.md |
| 8.6 KiB | .md | Y |  | Basic Usage   Better Auth | docs/web/Basic Usage _ Better Auth.md |
| 28.4 KiB | .md | Y |  | ChromeDevTools chrome devtools mcp  Chrome DevTools for coding agents | docs/web/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md |
| 5.2 KiB | .md | Y |  | Drizzle ORM Adapter   Better Auth | docs/web/Drizzle ORM Adapter _ Better Auth.md |
| 25.0 KiB | .md |  |  | **Technical Blueprint for a Next-Generation Leaving Certificate Education Platform: Architecture, Pedagogy, and Implemen | docs/web/Educational Website Tech Stack.md |
| 11.1 KiB | .md | Y |  | Expo Integration   Better Auth | docs/web/Expo Integration _ Better Auth.md |
| 34.3 KiB | .md |  |  | **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction** | docs/web/Frontend Idea Catalog Development.md |
| 2.2 KiB | .md |  |  | Web Research - Consolidated Index | docs/web/INDEX-from-bonneagar-web-research.md |
| 5.2 KiB | .md |  |  | docs/web/ — Web Architecture Knowledge Base | docs/web/INDEX.md |
| 28.7 KiB | .md |  |  | **Architecting the Isomorphic AI Tutor: A Comprehensive Research Report on Integrating TanStack AI, BAML, and LiteLLM** | docs/web/Integrating TanStack AI with LiteLLM.md |
| 12.5 KiB | .md | Y |  | Microfrontends | docs/web/Microfrontends.md |
| 4.9 KiB | .md | Y |  | Overview   TanStack AI Docs | docs/web/Overview _ TanStack AI Docs.md |
| 29.7 KiB | .md | Y |  | Overview   TanStack DB Docs | docs/web/Overview _ TanStack DB Docs.md |
| 3.6 KiB | .md | Y |  | PDF.js   Examples | docs/web/PDF.js - Examples.md |
| 2.5 KiB | .md | Y |  | Playground   Convex Developer Hub | docs/web/Playground _ Convex Developer Hub.md |
| 4.6 KiB | .md | Y |  | PostgreSQL   Better Auth | docs/web/PostgreSQL _ Better Auth.md |
| 6.8 KiB | .md | Y |  | RAG (Retrieval Augmented Generation) with the Agent component   Convex Developer Hub | docs/web/RAG (Retrieval-Augmented Generation) with the Agent component _ Convex Developer Hub.md |
| 1.2 KiB | .md |  |  | Frontend | docs/web/README.md |
| 9.0 KiB | .md |  |  | TanStack Examples Analysis - Complete Guide | docs/web/README_TANSTACK_ANALYSIS.md |
| 35.9 KiB | .md |  |  | **Architectural Blueprint for an Intelligent, British Curriculum-Aligned Interactive Exam Builder** | docs/web/React Drag-and-Drop for Exam Builder.md |
| 22.7 KiB | .md | Y |  | Release v28.0.0   Mesh Shaders, Immediates, and More! · gfx rs wgpu | docs/web/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md |
| 8.5 KiB | .md | Y |  | Sign In With Ethereum (SIWE)   Better Auth | docs/web/Sign In With Ethereum (SIWE) _ Better Auth.md |
| 18.3 KiB | .md |  |  | TanStack Examples Analysis | docs/web/TANSTACK_ANALYSIS.md |
| 8.9 KiB | .md |  |  | TanStack Examples Analysis - Complete Index | docs/web/TANSTACK_INDEX.md |
| 6.5 KiB | .md |  |  | TanStack Examples - Quick Reference | docs/web/TANSTACK_QUICK_REFERENCE.md |
| 8.2 KiB | .md |  |  | TanStack Examples - Executive Summary | docs/web/TANSTACK_SUMMARY.md |
| 35.1 KiB | .md |  |  | **The Convergent Stack: Architecting Reactive Data Systems with TanStack DB, DuckDB, RisingWave, and Marimo** | docs/web/TanStack DB Integration and Comparison.md |
| 2.6 KiB | .md | Y |  | TanStack Start Integration   Better Auth | docs/web/TanStack Start Integration _ Better Auth.md |
| 999 B | .md | Y |  | TanStack Start | docs/web/TanStack Start.md |
| 6.6 KiB | .md | Y |  | ag ui docs sdk kotlin overview.mdx at main · ag ui protocol ag ui | docs/web/ag-ui_docs_sdk_kotlin_overview.mdx at main · ag-ui-protocol_ag-ui.md |
| 32.6 KiB | .md |  |  | **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Educational Hub** | docs/web/agentic-platform.md |
| 9.5 KiB | .md | Y |  | alchemy run alchemy  Infrastructure as TypeScript | docs/web/alchemy-run_alchemy_ Infrastructure as TypeScript.md |
| 716 B | .md | Y |  | alchemy examples cloudflare sveltekit alchemy.run.ts at main · alchemy run alchemy | docs/web/alchemy_examples_cloudflare-sveltekit_alchemy.run.ts at main · alchemy-run_alchemy.md |
| 1.0 KiB | .md | Y |  | alchemy examples cloudflare tanstack start alchemy.run.ts at main · alchemy run alchemy | docs/web/alchemy_examples_cloudflare-tanstack-start_alchemy.run.ts at main · alchemy-run_alchemy.md |
| 1.1 KiB | .md | Y |  | alchemy examples cloudflare worker alchemy.run.ts at main · alchemy run alchemy | docs/web/alchemy_examples_cloudflare-worker_alchemy.run.ts at main · alchemy-run_alchemy.md |
| 8.5 KiB | .md | Y |  | auth setup | docs/web/auth-setup.md |
| 84.4 KiB | .md |  |  | Convex Authentication, Actions, and Integration Capabilities Research | docs/web/convex-authentication-and-integration-guide.md |
| 7.3 KiB | .md | Y |  | convex backend self hosted README.md at main · get convex convex backend | docs/web/convex-backend_self-hosted_README.md at main · get-convex_convex-backend.md |
| 33.7 KiB | .md |  |  | Convex: Core Features and Architecture | docs/web/convex-core-features-architecture.md |
| 31.6 KiB | .md |  |  | Effect.ts and Convex Integration Research | docs/web/effect-convex-integration-research.md |
| 60.9 KiB | .md |  |  | Effect.ts Comprehensive Research Report | docs/web/effect-ts-comprehensive-research.md |
| 36.1 KiB | .md |  |  | Effect.ts and TanStack Start Integration Research | docs/web/effect-ts-tanstack-start-integration.md |
| 37.2 KiB | .md |  |  | **A Unified Full-Stack Strategy for an Interactive AI Dashboard** | docs/web/full-stack-dashboard-integration-plan.md |
| 55.0 KiB | .md |  |  | Modern Full-Stack Web Application Architecture | docs/web/full-stack-web-architecture-consolidated.md |
| 41.0 KiB | .md |  |  | implementation plan self hosting betterauth convex supabase hono tanstack start | docs/web/implementation-plan-self-hosting-betterauth-convex-supabase-hono-tanstack-start.md |
| 1.5 KiB | .md | Y |  | mcp ui integration | docs/web/mcp-ui-integration.md |
| 35.0 KiB | .md |  |  | Comprehensive ORPC (oRPC) Research Report | docs/web/orpc-comprehensive-research.md |
| 2.4 KiB | .md |  |  | Cianfhoghlaim Base — KCG Summary | docs/web/ref-cianfhoghlaim-base-template.md |
| 12.0 KiB | .md |  |  | UI Inspiration Guide for sruth/ Frontends | docs/web/ref-ui-inspiration.md |
| 4.8 KiB | .md |  |  | Consolidated Examples — KCG Summary | docs/web/ref-unified-examples.md |
| 2.4 KiB | .md |  |  | AG-UI Protocol — KCG Summary | docs/web/repo-ag-ui-protocol.md |
| 3.4 KiB | .md |  |  | Cloudflare Workers — KCG Summary | docs/web/repo-cloudflare-workers.md |
| 3.9 KiB | .md |  |  | Convex — KCG Summary | docs/web/repo-convex.md |
| 1.8 KiB | .md |  |  | Hono — KCG Summary | docs/web/repo-hono.md |
| 2.1 KiB | .md |  |  | oRPC — KCG Summary | docs/web/repo-orpc.md |
| 3.8 KiB | .md |  |  | Restate.dev Coding Agent — KCG Summary | docs/web/repo-restate-coding-agent.md |
| 46 B | .md |  |  | UI | docs/web/repo-restate-ui-readme.md |
| 4.4 KiB | .md |  |  | TanStack — KCG Summary | docs/web/repo-tanstack.md |
| 37.0 KiB | .md |  |  | routing and layout | docs/web/routing-and-layout.md |
| 32.5 KiB | .md |  |  | TanStack Start: Comprehensive Architecture Research Report | docs/web/tanstack-start-architecture.md |
| 37.6 KiB | .md |  |  | TanStack Start: Comprehensive Research Report | docs/web/tanstack-start-research-report.md |
| 32.0 KiB | .md |  |  | TanStack Start: Visual Architecture Patterns | docs/web/tanstack-start-visual-patterns.md |
| 12.4 KiB | .md | Y |  | 🌉 How to Use Swift Inside Kotlin Multiplatform  The iOS Bridge Explained (with a Real Example) | docs/web/🌉 How to Use Swift Inside Kotlin Multiplatform_ The iOS Bridge Explained (with a Real Example).md |

### 5.8 docs/tuatha

| Size | Ext | FM? | IR? | Summary | File |
|---|---|---|---:|---|
| 347.7 KiB | .pdf |  |  | 2510.17652v1 | docs/sruth/tuatha/2510.17652v1.pdf |
| 10.0 KiB | .md |  |  | Adding New Agents | docs/sruth/tuatha/ADDING_AGENTS.md |
| 20.4 KiB | .md |  |  | Adding Data Sources | docs/sruth/tuatha/ADDING_DATA_SOURCES.md |
| 18.0 KiB | .md |  |  | Adding Agent Tools | docs/sruth/tuatha/ADDING_TOOLS.md |
| 12.0 KiB | .md |  |  | Adding New Game Zones | docs/sruth/tuatha/ADDING_ZONES.md |
| 3.7 KiB | .md | Y |  | AG UI and A2UI  Understanding the Differences   CopilotKit | docs/sruth/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md |
| 10.5 KiB | .md |  |  | Tuath Agent Architecture | docs/sruth/tuatha/AGENTS.md |
| 28.6 KiB | .md |  |  | **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Structured Extraction wi | docs/sruth/tuatha/AI Chemistry Education Image Generation.md |
| 15.5 KiB | .md |  |  | Cianfhoghlaim Project Analysis | docs/sruth/tuatha/ANALYSIS.md |
| 9.5 KiB | .md |  |  | Tuath API Reference | docs/sruth/tuatha/API.md |
| 32.6 KiB | .md |  |  | **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Educational Hub** | docs/sruth/tuatha/Agentic Education Platform Development.md |
| 31.9 KiB | .md |  |  | **Autonomous Web Intelligence Architecture: A Comprehensive Implementation Framework for Agentic Scraping and Reconstruc | docs/sruth/tuatha/Agentic Web Scraping Pipeline.md |
| 37.4 KiB | .md |  |  | **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms** | docs/sruth/tuatha/Asset Management for Full-Stack App.md |
| 33.2 KiB | .md |  |  | **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report** | docs/sruth/tuatha/British Isles Education Map.md |
| 31.4 KiB | .md |  |  | **Architectural Framework for Data-Driven 2.5D Geospatial Synthesis: Integrating Authoritative British Isles Data into R | docs/sruth/tuatha/British Isles Game Dev Data Pipeline.md |
| 38.8 KiB | .md |  |  | **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse** | docs/sruth/tuatha/British Isles Mythology MMO Research.md |
| 34.7 KiB | .md |  |  | **Architecting the Autonomous Epistemologist: A Technical Blueprint for Agentic Knowledge Acquisition and Dynamic Domain | docs/sruth/tuatha/Building an Educational Agent's Knowledge Base.md |
| 18.7 KiB | .md |  |  | Celtic Languages Integration | docs/sruth/tuatha/CELTIC_LANGUAGES.md |
| 19.3 KiB | .md |  |  | Cross-Platform Development Guide | docs/sruth/tuatha/CROSS_PLATFORM_GUIDE.md |
| 26.0 KiB | .md |  |  | Crypteolas Agent Integration Guide | docs/sruth/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md |
| 30.3 KiB | .md |  |  | Comprehensive Crypto & Payment Integration Summary for Crypteolas | docs/sruth/tuatha/CRYPTO_INTEGRATION_SUMMARY.md |
| 40.4 KiB | .md |  |  | **Compendium of Celtic Lexicography for Digital World-Building: A Comparative Analysis of Goidelic and Brythonic Heritag | docs/sruth/tuatha/Celtic Etymology for Game Names.md |
| 41.0 KiB | .md |  |  | **Unified Computational Infrastructure for Celtic Languages: Data Integration, Educational Analytics, and Strategic Mode | docs/sruth/tuatha/Celtic Language Data Aggregation & Analysis.md |
| 33.3 KiB | .md |  |  | **Philological and Ludological Feasibility Study: Celtic Nomenclature in Web3 Massively Multiplayer Online Environments* | docs/sruth/tuatha/Celtic MMO Web3 Concept Integration.md |
| 37.8 KiB | .md |  |  | **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architecture for Next-Generatio | docs/sruth/tuatha/Chemistry Education Asset Generation.md |
| 25.5 KiB | .md | Y |  | Comparing the Top 6 Agent Native Rails for the Agentic Internet  MCP, A2A, AP2, ACP, x402, and Kite | docs/sruth/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md |
| 39.2 KiB | .md |  |  | **Project Crypteolas: A Decentralized Architecture for Financial Knowledge Graph Federated Learning and Agentic Markets* | docs/sruth/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md |
| 35.2 KiB | .md |  |  | Crypto Analysis AI Agent System Architecture | docs/sruth/tuatha/Crypto Analysis AI Agent System Architecture.md |
| 17.0 KiB | .md |  |  | Deployment Guide | docs/sruth/tuatha/DEPLOYMENT.md |
| 27.2 KiB | .md | Y |  | ERC 4361  Sign In with Ethereum | docs/sruth/tuatha/ERC-4361_ Sign-In with Ethereum.md |
| 37.9 KiB | .md |  |  | **High-Fidelity Pedagogical Simulation: A Comprehensive Framework for Automating Scientifically Accurate Educational Vis | docs/sruth/tuatha/Educational Game Dev Pipeline.md |
| 17.9 KiB | .md |  |  | TanStack Start Frontend | docs/sruth/tuatha/FRONTEND.md |
| 33.1 KiB | .md |  |  | **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device | docs/sruth/tuatha/Federated AI Marketplace on iPhone.md |
| 32.2 KiB | .md |  |  | **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supe | docs/sruth/tuatha/Fine-tuning VLMs for iOS HTR.md |
| 34.3 KiB | .md |  |  | **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction** | docs/sruth/tuatha/Frontend Idea Catalog Development.md |
| 18.0 KiB | .md |  |  | Babylon.js Game Client | docs/sruth/tuatha/GAME_CLIENT.md |
| 15.8 KiB | .md |  |  | Godot + Rust Guide | docs/sruth/tuatha/GODOT_RUST_GUIDE.md |
| 9.8 KiB | .md |  |  | Graphics, Game Development & Rendering Documentation Index | docs/sruth/tuatha/GRAPHICS_INDEX.md |
| 33.1 KiB | .md |  |  | **Converging High-Fidelity Pre-Rendering and Database-Driven State: A Comprehensive Technical Blueprint for Next-Generat | docs/sruth/tuatha/Game Dev Pipeline Research & Plan.md |
| 38.5 KiB | .md |  |  | **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem** | docs/sruth/tuatha/Game Development Research & AI Integration.md |
| 30.8 KiB | .md |  |  | **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation in Real-Time Enviro | docs/sruth/tuatha/Game Particle Effects Research(2).md |
| 30.8 KiB | .md |  |  | **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation in Real-Time Enviro | docs/sruth/tuatha/Game Particle Effects Research.md |
| 44.3 KiB | .md |  |  | **Architectural Blueprint for Autonomous Reverse Engineering and Asset Reconstruction Systems: A Deep Research Report** | docs/sruth/tuatha/Game Reverse Engineering Workflow Design.md |
| 26.8 KiB | .md |  |  | **Architecting Agentic Creative Workflows: Deep Research into Generative AI Integration for React Ecosystems** | docs/sruth/tuatha/Generative AI Art Workflow Integration.md |
| 9.0 KiB | .md | Y |  | GeoAI | docs/sruth/tuatha/GeoAI.md |
| 29.8 KiB | .md |  |  | **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP and WebGPU Rendering f | docs/sruth/tuatha/Geospatial Workflow & Particle Effects.md |
| 13.8 KiB | .md |  | G (5) | Túatha Documentation Index | docs/sruth/tuatha/INDEX.md |
| 33.1 KiB | .md |  |  | **Architectural Synthesis of Sovereign Game State: Integrating SpacetimeDB, DuckDB WASM, TanStack Start, and CopilotKit* | docs/sruth/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md |
| 30.7 KiB | .md |  |  | **Architectural Convergence: The Agentic Pipeline for Structured Generative AI** | docs/sruth/tuatha/Interactive AI Pipeline Development.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the British Isles** | docs/sruth/tuatha/Interactive Map & AI Agents.md |
| 10.3 KiB | .md | Y |  | Introducing AnyLanguageModel  One API for Local and Remote LLMs on Apple Platforms | docs/sruth/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md |
| 32.9 KiB | .md |  |  | **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analysis of MLX, Llama.cp | docs/sruth/tuatha/Irish Handwriting App Development.md |
| 33.2 KiB | .md |  |  | **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework for Deploying Irish | docs/sruth/tuatha/Irish LLM for iPhone Development.md |
| 14.6 KiB | .md | Y |  | Kotlin Multiplatform vs. React Native  A cross platform comparison   Kotlin Multiplatform | docs/sruth/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md |
| 31.1 KiB | .md |  |  | **Architecting Unified Hybrid-Inference Gateways: A Comprehensive Analysis of Local-Cloud Interoperability for Multimoda | docs/sruth/tuatha/LLM Serving with MLflow & Langfuse.md |
| 40.9 KiB | .md |  |  | **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations** | docs/sruth/tuatha/Learn-to-Earn Blockchain and AI.md |
| 1.5 KiB | .md | Y |  | MCP UI | docs/sruth/tuatha/MCP-UI.md |
| 32.1 KiB | .md |  |  | **Technical Blueprint for a Browser-Based WebGPU MMO: The Geospatial Spirit World** | docs/sruth/tuatha/MMO Geospatial Data & Visual RAG.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for a Native Multimodal Knowledge Graph Pipeline: Integrating Video, Audio, and Text Intellige | docs/sruth/tuatha/Multimodal Video Knowledge Graph Pipeline.md |
| 34.8 KiB | .md |  |  | **Architecting Tuath: A Comprehensive Technical and Cultural Analysis of Decentralized MMO Infrastructure, Agentic Econo | docs/sruth/tuatha/Ogham Crypto MMO Research.md |
| 21.5 KiB | .md |  |  | Payment Integration Guide | docs/sruth/tuatha/PAYMENT_GUIDE.md |
| 20.2 KiB | .md |  |  | Performance Tuning Guide | docs/sruth/tuatha/PERFORMANCE_TUNING.md |
| 12.8 KiB | .md |  |  | Tuath Data Pipelines | docs/sruth/tuatha/PIPELINES.md |
| 12.1 KiB | .md |  |  | Game Development Reference Library | docs/sruth/tuatha/README.md |
| 22.7 KiB | .md | Y |  | Release v28.0.0   Mesh Shaders, Immediates, and More! · gfx rs wgpu | docs/sruth/tuatha/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md |
| 3.5 KiB | .md | Y |  | Rust Client | docs/sruth/tuatha/Rust Client.md |
| 39.2 KiB | .md |  |  | **Architectural Analysis and Implementation Strategy for a Rust-Based Full-Stack Gaming Ecosystem** | docs/sruth/tuatha/Rust Full-Stack Gaming Environment.md |
| 16.5 KiB | .md |  |  | SpacetimeDB Guide | docs/sruth/tuatha/SPACETIMEDB_GUIDE.md |
| 8.5 KiB | .md | Y |  | Sign In With Ethereum (SIWE)   Better Auth | docs/sruth/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md |
| 34.8 KiB | .md |  |  | **Architectural Specification: Decentralized Geospatial Procedural Generation Systems for the 'Anam' Project** | docs/sruth/tuatha/SpacetimeDB Ogham Stone Game Integration.md |
| 1.0 KiB | .md | Y |  | SpacetimeDB | docs/sruth/tuatha/SpacetimeDB.md |
| 29.6 KiB | .md |  |  | **Architectural Convergence: Implementing a Massively Multiplayer Celtic Odyssey via SpacetimeDB, Solana, and Ethereum ( | docs/sruth/tuatha/Spacetimedb Blockchain Integration Strategy.md |
| 10.4 KiB | .md | Y |  | Swift Transformers Reaches 1.0 – and Looks to the Future | docs/sruth/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md |
| 35.1 KiB | .md |  |  | **The Convergent Stack: Architecting Reactive Data Systems with TanStack DB, DuckDB, RisingWave, and Marimo** | docs/sruth/tuatha/TanStack DB Integration and Comparison.md |
| 50.3 KiB | .md |  |  | Technical Integration Plan  Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly) | docs/sruth/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md |
| 21.5 KiB | .md | Y | G (4) | The Expulsion of the Déisi   Wikipedia | docs/sruth/tuatha/The Expulsion of the Déisi - Wikipedia.md |
| 7.1 KiB | .md | Y |  | Unsloth Model Catalog   Unsloth Documentation | docs/sruth/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md |
| 20.1 KiB | .md |  |  | WGPU Guide | docs/sruth/tuatha/WGPU_GUIDE.md |
| 29.3 KiB | .md |  |  | **Architectural Blueprint for "Cianfhoghlaim": A Decentralized, Physical-Digital Educational Ecosystem** | docs/sruth/tuatha/Web3 Classroom Response System Design.md |
| 40.9 KiB | .md |  |  | **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Educational Ecosystem* | docs/sruth/tuatha/Web3 Gamified Education & Asset Generation.md |
| 12.1 KiB | .md |  |  | API Reference Index | docs/sruth/tuatha/api-README.md |
| 6.9 KiB | .md | Y |  | apple ml fastvlm  This repository contains the official implementation of  FastVLM  Efficient Vision Encoding for Vision | docs/sruth/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md |
| 32.2 KiB | .md |  |  | **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supe | docs/sruth/tuatha/celtic-ocr.md |
| 16.3 KiB | .md |  |  | Building an "Anam" Celtic educational MMO: technical foundations | docs/sruth/tuatha/celtic_mmo.md |
| 28.2 KiB | .md |  |  | Agentic UI learning pipeline: a multi-agent architecture for automated web scraping and design system extraction | docs/sruth/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md |
| 38.4 KiB | .md |  |  | Define the source using dlt's declarative REST API configuration | docs/sruth/tuatha/dlt_crawl4ai_lancedb.md |
| 18.9 KiB | .md |  |  | Educational Game Development | docs/sruth/tuatha/educational-game-development.md |
| 38.5 KiB | .md |  |  | **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem** | docs/sruth/tuatha/engine-selection.md |
| 33.1 KiB | .md |  |  | **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device | docs/sruth/tuatha/federated-marketplace.md |
| 1.6 KiB | .md |  |  | Game Design | docs/sruth/tuatha/game-design-README.md |
| 1.3 KiB | .md |  |  | Contributing | docs/sruth/tuatha/game_CONTRIBUTING.md |
| 5.3 KiB | .md |  |  | Development | docs/sruth/tuatha/game_DEVELOPMENT.md |
| 27.2 KiB | .md | Y |  | game siwe auth | docs/sruth/tuatha/game_siwe-auth.md |
| 6.0 KiB | .md |  |  | Rust bindings for Godot 4 | docs/sruth/tuatha/gdext-ReadMe.md |
| 32.0 KiB | .md |  |  | **Strategic Architecture for Converged Agentic Ecosystems: Integrating iOS Vision Intelligence with Cross-Platform Devel | docs/sruth/tuatha/iOS App Development Ecosystem Strategy.md |
| 2.2 KiB | .md |  |  | Infrastructure | docs/sruth/tuatha/infrastructure-README.md |
| 40.9 KiB | .md |  |  | **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations** | docs/sruth/tuatha/learn-to-earn-model.md |
| 1.4 KiB | .md |  |  | ML Models | docs/sruth/tuatha/ml-models-README.md |
| 38.8 KiB | .md |  |  | **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse** | docs/sruth/tuatha/mythology-framework.md |
| 1.7 KiB | .md |  |  | AnyLanguageModel — KCG Summary | docs/sruth/tuatha/repo-AnyLanguageModel.md |
| 1.7 KiB | .md |  |  | SpacetimeDB — KCG Summary | docs/sruth/tuatha/repo-SpacetimeDB.md |
| 2.2 KiB | .md |  |  | agui_kotlin — KCG Summary | docs/sruth/tuatha/repo-agui_kotlin.md |
| 1.8 KiB | .md |  |  | hophacks-spacetimedb-workshop — KCG Summary | docs/sruth/tuatha/repo-hophacks-spacetimedb-workshop.md |
| 1.4 KiB | .md |  |  | ireland — KCG Summary | docs/sruth/tuatha/repo-ireland.md |
| 1.5 KiB | .md |  |  | react-native-godot — KCG Summary | docs/sruth/tuatha/repo-react-native-godot.md |
| 1.3 KiB | .md |  |  | react-native-reusables — KCG Summary | docs/sruth/tuatha/repo-react-native-reusables.md |
| 2.5 KiB | .md |  |  | SpacetimeDB Cookbook — KCG Summary | docs/sruth/tuatha/repo-spacetimedb-cookbook.md |
| 2.1 KiB | .md |  |  | spacetimedb-typescript-sdk — KCG Summary | docs/sruth/tuatha/repo-spacetimedb-typescript-sdk.md |
| 3.0 KiB | .md |  |  | wgpu — KCG Summary | docs/sruth/tuatha/repo-wgpu.md |
| 1.5 KiB | .md |  |  | x402 — KCG Summary | docs/sruth/tuatha/repo-x402.md |
| 3.4 KiB | .md | Y |  | syft flwr notebooks fedrag README.md at main · OpenMined syft flwr | docs/sruth/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md |
| 1.2 KiB | .md |  |  | Tokenomics | docs/sruth/tuatha/tokenomics-README.md |
| 7.1 KiB | .md | Y |  | unsloth catalog | docs/sruth/tuatha/unsloth-catalog.md |
| 9.8 KiB | .md | Y |  | useAgent Hook | docs/sruth/tuatha/useAgent Hook.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the British Isles** | docs/sruth/tuatha/world-map.md |
| 40.9 KiB | .md |  |  | **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Educational Ecosystem* | docs/sruth/tuatha/x402-payments.md |
| 347.7 KiB | .pdf |  |  | 2510.17652v1 | docs/sruth/tuatha/sruth/tuatha/2510.17652v1.pdf |
| 10.0 KiB | .md |  |  | Adding New Agents | docs/sruth/tuatha/sruth/tuatha/ADDING_AGENTS.md |
| 20.4 KiB | .md |  |  | Adding Data Sources | docs/sruth/tuatha/sruth/tuatha/ADDING_DATA_SOURCES.md |
| 18.0 KiB | .md |  |  | Adding Agent Tools | docs/sruth/tuatha/sruth/tuatha/ADDING_TOOLS.md |
| 12.0 KiB | .md |  |  | Adding New Game Zones | docs/sruth/tuatha/sruth/tuatha/ADDING_ZONES.md |
| 3.7 KiB | .md | Y |  | AG UI and A2UI  Understanding the Differences   CopilotKit | docs/sruth/tuatha/sruth/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md |
| 10.5 KiB | .md |  |  | Tuath Agent Architecture | docs/sruth/tuatha/sruth/tuatha/AGENTS.md |
| 28.6 KiB | .md |  |  | **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Structured Extraction wi | docs/sruth/tuatha/sruth/tuatha/AI Chemistry Education Image Generation.md |
| 15.5 KiB | .md |  |  | Cianfhoghlaim Project Analysis | docs/sruth/tuatha/sruth/tuatha/ANALYSIS.md |
| 9.5 KiB | .md |  |  | Tuath API Reference | docs/sruth/tuatha/sruth/tuatha/API.md |
| 32.6 KiB | .md |  |  | **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Educational Hub** | docs/sruth/tuatha/sruth/tuatha/Agentic Education Platform Development.md |
| 31.9 KiB | .md |  |  | **Autonomous Web Intelligence Architecture: A Comprehensive Implementation Framework for Agentic Scraping and Reconstruc | docs/sruth/tuatha/sruth/tuatha/Agentic Web Scraping Pipeline.md |
| 37.4 KiB | .md |  |  | **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms** | docs/sruth/tuatha/sruth/tuatha/Asset Management for Full-Stack App.md |
| 33.2 KiB | .md |  |  | **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report** | docs/sruth/tuatha/sruth/tuatha/British Isles Education Map.md |
| 31.4 KiB | .md |  |  | **Architectural Framework for Data-Driven 2.5D Geospatial Synthesis: Integrating Authoritative British Isles Data into R | docs/sruth/tuatha/sruth/tuatha/British Isles Game Dev Data Pipeline.md |
| 38.8 KiB | .md |  |  | **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse** | docs/sruth/tuatha/sruth/tuatha/British Isles Mythology MMO Research.md |
| 34.7 KiB | .md |  |  | **Architecting the Autonomous Epistemologist: A Technical Blueprint for Agentic Knowledge Acquisition and Dynamic Domain | docs/sruth/tuatha/sruth/tuatha/Building an Educational Agent's Knowledge Base.md |
| 18.7 KiB | .md |  |  | Celtic Languages Integration | docs/sruth/tuatha/sruth/tuatha/CELTIC_LANGUAGES.md |
| 19.3 KiB | .md |  |  | Cross-Platform Development Guide | docs/sruth/tuatha/sruth/tuatha/CROSS_PLATFORM_GUIDE.md |
| 26.0 KiB | .md |  |  | Crypteolas Agent Integration Guide | docs/sruth/tuatha/sruth/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md |
| 30.3 KiB | .md |  |  | Comprehensive Crypto & Payment Integration Summary for Crypteolas | docs/sruth/tuatha/sruth/tuatha/CRYPTO_INTEGRATION_SUMMARY.md |
| 40.4 KiB | .md |  |  | **Compendium of Celtic Lexicography for Digital World-Building: A Comparative Analysis of Goidelic and Brythonic Heritag | docs/sruth/tuatha/sruth/tuatha/Celtic Etymology for Game Names.md |
| 41.0 KiB | .md |  |  | **Unified Computational Infrastructure for Celtic Languages: Data Integration, Educational Analytics, and Strategic Mode | docs/sruth/tuatha/sruth/tuatha/Celtic Language Data Aggregation & Analysis.md |
| 33.3 KiB | .md |  |  | **Philological and Ludological Feasibility Study: Celtic Nomenclature in Web3 Massively Multiplayer Online Environments* | docs/sruth/tuatha/sruth/tuatha/Celtic MMO Web3 Concept Integration.md |
| 37.8 KiB | .md |  |  | **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architecture for Next-Generatio | docs/sruth/tuatha/sruth/tuatha/Chemistry Education Asset Generation.md |
| 25.5 KiB | .md | Y |  | Comparing the Top 6 Agent Native Rails for the Agentic Internet  MCP, A2A, AP2, ACP, x402, and Kite | docs/sruth/tuatha/sruth/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md |
| 39.2 KiB | .md |  |  | **Project Crypteolas: A Decentralized Architecture for Financial Knowledge Graph Federated Learning and Agentic Markets* | docs/sruth/tuatha/sruth/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md |
| 35.2 KiB | .md |  |  | Crypto Analysis AI Agent System Architecture | docs/sruth/tuatha/sruth/tuatha/Crypto Analysis AI Agent System Architecture.md |
| 17.0 KiB | .md |  |  | Deployment Guide | docs/sruth/tuatha/sruth/tuatha/DEPLOYMENT.md |
| 27.2 KiB | .md | Y |  | ERC 4361  Sign In with Ethereum | docs/sruth/tuatha/sruth/tuatha/ERC-4361_ Sign-In with Ethereum.md |
| 37.9 KiB | .md |  |  | **High-Fidelity Pedagogical Simulation: A Comprehensive Framework for Automating Scientifically Accurate Educational Vis | docs/sruth/tuatha/sruth/tuatha/Educational Game Dev Pipeline.md |
| 17.9 KiB | .md |  |  | TanStack Start Frontend | docs/sruth/tuatha/sruth/tuatha/FRONTEND.md |
| 33.1 KiB | .md |  |  | **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device | docs/sruth/tuatha/sruth/tuatha/Federated AI Marketplace on iPhone.md |
| 32.2 KiB | .md |  |  | **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supe | docs/sruth/tuatha/sruth/tuatha/Fine-tuning VLMs for iOS HTR.md |
| 34.3 KiB | .md |  |  | **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction** | docs/sruth/tuatha/sruth/tuatha/Frontend Idea Catalog Development.md |
| 18.0 KiB | .md |  |  | Babylon.js Game Client | docs/sruth/tuatha/sruth/tuatha/GAME_CLIENT.md |
| 15.8 KiB | .md |  |  | Godot + Rust Guide | docs/sruth/tuatha/sruth/tuatha/GODOT_RUST_GUIDE.md |
| 9.8 KiB | .md |  |  | Graphics, Game Development & Rendering Documentation Index | docs/sruth/tuatha/sruth/tuatha/GRAPHICS_INDEX.md |
| 33.1 KiB | .md |  |  | **Converging High-Fidelity Pre-Rendering and Database-Driven State: A Comprehensive Technical Blueprint for Next-Generat | docs/sruth/tuatha/sruth/tuatha/Game Dev Pipeline Research & Plan.md |
| 38.5 KiB | .md |  |  | **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem** | docs/sruth/tuatha/sruth/tuatha/Game Development Research & AI Integration.md |
| 30.8 KiB | .md |  |  | **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation in Real-Time Enviro | docs/sruth/tuatha/sruth/tuatha/Game Particle Effects Research(2).md |
| 30.8 KiB | .md |  |  | **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation in Real-Time Enviro | docs/sruth/tuatha/sruth/tuatha/Game Particle Effects Research.md |
| 44.3 KiB | .md |  |  | **Architectural Blueprint for Autonomous Reverse Engineering and Asset Reconstruction Systems: A Deep Research Report** | docs/sruth/tuatha/sruth/tuatha/Game Reverse Engineering Workflow Design.md |
| 26.8 KiB | .md |  |  | **Architecting Agentic Creative Workflows: Deep Research into Generative AI Integration for React Ecosystems** | docs/sruth/tuatha/sruth/tuatha/Generative AI Art Workflow Integration.md |
| 9.0 KiB | .md | Y |  | GeoAI | docs/sruth/tuatha/sruth/tuatha/GeoAI.md |
| 29.8 KiB | .md |  |  | **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP and WebGPU Rendering f | docs/sruth/tuatha/sruth/tuatha/Geospatial Workflow & Particle Effects.md |
| 13.8 KiB | .md |  | G (5) | Túatha Documentation Index | docs/sruth/tuatha/sruth/tuatha/INDEX.md |
| 33.1 KiB | .md |  |  | **Architectural Synthesis of Sovereign Game State: Integrating SpacetimeDB, DuckDB WASM, TanStack Start, and CopilotKit* | docs/sruth/tuatha/sruth/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md |
| 30.7 KiB | .md |  |  | **Architectural Convergence: The Agentic Pipeline for Structured Generative AI** | docs/sruth/tuatha/sruth/tuatha/Interactive AI Pipeline Development.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the British Isles** | docs/sruth/tuatha/sruth/tuatha/Interactive Map & AI Agents.md |
| 10.3 KiB | .md | Y |  | Introducing AnyLanguageModel  One API for Local and Remote LLMs on Apple Platforms | docs/sruth/tuatha/sruth/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md |
| 32.9 KiB | .md |  |  | **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analysis of MLX, Llama.cp | docs/sruth/tuatha/sruth/tuatha/Irish Handwriting App Development.md |
| 33.2 KiB | .md |  |  | **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework for Deploying Irish | docs/sruth/tuatha/sruth/tuatha/Irish LLM for iPhone Development.md |
| 14.6 KiB | .md | Y |  | Kotlin Multiplatform vs. React Native  A cross platform comparison   Kotlin Multiplatform | docs/sruth/tuatha/sruth/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md |
| 31.1 KiB | .md |  |  | **Architecting Unified Hybrid-Inference Gateways: A Comprehensive Analysis of Local-Cloud Interoperability for Multimoda | docs/sruth/tuatha/sruth/tuatha/LLM Serving with MLflow & Langfuse.md |
| 40.9 KiB | .md |  |  | **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations** | docs/sruth/tuatha/sruth/tuatha/Learn-to-Earn Blockchain and AI.md |
| 1.5 KiB | .md | Y |  | MCP UI | docs/sruth/tuatha/sruth/tuatha/MCP-UI.md |
| 32.1 KiB | .md |  |  | **Technical Blueprint for a Browser-Based WebGPU MMO: The Geospatial Spirit World** | docs/sruth/tuatha/sruth/tuatha/MMO Geospatial Data & Visual RAG.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for a Native Multimodal Knowledge Graph Pipeline: Integrating Video, Audio, and Text Intellige | docs/sruth/tuatha/sruth/tuatha/Multimodal Video Knowledge Graph Pipeline.md |
| 34.8 KiB | .md |  |  | **Architecting Tuath: A Comprehensive Technical and Cultural Analysis of Decentralized MMO Infrastructure, Agentic Econo | docs/sruth/tuatha/sruth/tuatha/Ogham Crypto MMO Research.md |
| 21.5 KiB | .md |  |  | Payment Integration Guide | docs/sruth/tuatha/sruth/tuatha/PAYMENT_GUIDE.md |
| 20.2 KiB | .md |  |  | Performance Tuning Guide | docs/sruth/tuatha/sruth/tuatha/PERFORMANCE_TUNING.md |
| 12.8 KiB | .md |  |  | Tuath Data Pipelines | docs/sruth/tuatha/sruth/tuatha/PIPELINES.md |
| 12.1 KiB | .md |  |  | Game Development Reference Library | docs/sruth/tuatha/sruth/tuatha/README.md |
| 22.7 KiB | .md | Y |  | Release v28.0.0   Mesh Shaders, Immediates, and More! · gfx rs wgpu | docs/sruth/tuatha/sruth/tuatha/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md |
| 3.5 KiB | .md | Y |  | Rust Client | docs/sruth/tuatha/sruth/tuatha/Rust Client.md |
| 39.2 KiB | .md |  |  | **Architectural Analysis and Implementation Strategy for a Rust-Based Full-Stack Gaming Ecosystem** | docs/sruth/tuatha/sruth/tuatha/Rust Full-Stack Gaming Environment.md |
| 16.5 KiB | .md |  |  | SpacetimeDB Guide | docs/sruth/tuatha/sruth/tuatha/SPACETIMEDB_GUIDE.md |
| 8.5 KiB | .md | Y |  | Sign In With Ethereum (SIWE)   Better Auth | docs/sruth/tuatha/sruth/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md |
| 34.8 KiB | .md |  |  | **Architectural Specification: Decentralized Geospatial Procedural Generation Systems for the 'Anam' Project** | docs/sruth/tuatha/sruth/tuatha/SpacetimeDB Ogham Stone Game Integration.md |
| 1.0 KiB | .md | Y |  | SpacetimeDB | docs/sruth/tuatha/sruth/tuatha/SpacetimeDB.md |
| 29.6 KiB | .md |  |  | **Architectural Convergence: Implementing a Massively Multiplayer Celtic Odyssey via SpacetimeDB, Solana, and Ethereum ( | docs/sruth/tuatha/sruth/tuatha/Spacetimedb Blockchain Integration Strategy.md |
| 10.4 KiB | .md | Y |  | Swift Transformers Reaches 1.0 – and Looks to the Future | docs/sruth/tuatha/sruth/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md |
| 35.1 KiB | .md |  |  | **The Convergent Stack: Architecting Reactive Data Systems with TanStack DB, DuckDB, RisingWave, and Marimo** | docs/sruth/tuatha/sruth/tuatha/TanStack DB Integration and Comparison.md |
| 50.3 KiB | .md |  |  | Technical Integration Plan  Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly) | docs/sruth/tuatha/sruth/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md |
| 21.5 KiB | .md | Y | G (4) | The Expulsion of the Déisi   Wikipedia | docs/sruth/tuatha/sruth/tuatha/The Expulsion of the Déisi - Wikipedia.md |
| 7.1 KiB | .md | Y |  | Unsloth Model Catalog   Unsloth Documentation | docs/sruth/tuatha/sruth/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md |
| 20.1 KiB | .md |  |  | WGPU Guide | docs/sruth/tuatha/sruth/tuatha/WGPU_GUIDE.md |
| 29.3 KiB | .md |  |  | **Architectural Blueprint for "Cianfhoghlaim": A Decentralized, Physical-Digital Educational Ecosystem** | docs/sruth/tuatha/sruth/tuatha/Web3 Classroom Response System Design.md |
| 40.9 KiB | .md |  |  | **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Educational Ecosystem* | docs/sruth/tuatha/sruth/tuatha/Web3 Gamified Education & Asset Generation.md |
| 12.1 KiB | .md |  |  | API Reference Index | docs/sruth/tuatha/sruth/tuatha/api-README.md |
| 6.9 KiB | .md | Y |  | apple ml fastvlm  This repository contains the official implementation of  FastVLM  Efficient Vision Encoding for Vision | docs/sruth/tuatha/sruth/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md |
| 32.2 KiB | .md |  |  | **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supe | docs/sruth/tuatha/sruth/tuatha/celtic-ocr.md |
| 16.3 KiB | .md |  |  | Building an "Anam" Celtic educational MMO: technical foundations | docs/sruth/tuatha/sruth/tuatha/celtic_mmo.md |
| 28.2 KiB | .md |  |  | Agentic UI learning pipeline: a multi-agent architecture for automated web scraping and design system extraction | docs/sruth/tuatha/sruth/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md |
| 38.4 KiB | .md |  |  | Define the source using dlt's declarative REST API configuration | docs/sruth/tuatha/sruth/tuatha/dlt_crawl4ai_lancedb.md |
| 18.9 KiB | .md |  |  | Educational Game Development | docs/sruth/tuatha/sruth/tuatha/educational-game-development.md |
| 38.5 KiB | .md |  |  | **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem** | docs/sruth/tuatha/sruth/tuatha/engine-selection.md |
| 33.1 KiB | .md |  |  | **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device | docs/sruth/tuatha/sruth/tuatha/federated-marketplace.md |
| 1.6 KiB | .md |  |  | Game Design | docs/sruth/tuatha/sruth/tuatha/game-design-README.md |
| 1.3 KiB | .md |  |  | Contributing | docs/sruth/tuatha/sruth/tuatha/game_CONTRIBUTING.md |
| 5.3 KiB | .md |  |  | Development | docs/sruth/tuatha/sruth/tuatha/game_DEVELOPMENT.md |
| 27.2 KiB | .md | Y |  | game siwe auth | docs/sruth/tuatha/sruth/tuatha/game_siwe-auth.md |
| 6.0 KiB | .md |  |  | Rust bindings for Godot 4 | docs/sruth/tuatha/sruth/tuatha/gdext-ReadMe.md |
| 32.0 KiB | .md |  |  | **Strategic Architecture for Converged Agentic Ecosystems: Integrating iOS Vision Intelligence with Cross-Platform Devel | docs/sruth/tuatha/sruth/tuatha/iOS App Development Ecosystem Strategy.md |
| 2.2 KiB | .md |  |  | Infrastructure | docs/sruth/tuatha/sruth/tuatha/infrastructure-README.md |
| 40.9 KiB | .md |  |  | **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations** | docs/sruth/tuatha/sruth/tuatha/learn-to-earn-model.md |
| 1.4 KiB | .md |  |  | ML Models | docs/sruth/tuatha/sruth/tuatha/ml-models-README.md |
| 38.8 KiB | .md |  |  | **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse** | docs/sruth/tuatha/sruth/tuatha/mythology-framework.md |
| 1.7 KiB | .md |  |  | AnyLanguageModel — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-AnyLanguageModel.md |
| 1.7 KiB | .md |  |  | SpacetimeDB — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-SpacetimeDB.md |
| 2.2 KiB | .md |  |  | agui_kotlin — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-agui_kotlin.md |
| 1.8 KiB | .md |  |  | hophacks-spacetimedb-workshop — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-hophacks-spacetimedb-workshop.md |
| 1.4 KiB | .md |  |  | ireland — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-ireland.md |
| 1.5 KiB | .md |  |  | react-native-godot — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-react-native-godot.md |
| 1.3 KiB | .md |  |  | react-native-reusables — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-react-native-reusables.md |
| 2.5 KiB | .md |  |  | SpacetimeDB Cookbook — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-spacetimedb-cookbook.md |
| 2.1 KiB | .md |  |  | spacetimedb-typescript-sdk — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-spacetimedb-typescript-sdk.md |
| 3.0 KiB | .md |  |  | wgpu — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-wgpu.md |
| 1.5 KiB | .md |  |  | x402 — KCG Summary | docs/sruth/tuatha/sruth/tuatha/repo-x402.md |
| 3.4 KiB | .md | Y |  | syft flwr notebooks fedrag README.md at main · OpenMined syft flwr | docs/sruth/tuatha/sruth/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md |
| 1.2 KiB | .md |  |  | Tokenomics | docs/sruth/tuatha/sruth/tuatha/tokenomics-README.md |
| 7.1 KiB | .md | Y |  | unsloth catalog | docs/sruth/tuatha/sruth/tuatha/unsloth-catalog.md |
| 9.8 KiB | .md | Y |  | useAgent Hook | docs/sruth/tuatha/sruth/tuatha/useAgent Hook.md |
| 35.5 KiB | .md |  |  | **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the British Isles** | docs/sruth/tuatha/sruth/tuatha/world-map.md |
| 40.9 KiB | .md |  |  | **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Educational Ecosystem* | docs/sruth/tuatha/sruth/tuatha/x402-payments.md |

## 6. Super-Cluster Candidates (Consolidation Target Structure)

Proposed 12-cluster regrouping of all docs content:

### 01-Agents & Agentic Workflows

**Description:** Multi-agent systems, MCP protocol, browser orchestration, Agno/Google ADK frameworks
**Count:** 162 files, 4.6 MiB

- **docs/agents** (39 files):
  - `docs/agents/AGENT_IMPLEMENTATIONS_SUMMARY.md` — Agent-Related Implementations Analysis
  - `docs/agents/AGNO_COMPREHENSIVE_REFERENCE.md` — Agno Framework: Comprehensive Architecture Reference
  - `docs/agents/AI Agents for Irish Language Resources.md` — MERGED INTO IRISH_EDUCATION_PLATFORM_BLUEPRINT.md
  - `docs/agents/Agent UI Ecosystem - A2UI.md` — Agent UI Ecosystem   A2UI
  - `docs/agents/Agent _ Firecrawl.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/Agentic Education Platform Development.md` — MERGED INTO IRISH_EDUCATION_PLATFORM_BLUEPRINT.md
  - `docs/agents/Agentic Translation Workflow Technologies.md` — MERGED INTO IRISH_EDUCATION_PLATFORM_BLUEPRINT.md
  - `docs/agents/Agentic Web Scraping Pipeline.md` — MERGED INTO BAML_COMPREHENSIVE_GUIDE.md
  - `docs/agents/BAML Schemas for Irish Education.md` — MERGED INTO BAML_COMPREHENSIVE_GUIDE.md
  - `docs/agents/BAML for Syllabus-Driven Data Extraction.md` — MERGED INTO BAML_COMPREHENSIVE_GUIDE.md
  - `docs/agents/BAML_COMPREHENSIVE_GUIDE.md` — BAML Comprehensive Guide: Patterns, Architecture, and Production Applications
  - `docs/agents/BAML_DUCKDB_DRAGONFLY_ANALYSIS.md` — MERGED INTO BAML_COMPREHENSIVE_GUIDE.md
  - `docs/agents/BROWSER_AUTOMATION_PLATFORM.md` — Browser Automation Platform Reference
  - `docs/agents/CONVEX_AGENT_PLATFORM.md` — Convex Agent Platform Reference
  - `docs/agents/DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md` — Durable Execution: Restate & DBOS — Comprehensive Reference
  - `docs/agents/GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md` — Google Agent Development Kit (ADK) — Comprehensive Reference
  - `docs/agents/INDEX.md` — Agent Documentation Index
  - `docs/agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md` — Irish Education Platform Blueprint: Agentic Systems for Celtic Education
  - `docs/agents/MCP Server with x402.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/MCP Server.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/MCP Toolbox.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/MCP _ Better Auth.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/MCP-UI.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/MCP_COMPREHENSIVE_RESEARCH.md` — MCP Comprehensive Research: Protocol, Integration, and Applications
  - `docs/agents/MCP_RESEARCH.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/PYDIANTIC_AI_REFERENCE.md` — Pydantic AI Reference
  - `docs/agents/STAGEHAND_COMPREHENSIVE_REFERENCE.md` — Stagehand Comprehensive Reference: Browser Automation with AI
  - `docs/agents/Sign In With Ethereum (SIWE) _ Better Auth.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/agent-frameworks.md` — agent frameworks
  - `docs/agents/agno-architecture-guide.md` — MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md
  - `docs/agents/agno-openapi-specification-research.md` — MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md
  - `docs/agents/agno_architecure_z_ai.md` — MERGED INTO AGNO_COMPREHENSIVE_REFERENCE.md
  - `docs/agents/ai-sdk-tools.md` — ai sdk tools
  - `docs/agents/backend-platforms.md` — uackend platforms
  - `docs/agents/baml-patterns-and-best-practices.md` — MERGED INTO BAML_COMPREHENSIVE_GUIDE.md
  - `docs/agents/browser-automation.md` — urowser automation
  - `docs/agents/mcp-research-report.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/mcp-ui-gradio-evidence-integration-analysis.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
  - `docs/agents/x402_examples_typescript_servers_hono at main · coinbase_x402.md` — MERGED INTO MCP_COMPREHENSIVE_RESEARCH.md
- **docs/bonneagar** (8 files):
  - `docs/bonneagar/MCP Server Transports_ STDIO, Streamable HTTP & SSE.md` — MCP Server Transports  STDIO, Streamable HTTP & SSE
  - `docs/bonneagar/Open-Source Crawl4ai Anti-Bot Stack.md` — **Architectural Paradigms for Self-Hosted Autonomous Web Scraping: A Deep Technical Analysis of Clou
  - `docs/bonneagar/README.md` — Celtic Education Scraping Agent
  - `docs/bonneagar/Using MCP in Roo Code _ Roo Code Documentation.md` — Using MCP in Roo Code   Roo Code Documentation
  - `docs/bonneagar/agentic-scraping-architecture.md` — Agentic Scraping Architecture: Hunter-Gatherer-Operator Pattern
  - `docs/bonneagar/knowledge-graph-infrastructure.md` — Knowledge Graph Infrastructure: Unified Architecture Guide
  - `docs/bonneagar/web-scraping-automation.md` — Web Scraping & Automation
  - `docs/bonneagar/where-to-install-1password-cli-op.md` — where to install 1password cli op
- **docs/context** (21 files):
  - `docs/context/00-core/CLAUDE.md` — Cianfhoghlaim - AI Agent Instructions
  - `docs/context/00-core/CONSTRAINTS.md` — Critical Constraints
  - `docs/context/01-patterns/AGENTS.md` — Pattern: Agent Design
  - `docs/context/01-patterns/WEB.md` — Pattern: Web Frameworks (TanStack, AG-UI, MCP-UI)
  - `docs/context/02-architecture/AGENT_IMPLEMENTATIONS.md` — Agent-Related Implementations Analysis
  - `docs/context/02-architecture/MULTI_AGENT_PRODUCTION.md` — Building Production Multi-Agent Systems: Complete Implementation Guide
  - `docs/context/02-architecture/OIDEACHAIS_PIPELINE.md` — oideachais - Unified Celtic Education Platform
  - `docs/context/02-architecture/TUATH_MMO.md` — Tuath System Architecture
  - `docs/context/04-agents/MCP_RESEARCH.md` — Model Context Protocol (MCP) - Comprehensive Research Report
  - `docs/context/04-agents/TECH_STACK.md` — **Technical Blueprint for a Next-Generation Leaving Certificate Education Platform: Architecture, Pe
  - `docs/context/04-agents/TUATH_QUICKSTART.md` — Tuath Celtic Educational MMO - Quick Start
  - `docs/context/04-agents/browser_orchestrator.py` — browser orchestrator
  - `docs/context/04-agents/browser_session.py` — browser session
  - `docs/context/04-agents/durable_orchestrator.py` — durable orchestrator
  - `docs/context/07-skills/agno.md` — Agno - AI Agent Framework
  - `docs/context/08-examples/OPENSPEC_AGENTS.md` — OpenSpec Instructions for Cianfhoghlaim
  - `docs/context/package-ecosystem/ai-frameworks/agno.md` — Agno — Multi-Agent Orchestration Framework
  - `docs/context/package-ecosystem/ai-frameworks/google-adk.md` — Google ADK — Agent Development Kit
  - `docs/context/package-ecosystem/ai-frameworks/pydantic-ai.md` — Pydantic AI — Agent Framework with Structured Validation
  - `docs/context/package-ecosystem/frontend/ag-ui.md` — AG-UI — Agent-User Interaction Protocol (SSE)
  - `docs/context/package-ecosystem/frontend/copilotkit.md` — CopilotKit — AI Agent UI Components
- **docs/data_engineering** (3 files):
  - `docs/data_engineering/Generative AI Art Workflow Integration.md` — **Architecting Agentic Creative Workflows: Deep Research into Generative AI Integration for React Ec
  - `docs/data_engineering/cocoindex-comprehensive.md` — CocoIndex Comprehensive Guide
  - `docs/data_engineering/stage-3-production-multi-agent-systems.md` — Building Production Multi-Agent Systems: Complete Implementation Guide
- **docs/meaisínfhoghlaim** (13 files):
  - `docs/meaisínfhoghlaim/AGENTS.md` — Meaisínfhoghlaim (Machine Learning) - AI Agent Instructions
  - `docs/meaisínfhoghlaim/AI_MEMORY.md` — AI Memory, Agents & Knowledge Management
  - `docs/meaisínfhoghlaim/Agentic Crypto Platform Scaling Research.md` — **Architectural Due Diligence: Scaling the Crypteolas Agentic PaaS**
  - `docs/meaisínfhoghlaim/BAML, DLT, and AI Workflow Integration.md` — **Unified Schema Architecture for Agentic AI Systems: Integrating BAML, dlt, and TanStack AI across 
  - `docs/meaisínfhoghlaim/Building an Agentic Tutor.md` — **Architectural Blueprint for Autonomous Agentic Tutoring Systems: Integrating Hybrid Knowledge Grap
  - `docs/meaisínfhoghlaim/Federated AI Marketplace on iPhone.md` — **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Pay
  - `docs/meaisínfhoghlaim/INDEX.md` — Meaisínfhoghlaim — Machine Learning Research Index
  - `docs/meaisínfhoghlaim/Interactive AI Pipeline Development.md` — **Architectural Convergence: The Agentic Pipeline for Structured Generative AI**
  - `docs/meaisínfhoghlaim/Open-Source VLMs For PDF Extraction.md` — **The Semantic Frontier: A Comprehensive Architectural Analysis of Provider-Agnostic Document Intell
  - `docs/meaisínfhoghlaim/agent-patterns-reference.md` — Agent Patterns, MCP, and Autonomous Systems
  - `docs/meaisínfhoghlaim/agent-patterns.md` — agent patterns
  - `docs/meaisínfhoghlaim/iOS App Development Ecosystem Strategy.md` — **Strategic Architecture for Converged Agentic Ecosystems: Integrating iOS Vision Intelligence with 
  - `docs/meaisínfhoghlaim/motherduck_mcp.md` — MotherDuck's DuckDB MCP Server
- **docs/teanga** (16 files):
  - `docs/teanga/AI Agents for Irish Language Resources.md` — **Architecting the Neuro-Symbolic Gaeilge Engine: A Technical Blueprint for Agentic Knowledge Extrac
  - `docs/teanga/Agentic Education Platform Development.md` — **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Ed
  - `docs/teanga/Agentic Translation Workflow Technologies.md` — **The Neuro-Symbolic Agentic Translation Architecture: A Comprehensive Blueprint Leveraging T5Gemma-
  - `docs/teanga/Agentic Web Scraping Pipeline.md` — **Autonomous Web Intelligence Architecture: A Comprehensive Implementation Framework for Agentic Scr
  - `docs/teanga/BAML for Syllabus-Driven Data Extraction.md` — **Architecting the Adaptive Classroom: A Technical Blueprint for Agentic Educational Systems Using A
  - `docs/teanga/BAML, DLT, and AI Workflow Integration.md` — **Unified Schema Architecture for Agentic AI Systems: Integrating BAML, dlt, and TanStack AI across 
  - `docs/teanga/BAML, Graphiti, Tanstack AI Pipeline.md` — **ARCHITECTURAL CONVERGENCE FOR DETERMINISTIC AGENTIC SYSTEMS: INTEGRATING BAML, GRAPHITI, AND TANST
  - `docs/teanga/Celtic Data Scraping and Integration Plan.md` — **Computational Archiving of Celtic Digital Heritage: An Exhaustive Analysis of Skyvern Integration 
  - `docs/teanga/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md` — ChromeDevTools chrome devtools mcp  Chrome DevTools for coding agents
  - `docs/teanga/Enhancing English-Irish Translation with Diffusion Models.md` — **The Convergence of Diffusion Generative Models and Agentic Workflows: A Paradigm Shift for Low-Res
  - `docs/teanga/Game Development Research & AI Integration.md` — **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem**
  - `docs/teanga/Graph Tech Integration and Recommendation.md` — **Architectural Unification of Agentic Memory: Synthesizing Cognee, Cocoindex, and Graphiti within H
  - `docs/teanga/Interactive Map & AI Agents.md` — **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the Britis
  - `docs/teanga/kscanne-gbb-generation-conversation-README.md` — kscanne gbb generation conversation README
  - `docs/teanga/motherduck_mcp.md` — MotherDuck's DuckDB MCP Server
  - `docs/teanga/useAgent Hook.md` — useAgent Hook
- **docs/tuatha** (54 files):
  - `docs/sruth/tuatha/ADDING_AGENTS.md` — Adding New Agents
  - `docs/sruth/tuatha/ADDING_TOOLS.md` — Adding Agent Tools
  - `docs/sruth/tuatha/AGENTS.md` — Tuath Agent Architecture
  - `docs/sruth/tuatha/Agentic Education Platform Development.md` — **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Ed
  - `docs/sruth/tuatha/Agentic Web Scraping Pipeline.md` — **Autonomous Web Intelligence Architecture: A Comprehensive Implementation Framework for Agentic Scr
  - `docs/sruth/tuatha/Building an Educational Agent's Knowledge Base.md` — **Architecting the Autonomous Epistemologist: A Technical Blueprint for Agentic Knowledge Acquisitio
  - `docs/sruth/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md` — Crypteolas Agent Integration Guide
  - `docs/sruth/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md` — Comparing the Top 6 Agent Native Rails for the Agentic Internet  MCP, A2A, AP2, ACP, x402, and Kite
  - `docs/sruth/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md` — **Project Crypteolas: A Decentralized Architecture for Financial Knowledge Graph Federated Learning 
  - `docs/sruth/tuatha/Crypto Analysis AI Agent System Architecture.md` — Crypto Analysis AI Agent System Architecture
  - `docs/sruth/tuatha/Federated AI Marketplace on iPhone.md` — **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Pay
  - `docs/sruth/tuatha/Game Development Research & AI Integration.md` — **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem**
  - `docs/sruth/tuatha/Game Reverse Engineering Workflow Design.md` — **Architectural Blueprint for Autonomous Reverse Engineering and Asset Reconstruction Systems: A Dee
  - `docs/sruth/tuatha/Generative AI Art Workflow Integration.md` — **Architecting Agentic Creative Workflows: Deep Research into Generative AI Integration for React Ec
  - `docs/sruth/tuatha/Interactive AI Pipeline Development.md` — **Architectural Convergence: The Agentic Pipeline for Structured Generative AI**
  - `docs/sruth/tuatha/Interactive Map & AI Agents.md` — **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the Britis
  - `docs/sruth/tuatha/Learn-to-Earn Blockchain and AI.md` — **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations**
  - `docs/sruth/tuatha/MCP-UI.md` — MCP UI
  - `docs/sruth/tuatha/Ogham Crypto MMO Research.md` — **Architecting Tuath: A Comprehensive Technical and Cultural Analysis of Decentralized MMO Infrastru
  - `docs/sruth/tuatha/Web3 Gamified Education & Asset Generation.md` — **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Ed
  - `docs/sruth/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md` — Agentic UI learning pipeline: a multi-agent architecture for automated web scraping and design syste
  - `docs/sruth/tuatha/engine-selection.md` — **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem**
  - `docs/sruth/tuatha/federated-marketplace.md` — **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Pay
  - `docs/sruth/tuatha/iOS App Development Ecosystem Strategy.md` — **Strategic Architecture for Converged Agentic Ecosystems: Integrating iOS Vision Intelligence with 
  - `docs/sruth/tuatha/learn-to-earn-model.md` — **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations**
  - `docs/sruth/tuatha/sruth/tuatha/ADDING_AGENTS.md` — Adding New Agents
  - `docs/sruth/tuatha/sruth/tuatha/ADDING_TOOLS.md` — Adding Agent Tools
  - `docs/sruth/tuatha/sruth/tuatha/AGENTS.md` — Tuath Agent Architecture
  - `docs/sruth/tuatha/sruth/tuatha/Agentic Education Platform Development.md` — **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Ed
  - `docs/sruth/tuatha/sruth/tuatha/Agentic Web Scraping Pipeline.md` — **Autonomous Web Intelligence Architecture: A Comprehensive Implementation Framework for Agentic Scr
  - `docs/sruth/tuatha/sruth/tuatha/Building an Educational Agent's Knowledge Base.md` — **Architecting the Autonomous Epistemologist: A Technical Blueprint for Agentic Knowledge Acquisitio
  - `docs/sruth/tuatha/sruth/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md` — Crypteolas Agent Integration Guide
  - `docs/sruth/tuatha/sruth/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md` — Comparing the Top 6 Agent Native Rails for the Agentic Internet  MCP, A2A, AP2, ACP, x402, and Kite
  - `docs/sruth/tuatha/sruth/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md` — **Project Crypteolas: A Decentralized Architecture for Financial Knowledge Graph Federated Learning 
  - `docs/sruth/tuatha/sruth/tuatha/Crypto Analysis AI Agent System Architecture.md` — Crypto Analysis AI Agent System Architecture
  - `docs/sruth/tuatha/sruth/tuatha/Federated AI Marketplace on iPhone.md` — **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Pay
  - `docs/sruth/tuatha/sruth/tuatha/Game Development Research & AI Integration.md` — **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem**
  - `docs/sruth/tuatha/sruth/tuatha/Game Reverse Engineering Workflow Design.md` — **Architectural Blueprint for Autonomous Reverse Engineering and Asset Reconstruction Systems: A Dee
  - `docs/sruth/tuatha/sruth/tuatha/Generative AI Art Workflow Integration.md` — **Architecting Agentic Creative Workflows: Deep Research into Generative AI Integration for React Ec
  - `docs/sruth/tuatha/sruth/tuatha/Interactive AI Pipeline Development.md` — **Architectural Convergence: The Agentic Pipeline for Structured Generative AI**
  - `docs/sruth/tuatha/sruth/tuatha/Interactive Map & AI Agents.md` — **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the Britis
  - `docs/sruth/tuatha/sruth/tuatha/Learn-to-Earn Blockchain and AI.md` — **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations**
  - `docs/sruth/tuatha/sruth/tuatha/MCP-UI.md` — MCP UI
  - `docs/sruth/tuatha/sruth/tuatha/Ogham Crypto MMO Research.md` — **Architecting Tuath: A Comprehensive Technical and Cultural Analysis of Decentralized MMO Infrastru
  - `docs/sruth/tuatha/sruth/tuatha/Web3 Gamified Education & Asset Generation.md` — **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Ed
  - `docs/sruth/tuatha/sruth/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md` — Agentic UI learning pipeline: a multi-agent architecture for automated web scraping and design syste
  - `docs/sruth/tuatha/sruth/tuatha/engine-selection.md` — **Architectural Convergence in the Digital Heritage Economy: The 'Anam' MMO Ecosystem**
  - `docs/sruth/tuatha/sruth/tuatha/federated-marketplace.md` — **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Pay
  - `docs/sruth/tuatha/sruth/tuatha/iOS App Development Ecosystem Strategy.md` — **Strategic Architecture for Converged Agentic Ecosystems: Integrating iOS Vision Intelligence with 
  - `docs/sruth/tuatha/sruth/tuatha/learn-to-earn-model.md` — **Cianfhoghlaim: A Strategic Framework for Agentic Educational Ecosystems in the Celtic Nations**
  - `docs/sruth/tuatha/sruth/tuatha/useAgent Hook.md` — useAgent Hook
  - `docs/sruth/tuatha/sruth/tuatha/x402-payments.md` — **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Ed
  - `docs/sruth/tuatha/useAgent Hook.md` — useAgent Hook
  - `docs/sruth/tuatha/x402-payments.md` — **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Ed
- **docs/web** (8 files):
  - `docs/web/AG-UI Goes Mobile_ The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM.md` — AG UI Goes Mobile  The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM
  - `docs/web/BAML, Graphiti, Tanstack AI Pipeline.md` — **ARCHITECTURAL CONVERGENCE FOR DETERMINISTIC AGENTIC SYSTEMS: INTEGRATING BAML, GRAPHITI, AND TANST
  - `docs/web/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md` — ChromeDevTools chrome devtools mcp  Chrome DevTools for coding agents
  - `docs/web/Playground _ Convex Developer Hub.md` — Playground   Convex Developer Hub
  - `docs/web/RAG (Retrieval-Augmented Generation) with the Agent component _ Convex Developer Hub.md` — RAG (Retrieval Augmented Generation) with the Agent component   Convex Developer Hub
  - `docs/web/agentic-platform.md` — **Architecting the Agentic Academy: A Technical and Cultural Blueprint for a Decentralized Celtic Ed
  - `docs/web/mcp-ui-integration.md` — mcp ui integration
  - `docs/web/repo-restate-coding-agent.md` — Restate.dev Coding Agent — KCG Summary

### 02-BAML & Structured Extraction

**Description:** BAML schema-first extraction, structured LLM output, Pydantic/DSPy patterns
**Count:** 27 files, 844.9 KiB

- **docs/bonneagar** (2 files):
  - `docs/bonneagar/ai-pipelines.md` — AI-Native Data Pipelines
  - `docs/bonneagar/knowledge-graph-schema.md` — Cryptocurrency Knowledge Graph Schema
- **docs/context** (5 files):
  - `docs/context/01-patterns/BAML.md` — Pattern: BAML (Type-Safe LLM Extraction)
  - `docs/context/05-celtic-language/IRISH_ENGLISH_EDUCATION.md` — Technical Architecture for a Bilingual Irish/English Mathematics Education System
  - `docs/context/07-skills/baml.md` — BAML - Type-Safe LLM Development
  - `docs/context/07-skills/dlt.md` — dlt - Data Load Tool
  - `docs/context/package-ecosystem/ai-frameworks/baml.md` — BAML — Type-Safe LLM Extraction DSL
- **docs/data_engineering** (4 files):
  - `docs/data_engineering/Ontology and Temporal Graphs Research.md` — **Architectural Convergence: BAML, CocoIndex, Cognee, and Graphiti in Temporal Ontology Engineering*
  - `docs/data_engineering/assistant.md` — Feast Expert Assistant
  - `docs/data_engineering/data-pipeline-architecture.md` — Data Pipeline Architecture
  - `docs/data_engineering/knowledge-systems.md` — Knowledge Systems Reference
- **docs/meaisínfhoghlaim** (6 files):
  - `docs/meaisínfhoghlaim/AI Chemistry Education Image Generation.md` — **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Stru
  - `docs/meaisínfhoghlaim/AI Syllabus to JSON Schema.md` — **Bria Fibo and the Hugging Face Ecosystem: Architecting Educational Visualization Pipelines via Str
  - `docs/meaisínfhoghlaim/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md` — Auto Optimize Pydantic Models for Structured Information Extraction  A Complete Guide to DSPydantic
  - `docs/meaisínfhoghlaim/Prompt Optimization (Beta)(2).md` — Prompt Optimization (Beta)(2)
  - `docs/meaisínfhoghlaim/Prompt Optimization (Beta)(3).md` — Prompt Optimization (Beta)(3)
  - `docs/meaisínfhoghlaim/Prompt Optimization (Beta).md` — Prompt Optimization (Beta)
- **docs/teanga** (5 files):
  - `docs/teanga/AI Chemistry Education Image Generation.md` — **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Stru
  - `docs/teanga/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md` — Auto Optimize Pydantic Models for Structured Information Extraction  A Complete Guide to DSPydantic
  - `docs/teanga/BAML Schemas for Irish Education.md` — **Semantic Indexing and Knowledge Graph Architecture for the Irish Education System: A Comprehensive
  - `docs/teanga/Integrating TanStack AI with LiteLLM.md` — **Architecting the Isomorphic AI Tutor: A Comprehensive Research Report on Integrating TanStack AI, 
  - `docs/teanga/irish-english-education.md` — Technical Architecture for a Bilingual Irish/English Mathematics Education System
- **docs/tuatha** (4 files):
  - `docs/sruth/tuatha/AI Chemistry Education Image Generation.md` — **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Stru
  - `docs/sruth/tuatha/dlt_crawl4ai_lancedb.md` — Define the source using dlt's declarative REST API configuration
  - `docs/sruth/tuatha/sruth/tuatha/AI Chemistry Education Image Generation.md` — **Advanced Computational Workflows for Bilingual Educational Asset Generation: Integrating BAML Stru
  - `docs/sruth/tuatha/sruth/tuatha/dlt_crawl4ai_lancedb.md` — Define the source using dlt's declarative REST API configuration
- **docs/web** (1 files):
  - `docs/web/Integrating TanStack AI with LiteLLM.md` — **Architecting the Isomorphic AI Tutor: A Comprehensive Research Report on Integrating TanStack AI, 

### 03-OCR, VLMs & Document Intelligence

**Description:** OCR pipelines, handwriting recognition, QwenVL fine-tuning, document processing, FastVLM
**Count:** 41 files, 942.5 KiB

- **docs/bonneagar** (3 files):
  - `docs/bonneagar/document-processing-pipeline.md` — Document Processing Pipeline for Cryptocurrency Analytics
  - `docs/bonneagar/engineering.md` — Platform Engineering
  - `docs/bonneagar/vlm-ocr-comparison.md` — Vision-Language Models & OCR Systems Comparison
- **docs/context** (2 files):
  - `docs/context/02-architecture/DOCUMENT_PROCESSING.md` — Document Processing Pipeline for Cryptocurrency Analytics
  - `docs/context/package-ecosystem/embedding/colpali.md` — ColPali — Visual Late-Interaction Document Retrieval
- **docs/meaisínfhoghlaim** (14 files):
  - `docs/meaisínfhoghlaim/ANALYSIS_SUMMARY.md` — Comprehensive Analysis of HuggingFace Examples Directory
  - `docs/meaisínfhoghlaim/Blaizzy_mlx-vlm_ MLX-VLM is a package for inference and fine-tuning of Vision Language Models (VLMs) on your Mac using MLX..md` — Blaizzy mlx vlm  MLX VLM is a package for inference and fine tuning of Vision Language Models (VLMs)
  - `docs/meaisínfhoghlaim/Finetuning Qwen3-VL for Gaelic OCR.md` — **Deep Research Report: End-to-End Fine-Tuning of Qwen3-VL for Historic Manuscript Transcription usi
  - `docs/meaisínfhoghlaim/LLM and OCR Deployment Research.md` — **Advanced Architectures for Document Intelligence on Apple Silicon: A Comprehensive Analysis of Pad
  - `docs/meaisínfhoghlaim/Multimodal Irish Handwriting Generation Model.md` — **Architecting a Sovereign Multimodal Neuro-Symbolic System for the Preservation and Generative Synt
  - `docs/meaisínfhoghlaim/QUICK_REFERENCE.md` — Quick Reference Guide: OCR Models & Integration
  - `docs/meaisínfhoghlaim/README_ANALYSIS.md` — HuggingFace OCR & Vision-Language Models - Complete Analysis
  - `docs/meaisínfhoghlaim/Setting Up Local LLM Services on Mac.md` — **Architecting the Sovereign AI Stack: A Comprehensive Analysis of Integrating Llama.cpp, MLX-VLM, D
  - `docs/meaisínfhoghlaim/Supercharge your OCR Pipelines with Open Models.md` — Supercharge your OCR Pipelines with Open Models
  - `docs/meaisínfhoghlaim/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md` — apple ml fastvlm  This repository contains the official implementation of  FastVLM  Efficient Vision
  - `docs/meaisínfhoghlaim/deepseek_ocr_(3b)_eval.py` — -*- coding: utf-8 -*-
  - `docs/meaisínfhoghlaim/document-processing-reference.md` — Document Processing & OCR: VLM, OCR, and Heritage Digitization
  - `docs/meaisínfhoghlaim/notebooklm_1.md` — notebooklm 1
  - `docs/meaisínfhoghlaim/ocr-reference.md` — ocr reference
- **docs/teanga** (16 files):
  - `docs/teanga/Aligning Gaelic Script for QwenVL Finetuning.md` — **Automated Weakly-Supervised Alignment of Historical Gaelic Manuscripts: A Pipeline for Fine-Tuning
  - `docs/teanga/Celtic Language OCR Resource Analysis.md` — **Automated Paleography and Visual Document Understanding for the Celtic Languages: A Comprehensive 
  - `docs/teanga/Finetuning Qwen3-VL for Gaelic OCR.md` — **Deep Research Report: End-to-End Fine-Tuning of Qwen3-VL for Historic Manuscript Transcription usi
  - `docs/teanga/Handwriting Recognition and Dataset Creation.md` — **Advanced Architectures for Bilingual Heritage Archiving and Mathematical Document Intelligence: A 
  - `docs/teanga/Irish Handwriting App Development.md` — **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analy
  - `docs/teanga/Multimodal Irish Handwriting Generation Model.md` — **Architecting a Sovereign Multimodal Neuro-Symbolic System for the Preservation and Generative Synt
  - `docs/teanga/handwriting-Handwriting Recognition and Dataset Creation.md` — **Advanced Architectures for Bilingual Heritage Archiving and Mathematical Document Intelligence: A 
  - `docs/teanga/handwriting-Irish Handwriting App Development.md` — **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analy
  - `docs/teanga/handwriting-Multimodal Irish Handwriting Generation Model.md` — **Architecting a Sovereign Multimodal Neuro-Symbolic System for the Preservation and Generative Synt
  - `docs/teanga/kscanne-gbb-proofing-ocr-README.md` — kscanne gbb proofing ocr README
  - `docs/teanga/notebooklm_1.md` — notebooklm 1
  - `docs/teanga/ocr-Aligning Gaelic Script for QwenVL Finetuning.md` — **Automated Weakly-Supervised Alignment of Historical Gaelic Manuscripts: A Pipeline for Fine-Tuning
  - `docs/teanga/ocr-Celtic Language OCR Resource Analysis.md` — **Automated Paleography and Visual Document Understanding for the Celtic Languages: A Comprehensive 
  - `docs/teanga/ocr-Finetuning Qwen3-VL for Gaelic OCR.md` — **Deep Research Report: End-to-End Fine-Tuning of Qwen3-VL for Historic Manuscript Transcription usi
  - `docs/teanga/repo-escriptorium.md` — KCG_SUMMARY: eScriptorium — Historical Document Transcription Platform
  - `docs/teanga/repo-pylaia.md` — KCG_SUMMARY: PyLaia — Deep Learning Handwritten Text Recognition
- **docs/tuatha** (6 files):
  - `docs/sruth/tuatha/Irish Handwriting App Development.md` — **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analy
  - `docs/sruth/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md` — apple ml fastvlm  This repository contains the official implementation of  FastVLM  Efficient Vision
  - `docs/sruth/tuatha/celtic-ocr.md` — **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on i
  - `docs/sruth/tuatha/sruth/tuatha/Irish Handwriting App Development.md` — **Operationalizing Irish Handwriting Recognition on Apple Silicon: An Exhaustive Architectural Analy
  - `docs/sruth/tuatha/sruth/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md` — apple ml fastvlm  This repository contains the official implementation of  FastVLM  Efficient Vision
  - `docs/sruth/tuatha/sruth/tuatha/celtic-ocr.md` — **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on i

### 04-Data Pipelines & Orchestration

**Description:** Dagster, DLT, CocoIndex pipelines, data architecture, ETL patterns
**Count:** 50 files, 2.6 MiB

- **docs/bonneagar** (12 files):
  - `docs/bonneagar/Dagster Orchestration for Cocoindex, Graphiti.md` — **Architectural Blueprint for Mathematical Knowledge Extraction: A Modular Orchestration Strategy Us
  - `docs/bonneagar/Deploying Dagster to Google Cloud Platform _ Dagster Docs.md` — Deploying Dagster to Google Cloud Platform   Dagster Docs
  - `docs/bonneagar/KOMODO_COMPLETE_GUIDE.md` — Komodo — Complete Deployment Orchestration Guide
  - `docs/bonneagar/Monorepo Toolchain_ Mise, Dagger, Taskipy.md` — **Orchestrating the Polyglot Monorepo: A Comparative Architectural Analysis of Mise-en-place, Taskip
  - `docs/bonneagar/bunchloch.md` — Bunchloch Infrastructure Stack
  - `docs/bonneagar/dagger-pipeline-orchestration-komodo-pangolin-fullstack-deployment.md` — dagger pipeline orchestration komodo pangolin fullstack deployment
  - `docs/bonneagar/dagger-unified-pipeline-architecture.md` — Comprehensive Dagger Pipeline Orchestration
  - `docs/bonneagar/data-acquisition.md` — Data Acquisition & Integrations
  - `docs/bonneagar/deploy.md` — Pangolin Deployment Assistant
  - `docs/bonneagar/infrastructure-devops.md` — Infrastructure & DevOps
  - `docs/bonneagar/komodo-deployment.md` — Komodo Deployment and Orchestration
  - `docs/bonneagar/orchestration-infrastructure.md` — Model Orchestration & Infrastructure
- **docs/context** (12 files):
  - `docs/context/01-patterns/DATA_PIPELINE.md` — Pattern: Data Pipeline (DLT → Dagster → CocoIndex)
  - `docs/context/02-architecture/SRUTH_OVERVIEW.md` — Sruth - Data Flows
  - `docs/context/03-pipelines/dagster_definitions.py` — dagster definitions
  - `docs/context/03-pipelines/dagster_factories.py` — dagster factories
  - `docs/context/07-skills/cocoindex.md` — CocoIndex
  - `docs/context/07-skills/dagster.md` — Dagster - Modern Data Orchestration
  - `docs/context/07-skills/oideachas-pipeline.md` — Oideachas Pipeline
  - `docs/context/08-examples/DATA_ARCHITECTURE.md` — Data Architecture for Irish Education Platform
  - `docs/context/package-ecosystem/orchestration/cocoindex.md` — CocoIndex — Data Transformation Pipeline SDK
  - `docs/context/package-ecosystem/orchestration/dagster-sdk.md` — Dagster Python SDK — Data Orchestration Framework
  - `docs/context/package-ecosystem/orchestration/dlt.md` — dlt — Data Load Tool (Python SDK)
  - `docs/context/package-ecosystem/orchestration/sqlmesh.md` — SQLMesh — Data Transformation Framework
- **docs/data_engineering** (6 files):
  - `docs/data_engineering/DLT_COMPLETE_GUIDE.md` — DLT (Data Load Tool) — Complete Reference Guide
  - `docs/data_engineering/INDEX.md` — Data Engineering — Research Index
  - `docs/data_engineering/dagster-comprehensive.md` — Dagster Comprehensive Guide
  - `docs/data_engineering/data-architecture.md` — Data Architecture Reference
  - `docs/data_engineering/data-sources.md` — Geospatial Data Sources for Celtic Language Mapping
  - `docs/data_engineering/dlt-comprehensive.md` — dlt (Data Load Tool) Comprehensive Guide
- **docs/meaisínfhoghlaim** (3 files):
  - `docs/meaisínfhoghlaim/Integrating Skyvern with Crawl4AI_Stagehand.md` — **Architectural Convergence: Orchestrating Skyvern, Crawl4AI, and Stagehand for Semantic Web Mapping
  - `docs/meaisínfhoghlaim/Irish LLM for iPhone Development.md` — **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework
  - `docs/meaisínfhoghlaim/mlflow (dagster-mlflow) _ Dagster Docs.md` — mlflow (dagster mlflow)   Dagster Docs
- **docs/teanga** (7 files):
  - `docs/teanga/Celtic Language Educational Data Scrape.md` — **Celtic-Bench: A Comprehensive Technical and Linguistic Analysis of Educational Data Architectures 
  - `docs/teanga/Explore data with marimo _ dlt Docs.md` — Explore data with marimo   dlt Docs
  - `docs/teanga/Irish LLM for iPhone Development.md` — **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework
  - `docs/teanga/british_isles_parallel_data_sources.md` — Parallel Education Data Sources for the British Isles
  - `docs/teanga/datasets-british_isles_parallel_data_sources.md` — Parallel Education Data Sources for the British Isles
  - `docs/teanga/gaeilge.md` — gaeilge
  - `docs/teanga/irish-gaeilge.md` — irish gaeilge
- **docs/tuatha** (10 files):
  - `docs/sruth/tuatha/ADDING_DATA_SOURCES.md` — Adding Data Sources
  - `docs/sruth/tuatha/British Isles Game Dev Data Pipeline.md` — **Architectural Framework for Data-Driven 2.5D Geospatial Synthesis: Integrating Authoritative Briti
  - `docs/sruth/tuatha/Irish LLM for iPhone Development.md` — **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework
  - `docs/sruth/tuatha/PIPELINES.md` — Tuath Data Pipelines
  - `docs/sruth/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md` — Technical Integration Plan  Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly)
  - `docs/sruth/tuatha/sruth/tuatha/ADDING_DATA_SOURCES.md` — Adding Data Sources
  - `docs/sruth/tuatha/sruth/tuatha/British Isles Game Dev Data Pipeline.md` — **Architectural Framework for Data-Driven 2.5D Geospatial Synthesis: Integrating Authoritative Briti
  - `docs/sruth/tuatha/sruth/tuatha/Irish LLM for iPhone Development.md` — **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework
  - `docs/sruth/tuatha/sruth/tuatha/PIPELINES.md` — Tuath Data Pipelines
  - `docs/sruth/tuatha/sruth/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md` — Technical Integration Plan  Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly)

### 05-Knowledge Graphs & AI Memory

**Description:** Cognee, Graphiti, Memgraph, Neo4j, temporal knowledge graphs, entity resolution
**Count:** 13 files, 269.5 KiB

- **docs/bonneagar** (5 files):
  - `docs/bonneagar/Backend Strategy For Educational Tutoring System.md` — **Backend Architecture Strategy for a Bilingual Temporal Knowledge Graph in Mathematics Education**
  - `docs/bonneagar/cognee-entity-resolution.md` — Cognee: Entity Resolution and Knowledge Structuring
  - `docs/bonneagar/education-kg.md` — Education Knowledge Graph
  - `docs/bonneagar/graphiti-crypto-adaptation.md` — Graphiti Adaptation for Cryptocurrency Analytics
  - `docs/bonneagar/infrastructure-knowledge-graph.md` — Theme: Knowledge Graph Infrastructure & EdTech Backend
- **docs/context** (5 files):
  - `docs/context/07-skills/graphiti.md` — Graphiti
  - `docs/context/07-skills/memgraph.md` — Memgraph - High-Performance Graph Database
  - `docs/context/package-ecosystem/memory-kg/cognee-sdk.md` — Cognee Python SDK — GraphRAG Memory System
  - `docs/context/package-ecosystem/memory-kg/graphiti-sdk.md` — Graphiti Python SDK — Temporal Knowledge Graph
  - `docs/context/package-ecosystem/storage/neo4j.md` — Neo4j Python Driver — Graph Database SDK
- **docs/teanga** (1 files):
  - `docs/teanga/Backend Strategy For Educational Tutoring System.md` — **Backend Architecture Strategy for a Bilingual Temporal Knowledge Graph in Mathematics Education**
- **docs/tuatha** (2 files):
  - `docs/sruth/tuatha/Multimodal Video Knowledge Graph Pipeline.md` — **Architectural Blueprint for a Native Multimodal Knowledge Graph Pipeline: Integrating Video, Audio
  - `docs/sruth/tuatha/sruth/tuatha/Multimodal Video Knowledge Graph Pipeline.md` — **Architectural Blueprint for a Native Multimodal Knowledge Graph Pipeline: Integrating Video, Audio

### 06-Vector Storage & Lakehouse

**Description:** LanceDB, DuckDB, DuckLake, MotherDuck, embeddings, vector search, data versioning
**Count:** 49 files, 1.3 MiB

- **docs/bonneagar** (8 files):
  - `docs/bonneagar/Docker Compose Setup for Data Tools.md` — **Architecting the Composable Data Fabric: A Definitive Implementation Guide for Local-First Lakehou
  - `docs/bonneagar/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md` — From BI to AI  A Modern Lakehouse Stack with Lance and Iceberg
  - `docs/bonneagar/Rust Client.md` — Rust Client
  - `docs/bonneagar/deploying-komodo-periphery-pangolin-private-access-lancedb-stack.md` — deploying komodo periphery pangolin private access lancedb stack
  - `docs/bonneagar/embedding_vs_statistical.py` — embedding vs statistical
  - `docs/bonneagar/hosting-lancedb-docker-compose.md` — hosting lancedb docker compose
  - `docs/bonneagar/lakehouse-architecture.md` — Real-Time Open Data Lakehouse Architecture
  - `docs/bonneagar/metadata-control-plane.md` — Metadata Control Plane: DuckDB-Backed Dynamic Source Management
- **docs/context** (13 files):
  - `docs/context/01-patterns/EMBEDDINGS.md` — Pattern: Embeddings (Batching, Models, Indexes)
  - `docs/context/01-patterns/STORAGE.md` — Pattern: Storage (DuckDB, LanceDB, DuckLake)
  - `docs/context/03-pipelines/curriculum_embedding.py` — curriculum embedding
  - `docs/context/03-pipelines/storage_init.py` — storage init
  - `docs/context/05-celtic-language/LANGUAGE_ARCHITECTURE.md` — DuckLake Unified Platform - Architecture Analysis
  - `docs/context/06-infrastructure/models_registry.yaml` — ===========================================================================
  - `docs/context/07-skills/duckdb.md` — DuckDB - In-Process Analytical Database
  - `docs/context/07-skills/lancedb.md` — LanceDB - Embedded Vector Database
  - `docs/context/package-ecosystem/embedding/bge-m3.md` — BGE-M3 — Multilingual Embedding Model
  - `docs/context/package-ecosystem/embedding/gabert.md` — GaBERT — Irish Language BERT Embedding Model
  - `docs/context/package-ecosystem/storage/cloudflare-r2.md` — Cloudflare R2 — Zero-Egress Object Storage SDK
  - `docs/context/package-ecosystem/storage/duckdb.md` — DuckDB — Embedded Analytical Database
  - `docs/context/package-ecosystem/storage/ducklake.md` — DuckLake — Lightweight Data Lakehouse on Object Storage
- **docs/data_engineering** (5 files):
  - `docs/data_engineering/data-versioning.md` — Data Versioning Reference
  - `docs/data_engineering/duckdb-reference.md` — DuckDB Reference
  - `docs/data_engineering/init.md` — Initialize LanceDB in Project
  - `docs/data_engineering/lancedb-reference.md` — LanceDB Reference
  - `docs/data_engineering/quickref.md` — LanceDB Quick Reference
- **docs/meaisínfhoghlaim** (2 files):
  - `docs/meaisínfhoghlaim/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md` — Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray
  - `docs/meaisínfhoghlaim/ducklake_explorer.py` — Local development
- **docs/teanga** (14 files):
  - `docs/teanga/ARCHITECTURE_ANALYSIS.md` — DuckLake Unified Platform - Architecture Analysis
  - `docs/teanga/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md` — From BI to AI  A Modern Lakehouse Stack with Lance and Iceberg
  - `docs/teanga/Geospatial Data Analysis and DuckDB.md` — **Convergence of Spatial Analytics and Digital Folkloristics: A Technical and Theoretical Examinatio
  - `docs/teanga/Geospatial Data Visualization with Ibis.md` — **Modernizing Educational Geospatial Intelligence: A Comprehensive Architectural Analysis of Ibis, D
  - `docs/teanga/Ibis, LanceDB, and Data Stack Integration.md` — **The Converged Lakehouse: Architecting a Multimodal Data Environment with Lance Namespace and the C
  - `docs/teanga/Iceberg in the Browser.md` — Iceberg in the Browser
  - `docs/teanga/Integrating Olake, Lakekeeper, RisingWave.md` — **Architecting the Real-Time Open Data Lakehouse: A Comprehensive Technical Analysis of Integrating 
  - `docs/teanga/Integrating Rust, DuckDB, TanStack, CopilotKit.md` — **Architectural Synthesis of Sovereign Game State: Integrating SpacetimeDB, DuckDB WASM, TanStack St
  - `docs/teanga/PlanetScale _ MotherDuck Docs.md` — PlanetScale   MotherDuck Docs
  - `docs/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1).md` — Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1)
  - `docs/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md` — Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray
  - `docs/teanga/Using MotherDuck with PlanetScale — PlanetScale.md` — Using MotherDuck with PlanetScale — PlanetScale
  - `docs/teanga/geoai-Geospatial Data Analysis and DuckDB.md` — **Convergence of Spatial Analytics and Digital Folkloristics: A Technical and Theoretical Examinatio
  - `docs/teanga/geoai-Geospatial Data Visualization with Ibis.md` — **Modernizing Educational Geospatial Intelligence: A Comprehensive Architectural Analysis of Ibis, D
- **docs/tuatha** (6 files):
  - `docs/sruth/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md` — **Architectural Synthesis of Sovereign Game State: Integrating SpacetimeDB, DuckDB WASM, TanStack St
  - `docs/sruth/tuatha/Rust Client.md` — Rust Client
  - `docs/sruth/tuatha/TanStack DB Integration and Comparison.md` — **The Convergent Stack: Architecting Reactive Data Systems with TanStack DB, DuckDB, RisingWave, and
  - `docs/sruth/tuatha/sruth/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md` — **Architectural Synthesis of Sovereign Game State: Integrating SpacetimeDB, DuckDB WASM, TanStack St
  - `docs/sruth/tuatha/sruth/tuatha/Rust Client.md` — Rust Client
  - `docs/sruth/tuatha/sruth/tuatha/TanStack DB Integration and Comparison.md` — **The Convergent Stack: Architecting Reactive Data Systems with TanStack DB, DuckDB, RisingWave, and
- **docs/web** (1 files):
  - `docs/web/TanStack DB Integration and Comparison.md` — **The Convergent Stack: Architecting Reactive Data Systems with TanStack DB, DuckDB, RisingWave, and

### 07-Model Training & Fine-Tuning

**Description:** Unsloth, HuggingFace, TRL, LoRA/QLoRA, GGUF, MLX, training pipelines
**Count:** 68 files, 1.4 MiB

- **docs/bonneagar** (2 files):
  - `docs/bonneagar/New in llama.cpp_ Model Management.md` — New in llama.cpp  Model Management
  - `docs/bonneagar/model-finetuning-strategy.md` — Model Fine-Tuning Strategy for Cryptocurrency Domain
- **docs/context** (9 files):
  - `docs/context/05-celtic-language/CELTIC_AI_RESOURCES.md` — Celtic Languages AI Resources on HuggingFace
  - `docs/context/05-celtic-language/IRISH_HUGGINGFACE.md` — Irish (Gaeilge) Language AI Resources on HuggingFace
  - `docs/context/05-celtic-language/MODEL_TRAINING.md` — MODEL TRAINING
  - `docs/context/06-infrastructure/ML_MODELS_REGISTRY.md` — Meaisínfhoghlaim - ML Models
  - `docs/context/08-examples/MODEL_FINETUNING.md` — Model Fine-Tuning Strategy for Cryptocurrency Domain
  - `docs/context/package-ecosystem/fine-tuning/lora-qlora.md` — LoRA / QLoRA — Parameter-Efficient Fine-Tuning
  - `docs/context/package-ecosystem/fine-tuning/modal.md` — Modal — Serverless GPU Cloud
  - `docs/context/package-ecosystem/fine-tuning/trl.md` — TRL — Transformer Reinforcement Learning (HuggingFace)
  - `docs/context/package-ecosystem/fine-tuning/unsloth.md` — Unsloth — Efficient LLM Fine-Tuning
- **docs/meaisínfhoghlaim** (28 files):
  - `docs/meaisínfhoghlaim/Datasets Guide _ Unsloth Documentation.md` — Datasets Guide   Unsloth Documentation
  - `docs/meaisínfhoghlaim/Fine-tuning LLMs Guide _ Unsloth Documentation.md` — Fine tuning LLMs Guide   Unsloth Documentation
  - `docs/meaisínfhoghlaim/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md` — How to Run and Deploy LLMs on your iOS or Android Phone   Unsloth Documentation
  - `docs/meaisínfhoghlaim/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md` — Introducing AnyLanguageModel  One API for Local and Remote LLMs on Apple Platforms
  - `docs/meaisínfhoghlaim/LLM based TTS models.md` — LLM based TTS models
  - `docs/meaisínfhoghlaim/LoRA Hyperparameters Guide _ Unsloth Documentation.md` — LoRA Hyperparameters Guide   Unsloth Documentation
  - `docs/meaisínfhoghlaim/Local macOS MLX_MPS LLM Workflow.md` — **Convergent Local Intelligence: Architecting High-Fidelity Multi-Modal Document Workflows on Apple 
  - `docs/meaisínfhoghlaim/Ministral 3 - How to Run Guide _ Unsloth Documentation.md` — Ministral 3   How to Run Guide   Unsloth Documentation
  - `docs/meaisínfhoghlaim/Neuro-Symbolic Translation Model Training.md` — **Architectural Blueprint for the Neuro-Symbolic Gaeilge Engine: Integrating InkSpire Diffusion Arch
  - `docs/meaisínfhoghlaim/New in llama.cpp_ Model Management.md` — New in llama.cpp  Model Management
  - `docs/meaisínfhoghlaim/Quantization-Aware Training (QAT) _ Unsloth Documentation.md` — Quantization Aware Training (QAT)   Unsloth Documentation
  - `docs/meaisínfhoghlaim/README.md` — Meaisínfhoghlaim - ML Models
  - `docs/meaisínfhoghlaim/Streaming datasets_ 100x More Efficient.md` — Streaming datasets  100x More Efficient
  - `docs/meaisínfhoghlaim/Swift Transformers Reaches 1.0 – and Looks to the Future.md` — Swift Transformers Reaches 1.0 – and Looks to the Future
  - `docs/meaisínfhoghlaim/Tokenization in Transformers v5_ Simpler, Clearer, and More Modular.md` — Tokenization in Transformers v5  Simpler, Clearer, and More Modular
  - `docs/meaisínfhoghlaim/Unsloth Model Catalog _ Unsloth Documentation(1).md` — Unsloth Model Catalog   Unsloth Documentation(1)
  - `docs/meaisínfhoghlaim/Unsloth Model Catalog _ Unsloth Documentation.md` — Unsloth Model Catalog   Unsloth Documentation
  - `docs/meaisínfhoghlaim/Unsloth Models for Celtic Datasets.md` — **Optimizing Open-Weights Large Language Models for Celtic Linguistics, Educational Analytics, and M
  - `docs/meaisínfhoghlaim/We Got Claude to Fine-Tune an Open Source LLM.md` — We Got Claude to Fine Tune an Open Source LLM
  - `docs/meaisínfhoghlaim/What Model Should I Use for Fine-tuning_ _ Unsloth Documentation.md` — What Model Should I Use for Fine tuning    Unsloth Documentation
  - `docs/meaisínfhoghlaim/gguf.md` — GGUF
  - `docs/meaisínfhoghlaim/huggingface-design-patterns-analysis.md` — Hugging Face Design Patterns and Best Practices: Comprehensive Analysis
  - `docs/meaisínfhoghlaim/huggingface-ontologies-research.md` — Hugging Face Ontologies, Taxonomies, and Data Structures
  - `docs/meaisínfhoghlaim/huggingface.md` — Hugging Face Expert
  - `docs/meaisínfhoghlaim/madroidmaq_mlx-omni-server.md` — madroidmaq mlx omni server
  - `docs/meaisínfhoghlaim/model-serving-guide.md` — Model Serving & Inference on Apple Silicon & Local Hardware
  - `docs/meaisínfhoghlaim/model-serving.md` — model serving
  - `docs/meaisínfhoghlaim/training-pipeline.md` — training pipeline
- **docs/teanga** (16 files):
  - `docs/teanga/CELTIC_LANGUAGES_AI_RESOURCES.md` — Celtic Languages AI Resources on HuggingFace
  - `docs/teanga/Frontend Idea Catalog Development.md` — **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction**
  - `docs/teanga/INDEX.md` — docs/teanga — Celtic Language AI Reference Library
  - `docs/teanga/Neuro-Symbolic Translation Model Training.md` — **Architectural Blueprint for the Neuro-Symbolic Gaeilge Engine: Integrating InkSpire Diffusion Arch
  - `docs/teanga/RESOURCES.md` — Celtic Languages AI Resources on HuggingFace
  - `docs/teanga/irish-irish_gaeilge_huggingface_resources.md` — Irish (Gaeilge) Language AI Resources on HuggingFace
  - `docs/teanga/irish_gaeilge_huggingface_resources.md` — Irish (Gaeilge) Language AI Resources on HuggingFace
  - `docs/teanga/kscanne-gbb-datasets-charles-README.md` — kscanne gbb datasets charles README
  - `docs/teanga/model_training.md` — model training
  - `docs/teanga/repo-chatterbox-finetuning.md` — KCG_SUMMARY: Chatterbox TTS — Fine-Tuning & Inference Kit
  - `docs/teanga/repo-historical-document-analysis.md` — KCG_SUMMARY: Historical Document Analysis — Multi-Modal Deep Learning Pipeline
  - `docs/teanga/scottish-scottish_gaelic_huggingface_resources.md` — Scottish Gaelic AI Resources on HuggingFace
  - `docs/teanga/scottish_gaelic_huggingface_resources.md` — Scottish Gaelic AI Resources on HuggingFace
  - `docs/teanga/utter-project_EuroLLM-22B-Instruct-2512 · Hugging Face.md` — utter project EuroLLM 22B Instruct 2512 · Hugging Face
  - `docs/teanga/welsh-huggingface-resources.md` — Welsh (Cymraeg) Language AI Resources on HuggingFace
  - `docs/teanga/welsh-welsh-huggingface-resources.md` — Welsh (Cymraeg) Language AI Resources on HuggingFace
- **docs/tuatha** (12 files):
  - `docs/sruth/tuatha/Frontend Idea Catalog Development.md` — **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction**
  - `docs/sruth/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md` — Introducing AnyLanguageModel  One API for Local and Remote LLMs on Apple Platforms
  - `docs/sruth/tuatha/LLM Serving with MLflow & Langfuse.md` — **Architecting Unified Hybrid-Inference Gateways: A Comprehensive Analysis of Local-Cloud Interopera
  - `docs/sruth/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md` — Swift Transformers Reaches 1.0 – and Looks to the Future
  - `docs/sruth/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md` — Unsloth Model Catalog   Unsloth Documentation
  - `docs/sruth/tuatha/sruth/tuatha/Frontend Idea Catalog Development.md` — **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction**
  - `docs/sruth/tuatha/sruth/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md` — Introducing AnyLanguageModel  One API for Local and Remote LLMs on Apple Platforms
  - `docs/sruth/tuatha/sruth/tuatha/LLM Serving with MLflow & Langfuse.md` — **Architecting Unified Hybrid-Inference Gateways: A Comprehensive Analysis of Local-Cloud Interopera
  - `docs/sruth/tuatha/sruth/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md` — Swift Transformers Reaches 1.0 – and Looks to the Future
  - `docs/sruth/tuatha/sruth/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md` — Unsloth Model Catalog   Unsloth Documentation
  - `docs/sruth/tuatha/sruth/tuatha/unsloth-catalog.md` — unsloth catalog
  - `docs/sruth/tuatha/unsloth-catalog.md` — unsloth catalog
- **docs/web** (1 files):
  - `docs/web/Frontend Idea Catalog Development.md` — **Automated Frontend Intelligence: A Multi-Modal Framework for Design Pattern Extraction**

### 08-Infrastructure & DevOps

**Description:** Pulumi, Komodo, Pangolin, Docker Compose, Dagger, Ansible, 1Password
**Count:** 84 files, 4.3 MiB

- **docs/bonneagar** (61 files):
  - `docs/bonneagar/ARCHITECTURE.md` — Infrastructure Architecture Reference
  - `docs/bonneagar/Building preconfigured OS images with HashiCorp Packer.md` — Building preconfigured OS images with HashiCorp Packer
  - `docs/bonneagar/Configuration File.md` — Configuration File
  - `docs/bonneagar/DAGGER_GUIDE_INDEX.md` — Dagger CI/CD - Complete Guide Index
  - `docs/bonneagar/DAGGER_PATTERNS_ANALYSIS.md` — Comprehensive Analysis of Dagger Examples
  - `docs/bonneagar/DAGGER_QUICK_REFERENCE.md` — Dagger Patterns Quick Reference
  - `docs/bonneagar/DECISION_MATRICES.md` — Infrastructure Decision Matrices
  - `docs/bonneagar/DOCKER_COMPOSE_ARCHITECTURE.md` — Docker Compose Architecture Overview
  - `docs/bonneagar/DOCKER_COMPOSE_QUICKSTART.md` — Docker Compose Analysis - Complete Documentation Index
  - `docs/bonneagar/DOCKER_COMPOSE_REFERENCE.md` — Docker Compose Stacks Analysis - Hackathon Project
  - `docs/bonneagar/Docker Provider.md` — Docker Provider
  - `docs/bonneagar/Enhancing Monorepo Ansible Workflow.md` — **Architecting the Modern Platform: Integrating Ansible into High-Performance Monorepo Ecosystems**
  - `docs/bonneagar/Get started with a 1Password Connect server _ 1Password Developer.md` — Get started with a 1Password Connect server   1Password Developer
  - `docs/bonneagar/High-Availability Kubernetes on Hetzner with Talos 1.11.md` — High Availability Kubernetes on Hetzner with Talos 1.11
  - `docs/bonneagar/IMPLEMENTATION_GUIDE.md` — Infrastructure Implementation Guide
  - `docs/bonneagar/INDEX.md` — Bonneagar — Infrastructure Research Index
  - `docs/bonneagar/INDEX1.md` — Infrastructure Research - Consolidated Index
  - `docs/bonneagar/PANGOLIN_COMPLETE_GUIDE.md` — Pangolin — Complete Zero-Trust Networking Guide
  - `docs/bonneagar/Pigsty, Mathesar, Komodo Deployment Outline.md` — **Architectural Blueprint for the Unified Deployment of Pigsty and Mathesar: A Simplified Komodo-Ans
  - `docs/bonneagar/Provision Resources on Hetzner Cloud with Pulumi.md` — Provision Resources on Hetzner Cloud with Pulumi
  - `docs/bonneagar/Register a Hetzner Server.md` — Register a Hetzner Server
  - `docs/bonneagar/Release Komodo v2.0.0-dev-102 · moghtech_komodo.md` — Release Komodo v2.0.0 dev 102 · moghtech komodo
  - `docs/bonneagar/SETUP.md` — Automation Setup Guide
  - `docs/bonneagar/Self-Hosted Stack Visualization & Management.md` — **Architectural Convergence in Modern Self-Hosted Infrastructure: A Comprehensive Analysis of Visual
  - `docs/bonneagar/ansible-role-komodo_examples at komodo_v2 · bpbradley_ansible-role-komodo.md` — ansible role komodo examples at komodo v2 · bpbradley ansible role komodo
  - `docs/bonneagar/api.md` — Pangolin API Development Assistant
  - `docs/bonneagar/apple-silicon-deployment.md` — Apple Silicon LLM Deployment
  - `docs/bonneagar/apple-silicon-deployment_1.md` — Apple Silicon Deployment for Document Intelligence
  - `docs/bonneagar/architecture-patterns.md` — Pangolin Project: Architecture Patterns & Best Practices
  - `docs/bonneagar/automation_readme.md` — Automating Deployment with Komodo and Docker
  - `docs/bonneagar/celtic-platform.md` — Celtic Language Platform
  - `docs/bonneagar/comparing-approaches-pangolin-registration-komodo-deployment.md` — comparing approaches pangolin registration komodo deployment
  - `docs/bonneagar/compose.yaml` — compose
  - `docs/bonneagar/dagger-docker-compose-workflow-komodo-periphery-pangolin-newt-olm.md` — dagger docker compose workflow komodo periphery pangolin newt olm
  - `docs/bonneagar/dagger-implementation-checklist.md` — Dagger Pipeline Implementation Checklist
  - `docs/bonneagar/debug.md` — Pangolin Debugging Assistant
  - `docs/bonneagar/development-tools.md` — Development Tools
  - `docs/bonneagar/docker-compose(1).yaml` — docker compose(1)
  - `docs/bonneagar/docker-compose-patterns.md` — Docker Compose Patterns for AI Infrastructure
  - `docs/bonneagar/docker_hooks_examples.py` — docker hooks examples
  - `docs/bonneagar/docker_python_sdk.py` — If jwt is enabled, authenticate first
  - `docs/bonneagar/docker_webhook_example.py` — docker webhook example
  - `docs/bonneagar/extending-komodo-pr-deploy-pangolin-integration-komodo-actions.md` — extending komodo pr deploy pangolin integration komodo actions
  - `docs/bonneagar/generating-typescript-client-pangolin-api-openapi-spec.md` — generating typescript client pangolin api openapi spec
  - `docs/bonneagar/hosting-litellm-pangolin-public-vs-private-access-models.md` — hosting litellm pangolin public vs private access models
  - `docs/bonneagar/infrastructure-tools.md` — Infrastructure Tools
  - `docs/bonneagar/integrating-1password-cli-connect-komodo-ansible-deployment.md` — integrating 1password cli connect komodo ansible deployment
  - `docs/bonneagar/integrating-1password-cli-komodo-ansible-deployment.md` — integrating 1password cli komodo ansible deployment
  - `docs/bonneagar/integrating-dagger-polyglot-monorepo-ci-cd-workflow.md` — integrating dagger polyglot monorepo ci cd workflow
  - `docs/bonneagar/komodo-api-summary.md` — Komodo (komo.do) API Summary
  - `docs/bonneagar/komodo-openapi-research.md` — Komodo (komo.do) OpenAPI Research Report
  - `docs/bonneagar/komodo.md` — Komodo Infrastructure Management Skill
  - `docs/bonneagar/pangolin-openapi-specification-research.md` — Pangolin OpenAPI Specification Research Report
  - `docs/bonneagar/pangolin-patterns.md` — Pangolin Project: Patterns and Ontologies Deep Dive
  - `docs/bonneagar/pangolin.md` — Pangolin Development Assistant
  - `docs/bonneagar/pulumi-infrastructure-as-code.md` — Pulumi Infrastructure as Code: Comprehensive Guide for LLMs
  - `docs/bonneagar/pulumi-typescript-guide-provisioning-cloudflare-d1-r2-1password-integration.md` — pulumi typescript guide provisioning cloudflare d1 r2 1password integration
  - `docs/bonneagar/pulumi.md` — Pulumi Infrastructure as Code
  - `docs/bonneagar/pulumi_1.md` — Pulumi Infrastructure as Code Expert Skill
  - `docs/bonneagar/stealth-browser-stack.md` — Stealth Browser Infrastructure
  - `docs/bonneagar/termix.md` — Termix Development Assistant
- **docs/context** (5 files):
  - `docs/context/06-infrastructure/BONNEAGAR_OVERVIEW.md` — Taisce - Modular Docker Stacks
  - `docs/context/06-infrastructure/ML_STACK.md` — ML STACK
  - `docs/context/06-infrastructure/auto-deploy-stacks.toml` — auto deploy stacks
  - `docs/context/06-infrastructure/celtic_ml_models.yaml` — Celtic Language ML Models Registry
  - `docs/context/07-skills/celtic-language-ai.md` — Celtic Language AI/ML Resources
- **docs/data_engineering** (1 files):
  - `docs/data_engineering/marimo-reference.md` — Marimo Reference
- **docs/meaisínfhoghlaim** (2 files):
  - `docs/meaisínfhoghlaim/litellm-deployment-guide.md` — LiteLLM Proxy - Deployment & Operations Guide
  - `docs/meaisínfhoghlaim/mlflow-model-registry-deployment-reference.md` — MLflow Model Registry and Deployment Reference
- **docs/teanga** (4 files):
  - `docs/teanga/Celtic Language Data Aggregation & Analysis.md` — **Unified Computational Infrastructure for Celtic Languages: Data Integration, Educational Analytics
  - `docs/teanga/gaois-KCG_SUMMARY.md` — KCG_SUMMARY: Gaois — Irish Language Digital Infrastructure (DCU)
  - `docs/teanga/gaois-documental-docs-software-documental-deployment.en.md` — gaois documental docs software documental deployment.en
  - `docs/teanga/gaois-documental-docs-software-documental-deployment.ga.md` — gaois documental docs software documental deployment.ga
- **docs/tuatha** (10 files):
  - `docs/sruth/tuatha/Celtic Language Data Aggregation & Analysis.md` — **Unified Computational Infrastructure for Celtic Languages: Data Integration, Educational Analytics
  - `docs/sruth/tuatha/DEPLOYMENT.md` — Deployment Guide
  - `docs/sruth/tuatha/README.md` — Game Development Reference Library
  - `docs/sruth/tuatha/celtic_mmo.md` — Building an "Anam" Celtic educational MMO: technical foundations
  - `docs/sruth/tuatha/infrastructure-README.md` — Infrastructure
  - `docs/sruth/tuatha/sruth/tuatha/Celtic Language Data Aggregation & Analysis.md` — **Unified Computational Infrastructure for Celtic Languages: Data Integration, Educational Analytics
  - `docs/sruth/tuatha/sruth/tuatha/DEPLOYMENT.md` — Deployment Guide
  - `docs/sruth/tuatha/sruth/tuatha/README.md` — Game Development Reference Library
  - `docs/sruth/tuatha/sruth/tuatha/celtic_mmo.md` — Building an "Anam" Celtic educational MMO: technical foundations
  - `docs/sruth/tuatha/sruth/tuatha/infrastructure-README.md` — Infrastructure
- **docs/web** (1 files):
  - `docs/web/alchemy-run_alchemy_ Infrastructure as TypeScript.md` — alchemy run alchemy  Infrastructure as TypeScript

### 09-Cloudflare Platform

**Description:** Workers, D1, R2, Tunnels, Containers, OpenAPI specs, portfolio hosting
**Count:** 12 files, 263.7 KiB

- **docs/bonneagar** (8 files):
  - `docs/bonneagar/Portfolio Tech Stack & Cloudflare R2.md` — **Architecting the Polymath Studio: A Full-Stack Blueprint for Game Development and Audio Production
  - `docs/bonneagar/cloudflare-backpine-summary.md` — Cloudflare Full-Stack Repository Summary
  - `docs/bonneagar/cloudflare-containers-research.md` — Cloudflare Containers: Comprehensive Research Report
  - `docs/bonneagar/cloudflare-d1-research.md` — Cloudflare D1 - Comprehensive Research Report
  - `docs/bonneagar/cloudflare-openapi-specification-research.md` — Cloudflare API OpenAPI Specification Research
  - `docs/bonneagar/cloudflare-tunnel-research.md` — Cloudflare Tunnel: Comprehensive Research Report
  - `docs/bonneagar/cloudflare-workers-research.md` — Cloudflare Workers: Comprehensive Research Report
  - `docs/bonneagar/cloudflare.md` — Cloudflare Developer Platform Expert
- **docs/web** (4 files):
  - `docs/web/alchemy_examples_cloudflare-sveltekit_alchemy.run.ts at main · alchemy-run_alchemy.md` — alchemy examples cloudflare sveltekit alchemy.run.ts at main · alchemy run alchemy
  - `docs/web/alchemy_examples_cloudflare-tanstack-start_alchemy.run.ts at main · alchemy-run_alchemy.md` — alchemy examples cloudflare tanstack start alchemy.run.ts at main · alchemy run alchemy
  - `docs/web/alchemy_examples_cloudflare-worker_alchemy.run.ts at main · alchemy-run_alchemy.md` — alchemy examples cloudflare worker alchemy.run.ts at main · alchemy run alchemy
  - `docs/web/repo-cloudflare-workers.md` — Cloudflare Workers — KCG Summary

### 10-Frontend & Full-Stack Web

**Description:** TanStack Start/Router/DB, Hono, Convex, Effect-TS, Better Auth, oRPC, CopilotKit
**Count:** 72 files, 1.5 MiB

- **docs/bonneagar** (3 files):
  - `docs/bonneagar/Rust Full-Stack Gaming Environment.md` — **Architectural Analysis and Implementation Strategy for a Rust-Based Full-Stack Gaming Ecosystem**
  - `docs/bonneagar/crypto_analysis_example.py` — crypto analysis example
  - `docs/bonneagar/web-tech-tutorials-and-examples.md` — **The 2025 Composable SaaS Stack: An Expert Analysis of TanStack Start, Hono, Polar.sh, and Better-A
- **docs/context** (3 files):
  - `docs/context/07-skills/tanstack-start.md` — TanStack Start - Full-Stack React Framework
  - `docs/context/package-ecosystem/frontend/hono.md` — Hono — Lightweight Web API Framework
  - `docs/context/package-ecosystem/frontend/tanstack-start.md` — TanStack Start — React Full-Stack Framework
- **docs/teanga** (7 files):
  - `docs/teanga/Asset Management for Full-Stack App.md` — **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms**
  - `docs/teanga/Geospatial Workflow & Particle Effects(1).md` — **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP an
  - `docs/teanga/gaois-IrishSurnameIndex-README.md` — IrishSurnameIndex
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-coiste.en.md` — The Terminology Committee
  - `docs/teanga/geoai-Geospatial Workflow & Particle Effects(1).md` — **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP an
  - `docs/teanga/kscanne-crubadan-transliterate-README.md` — kscanne crubadan transliterate README
  - `docs/teanga/kscanne-gbb-classification-author-README.md` — kscanne gbb classification author README
- **docs/tuatha** (22 files):
  - `docs/sruth/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md` — AG UI and A2UI  Understanding the Differences   CopilotKit
  - `docs/sruth/tuatha/Asset Management for Full-Stack App.md` — **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms**
  - `docs/sruth/tuatha/FRONTEND.md` — TanStack Start Frontend
  - `docs/sruth/tuatha/GRAPHICS_INDEX.md` — Graphics, Game Development & Rendering Documentation Index
  - `docs/sruth/tuatha/Game Particle Effects Research(2).md` — **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation
  - `docs/sruth/tuatha/Game Particle Effects Research.md` — **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation
  - `docs/sruth/tuatha/Geospatial Workflow & Particle Effects.md` — **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP an
  - `docs/sruth/tuatha/Rust Full-Stack Gaming Environment.md` — **Architectural Analysis and Implementation Strategy for a Rust-Based Full-Stack Gaming Ecosystem**
  - `docs/sruth/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md` — Sign In With Ethereum (SIWE)   Better Auth
  - `docs/sruth/tuatha/game_DEVELOPMENT.md` — Development
  - `docs/sruth/tuatha/game_siwe-auth.md` — game siwe auth
  - `docs/sruth/tuatha/sruth/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md` — AG UI and A2UI  Understanding the Differences   CopilotKit
  - `docs/sruth/tuatha/sruth/tuatha/Asset Management for Full-Stack App.md` — **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms**
  - `docs/sruth/tuatha/sruth/tuatha/FRONTEND.md` — TanStack Start Frontend
  - `docs/sruth/tuatha/sruth/tuatha/GRAPHICS_INDEX.md` — Graphics, Game Development & Rendering Documentation Index
  - `docs/sruth/tuatha/sruth/tuatha/Game Particle Effects Research(2).md` — **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation
  - `docs/sruth/tuatha/sruth/tuatha/Game Particle Effects Research.md` — **The Anam Initiative: Architectural Blueprints for High-Fidelity Meteorological Particle Simulation
  - `docs/sruth/tuatha/sruth/tuatha/Geospatial Workflow & Particle Effects.md` — **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP an
  - `docs/sruth/tuatha/sruth/tuatha/Rust Full-Stack Gaming Environment.md` — **Architectural Analysis and Implementation Strategy for a Rust-Based Full-Stack Gaming Ecosystem**
  - `docs/sruth/tuatha/sruth/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md` — Sign In With Ethereum (SIWE)   Better Auth
  - `docs/sruth/tuatha/sruth/tuatha/game_DEVELOPMENT.md` — Development
  - `docs/sruth/tuatha/sruth/tuatha/game_siwe-auth.md` — game siwe auth
- **docs/web** (37 files):
  - `docs/web/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md` — AG UI and A2UI  Understanding the Differences   CopilotKit
  - `docs/web/Asset Management for Full-Stack App.md` — **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms**
  - `docs/web/Basic Usage _ Better Auth.md` — Basic Usage   Better Auth
  - `docs/web/Drizzle ORM Adapter _ Better Auth.md` — Drizzle ORM Adapter   Better Auth
  - `docs/web/Expo Integration _ Better Auth.md` — Expo Integration   Better Auth
  - `docs/web/INDEX.md` — docs/web/ — Web Architecture Knowledge Base
  - `docs/web/Microfrontends.md` — Microfrontends
  - `docs/web/Overview _ TanStack AI Docs.md` — Overview   TanStack AI Docs
  - `docs/web/Overview _ TanStack DB Docs.md` — Overview   TanStack DB Docs
  - `docs/web/PostgreSQL _ Better Auth.md` — PostgreSQL   Better Auth
  - `docs/web/README_TANSTACK_ANALYSIS.md` — TanStack Examples Analysis - Complete Guide
  - `docs/web/Sign In With Ethereum (SIWE) _ Better Auth.md` — Sign In With Ethereum (SIWE)   Better Auth
  - `docs/web/TANSTACK_ANALYSIS.md` — TanStack Examples Analysis
  - `docs/web/TANSTACK_INDEX.md` — TanStack Examples Analysis - Complete Index
  - `docs/web/TANSTACK_QUICK_REFERENCE.md` — TanStack Examples - Quick Reference
  - `docs/web/TANSTACK_SUMMARY.md` — TanStack Examples - Executive Summary
  - `docs/web/TanStack Start Integration _ Better Auth.md` — TanStack Start Integration   Better Auth
  - `docs/web/TanStack Start.md` — TanStack Start
  - `docs/web/auth-setup.md` — auth setup
  - `docs/web/convex-authentication-and-integration-guide.md` — Convex Authentication, Actions, and Integration Capabilities Research
  - `docs/web/convex-backend_self-hosted_README.md at main · get-convex_convex-backend.md` — convex backend self hosted README.md at main · get convex convex backend
  - `docs/web/convex-core-features-architecture.md` — Convex: Core Features and Architecture
  - `docs/web/effect-convex-integration-research.md` — Effect.ts and Convex Integration Research
  - `docs/web/effect-ts-comprehensive-research.md` — Effect.ts Comprehensive Research Report
  - `docs/web/effect-ts-tanstack-start-integration.md` — Effect.ts and TanStack Start Integration Research
  - `docs/web/full-stack-dashboard-integration-plan.md` — **A Unified Full-Stack Strategy for an Interactive AI Dashboard**
  - `docs/web/full-stack-web-architecture-consolidated.md` — Modern Full-Stack Web Application Architecture
  - `docs/web/implementation-plan-self-hosting-betterauth-convex-supabase-hono-tanstack-start.md` — implementation plan self hosting betterauth convex supabase hono tanstack start
  - `docs/web/orpc-comprehensive-research.md` — Comprehensive ORPC (oRPC) Research Report
  - `docs/web/repo-convex.md` — Convex — KCG Summary
  - `docs/web/repo-hono.md` — Hono — KCG Summary
  - `docs/web/repo-orpc.md` — oRPC — KCG Summary
  - `docs/web/repo-tanstack.md` — TanStack — KCG Summary
  - `docs/web/routing-and-layout.md` — routing and layout
  - `docs/web/tanstack-start-architecture.md` — TanStack Start: Comprehensive Architecture Research Report
  - `docs/web/tanstack-start-research-report.md` — TanStack Start: Comprehensive Research Report
  - `docs/web/tanstack-start-visual-patterns.md` — TanStack Start: Visual Architecture Patterns

### 11-Celtic Languages, Education & Translation

**Description:** Irish/Gaelic/Welsh resources, parallel corpora, bilingual edtech, HuggingFace models, TTS/ASR
**Count:** 294 files, 4.6 MiB

- **docs/bonneagar** (22 files):
  - `docs/bonneagar/Leaving Certificate Subject Analysis Plan.md` — **Comprehensive Architectural Strategy for the Pan-Curricular Expansion of the Irish Leaving Certifi
  - `docs/bonneagar/Open-Source Web Scraping Architecture Analysis.md` — **Strategic Architecture for Autonomous Educational Data Acquisition: Integrating Skyvern, Crawl4AI,
  - `docs/bonneagar/Resource Maximization and Project Planning(1).md` — **Strategic Resource Maximization: Architecting the Celtic Heritage Intelligence Platform (CHIP)**
  - `docs/bonneagar/Resource Maximization and Project Planning.md` — **Strategic Resource Maximization: Architecting the Celtic Heritage Intelligence Platform (CHIP)**
  - `docs/bonneagar/ai-ml-pipeline.md` — AI/ML Pipeline for Irish Education Platform
  - `docs/bonneagar/alignment-tools.md` — Text Alignment Tools for Irish-English
  - `docs/bonneagar/bilingual-scraper-implementation.md` — Bilingual Irish Educational Resources Scraper
  - `docs/bonneagar/education-subject-inventory.md` — Irish Education Subject Data Inventory
  - `docs/bonneagar/enrollment-statistics.md` — Celtic Language Education Enrollment Statistics
  - `docs/bonneagar/frontend-stack.md` — Frontend Stack for Irish Education Platform
  - `docs/bonneagar/gaelic-heritage-pipeline.md` — Gaelic Heritage Digitization Pipeline
  - `docs/bonneagar/gaois-api-reference.md` — Gaois API Reference
  - `docs/bonneagar/irish-archives-workflow.md` — Irish Educational Archives Workflow
  - `docs/bonneagar/irish-nlp-resources.md` — Irish (Gaeilge) Language AI Resources
  - `docs/bonneagar/maplibre-visualization.md` — MapLibre Visualization for Celtic Language Data
  - `docs/bonneagar/pan-celtic-scraping.md` — Pan-Celtic Web Scraping Strategy
  - `docs/bonneagar/parallel-corpus-sources.md` — Parallel Corpus Sources for Irish-English
  - `docs/bonneagar/policy-frameworks.md` — Celtic Language Education Policy Frameworks
  - `docs/bonneagar/scottish-gaelic-resources.md` — Scottish Gaelic AI Resources
  - `docs/bonneagar/teacher-supply.md` — Celtic Language Teacher Supply Crisis
  - `docs/bonneagar/unified-model-comparison.md` — Celtic Language AI - Unified Model Comparison
  - `docs/bonneagar/welsh-resources.md` — Welsh (Cymraeg) AI Resources
- **docs/context** (15 files):
  - `docs/context/02-architecture/EDUCATION_ARCHITECTURE.md` — Data Stack Architecture Reference
  - `docs/context/02-architecture/IRISH_EDTECH.md` — Irish EdTech Platform Architecture
  - `docs/context/03-pipelines/AI_ML_PIPELINE.md` — AI/ML Pipeline for Irish Education Platform
  - `docs/context/03-pipelines/api_main.py` — api main
  - `docs/context/03-pipelines/observability_init.py` — observability init
  - `docs/context/05-celtic-language/BILINGUAL_EDTECH.md` — **Architectural Blueprint for a Bilingual EdTech Platform: Leveraging Edge Computing and WebAssembly
  - `docs/context/08-examples/FRONTEND_STACK.md` — Frontend Stack for Irish Education Platform
  - `docs/context/Apple Education and AI Goals.pdf` — Apple Education and AI Goals
  - `docs/context/Irish Language Copyright and Education.pdf` — Irish Language Copyright and Education
  - `docs/context/package-ecosystem/speech/chatterbox.md` — Chatterbox — Text-to-Speech (TTS)
  - `docs/context/package-ecosystem/speech/wav2vec2-xlsr-irish.md` — wav2vec2-XLSR-Irish — Irish Speech Recognition
  - `docs/context/package-ecosystem/speech/whisper-faster-whisper.md` — Whisper / faster-whisper — Speech Recognition (ASR)
  - `docs/context/package-ecosystem/translation/helsinki-opus-mt.md` — Helsinki OPUS-MT — Celtic Language Pair Translation
  - `docs/context/package-ecosystem/translation/m2m-100.md` — M2M-100 — Many-to-Many Multilingual Translation
  - `docs/context/package-ecosystem/translation/nllb-200.md` — NLLB-200 — 200-Language Neural Machine Translation
- **docs/meaisínfhoghlaim** (10 files):
  - `docs/meaisínfhoghlaim/Call for papers_ A special edition of TEANGA on corpus linguistics in an Irish-language context.md` — Call for papers  A special edition of TEANGA on corpus linguistics in an Irish language context
  - `docs/meaisínfhoghlaim/Chemistry Education Asset Generation.md` — **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architectur
  - `docs/meaisínfhoghlaim/Fine-tuning VLMs for iOS HTR.md` — **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on i
  - `docs/meaisínfhoghlaim/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md` — Gaelic in the Digital Age  Inside the ÈIST Project – Gaelic Algorithmic Research Group
  - `docs/meaisínfhoghlaim/README_1.md` — Gaeilge Research - Organized Collection
  - `docs/meaisínfhoghlaim/React Drag-and-Drop for Exam Builder.md` — **Architectural Blueprint for an Intelligent, British Curriculum-Aligned Interactive Exam Builder**
  - `docs/meaisínfhoghlaim/Resource Maximization and Project Planning.md` — **Strategic Resource Maximization: Architecting the Celtic Heritage Intelligence Platform (CHIP)**
  - `docs/meaisínfhoghlaim/celtic-language-ai.md` — celtic language ai
  - `docs/meaisínfhoghlaim/gpu_experiment_guide.md` — GPU Experiment Guide: Reproducing & Improving Celtic Language Models
  - `docs/meaisínfhoghlaim/irish_tts_finetune.py` — irish tts finetune
- **docs/teanga** (201 files):
  - `docs/teanga/British Isles Celtic Language Education Data.md` — **The State of Education and Celtic Language Revitalisation in the British Isles: Demographic Shifts
  - `docs/teanga/British Isles Education Map.md` — **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report**
  - `docs/teanga/Building Bilingual EdTech Platform.md` — **Architectural Blueprint for a Bilingual EdTech Platform: Leveraging Edge Computing and WebAssembly
  - `docs/teanga/Chemistry Education Asset Generation.md` — **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architectur
  - `docs/teanga/Educational Game Dev Pipeline.md` — **High-Fidelity Pedagogical Simulation: A Comprehensive Framework for Automating Scientifically Accu
  - `docs/teanga/Educational Website Tech Stack.md` — **Technical Blueprint for a Next-Generation Leaving Certificate Education Platform: Architecture, Pe
  - `docs/teanga/Fine-tuning VLMs for iOS HTR.md` — **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on i
  - `docs/teanga/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md` — Gaelic in the Digital Age  Inside the ÈIST Project – Gaelic Algorithmic Research Group
  - `docs/teanga/Leaving Certificate Material App.md` — **Architectural & Curricular Analysis: Digital Transformation of Leaving Certificate Prescribed Mate
  - `docs/teanga/Scraping Irish Audio Files.md` — **Technical Feasibility Study: Archival and Organization of Irish Language Audio Corpora (Teanglann.
  - `docs/teanga/datasets-irish_bilingual_dataset_research.md` — Irish-English Bilingual Dataset Creation: Technical Research Outline
  - `docs/teanga/gaois-DuchasAPI-docs-CHANGELOG.md` — Changelog
  - `docs/teanga/gaois-DuchasAPI-docs-DATADICT.md` — Dúchas Application Programming Interface (Version 0.5): Data dictionary
  - `docs/teanga/gaois-DuchasAPI-docs-README.md` — Dúchas Application Programming Interface (Version 0.5): Developer documentation
  - `docs/teanga/gaois-DuchasAPI-docs-TODO.md` — Issues to be addressed
  - `docs/teanga/gaois-Gaois.Localizer-README.md` — Gaois.Localizer
  - `docs/teanga/gaois-Gaois.QueryLogger-README.md` — Gaois.QueryLogger
  - `docs/teanga/gaois-GeoNames2Sql-LICENSE.md` — gaois GeoNames2Sql LICENSE
  - `docs/teanga/gaois-GeoNames2Sql-README.md` — GeoNames2Sql
  - `docs/teanga/gaois-LogainmAPI-docs-CHANGELOG.md` — Changelog
  - `docs/teanga/gaois-LogainmAPI-docs-DATADICT.md` — Logainm Application Programming Interface (Version 0.9): Data dictionary
  - `docs/teanga/gaois-LogainmAPI-docs-DECISIONS.md` — API Design Decisions
  - `docs/teanga/gaois-LogainmAPI-docs-README.md` — Logainm Application Programming Interface (Version 0.9): Developer documentation
  - `docs/teanga/gaois-Nationalist-README.md` — Nationalist
  - `docs/teanga/gaois-PublicDocs-README.md` — PublicDocs
  - `docs/teanga/gaois-PublicDocs-cbe-xml-documentation.md` — The Data Structure of the National Folklore Collection *Main Manuscript Collection*
  - `docs/teanga/gaois-Tearma-README.md` — téarma.ie
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-brabhsail.en.md` — Browse
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-brabhsail.ga.md` — Brabhsáil
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cad-is-tearma.en.md` — What is a term?
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cad-is-tearma.ga.md` — Cad is téarma ann?
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-conas-usaid.en.md` — How to use the site
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-conas-usaid.ga.md` — Conas an suíomh a úsáid
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-casta.en.md` — How to use Advanced Search
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-casta.ga.md` — Conas an Cuardach Casta a úsáid
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-tapa.en.md` — Quick Search
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-cuardach-tapa.ga.md` — An Cuardach Tapa
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-gan-toradh.en.md` — I didn’t find what I was looking for
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-gan-toradh.ga.md` — Níor aimsigh mé a raibh uaim
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-torthai-a-thuiscint.en.md` — Understanding search results
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-cabhair-torthai-a-thuiscint.ga.md` — Conas na torthaí cuardaigh a thuiscint
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-abhar.en.md` — About the Content
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-abhar.ga.md` — Eolas Faoin Ábhar
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-coiste.ga.md` — An Coiste Téarmaíochta
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-corpus.en.md` — Link between téarma.ie and the New Corpus for Ireland
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-corpus.ga.md` — An ceangal idir téarma.ie agus Nua-Chorpas na hÉireann
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-cosaint-sonrai.en.md` — Data protection information
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-cosaint-sonrai.ga.md` — Eolas cosanta sonraí
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-stair.en.md` — The History of focal.ie/téarma.ie
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-stair.ga.md` — Stair focal.ie/téarma.ie
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-tionscadal.en.md` — The téarma.ie project
  - `docs/teanga/gaois-Tearma-TearmaWeb-wwwroot-eolas-tionscadal.ga.md` — Tionscadal téarma.ie
  - `docs/teanga/gaois-documental-README.md` — Documental
  - `docs/teanga/gaois-documental-docs-software-documental-developers.en.md` — gaois documental docs software documental developers.en
  - `docs/teanga/gaois-documental-docs-software-documental-developers.ga.md` — gaois documental docs software documental developers.ga
  - `docs/teanga/gaois-documental-docs-software-documental-editors.en.md` — gaois documental docs software documental editors.en
  - `docs/teanga/gaois-documental-docs-software-documental-editors.ga.md` — gaois documental docs software documental editors.ga
  - `docs/teanga/gaois-documental-docs-software-documental-intro.en.md` — gaois documental docs software documental intro.en
  - `docs/teanga/gaois-documental-docs-software-documental-intro.ga.md` — gaois documental docs software documental intro.ga
  - `docs/teanga/gaois-documental-docs-software-geonames2sql-index.en.md` — gaois documental docs software geonames2sql index.en
  - `docs/teanga/gaois-documental-docs-software-geonames2sql-index.ga.md` — gaois documental docs software geonames2sql index.ga
  - `docs/teanga/gaois-documental-docs-software-localizer-index.en.md` — gaois documental docs software localizer index.en
  - `docs/teanga/gaois-documental-docs-software-localizer-index.ga.md` — gaois documental docs software localizer index.ga
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-configuration.en.md` — gaois documental docs software querylogger v0.7 configuration.en
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-configuration.ga.md` — gaois documental docs software querylogger v0.7 configuration.ga
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-data.en.md` — gaois documental docs software querylogger v0.7 data.en
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-data.ga.md` — gaois documental docs software querylogger v0.7 data.ga
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-faulttolerance.en.md` — gaois documental docs software querylogger v0.7 faulttolerance.en
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-faulttolerance.ga.md` — gaois documental docs software querylogger v0.7 faulttolerance.ga
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-intro.en.md` — gaois documental docs software querylogger v0.7 intro.en
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-intro.ga.md` — gaois documental docs software querylogger v0.7 intro.ga
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-net461.en.md` — gaois documental docs software querylogger v0.7 net461.en
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-net461.ga.md` — gaois documental docs software querylogger v0.7 net461.ga
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-netcore.en.md` — gaois documental docs software querylogger v0.7 netcore.en
  - `docs/teanga/gaois-documental-docs-software-querylogger-v0.7-netcore.ga.md` — gaois documental docs software querylogger v0.7 netcore.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-configuration.en.md` — gaois documental docs software terminologue configuration.en
  - `docs/teanga/gaois-documental-docs-software-terminologue-configuration.ga.md` — gaois documental docs software terminologue configuration.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-installation.en.md` — gaois documental docs software terminologue installation.en
  - `docs/teanga/gaois-documental-docs-software-terminologue-installation.ga.md` — gaois documental docs software terminologue installation.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-intro.en.md` — gaois documental docs software terminologue intro.en
  - `docs/teanga/gaois-documental-docs-software-terminologue-intro.ga.md` — gaois documental docs software terminologue intro.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-source-code.en.md` — gaois documental docs software terminologue source code.en
  - `docs/teanga/gaois-documental-docs-software-terminologue-source-code.ga.md` — gaois documental docs software terminologue source code.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-tbx-export.ga.md` — gaois documental docs software terminologue tbx export.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-tbx-import.ga.md` — gaois documental docs software terminologue tbx import.ga
  - `docs/teanga/gaois-documental-docs-software-terminologue-txt-export.ga.md` — gaois documental docs software terminologue txt export.ga
  - `docs/teanga/gaois-gaoisalign-README.md` — gaoisalign
  - `docs/teanga/gaois-screenful-README.md` — Screenful
  - `docs/teanga/gaois-sloinnte-README.md` — Database of Irish-Language Surnames
  - `docs/teanga/gaois-terminologue-README.md` — Terminologue
  - `docs/teanga/gaois-terminologue-docs-configuring.md` — gaois terminologue docs configuring
  - `docs/teanga/gaois-terminologue-docs-index.md` — gaois terminologue docs index
  - `docs/teanga/gaois-terminologue-docs-info.nb.md` — Om *Terminologue*
  - `docs/teanga/gaois-terminologue-docs-installation.md` — gaois terminologue docs installation
  - `docs/teanga/gaois-terminologue-docs-intro.nb.md` — Kjapp innføring i Terminologue
  - `docs/teanga/gaois-terminologue-docs-sourcecode.md` — gaois terminologue docs sourcecode
  - `docs/teanga/gaois-terminologue-shared-README.md` — gaois terminologue shared README
  - `docs/teanga/gaois-terminologue-website-docs-info.ar.md` — حول Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-info.ca.md` — Sobre *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.cy.md` — Ynghylch *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.de.md` — Über *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.el.md` — Σχετικά με το *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.en.md` — About *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.es.md` — Acerca de *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.eu.md` — *Terminologue*-ri buruz
  - `docs/teanga/gaois-terminologue-website-docs-info.fi.md` — Tietoa *Terminologuesta*
  - `docs/teanga/gaois-terminologue-website-docs-info.fr.md` — À propos de Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-info.ga.md` — Maidir le *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.hr.md` — O *Terminologueu*
  - `docs/teanga/gaois-terminologue-website-docs-info.lt.md` — Apie *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.nb.md` — Om *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.nl.md` — Over *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.ru.md` — О *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.sv.md` — Om *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-info.tr.md` — *Terminologue* Hakkında
  - `docs/teanga/gaois-terminologue-website-docs-info.zh.md` — 關於*Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-intro.ar.md` — مقدمة لطيفة لـبرنامج Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.ca.md` — Introducció senzilla a Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.cy.md` — Cyflwyniad cryno i Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.de.md` — Behutsame Einführung in Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.el.md` — Ευγενική εισαγωγή στο Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.en.md` — Gentle introduction to Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.es.md` — Sencilla iniciación a Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.eu.md` — Terminologuerako sarrera arina
  - `docs/teanga/gaois-terminologue-website-docs-intro.fi.md` — Terminologuen lyhyt esittely
  - `docs/teanga/gaois-terminologue-website-docs-intro.fr.md` — Brève introduction à Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.ga.md` — Treoir úsáideora Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.hr.md` — Uvod u Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.lt.md` — Trumpas įvadas į *Terminologue*
  - `docs/teanga/gaois-terminologue-website-docs-intro.nb.md` — Kjapp innføring i Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.nl.md` — Korte inleiding tot Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.ru.md` — Знакомство с Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.sv.md` — Kort introduktion till Terminologue
  - `docs/teanga/gaois-terminologue-website-docs-intro.tr.md` — Terminologue'a kısa bir giriş
  - `docs/teanga/gaois-terminologue-website-docs-intro.zh.md` — Terminologue簡介
  - `docs/teanga/gaois-terminologue-website-docs-top.en.md` — Terminologue Offline Processor
  - `docs/teanga/gaois-terminologue-website-libs-screenful-README.md` — Screenful
  - `docs/teanga/gaois-terminologue-website-libs-xonomy-README.md` — Xonomy
  - `docs/teanga/geoai-British Isles Celtic Language Education Data.md` — **The State of Education and Celtic Language Revitalisation in the British Isles: Demographic Shifts
  - `docs/teanga/geoai-British Isles Education Map.md` — **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report**
  - `docs/teanga/irish_bilingual_dataset_research.md` — Irish-English Bilingual Dataset Creation: Technical Research Outline
  - `docs/teanga/kscanne-1070-README.md` — kscanne 1070 README
  - `docs/teanga/kscanne-2100-README.md` — kscanne 2100 README
  - `docs/teanga/kscanne-2300-README.md` — 2300
  - `docs/teanga/kscanne-5750-README.md` — 5750
  - `docs/teanga/kscanne-5755-README.md` — kscanne 5755 README
  - `docs/teanga/kscanne-Hyphenator-README.md` — Hyphenator.js
  - `docs/teanga/kscanne-Irish-Dependency-Treebank-README.md` — kscanne Irish Dependency Treebank README
  - `docs/teanga/kscanne-Irish-Universal-Dependency-Treebank-README.md` — kscanne Irish Universal Dependency Treebank README
  - `docs/teanga/kscanne-KCG_SUMMARY.md` — KCG_SUMMARY: kscanne — Irish NLP Tools Repository
  - `docs/teanga/kscanne-UD_Irish-IDT-CONTRIBUTING.md` — Contributing
  - `docs/teanga/kscanne-beach-README.md` — kscanne beach README
  - `docs/teanga/kscanne-cadhan.com-README.md` — cadhan.com
  - `docs/teanga/kscanne-chichewa-README.md` — kscanne chichewa README
  - `docs/teanga/kscanne-crubadan.web-README.md` — An Crúbadán - Web
  - `docs/teanga/kscanne-crubadan_clld-README.md` — An Crúbadán - clld
  - `docs/teanga/kscanne-fst-README.md` — fst
  - `docs/teanga/kscanne-fulah-wordlist-README.md` — fulah-wordlist
  - `docs/teanga/kscanne-gbb-README.md` — kscanne gbb README
  - `docs/teanga/kscanne-gbb-classification-dialect-README.md` — kscanne gbb classification dialect README
  - `docs/teanga/kscanne-gbb-classification-gender-README.md` — kscanne gbb classification gender README
  - `docs/teanga/kscanne-gbb-classification-native-README.md` — kscanne gbb classification native README
  - `docs/teanga/kscanne-gbb-classification-sentiment-README.md` — kscanne gbb classification sentiment README
  - `docs/teanga/kscanne-gbb-classification-topic-README.md` — kscanne gbb classification topic README
  - `docs/teanga/kscanne-gbb-datasets-bli-README.md` — kscanne gbb datasets bli README
  - `docs/teanga/kscanne-gbb-datasets-blogspot-README.md` — kscanne gbb datasets blogspot README
  - `docs/teanga/kscanne-gbb-datasets-errors-README.md` — kscanne gbb datasets errors README
  - `docs/teanga/kscanne-gbb-datasets-inscne-README.md` — kscanne gbb datasets inscne README
  - `docs/teanga/kscanne-gbb-datasets-iudt-README.md` — kscanne gbb datasets iudt README
  - `docs/teanga/kscanne-gbb-datasets-sentiment-README.md` — kscanne gbb datasets sentiment README
  - `docs/teanga/kscanne-gbb-datasets-topaic-README.md` — kscanne gbb datasets topaic README
  - `docs/teanga/kscanne-gbb-datasets-tuairisc-README.md` — kscanne gbb datasets tuairisc README
  - `docs/teanga/kscanne-gbb-datasets-twittirish-README.md` — kscanne gbb datasets twittirish README
  - `docs/teanga/kscanne-gbb-generation-lm-README.md` — kscanne gbb generation lm README
  - `docs/teanga/kscanne-gbb-generation-qa-README.md` — kscanne gbb generation qa README
  - `docs/teanga/kscanne-gbb-proofing-diacritics-README.md` — kscanne gbb proofing diacritics README
  - `docs/teanga/kscanne-gbb-proofing-grammar-README.md` — kscanne gbb proofing grammar README
  - `docs/teanga/kscanne-gbb-proofing-mutations-README.md` — kscanne gbb proofing mutations README
  - `docs/teanga/kscanne-gbb-proofing-standardization-README.md` — kscanne gbb proofing standardization README
  - `docs/teanga/kscanne-gbb-syntax-chunking-README.md` — kscanne gbb syntax chunking README
  - `docs/teanga/kscanne-gbb-syntax-constituency-README.md` — kscanne gbb syntax constituency README
  - `docs/teanga/kscanne-gbb-syntax-dependency-README.md` — kscanne gbb syntax dependency README
  - `docs/teanga/kscanne-gbb-tagging-codeswitch-README.md` — kscanne gbb tagging codeswitch README
  - `docs/teanga/kscanne-gbb-tagging-lemmatization-README.md` — kscanne gbb tagging lemmatization README
  - `docs/teanga/kscanne-gbb-tagging-ner-README.md` — kscanne gbb tagging ner README
  - `docs/teanga/kscanne-gbb-tagging-pos-README.md` — kscanne gbb tagging pos README
  - `docs/teanga/kscanne-gbb-translation-en-README.md` — kscanne gbb translation en README
  - `docs/teanga/kscanne-gbb-translation-gd-README.md` — kscanne gbb translation gd README
  - `docs/teanga/kscanne-gbb-translation-gv-README.md` — kscanne gbb translation gv README
  - `docs/teanga/kscanne-gbb-translation-lexicon-README.md` — kscanne gbb translation lexicon README
  - `docs/teanga/kscanne-gramadoir-API.md` — kscanne gramadoir API
  - `docs/teanga/kscanne-grammatach-README.md` — kscanne grammatach README
  - `docs/teanga/kscanne-hunspell-rw-README.md` — hunspell-rw
  - `docs/teanga/kscanne-itweets-geodata-README.md` — kscanne itweets geodata README
  - `docs/teanga/kscanne-nishanimate-README.md` — NishAnimate
  - `docs/teanga/kscanne-ogham-README.md` — kscanne ogham README
  - `docs/teanga/kscanne-spelling-errors-GA-README.md` — spelling-errors-GA
  - `docs/teanga/kscanne-treocht-API.md` — kscanne treocht API
  - `docs/teanga/kscanne-unicorn-README.md` — kscanne unicorn README
  - `docs/teanga/repo-IRLBench.md` — KCG_SUMMARY: IRLBench — Irish-English Bilingual LLM Benchmark
  - `docs/teanga/repo-tts-dataset-generator.md` — KCG_SUMMARY: TTS Dataset Generator — Automated Speech Dataset Creation
- **docs/tuatha** (44 files):
  - `docs/sruth/tuatha/ADDING_ZONES.md` — Adding New Game Zones
  - `docs/sruth/tuatha/API.md` — Tuath API Reference
  - `docs/sruth/tuatha/British Isles Education Map.md` — **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report**
  - `docs/sruth/tuatha/British Isles Mythology MMO Research.md` — **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse**
  - `docs/sruth/tuatha/CELTIC_LANGUAGES.md` — Celtic Languages Integration
  - `docs/sruth/tuatha/CROSS_PLATFORM_GUIDE.md` — Cross-Platform Development Guide
  - `docs/sruth/tuatha/Celtic Etymology for Game Names.md` — **Compendium of Celtic Lexicography for Digital World-Building: A Comparative Analysis of Goidelic a
  - `docs/sruth/tuatha/Celtic MMO Web3 Concept Integration.md` — **Philological and Ludological Feasibility Study: Celtic Nomenclature in Web3 Massively Multiplayer 
  - `docs/sruth/tuatha/Chemistry Education Asset Generation.md` — **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architectur
  - `docs/sruth/tuatha/Educational Game Dev Pipeline.md` — **High-Fidelity Pedagogical Simulation: A Comprehensive Framework for Automating Scientifically Accu
  - `docs/sruth/tuatha/Fine-tuning VLMs for iOS HTR.md` — **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on i
  - `docs/sruth/tuatha/GAME_CLIENT.md` — Babylon.js Game Client
  - `docs/sruth/tuatha/PAYMENT_GUIDE.md` — Payment Integration Guide
  - `docs/sruth/tuatha/PERFORMANCE_TUNING.md` — Performance Tuning Guide
  - `docs/sruth/tuatha/SPACETIMEDB_GUIDE.md` — SpacetimeDB Guide
  - `docs/sruth/tuatha/Spacetimedb Blockchain Integration Strategy.md` — **Architectural Convergence: Implementing a Massively Multiplayer Celtic Odyssey via SpacetimeDB, So
  - `docs/sruth/tuatha/WGPU_GUIDE.md` — WGPU Guide
  - `docs/sruth/tuatha/Web3 Classroom Response System Design.md` — **Architectural Blueprint for "Cianfhoghlaim": A Decentralized, Physical-Digital Educational Ecosyst
  - `docs/sruth/tuatha/api-README.md` — API Reference Index
  - `docs/sruth/tuatha/educational-game-development.md` — Educational Game Development
  - `docs/sruth/tuatha/mythology-framework.md` — **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse**
  - `docs/sruth/tuatha/sruth/tuatha/ADDING_ZONES.md` — Adding New Game Zones
  - `docs/sruth/tuatha/sruth/tuatha/API.md` — Tuath API Reference
  - `docs/sruth/tuatha/sruth/tuatha/British Isles Education Map.md` — **The British Isles Demographic Atlas: A Comprehensive Technical and Statistical Report**
  - `docs/sruth/tuatha/sruth/tuatha/British Isles Mythology MMO Research.md` — **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse**
  - `docs/sruth/tuatha/sruth/tuatha/CELTIC_LANGUAGES.md` — Celtic Languages Integration
  - `docs/sruth/tuatha/sruth/tuatha/CROSS_PLATFORM_GUIDE.md` — Cross-Platform Development Guide
  - `docs/sruth/tuatha/sruth/tuatha/Celtic Etymology for Game Names.md` — **Compendium of Celtic Lexicography for Digital World-Building: A Comparative Analysis of Goidelic a
  - `docs/sruth/tuatha/sruth/tuatha/Celtic MMO Web3 Concept Integration.md` — **Philological and Ludological Feasibility Study: Celtic Nomenclature in Web3 Massively Multiplayer 
  - `docs/sruth/tuatha/sruth/tuatha/Chemistry Education Asset Generation.md` — **Digital Transformation of the Irish Chemistry Specification: A Comprehensive Technical Architectur
  - `docs/sruth/tuatha/sruth/tuatha/Educational Game Dev Pipeline.md` — **High-Fidelity Pedagogical Simulation: A Comprehensive Framework for Automating Scientifically Accu
  - `docs/sruth/tuatha/sruth/tuatha/Fine-tuning VLMs for iOS HTR.md` — **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on i
  - `docs/sruth/tuatha/sruth/tuatha/GAME_CLIENT.md` — Babylon.js Game Client
  - `docs/sruth/tuatha/sruth/tuatha/PAYMENT_GUIDE.md` — Payment Integration Guide
  - `docs/sruth/tuatha/sruth/tuatha/PERFORMANCE_TUNING.md` — Performance Tuning Guide
  - `docs/sruth/tuatha/sruth/tuatha/SPACETIMEDB_GUIDE.md` — SpacetimeDB Guide
  - `docs/sruth/tuatha/sruth/tuatha/Spacetimedb Blockchain Integration Strategy.md` — **Architectural Convergence: Implementing a Massively Multiplayer Celtic Odyssey via SpacetimeDB, So
  - `docs/sruth/tuatha/sruth/tuatha/WGPU_GUIDE.md` — WGPU Guide
  - `docs/sruth/tuatha/sruth/tuatha/Web3 Classroom Response System Design.md` — **Architectural Blueprint for "Cianfhoghlaim": A Decentralized, Physical-Digital Educational Ecosyst
  - `docs/sruth/tuatha/sruth/tuatha/api-README.md` — API Reference Index
  - `docs/sruth/tuatha/sruth/tuatha/educational-game-development.md` — Educational Game Development
  - `docs/sruth/tuatha/sruth/tuatha/mythology-framework.md` — **Project Anam: A Foundation for a Pan-Celtic Linguistic Metaverse**
  - `docs/sruth/tuatha/sruth/tuatha/world-map.md` — **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the Britis
  - `docs/sruth/tuatha/world-map.md` — **Architectural Blueprint for "Celtic OS": A Spatial-Interactive Learning Environment for the Britis
- **docs/web** (2 files):
  - `docs/web/Educational Website Tech Stack.md` — **Technical Blueprint for a Next-Generation Leaving Certificate Education Platform: Architecture, Pe
  - `docs/web/React Drag-and-Drop for Exam Builder.md` — **Architectural Blueprint for an Intelligent, British Curriculum-Aligned Interactive Exam Builder**

### 12-Gaming, Crypto & Web3 (Túatha)

**Description:** Godot, WGPU, SpacetimeDB, Babylon.js, x402, SIWE, tokenomics, MMO architecture
**Count:** 40 files, 466.8 KiB

- **docs/bonneagar** (1 files):
  - `docs/bonneagar/frontend-integration.md` — Frontend Integration for Crypto Analytics Platform
- **docs/context** (1 files):
  - `docs/context/package-ecosystem/frontend/babylonjs.md` — Babylon.js — 3D Web Rendering Engine
- **docs/teanga** (1 files):
  - `docs/teanga/Game Dev Pipeline Research & Plan.md` — **Converging High-Fidelity Pre-Rendering and Database-Driven State: A Comprehensive Technical Bluepr
- **docs/tuatha** (36 files):
  - `docs/sruth/tuatha/CRYPTO_INTEGRATION_SUMMARY.md` — Comprehensive Crypto & Payment Integration Summary for Crypteolas
  - `docs/sruth/tuatha/GODOT_RUST_GUIDE.md` — Godot + Rust Guide
  - `docs/sruth/tuatha/Game Dev Pipeline Research & Plan.md` — **Converging High-Fidelity Pre-Rendering and Database-Driven State: A Comprehensive Technical Bluepr
  - `docs/sruth/tuatha/MMO Geospatial Data & Visual RAG.md` — **Technical Blueprint for a Browser-Based WebGPU MMO: The Geospatial Spirit World**
  - `docs/sruth/tuatha/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md` — Release v28.0.0   Mesh Shaders, Immediates, and More! · gfx rs wgpu
  - `docs/sruth/tuatha/SpacetimeDB Ogham Stone Game Integration.md` — **Architectural Specification: Decentralized Geospatial Procedural Generation Systems for the 'Anam'
  - `docs/sruth/tuatha/SpacetimeDB.md` — SpacetimeDB
  - `docs/sruth/tuatha/game-design-README.md` — Game Design
  - `docs/sruth/tuatha/game_CONTRIBUTING.md` — Contributing
  - `docs/sruth/tuatha/gdext-ReadMe.md` — Rust bindings for Godot 4
  - `docs/sruth/tuatha/repo-SpacetimeDB.md` — SpacetimeDB — KCG Summary
  - `docs/sruth/tuatha/repo-hophacks-spacetimedb-workshop.md` — hophacks-spacetimedb-workshop — KCG Summary
  - `docs/sruth/tuatha/repo-react-native-godot.md` — react-native-godot — KCG Summary
  - `docs/sruth/tuatha/repo-spacetimedb-cookbook.md` — SpacetimeDB Cookbook — KCG Summary
  - `docs/sruth/tuatha/repo-spacetimedb-typescript-sdk.md` — spacetimedb-typescript-sdk — KCG Summary
  - `docs/sruth/tuatha/repo-wgpu.md` — wgpu — KCG Summary
  - `docs/sruth/tuatha/repo-x402.md` — x402 — KCG Summary
  - `docs/sruth/tuatha/tokenomics-README.md` — Tokenomics
  - `docs/sruth/tuatha/sruth/tuatha/CRYPTO_INTEGRATION_SUMMARY.md` — Comprehensive Crypto & Payment Integration Summary for Crypteolas
  - `docs/sruth/tuatha/sruth/tuatha/GODOT_RUST_GUIDE.md` — Godot + Rust Guide
  - `docs/sruth/tuatha/sruth/tuatha/Game Dev Pipeline Research & Plan.md` — **Converging High-Fidelity Pre-Rendering and Database-Driven State: A Comprehensive Technical Bluepr
  - `docs/sruth/tuatha/sruth/tuatha/MMO Geospatial Data & Visual RAG.md` — **Technical Blueprint for a Browser-Based WebGPU MMO: The Geospatial Spirit World**
  - `docs/sruth/tuatha/sruth/tuatha/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md` — Release v28.0.0   Mesh Shaders, Immediates, and More! · gfx rs wgpu
  - `docs/sruth/tuatha/sruth/tuatha/SpacetimeDB Ogham Stone Game Integration.md` — **Architectural Specification: Decentralized Geospatial Procedural Generation Systems for the 'Anam'
  - `docs/sruth/tuatha/sruth/tuatha/SpacetimeDB.md` — SpacetimeDB
  - `docs/sruth/tuatha/sruth/tuatha/game-design-README.md` — Game Design
  - `docs/sruth/tuatha/sruth/tuatha/game_CONTRIBUTING.md` — Contributing
  - `docs/sruth/tuatha/sruth/tuatha/gdext-ReadMe.md` — Rust bindings for Godot 4
  - `docs/sruth/tuatha/sruth/tuatha/repo-SpacetimeDB.md` — SpacetimeDB — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/repo-hophacks-spacetimedb-workshop.md` — hophacks-spacetimedb-workshop — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/repo-react-native-godot.md` — react-native-godot — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/repo-spacetimedb-cookbook.md` — SpacetimeDB Cookbook — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/repo-spacetimedb-typescript-sdk.md` — spacetimedb-typescript-sdk — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/repo-wgpu.md` — wgpu — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/repo-x402.md` — x402 — KCG Summary
  - `docs/sruth/tuatha/sruth/tuatha/tokenomics-README.md` — Tokenomics
- **docs/web** (1 files):
  - `docs/web/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md` — Release v28.0.0   Mesh Shaders, Immediates, and More! · gfx rs wgpu

### 13-Unclassified / Miscellaneous

**Count:** 124 files
**Description:** Files that didn't match any cluster keyword. Mostly indexes, READMEs, and general overviews.

- `docs/bonneagar/.!31103!monorepo-best-practices-2025.md` — Monorepo Management Best Practices Research
- `docs/bonneagar/AI Partner Catalyst_ Accelerate Innovation(1).md` — AI Partner Catalyst  Accelerate Innovation(1)
- `docs/bonneagar/Crawl4ai Scraping and Site Analysis.md` — **Architectural Blueprint for Autonomous Web Reconnaissance and High-Value Asset Extraction: Integra
- `docs/bonneagar/OPENAPI_SPECS_SUMMARY.md` — OpenAPI Specifications Research Summary
- `docs/bonneagar/OPENSPEC_ANALYSIS.md` — OpenSpec Analysis Report: Comprehensive Structure and Guidelines
- `docs/bonneagar/OPENSPEC_README.md` — OpenSpec Documentation Index
- `docs/bonneagar/Register a GCP Instance.md` — Register a GCP Instance
- `docs/bonneagar/SECRETS_MANAGEMENT_GUIDE.md` — Secrets Management — Locket + Infisical Complete Guide
- `docs/bonneagar/TECH_STACK.md` — TECH STACK
- `docs/bonneagar/Unified Scraping Swarm Stack Optimization.md` — **Architectural Synthesis of a Unified Scraping Swarm: Optimizing Skyvern, Crawl4AI, and Stagehand v
- `docs/bonneagar/acquisition-pipeline.md` — Data Acquisition Pipeline Implementation
- `docs/bonneagar/backend.md` — Ibis Backend Selection Assistant
- `docs/bonneagar/crawlai_vs_firecrawl.py` — append the path to the root of the project
- `docs/bonneagar/demo_multi_config_clean.py` — demo multi config clean
- `docs/bonneagar/firecrawl-openapi-research.md` — Firecrawl OpenAPI Specification Research Report
- `docs/bonneagar/graph-visualization.md` — Graph Visualization Tools and Patterns
- `docs/bonneagar/infisical.md` — Infisical Development Assistant
- `docs/bonneagar/llm_config_example.py` — llm config example
- `docs/bonneagar/llm_extraction_openai_pricing.py` — llm extraction openai pricing
- `docs/bonneagar/monorepo-best-practices-2025.md` — Monorepo Management Best Practices Research
- `docs/bonneagar/overview.md` — Cianfhoghlaim Platform Overview
- `docs/bonneagar/scraping_strategies_performance.py` — WebScrapingStrategy is now an alias for LXMLWebScrapingStrategy
- `docs/bonneagar/specialized-pipelines.md` — Specialized Pipelines
- `docs/bonneagar/subject-implementations.md` — Subject-Specific Implementations
- `docs/bonneagar/summarize_page.py` — summarize page
- `docs/bonneagar/technical-implementation.md` — Technical Implementation
- `docs/bonneagar/tmx-processing.md` — TMX File Processing
- `docs/bonneagar/update-specs.md` — Update Specs
- `docs/context/00-core/PROJECT_SPEC.md` — Cianfhoghlaim Project Conventions
- `docs/context/01-patterns/OBSERVABILITY.md` — Pattern: Observability (Datadog, MLflow, Langfuse, Ragas)
- `docs/context/02-architecture/ALEYUM_PORTFOLIO.md` — Aleyum Portfolio
- `docs/context/02-architecture/ML_SYSTEMS.md` — Comprehensive AI/ML Systems Architecture & Integration Guide
- `docs/context/03-pipelines/ag_ui_protocol.py` — ag ui protocol
- `docs/context/08-examples/BEADS_TRACKER.md` — Beads - AI-Native Issue Tracking
- `docs/context/08-examples/IMPLEMENTATION_GUIDE.md` — Implementation Guide & Best Practices
- `docs/context/08-examples/OIDEACHAIS_SPEC.md` — Oideachais Pipeline Capability
- `docs/context/08-examples/SUBJECT_IMPLEMENTATIONS.md` — Subject-Specific Implementations
- `docs/context/2602.15763v2.pdf` — 2602.15763v2
- `docs/context/INDEX.md` — Cianfhoghlaim Context Library
- `docs/context/Licensing and Government Opportunities.pdf` — Licensing and Government Opportunities
- `docs/context/james_hardiman_library.pdf` — james hardiman library
- `docs/context/package-ecosystem/ai-frameworks/ragas.md` — RAGAS — RAG Evaluation Framework
- `docs/context/package-ecosystem/browser/crawl4ai-sdk.md` — Crawl4AI — AI-Powered Web Crawling SDK
- `docs/context/package-ecosystem/browser/patchright.md` — Patchright — Stealth Browser Automation
- `docs/context/package-ecosystem/browser/stagehand.md` — Stagehand — AI Browser Operator (Python SDK)
- `docs/data_engineering/21109422_universal-junior-cycle-short-course-scoping-document_ga.docx` — 21109422 universal junior cycle short course scoping document ga
- `docs/data_engineering/ARCHITECTURE.md` — Data Stack Architecture Reference
- `docs/data_engineering/FIBO Hackathon.md` — FIBO Hackathon
- `docs/data_engineering/geoai-reference.md` — GeoAI Reference
- `docs/data_engineering/migrate.md` — pandas to Ibis Migration Assistant
- `docs/data_engineering/query.md` — Ibis Query Builder Assistant
- `docs/data_engineering/semantic-layer-reference.md` — Semantic Layer Reference
- `docs/data_engineering/tool-ecosystem.md` — Tool Ecosystem Reference
- `docs/data_engineering/transformers.md` — Transformers.js
- `docs/meaisínfhoghlaim/Federated RAG Tutorial_ Build Privacy-Preserving LLM Systems in Python ⬩OpenMined.md` — Federated RAG Tutorial  Build Privacy Preserving LLM Systems in Python ⬩OpenMined
- `docs/meaisínfhoghlaim/Google ADK with LiteLLM _ liteLLM.md` — Google ADK with LiteLLM   liteLLM
- `docs/meaisínfhoghlaim/IMPLEMENTATION_GUIDE.md` — Implementation Guide & Best Practices
- `docs/meaisínfhoghlaim/Interactions API _ Gemini API _ Google AI for Developers.md` — Interactions API   Gemini API   Google AI for Developers
- `docs/meaisínfhoghlaim/Introducing Bolmo_ Byteifying the next generation of language models _ Ai2.md` — Introducing Bolmo  Byteifying the next generation of language models   Ai2
- `docs/meaisínfhoghlaim/LiteLLM - Pydantic Logfire Documentation.md` — LiteLLM   Pydantic Logfire Documentation
- `docs/meaisínfhoghlaim/Pydantic AI Gateway - Pydantic AI.md` — Pydantic AI Gateway   Pydantic AI
- `docs/meaisínfhoghlaim/RESEARCH_CONSOLIDATION_PLAN.md` — Research Analysis & Centralization Plan
- `docs/meaisínfhoghlaim/Train a tiny model to generate 3D files (v2) through example diversification.md` — Train a tiny model to generate 3D files (v2) through example diversification
- `docs/meaisínfhoghlaim/ag-ui_sdks_community_kotlin at main · ag-ui-protocol_ag-ui.md` — ag ui sdks community kotlin at main · ag ui protocol ag ui
- `docs/meaisínfhoghlaim/ai-compute-allocation-strategy.md` — **A Strategic Blueprint for a Polyglot AI & Data Platform**
- `docs/meaisínfhoghlaim/ai-ml-systems-consolidated.md` — Comprehensive AI/ML Systems Architecture & Integration Guide
- `docs/meaisínfhoghlaim/dual-engine-graph-llm-serving-integration.md` — Dual-Engine Graph + Complementary LLM Serving Integration
- `docs/meaisínfhoghlaim/fine-tuning-guide.md` — fine tuning guide
- `docs/meaisínfhoghlaim/fine-tuning-reference.md` — Comprehensive LLM Fine-Tuning Reference
- `docs/meaisínfhoghlaim/langfuse-guide.md` — Langfuse LLM Observability Platform - Comprehensive Research
- `docs/meaisínfhoghlaim/langfuse_ragas.md` — langfuse ragas
- `docs/meaisínfhoghlaim/litellm-comprehensive-guide.md` — LiteLLM API Patterns and Usage Conventions - Comprehensive Research
- `docs/meaisínfhoghlaim/litellm_config.yaml` — LiteLLM Configuration File
- `docs/meaisínfhoghlaim/mlflow-llm-guide.md` — MLflow LLM Features Reference Documentation
- `docs/meaisínfhoghlaim/mlflow_ragas.md` — mlflow ragas
- `docs/meaisínfhoghlaim/model-ecosystem.md` — model ecosystem
- `docs/meaisínfhoghlaim/notebook-catalog.md` — noteuook catalog
- `docs/meaisínfhoghlaim/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md` — syft flwr notebooks fedrag README.md at main · OpenMined syft flwr
- `docs/meaisínfhoghlaim/transformers.md` — Transformers.js
- `docs/teanga/AI Partner Catalyst_ Accelerate Innovation.md` — AI Partner Catalyst  Accelerate Innovation
- `docs/teanga/BritLLM.md` — BritLLM
- `docs/teanga/Digital Resources for the Languages in Ireland and Britain(1).md` — Digital Resources for the Languages in Ireland and Britain(1)
- `docs/teanga/Digital Resources for the Languages in Ireland and Britain.md` — Digital Resources for the Languages in Ireland and Britain
- `docs/teanga/Google ADK with LiteLLM _ liteLLM.md` — Google ADK with LiteLLM   liteLLM
- `docs/teanga/datasets-BritLLM.md` — datasets BritLLM
- `docs/teanga/repo-genizah_search.md` — KCG_SUMMARY: Genizah Search — Cairo Genizah AI Semantic Search Application
- `docs/sruth/tuatha/2510.17652v1.pdf` — 2510.17652v1
- `docs/sruth/tuatha/ANALYSIS.md` — Cianfhoghlaim Project Analysis
- `docs/sruth/tuatha/ERC-4361_ Sign-In with Ethereum.md` — ERC 4361  Sign In with Ethereum
- `docs/sruth/tuatha/GeoAI.md` — GeoAI
- `docs/sruth/tuatha/INDEX.md` — Túatha Documentation Index
- `docs/sruth/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md` — Kotlin Multiplatform vs. React Native  A cross platform comparison   Kotlin Multiplatform
- `docs/sruth/tuatha/The Expulsion of the Déisi - Wikipedia.md` — The Expulsion of the Déisi   Wikipedia
- `docs/sruth/tuatha/ml-models-README.md` — ML Models
- `docs/sruth/tuatha/repo-AnyLanguageModel.md` — AnyLanguageModel — KCG Summary
- `docs/sruth/tuatha/repo-agui_kotlin.md` — agui_kotlin — KCG Summary
- `docs/sruth/tuatha/repo-ireland.md` — ireland — KCG Summary
- `docs/sruth/tuatha/repo-react-native-reusables.md` — react-native-reusables — KCG Summary
- `docs/sruth/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md` — syft flwr notebooks fedrag README.md at main · OpenMined syft flwr
- `docs/sruth/tuatha/sruth/tuatha/2510.17652v1.pdf` — 2510.17652v1
- `docs/sruth/tuatha/sruth/tuatha/ANALYSIS.md` — Cianfhoghlaim Project Analysis
- `docs/sruth/tuatha/sruth/tuatha/ERC-4361_ Sign-In with Ethereum.md` — ERC 4361  Sign In with Ethereum
- `docs/sruth/tuatha/sruth/tuatha/GeoAI.md` — GeoAI
- `docs/sruth/tuatha/sruth/tuatha/INDEX.md` — Túatha Documentation Index
- `docs/sruth/tuatha/sruth/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md` — Kotlin Multiplatform vs. React Native  A cross platform comparison   Kotlin Multiplatform
- `docs/sruth/tuatha/sruth/tuatha/The Expulsion of the Déisi - Wikipedia.md` — The Expulsion of the Déisi   Wikipedia
- `docs/sruth/tuatha/sruth/tuatha/ml-models-README.md` — ML Models
- `docs/sruth/tuatha/sruth/tuatha/repo-AnyLanguageModel.md` — AnyLanguageModel — KCG Summary
- `docs/sruth/tuatha/sruth/tuatha/repo-agui_kotlin.md` — agui_kotlin — KCG Summary
- `docs/sruth/tuatha/sruth/tuatha/repo-ireland.md` — ireland — KCG Summary
- `docs/sruth/tuatha/sruth/tuatha/repo-react-native-reusables.md` — react-native-reusables — KCG Summary
- `docs/sruth/tuatha/sruth/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md` — syft flwr notebooks fedrag README.md at main · OpenMined syft flwr
- `docs/web/AG-UI - Pydantic AI.md` — AG UI   Pydantic AI
- `docs/web/AG-UI Overview.md` — AG UI Overview
- `docs/web/INDEX-from-bonneagar-web-research.md` — Web Research - Consolidated Index
- `docs/web/PDF.js - Examples.md` — PDF.js   Examples
- `docs/web/README.md` — Frontend
- `docs/web/ag-ui_docs_sdk_kotlin_overview.mdx at main · ag-ui-protocol_ag-ui.md` — ag ui docs sdk kotlin overview.mdx at main · ag ui protocol ag ui
- `docs/web/ref-cianfhoghlaim-base-template.md` — Cianfhoghlaim Base — KCG Summary
- `docs/web/ref-ui-inspiration.md` — UI Inspiration Guide for sruth/ Frontends
- `docs/web/ref-unified-examples.md` — Consolidated Examples — KCG Summary
- `docs/web/repo-ag-ui-protocol.md` — AG-UI Protocol — KCG Summary
- `docs/web/repo-restate-ui-readme.md` — UI
- `docs/web/🌉 How to Use Swift Inside Kotlin Multiplatform_ The iOS Bridge Explained (with a Real Example).md` — 🌉 How to Use Swift Inside Kotlin Multiplatform  The iOS Bridge Explained (with a Real Example)

## 7. Consolidation Recommendations

### Immediate Actions (Zero-Risk)
1. **Delete `docs/sruth/tuatha/sruth/tuatha/`** — 116 exact duplicates of parent directory files.
2. **Deduplicate the 3 identical `Prompt Optimization (Beta)` copies** in `docs/meaisínfhoghlaim/`.
3. **Remove `.DS_Store` files** from all subtrees.

### Structural Consolidation
4. **Merge duplicate research articles** across subtrees — many articles appear in both `docs/teanga/` and `docs/sruth/tuatha/`, and between `docs/meaisínfhoghlaim/` and `docs/teanga/`.
5. **Adopt the 12-cluster structure** above as the new canonical docs layout.
6. **Standardize frontmatter** with required fields: `title:`, `domain:`, `status:`, `cluster:`.
7. **Split bilingual files** — `.ga.md` and `.en.md` pairs should be kept together in locale subdirectories or merged with lang tabs.
8. **Consolidate the gaois/kscanne READMEs** — many 1-line stub files that could be a single index page.

### Size Hotspots (files > 200 KiB)

| Size | File | Summary |
|---|---|---|
| 15.2 MiB | docs/context/james_hardiman_library.pdf | james hardiman library |
| 6.2 MiB | docs/context/2602.15763v2.pdf | 2602.15763v2 |
| 2.1 MiB | docs/bonneagar/development-tools.md | Development Tools |
| 824.1 KiB | docs/data_engineering/tool-ecosystem.md | Tool Ecosystem Reference |
| 643.4 KiB | docs/data_engineering/cocoindex-comprehensive.md | CocoIndex Comprehensive Guide |
| 636.4 KiB | docs/meaisínfhoghlaim/celtic-language-ai.md | celtic language ai |
| 549.8 KiB | docs/bonneagar/infrastructure-tools.md | Infrastructure Tools |
| 504.8 KiB | docs/data_engineering/data-architecture.md | Data Architecture Reference |
| 492.7 KiB | docs/data_engineering/dagster-comprehensive.md | Dagster Comprehensive Guide |
| 421.3 KiB | docs/context/Licensing and Government Opportunities.pdf | Licensing and Government Opportunities |
| 377.0 KiB | docs/bonneagar/data-acquisition.md | Data Acquisition & Integrations |
| 363.3 KiB | docs/agents/agent-frameworks.md | agent frameworks |
| 359.3 KiB | docs/meaisínfhoghlaim/training-pipeline.md | training pipeline |
| 351.5 KiB | docs/context/Apple Education and AI Goals.pdf | Apple Education and AI Goals |
| 347.7 KiB | docs/sruth/tuatha/2510.17652v1.pdf | 2510.17652v1 |
| 347.7 KiB | docs/sruth/tuatha/sruth/tuatha/2510.17652v1.pdf | 2510.17652v1 |
| 331.2 KiB | docs/bonneagar/overview.md | Cianfhoghlaim Platform Overview |
| 310.0 KiB | docs/meaisínfhoghlaim/notebook-catalog.md | noteuook catalog |
| 289.9 KiB | docs/context/Irish Language Copyright and Education.pdf | Irish Language Copyright and Education |
| 278.4 KiB | docs/meaisínfhoghlaim/model-ecosystem.md | model ecosystem |
| 270.2 KiB | docs/data_engineering/dlt-comprehensive.md | dlt (Data Load Tool) Comprehensive Guide |
| 268.8 KiB | docs/data_engineering/data-versioning.md | Data Versioning Reference |
| 266.1 KiB | docs/data_engineering/semantic-layer-reference.md | Semantic Layer Reference |
| 204.0 KiB | docs/data_engineering/knowledge-systems.md | Knowledge Systems Reference |
