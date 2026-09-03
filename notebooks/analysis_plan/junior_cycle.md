# Junior Cycle — Analysis Plan

Cianfhoghlaim Oideachais — bilingual agentic platform. This analysis plan is
for the `sruth/oideachais/notebooks/dashboards/junior_cycle.py` marimo notebook.

## Questions

1. **Subject coverage**: Outcomes per `JuniorCycleSubject` (18 core + 16 short)
2. **CBA rubric distribution**: AchievementLevel distribution per CBA
3. **L2LP coverage**: How many Level 2 Learning Programme outcomes?
4. **Bridge to SC**: How many JC outcomes link to Senior Cycle outcomes?

## Data Sources

- LanceDB `junior_cycle_knowledge_graph`
- Cognee `oideachais.junior_cycle`

## Chart Specs

- Bar chart: outcomes per JC subject
- Stacked bar: AchievementLevel distribution
- KPI tile: L2LP coverage
- Sankey: JC → SC bridge
