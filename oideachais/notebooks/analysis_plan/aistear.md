# Aistear (Early Childhood) — Analysis Plan

Cianfhoghlaim Oideachais — bilingual agentic platform. This analysis plan is
for the `oideachais/notebooks/dashboards/aistear.py` marimo notebook, which
reads from the `oideachais.aistear` Cognee dataset and the
`aistear_knowledge_graph` LanceDB table.

## Questions

1. **Theme distribution**: How many Aistear learning goals exist per theme
   (Well-being, Identity & Belonging, Communicating, Exploring & Thinking)?
   Stacked bar chart, bilingual labels.
2. **Age-band distribution**: How do the learning goals split across the 4
   age bands (Infants, Toddlers, Pre-school, Early-Primary Bridge)? Faceted
   bar chart.
3. **Naíonra density by county**: How many Irish-medium pre-schools (naíonra)
   exist per county? Choropleth map of Ireland. Source: gaeloideachas.ie
   listings.
4. **Bridge rate**: What percentage of Aistear learning goals have been
   bridged to Primary Stage 1 (Infants) outcomes? KPI tile + count.
5. **Parent-tip library**: How many bilingual (EN/GA) parenting tips are in
   the Cognee dataset? Word cloud of the tip keywords (e.g., "free play",
   "scéal", "amhrán").
6. **Theme × age-band heatmap**: A heatmap showing the count of learning
   goals per (theme, age_band) cell.

## Data Sources

- **LanceDB**: `aistear_knowledge_graph` table
- **Cognee**: `oideachais.aistear` dataset (BAML-extracted)
- **DLT**: `aistear_curriculum` source (aistear_documents, naionra_listings)
- **BAML**: `baml_src/aistear.baml` (`AistearDocument`, `AistearPrinciple`,
  `AistearLearningGoal`, `Naionra`, `BridgeEdge`)

## Chart Specs (for the marimo build)

- Bar chart: theme distribution
- Faceted bar chart: age-band distribution
- Choropleth: naíonra density (per county)
- KPI tile: bridge rate
- Word cloud: parent-tip keywords
- Heatmap: theme × age-band

## Bilingual Toggle

Every label, axis, tooltip, and KPI must support EN/GA flipping via the
`<TranslationToggle>` chip in the header. The notebook itself reads
`locale` from a marimo `mo.ui.dropdown` and binds labels accordingly.
