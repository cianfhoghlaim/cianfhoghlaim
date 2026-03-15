# Tangent 3: Automated Assessment & Grade Forecasting Oracle

## Executive Summary
This document outlines the strategic plan for developing an Automated Assessment and Grade Forecasting Oracle. This system will leverage historical educational data (standardized and managed via `dlt` into DuckDB) alongside advanced Vision OCR models to provide instant, syllabus-aligned feedback on student written work and predict future academic outcomes based on historical trends.

## 1. System Architecture & Components

### 1.1 Data Ingestion & Storage (`dlt` & DuckDB)
- **Historical Data:** Ingest past exam results, marking schemes, and historical grade boundaries using `dlt` pipelines.
- **Syllabus Data:** Load curriculum documents and learning outcomes to provide a benchmark for assessment.
- **Data Lakehouse:** Utilize DuckDB as the analytical engine to query historical performance data rapidly, enabling the forecasting models to calculate probabilities based on large datasets.

### 1.2 Vision OCR & Handwriting Recognition
- **Image Processing:** Use vision models (e.g., Gemini Pro Vision, GPT-4o, or specialized handwriting OCR like Google Cloud Vision/AWS Textract) to extract text from images of handwritten student work.
- **Layout Analysis:** Preserve the structure of the document (equations, diagrams, crossed-out text) to provide context to the assessment model.

### 1.3 Assessment Engine (LLM)
- **Syllabus Alignment:** The LLM evaluates the OCR-extracted text against the specific syllabus learning outcomes and marking rubrics retrieved from DuckDB.
- **Feedback Generation:** Generates constructive, instantaneous feedback, highlighting areas of strength and specific gaps in knowledge.

### 1.4 Grade Forecasting Oracle
- **Predictive Modeling:** Combines the student's current assessment performance with historical DuckDB data (e.g., "Students who scored X on this topic historically achieved Y in the final exam").
- **Confidence Intervals:** Provides grade predictions with confidence bounds based on the variance in historical grade boundaries.

## 2. Integration Strategy

1. **Student Submission Workflow:**
   - Student uploads an image/scan of their written assignment.
   - The UI sends the image to the Vision OCR service.
2. **Context Retrieval:**
   - The system queries DuckDB for the relevant syllabus rubric and historical marking schemes for the specific topic.
3. **Assessment & Inference:**
   - The OCR output and DuckDB context are fed into the LLM Assessment Engine.
   - The LLM grades the work and generates feedback.
4. **Forecasting Update:**
   - The grade is logged, and the Forecasting Oracle queries DuckDB to update the student's predicted final grade trajectory based on historical cohorts.

## 3. Implementation Steps

- [ ] **Phase 1: Data Foundation**
  - Implement `dlt` pipelines for historical exam data and grade boundaries.
  - Structure and optimize DuckDB schemas for fast analytical queries.
- [ ] **Phase 2: Vision OCR Pipeline**
  - Integrate a robust Vision OCR model capable of handling messy handwriting and mathematical notation.
  - Build a preprocessing pipeline to normalize images before extraction.
- [ ] **Phase 3: Assessment Prompt Engineering**
  - Develop LLM prompts that strictly adhere to ingested marking schemes and rubrics to minimize hallucination and subjectivity.
- [ ] **Phase 4: Forecasting Algorithm**
  - Develop the statistical or machine learning model that correlates current performance with historical DuckDB data to predict final outcomes.
- [ ] **Phase 5: User Interface & MVP**
  - Build the student/teacher dashboard to upload work and view the instant feedback and forecasted grades.

## 4. Risks & Mitigations

- **Handwriting Recognition Errors:** OCR can fail on poor handwriting. *Mitigation:* Implement a "human-in-the-loop" flag for low-confidence OCR extractions.
- **Assessment Bias:** LLMs may grade inconsistently. *Mitigation:* Anchor all LLM assessments strictly to the DuckDB-stored marking rubrics and provide citations for deducted marks.
- **Data Privacy:** Handling student assessments requires strict compliance. *Mitigation:* Ensure all uploaded images are processed ephemerally or securely anonymized before storage.

## 5. Conclusion
The combination of `dlt`/DuckDB's structured historical data and the unstructured processing power of Vision OCR creates a powerful oracle. This tool will drastically reduce teacher marking workload while providing students with the real-time, actionable feedback necessary for iterative learning.