---
title: 'Tangent 5 Policy Simulator'
status: deferred
supersedes: []
superseded_by: [docs/00-deploy-plans/05-policy-simulator.md, archive: openspec/plans/archive/tangent_5_policy_simulator.md]
last_touched: 2026-06-13
---

# Tangent 5: Real-time Educational Policy Impact Simulator

## 1. Executive Summary

This plan outlines a strategic approach to simulating and evaluating educational policy impacts across the UK and Irish standardization bodies. By utilizing temporal diffs of normalized `CrossNationCurriculumSpec` objects, our platform can generate systemic impact analyses in real-time, displaying them on an interactive dashboard.

## 2. Core Architecture: Versioned CrossNationCurriculumSpec

### 2.1. Structural Normalization
Before temporal diffs can be evaluated, diverse regional inputs (e.g., NCCA from Ireland, CCEA from Northern Ireland, DfE from England) must map into a universally structured `CrossNationCurriculumSpec`.

*   **Taxonomy Alignment:** Uniform tagging of subjects, learning outcomes, and assessment methodologies across the bodies.
*   **Temporal Versioning:** Each revision captured is assigned a strict monotonic timestamp and semantic versioning schema reflecting the policy document update.

### 2.2. Diffing Strategies over Time

To measure the systemic impact of policy changes:
*   **Outcome Drift Detection:** Compare semantic embeddings of learning outcomes over time using a vector database. Shift magnitudes will expose how much "learning emphasis" has moved.
*   **Gap Analysis:** Identify structural removals or additions within standardizations.
*   **Prerequisite Ripple Effect:** A modification in an early key stage's outcome may impact prerequisite knowledge chains in later stages. Graph traversal algorithms (via Knowledge Graph) will simulate these systemic ripples.

## 3. Interactive Dashboard: Systemic Simulation UI

### 3.1. Policy 'What-If' Playground
Users can toggle proposed policy modifications (e.g., "Add AI basics to KS3 Computing" or "Modify Irish Leaving Cert Assessment Ratios") and view the simulated ripple effect on downstream qualifications.

### 3.2. Metrics & Visualizations
*   **Cross-border Adoption Curve:** Visualizing the latency of adoption between standardisation bodies for new topics (e.g., when England introduces coding vs Ireland).
*   **Heatmaps of Change:** Highlighting high-volatility subjects where curriculum specifications are rapidly diverging or converging.

## 4. Action Plan

1.  **Data Ingestion & Versioning Engine:** Establish strict temporal tracking for existing DLT pipelines that pull curriculum data.
2.  **Diff Generation Logic:** Implement semantic text comparison and knowledge graph node difference logic to track changes across document versions.
3.  **CrossNationCurriculumSpec Extension:** Add `supersedes` and `valid_from` fields to the canonical schema to formally support time-based operations.
4.  **Dashboard Prototyping:** Build a Marimo or Streamlit prototype to explore diff data.
