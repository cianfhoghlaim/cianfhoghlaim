---
domain: product
title: Educational Platform
description: Consolidated educational platform design, Leaving Cert curriculum, Celtic language learning, interactive tools, OCR pipelines, and all educational technology.
supersedes:
  - docs/tuatha/celtic-ocr.md
  - docs/tuatha/dlt_crawl4ai_lancedb.md
  - docs/tuatha/infrastructure-README.md
  - docs/tuatha/ml-models-README.md
  - docs/tuatha/unsloth-catalog.md
  - docs/tuatha/Unsloth Model Catalog _ Unsloth Documentation.md
  - docs/tuatha/Fine-tuning VLMs for iOS HTR.md
  - docs/tuatha/Irish Handwriting App Development.md
  - docs/tuatha/Irish LLM for iPhone Development.md
  - docs/tuatha/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md
  - docs/tuatha/syft-flwr_notebooks_fedrag_README.md at main · OpenMined_syft-flwr.md
  - docs/tuatha/repo-agui_kotlin.md
  - docs/tuatha/repo-AnyLanguageModel.md
  - docs/tuatha/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md
  - docs/tuatha/2510.17652v1.pdf
cognee_entities:
  - entity: CelticCurriculum
    type: EducationalContent
    relationships:
      - covers: NCCAStandards
      - covers: SQAStandards
      - covers: WJECStandards
      - delivered_via: InteractivePlatform
  - entity: CelticOCR
    type: Pipeline
    relationships:
      - uses: VLMModels
      - processes: GaelicManuscripts
      - outputs: DigitalText
ccc_query_hints:
  - "Celtic language learning platform"
  - "Leaving Cert Irish curriculum"
  - "Gaelic OCR pipeline"
  - "interactive Celtic education"
  - "fine-tuning VLM Irish"
updated: 2026-06-06
---

# Educational Platform

The educational platform delivers Celtic language learning, Leaving Cert curriculum preparation, and interactive cultural exploration through a gamified, AI-powered interface.

## 1. Platform Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Educational Platform                        │
├───────────────┬──────────────┬───────────────┬───────────────┤
│ Curriculum    │ AI Tutoring  │ Gamification  │ Assessment    │
│ Engine        │ System       │ Layer         │ Engine        │
├───────────────┴──────────────┴───────────────┴───────────────┤
│               Content Delivery (Web + Mobile)                 │
├──────────────────────────────────────────────────────────────┤
│                 Knowledge Graph (Graphiti/Cognee)             │
├──────────────────────────────────────────────────────────────┤
│        Data Pipeline (Dagster + DLT + CocoIndex)             │
└──────────────────────────────────────────────────────────────┘
```

## 2. Curriculum Scope

### Languages and Standards

| Language | Standard | Region |
|----------|----------|--------|
| **Irish (Gaeilge)** | NCCA — Junior Cycle & Leaving Cert | Republic of Ireland |
| **Welsh (Cymraeg)** | WJEC — GCSE & A-Level | Wales |
| **Scottish Gaelic (Gàidhlig)** | SQA — National 5, Higher, Advanced Higher | Scotland |

### Curriculum Content Domains

| Domain | Sub-Topics | Delivery |
|--------|-----------|----------|
| **Language** | Grammar, vocabulary, pronunciation, comprehension | Interactive quizzes, voice recognition, translation exercises |
| **Literature** | Poetry, prose, drama — Irish/Welsh/Scottish canon | AI-narrated stories, character analysis, essay practice |
| **Oral** | Conversation, storytelling, recitation | Voice recording, AI pronunciation feedback, peer practice |
| **Aural** | Listening comprehension | Audio clips with interactive questions |
| **Culture** | History, mythology, traditions, festivals | Quest-based exploration, mythology narratives |
| **Writing** | Essay, letter, diary entry, debate | AI-assisted writing, grammar checking, style suggestions |

### Leaving Cert Irish Structure (NCCA)

The platform maps directly to Leaving Cert Irish assessment components:

| Component | Weight | Platform Feature |
|-----------|--------|-----------------|
| **Oral (Béaltriail)** | 40% | AI voice practice, pronunciation scoring |
| **Aural (Cluastuiscint)** | 10% | Timed listening comprehension exercises |
| **Paper 1 (Composition)** | 25% | Essay writing with AI feedback |
| **Paper 2 (Literature & Language)** | 25% | Interactive text analysis, grammar drills |

## 3. Interactive Learning Features

### AI Tutor (CopilotKit + MCP-UI)

```typescript
// Embedded AI chat tutor
<CopilotChat
  labels={{
    title: "Cúntóir Gaeilge",
    initial: "Dia dhuit! Conas is féidir liom cabhrú leat inniu?"
  }}
/>

// Agent actions for curriculum delivery
useCopilotAction({
  name: "generate_grammar_exercise",
  description: "Create a grammar exercise for the given topic",
  parameters: [
    { name: "topic", type: "string", enum: ["verbs", "nouns", "prepositions", "mutations"] },
    { name: "difficulty", type: "number", minimum: 1, maximum: 5 },
    { name: "language", type: "string", enum: ["ga", "cy", "gd"] },
  ],
  handler: async ({ topic, difficulty, language }) => {
    return await curriculumAPI.generateExercise(topic, difficulty, language)
  },
})
```

### Voice Recognition (Oracy Mining)

- Browser-based Web Speech API for voice input
- Custom acoustic models for Celtic language pronunciation
- Real-time feedback on accuracy, fluency, and intonation
- Comparison against native speaker recordings

### Handwriting Capture (Translation Mining)

- PDF.js for rendering Leaving Cert exam papers
- Canvas-based handwriting capture
- Vision-Language Models for Gaelic handwriting recognition (HTR)
- Fine-tuned on historical manuscripts and modern student samples

### Knowledge Graph Integration

The platform uses a temporal knowledge graph for curriculum relationships:

| Entity | Relationship | Target |
|--------|-------------|--------|
| `GrammarTopic` | `PREREQUISITE_OF` | `GrammarTopic` |
| `Vocabulary` | `RELATED_TO` | `Theme` |
| `LiteraryWork` | `PART_OF` | `CurriculumUnit` |
| `Student` | `MASTERED` | `LearningOutcome` |

This enables: personalized learning paths, prerequisite validation, and progress tracking.

## 4. Celtic OCR Pipeline

### Document Intelligence Stack

```
Celtic Manuscript / Exam Paper
    ↓
Document Scanning / PDF Parsing
    ↓
Layout Analysis (table detection, column separation)
    ↓
Vision-Language Model (Fine-tuned VLM)
    ↓
Text Extraction (Irish/Welsh/English)
    ↓
Post-processing (spell check, grammar validation)
    ↓
Knowledge Graph Ingestion (Graphiti)
```

### Models

| Model | Purpose | Fine-tuning |
|-------|---------|------------|
| **PaddleOCR** | General text detection | Trained on Gaelic manuscripts |
| **DeepSeek-OCR** | Multi-language OCR | Celtic language corpus |
| **Granite Docling** | Document understanding | Exam paper structures |
| **FastVLM (Apple CVPR 2025)** | Efficient vision encoding | iOS HTR deployment |
| **Unsloth** | Efficient VLM fine-tuning | 70% VRAM reduction, 2x speedup |

### Unsloth Model Catalog (Celtic Focus)

| Base Model | Fine-Tuned For | Hardware Requirement |
|------------|---------------|---------------------|
| Llama-3-8B | Irish grammar generation | 16GB VRAM |
| Mistral-7B | Welsh literary analysis | 16GB VRAM |
| Gemma-2-9B | Scottish Gaelic tutor | 16GB VRAM |
| Qwen2-VL-7B | Gaelic manuscript OCR | 24GB VRAM |
| Phi-3-Vision | On-device handwriting | Apple Silicon 8GB |

## 5. Data Pipeline Architecture

### Curriculum Ingestion

```
NCCA Syllabus PDFs
    ↓
DLT Filesystem Pipeline (filesystem source → LanceDB)
    ↓
CocoIndex Text Splitting + Embedding (BGE-M3)
    ↓
Dagster Asset Materialization
    ↓
LanceDB Vector Store (hybrid search)
    ↓
Graphiti Knowledge Graph (temporal relationships)
```

### Pipeline Components

| Tool | Role |
|------|------|
| **Dagster** | Orchestration — asset-based scheduling, partitions |
| **DLT** | Data ingestion — curriculum docs to LanceDB |
| **CocoIndex** | Embedding pipeline — text → vectors |
| **LanceDB** | Vector database — HNSW indexing, hybrid search, MVCC |
| **DuckDB** | Analytical queries — student progress, curriculum analytics |
| **Feast** | Feature store — ML training-serving consistency |
| **Graphiti** | Temporal knowledge graph — prerequisite tracking |
| **MLflow** | Experiment tracking, model registry |
| **Langfuse** | LLM observability — traces, prompts, evaluations |

### Web Scraping Pipeline

Agentic browser automation for curriculum content:

```
Firecrawl / Crawl4AI / Stagehand
    ↓
Stealth Browser (sruth-browser)
    ↓
NCCA / SQA / WJEC websites
    ↓
Markdown extraction → Curriculum Pipeline
```

## 6. Mobile Strategy

### iOS App
- **Swift + SwiftUI** native interface
- **AnyLanguageModel** for multi-provider LLM (Apple, MLX, Ollama, OpenAI)
- **Swift Transformers** for on-device Celtic language models
- **Core ML** for offline handwriting recognition
- **FastVLM** for efficient vision encoding on Apple Silicon

### Android
- **Kotlin Multiplatform** shared code with iOS
- **AG-UI Kotlin SDK** for agent connectivity
- **React Native** for shared UI components
- **React Native Godot** for 3D educational content

### Cross-Platform Strategy

| Concern | iOS | Android | Shared |
|---------|-----|---------|--------|
| **AI Inference** | Core ML / MLX | TensorFlow Lite / ONNX | Model format conversion |
| **UI** | SwiftUI | Jetpack Compose | React Native for basic screens |
| **3D/Game** | Godot view | Godot view | Godot project |
| **Network** | SpacetimeDB SDK | SpacetimeDB SDK | SpacetimeDB protocol |
| **Auth** | BetterAuth + SIWE | BetterAuth + SIWE | OIDC / SIWE flow |

## 7. Assessment Types

### Interactive Quiz Formats
- Multiple choice (radio buttons)
- Multiple answer (checkboxes)
- True/False
- Short answer (text input)
- Essay (rich text with Tiptap)
- Drag-and-drop matching
- Fill in the blank
- Voice response (audio recording)

### AI-Assisted Scoring
- Grammar checking against curriculum rubrics
- Pronunciation assessment via acoustic models
- Essay scoring with LLM-based rubric application
- Real-time feedback with correction suggestions

### Progress Tracking
- **Soul Level**: Abstracted competence metric
- **Skill Trees**: Per-domain mastery visualization
- **NCCA Learning Outcome Mapping**: Direct curriculum alignment
- **Spaced Repetition**: Smart review scheduling

## 8. Chemistry & STEM Education

The platform extends beyond Celtic studies into STEM:

- **Chemistry Assets**: AI-generated molecular visualizations and reaction animations
- **Image Generation**: FLUX.1/SDXL for educational diagrams
- **Interactive 3D**: Godot-based molecular models and physics simulations
- **Bridge Curriculum**: Connecting Celtic heritage (metallurgy, astronomy, herbalism) to modern STEM

## 9. Federated Learning Integration

A decentralized model training approach preserving data privacy:

- **OpenMined / Syft + Flower**: Federated learning framework
- **iOS On-Device Training**: Apple Silicon optimized (MLX, Core ML)
- **Gradient Aggregation**: Secure aggregation without raw data sharing
- **Token Rewards**: Contributors earn Tuath tokens for providing compute and data
- **Model Registry**: MLflow tracking for federated training runs

## 10. Educational Game Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Contextual Learning** | Grammar taught through quest NPC dialogue |
| **Spaced Repetition** | Smart review scheduling based on forgetting curves |
| **Immediate Feedback** | Real-time AI scoring and correction |
| **Scaffolded Difficulty** | Content adapts to proficiency level (A1 → C2 CEFR) |
| **Social Learning** | Anam Cara bonds for cooperative study |
| **Intrinsic Motivation** | Earn Tuath tokens for knowledge, not grinding |
| **Cultural Immersion** | Mythology and geography as learning context |

## 11. Infrastructure

The platform is self-hosted on the Pangolin convergence architecture:

| Service | Host | Purpose |
|---------|------|---------|
| **Convex** | bunchloch (MacBook M4) | Real-time backend |
| **SpacetimeDB** | bunchloch | Game state |
| **Dagster** | bunchloch | Pipeline orchestration |
| **LanceDB** | bunchloch | Vector search |
| **DuckDB** | bunchloch | Analytics |
| **LLM Inference** | bunchloch (MLX) + API fallback | AI models |
| **Pangolin** | arm1-oci | Routing, reverse proxy |
| **Komodo** | arm1-oci | Container orchestration |
| **Pocket ID** | arm1-oci | OIDC authentication |
| **Infisical** | arm1-oci | Secrets management |
