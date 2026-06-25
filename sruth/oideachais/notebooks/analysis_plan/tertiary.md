# Tertiary (CAO + QQI + Apprenticeship) — Analysis Plan

Cianfhoghlaim Oideachais — bilingual agentic platform. This analysis plan is
for the `oideachais/notebooks/dashboards/tertiary.py` marimo notebook,
which reads from the `oideachais.tertiary` Cognee dataset and the
`tertiary_knowledge_graph` LanceDB table.

## Questions

1. **CAO points trend per course**: For the 10 most popular courses
   (Medicine, Dentistry, Nursing, Law, Engineering, Computer Science,
   Business, Arts, Science, Education), how have the cutoff points drifted
   2018→2024? Line chart.
2. **HEI distribution**: How many CAO courses are offered by each of the
   13 HEIs in `hei.json`? Bar chart.
3. **NFQ level distribution**: How many courses are at each NFQ level
   (6, 7, 8, 9, 10)? Stacked bar chart.
4. **Bilingual coverage**: How many CAO courses have both `title_en` and
   `title_ga`? KPI tile.
5. **QQI ladder destinations**: For the 8 QQI FET awards, which CAO courses
   do they ladder into? Sankey diagram.
6. **Apprenticeship uptake by HEI**: How many apprenticeship programmes
   run through each of the IoTs? Bar chart.
7. **Application timeline calendar**: A Gantt-style chart of the CAO
   timeline (open, close, late close, offer rounds 1+2, registration open).
8. **Matriculation audit pass rate**: For a sample of 10 applicant grade
   profiles, how many pass the NUI/UCC/UL standard matriculation rules?
9. **Subject → CAO course edges**: What are the most-`REQUIRED_FOR` LC
   subjects (count of CAO courses that list them as a matriculation req)?
10. **Specialism distribution**: How many courses are tagged with each of
    the 8 Specialism values (Sciences, Languages, Business, Humanities,
    Practical, Arts, Applied, Interdisciplinary)?

## Data Sources

- **LanceDB**: `tertiary_knowledge_graph` table
- **Cognee**: `oideachais.tertiary` dataset
- **DLT**: `tertiary_courses` source (cao_courses, matriculation_rules,
  qqi_fet_awards, apprenticeships, application_timelines)
- **BAML**: `baml_src/tertiary.baml` (CAOCourse, MatriculationRequirement,
  QqiFetAward, Apprenticeship, Programme, ApplicationTimeline,
  CAOGradeProfile, CoursePointsPrediction, MatriculationAudit)
- **JSON manifest**: `oideachais/data_platform/subjects/hei.json` (13 HEIs
  + 8 QQI awards)

## Chart Specs

- Line chart: CAO points trend (10 courses × 7 years)
- Bar chart: HEI distribution
- Stacked bar: NFQ level distribution
- KPI tile: bilingual coverage
- Sankey: QQI ladder destinations
- Bar chart: Apprenticeship by HEI
- Gantt: application timeline
- KPI tile: matriculation pass rate
- Bar chart: top 10 most-required LC subjects
- Stacked bar: specialism distribution

## Bilingual Toggle

Every label, axis, tooltip, and KPI must support EN/GA flipping.
