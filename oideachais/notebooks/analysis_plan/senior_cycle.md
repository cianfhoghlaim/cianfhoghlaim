# Senior Cycle (Leaving Certificate) — Analysis Plan

Cianfhoghlaim Oideachais — bilingual agentic platform. This analysis plan is
for the `oideachais/notebooks/dashboards/senior_cycle.py` marimo notebook,
which reads from the `oideachais.senior_cycle` Cognee dataset and the
`senior_cycle_knowledge_graph` LanceDB table.

## Questions

1. **Subject family breakdown**: How many of the 50+ LC subjects fall into
   each of the 7 families (Sciences, Languages, Business, Humanities,
   Practical, Arts, LCA)? Stacked bar chart.
2. **Top 10 subjects by past-paper coverage**: Which subjects have the most
   past papers (1980-2025) extracted into the lakehouse? Bar chart.
3. **Per-question mean mark drift**: How has the mean mark for Paper 1 Q1
   drifted 2014→2024? Per-subject line chart (12 subjects).
4. **Highest zero-rate questions**: Which questions have the highest
   percentage of zero-mark candidates? Heatmap of subject × year.
5. **Rubric style distribution**: How many subjects use each of the 10
   `RubricStyle` values (PCLM, SRP, EQUATION_STEPS, etc.)? Stacked bar.
6. **Aural/oral percentage**: For Languages (English, Gaeilge, French,
   German, Spanish), how does the aural/oral weighting break down?
7. **CAO points table**: The full H1-H8 / O1-O8 + H6+25 bonus table as a
   reference panel.
8. **Bilingual extraction coverage**: What percentage of BAML extractions
   have both `*_en` and `*_ga` fields populated?

## Data Sources

- **LanceDB**: `senior_cycle_knowledge_graph` table (BAAI/bge-m3 embeddings)
- **Cognee**: `oideachais.senior_cycle` dataset
- **DLT**: `senior_cycle_with_lazy_extract` source
- **BAML**: `baml_src/curriculum_extraction.baml` (extended with
  `LeavingCertSubject`, `RubricStyle`, `SubjectRubric`, `LazyExtractExamPaper`)
- **JSON manifest**: `oideachais/data_platform/subjects/lc_subjects.json`

## Chart Specs

- Stacked bar: subject family breakdown
- Bar chart: top 10 subjects by past-paper coverage
- Line chart: per-question mean mark drift (12 subjects)
- Heatmap: highest zero-rate questions
- Stacked bar: rubric style distribution
- Bar chart: aural/oral weighting per language
- Table: CAO points reference panel
- KPI tile: bilingual extraction coverage

## Bilingual Toggle

Every label, axis, tooltip, and KPI must support EN/GA flipping.
