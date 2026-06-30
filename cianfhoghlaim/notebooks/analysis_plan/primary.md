# Primary Curriculum — Analysis Plan

Cianfhoghlaim Oideachais — bilingual agentic platform. This analysis plan is
for the `sruth/oideachais/notebooks/dashboards/primary.py` marimo notebook.

## Questions

1. **Curriculum area coverage**: How many learning outcomes per
   `PrimaryCurriculumArea` (12 areas)?
2. **Stage distribution**: Outcomes per `PrimaryStage` (4 stages)?
3. **Strand distribution per area**: For each area, how many strands?
4. **Action verb distribution**: Top 15 action verbs across all areas.
5. **Aistear→Primary bridge rate**: What % of Aistear learning goals
   bridge to a Primary Stage 1 outcome?

## Data Sources

- LanceDB `primary_knowledge_graph`
- Cognee `oideachais.primary`

## Chart Specs

- Bar chart: outcomes per area
- Stacked bar: outcomes per stage
- Heatmap: strands per area
- Word cloud: action verbs
- KPI tile: bridge rate
