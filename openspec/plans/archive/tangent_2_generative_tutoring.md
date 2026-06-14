---
title: 'Tangent 2 Generative Tutoring'
status: deferred
supersedes: []
superseded_by: [docs/00-deploy-plans/02-generative-tutoring.md, archive: openspec/plans/archive/tangent_2_generative_tutoring.md]
last_touched: 2026-06-13
---

# Strategic Plan: Tangent 2 - Hyper-Personalized, Cross-Lingual Generative Tutoring System

## 1. Executive Summary

**Tangent 2** envisions a next-generation, real-time generative tutoring system designed to seamlessly bridge concepts across English, Irish, and other Celtic languages. By combining the specialized linguistic capabilities of `UCCIX-Llama2-13B-Instruct` with the high-performance, embedded vector search of LanceDB, the platform will offer a hyper-personalized, context-aware learning experience. This system will not merely translate content but will understand conceptual links between languages, dynamically adjusting to a learner's proficiency and learning style.

## 2. Core Technological Synergies

### 2.1. UCCIX-Llama2-13B-Instruct: The Pedagogical Engine
*   **Role**: Serves as the primary conversational and reasoning engine, specialized for nuanced Irish/English bilingual interaction.
*   **Strengths**: Its 13B parameter size provides an ideal balance of robust reasoning capabilities and deployability. Its specific instruction-tuning allows for targeted pedagogical prompting (e.g., "Explain this mathematical concept in Irish, but provide the core vocabulary in English").
*   **Application**: Generating real-time explanations, generating quizzes, evaluating open-ended student responses, and dynamically adjusting the complexity of the language used.

### 2.2. LanceDB: The Conceptual Memory
*   **Role**: The vector database handling high-speed retrieval of educational content, curriculum standards, and user history.
*   **Strengths**: Serverless, embedded architecture ideal for real-time applications; multimodal capabilities allow linking text, audio, and visual learning aids.
*   **Application**: Storing cross-lingual embeddings. A concept like "Photosynthesis" in English and "Fótaisintéis" in Irish will map to similar vector spaces, allowing the system to retrieve related context regardless of the query language.

## 3. System Architecture & Cross-Lingual Bridging

### 3.1. The Shared Embedding Space
To achieve true cross-lingual tutoring, the system relies on a unified vector space:
1.  **Ingestion**: Educational materials (in English, Irish, etc.) are processed through a multilingual embedding model (e.g., an XLM-R or LaBSE variant) and stored in LanceDB.
2.  **Conceptual Mapping**: Because the embeddings represent semantic meaning rather than just keywords, querying LanceDB for a concept in Irish will yield relevant foundational materials in both Irish and English.
3.  **Retrieval-Augmented Generation (RAG)**: When a student asks a question, LanceDB retrieves the relevant multilingual context. This context is injected into the prompt for `UCCIX-Llama2-13B-Instruct`.

### 3.2. Real-Time Tutoring Workflow
1.  **User Input**: Student asks a question or submits an answer (e.g., in Irish).
2.  **State Assessment**: The system checks the student's profile (current proficiency in target language, preferred learning style).
3.  **Vector Retrieval**: LanceDB retrieves the relevant topic materials and past interactions.
4.  **Prompt Synthesis**: A complex prompt is assembled, dictating the persona (tutor), the context (from LanceDB), and the constraints (e.g., "Use B1 level Irish, provide English translations for technical terms").
5.  **Generation**: `UCCIX-Llama2-13B-Instruct` streams the personalized response back to the user.

## 4. Hyper-Personalization Strategy

*   **Dynamic Language Scaffolding**: For learners transitioning between languages (e.g., moving from English-medium to Irish-medium education), the tutor dynamically adjusts the ratio of English to Irish based on real-time comprehension checks.
*   **Knowledge Tracing**: LanceDB stores vector representations of the student's past errors and successes. If a student struggles with a concept, the system retrieves analogies that worked for them previously.
*   **Cultural Contextualization**: The generative model weaves in relevant cultural or local context to make abstract concepts more relatable, bridging the gap between standard curricula and local heritage.

## 5. Action Plan & Implementation Roadmap

### Phase 1: Foundation & Proof of Concept (Weeks 1-4)
*   **Task**: Setup LanceDB locally and ingest a constrained dataset (e.g., Junior Cycle Science curriculum in both English and Irish).
*   **Task**: Deploy `UCCIX-Llama2-13B-Instruct` via a local inference server (e.g., vLLM or Ollama) for rapid testing.
*   **Task**: Develop a basic RAG pipeline to verify cross-lingual retrieval accuracy (querying in Irish, retrieving English/Irish context, and generating an Irish response).

### Phase 2: Tutoring Engine Development (Weeks 5-8)
*   **Task**: Design and iterate on pedagogical prompt templates for `UCCIX-Llama2` (Socratic questioning, scaffolding, summarization).
*   **Task**: Implement the User State Manager to track session-level proficiency and learning styles.
*   **Task**: Build a simple chat interface to test the real-time latency and streaming capabilities.

### Phase 3: Advanced Features & Optimization (Weeks 9-12)
*   **Task**: Implement multi-turn memory utilizing LanceDB to store conversation histories as vectors.
*   **Task**: Fine-tune the multilingual embedding model if out-of-the-box cross-lingual semantic similarity is insufficient for specific educational domains.
*   **Task**: Conduct alpha testing with a small group of bilingual educators/students to gather qualitative feedback on the tutor's effectiveness and language naturalness.