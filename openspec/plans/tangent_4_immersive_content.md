# Strategic Plan: Tangent 4 - Immersive Multi-Modal Content Generation Engine

## 1. Executive Summary
The goal of Tangent 4 is to transition the platform from a passive aggregator of educational data into an **active synthesis engine**. By expanding our existing Dagster data ingestion pipelines, we will automatically generate highly targeted, interactive, and multi-modal learning materials. Crucially, this generation will be dynamically tailored to address the specific pedagogical and syllabus differences between the **GCSE (UK/NI)** and **Junior Cycle (Ireland)** curricula.

## 2. Core Objectives
*   **Curriculum-Aware Synthesis:** Leverage the curriculum data (ingested via dlt/Dagster) to identify conceptual overlaps and pedagogical gaps between GCSE and Junior Cycle.
*   **Multi-Modal Output:** Generate diverse content types, specifically focusing on visual flashcards and interactive Marimo notebooks.
*   **Pipeline Integration:** Seamlessly extend the existing Dagster ecosystem to handle content generation as downstream data assets.

## 3. Curriculum Alignment Engine (GCSE vs. Junior Cycle)
Before generating content, the system must understand *what* needs to be generated and *how* it should be framed.
*   **Mapping the Divide:** Use LLM-assisted analysis within Dagster to map learning outcomes from the Junior Cycle against GCSE specifications.
*   **Targeted Generation:**
    *   *Scenario A (Overlap):* Generate universal foundational content suitable for both cohorts.
    *   *Scenario B (Divergence):* Generate specialized "bridge" content. For example, if GCSE covers a specific physics formula that Junior Cycle omits, generate a targeted Marimo notebook for the GCSE cohort, or an extension module for the Junior Cycle cohort.
    *   *Tone and Terminology:* Ensure the generated text uses the correct localized terminology (e.g., "Marks Scheme" vs. "Marking Scheme", specific exam board vernacular).

## 4. Dagster Pipeline Expansion: The Generation Assets
We will introduce a new tier of Dagster Software-Defined Assets (SDAs) focused purely on generation.

*   **`content_generation_resource`:** A Dagster resource configured to communicate with multi-modal LLMs (e.g., Gemini 1.5 Pro/Flash) capable of handling both text and code/image generation.
*   **Asset Lineage:**
    1.  `raw_curriculum_data` (Existing dlt source)
    2.  `curriculum_mapping_graph` (New: Maps GCSE to Junior Cycle)
    3.  `learning_concept_nodes` (New: Granular topics extracted from the map)
    4.  `generated_flashcards` & `generated_marimo_notebooks` (New: The final multi-modal assets)

## 5. Multi-Modal Content Streams

### A. Visual Flashcard Synthesizer
*   **Concept:** Automated creation of highly visual, spaced-repetition-ready flashcards.
*   **Pipeline Steps:**
    1.  **Prompt Engineering:** For a given `learning_concept_node`, prompt the LLM to generate a concise Q&A pair.
    2.  **Visual Generation:** Prompt a vision model (or utilize a specialized library like Manim for math/science) to generate a corresponding explanatory diagram or mnemonic image.
    3.  **Assembly:** Combine text and image into standardized formats (e.g., JSON arrays, Anki `.apkg` packages, or a native web database format).
*   **Curriculum Twist:** A flashcard for a Junior Cycle student might focus on the qualitative understanding of a concept, while the GCSE version might include a required formula.

### B. Dynamic Marimo Notebook Generator
*   **Concept:** Generate executable, reactive Python notebooks using Marimo for interactive learning, particularly suited for Computer Science, Maths, and Data modules.
*   **Pipeline Steps:**
    1.  **Template Selection:** Select base Marimo templates based on the subject matter (e.g., data visualization, algorithm tracing, physics simulation).
    2.  **Code Synthesis:** Use an LLM (via Dagster) to inject specific, runnable Python code into the Marimo cells that demonstrate the concept.
    3.  **Interactivity Injection:** Automatically add Marimo UI elements (`mo.ui.slider`, `mo.ui.text`) to allow students to manipulate variables (e.g., changing the gravity constant in a physics equation) and see real-time updates.
*   **Curriculum Twist:** Generating a Marimo notebook that specifically bridges the gap in programming requirements between the Irish Leaving Cert/Junior Cycle coding short courses and the UK GCSE Computer Science syllabus.

## 6. Architecture & Data Flow
1.  **Ingestion:** dlt pulls updates from gov.uk (GCSE) and NCCA/curriculumonline.ie (Junior Cycle).
2.  **Processing (Dagster):** Data is cleaned, normalized, and mapped.
3.  **Trigger (Dagster Sensor/Schedule):** When new curriculum topics are identified or requested, the Generation pipeline is triggered.
4.  **Synthesis (LLM Resource):**
    *   *Path 1:* Text + Image generation -> Flashcard Asset Store.
    *   *Path 2:* Python/Marimo code generation -> `.py` notebook repository.
5.  **Delivery:** The front-end application serves the appropriate assets to the student based on their enrolled curriculum profile.

## 7. Action Plan
*   **Phase 1: Foundation.** Set up the LLM integration within Dagster (`ContentGeneratorResource`).
*   **Phase 2: The Mapper.** Build the Dagster asset that compares GCSE and Junior Cycle learning outcomes for a specific pilot subject (e.g., Science).
*   **Phase 3: Marimo Pilot.** Create a pipeline that generates a set of 5 interactive Marimo notebooks for the overlapping science concepts.
*   **Phase 4: Flashcard Pilot.** Implement the text-to-image flashcard generation pipeline for the divergent concepts.
*   **Phase 5: UI Integration.** Develop the frontend components to render the generated `.apkg` data and serve the Marimo notebooks via WebAssembly (Pyodide).
