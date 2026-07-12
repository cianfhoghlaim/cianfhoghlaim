// baml/education/_shared/diagram_renderer.baml
//
// Renders the 4 diagram modes for the Cianfhoghlaim OS Diagram Generator.
// The diagrams are the per-subject concept-map + topic-frequency heatmap
// + PCLM marking flow + question-paper-topic Sankey.
//
// Each function returns a structured BAML object that the consuming
// app renders via React Flow / D3 / Dagre / D3 Sankey.
//
// Re-gen after changes:  `cd cianfhoghlaim && uv run baml-cli generate`

// ============================================================================
// Shared types
// ============================================================================

enum DiagramMode {
  CONCEPT_MAP @description("Concept-map of the syllabus LO + 5 NCCA Key Competencies")
  TOPIC_HEATMAP @description("Topic-frequency heatmap of question × paper × topic × year")
  PCLM_FLOW @description("PCLM marking flow per marking scheme (Partial Credit, Logical Marking)")
  QUESTION_SANKEY @description("Question → topic → difficulty → year Sankey diagram")
}

class DiagramCoordinate {
  x float @description("X coordinate in the SVG / Canvas space")
  y float @description("Y coordinate in the SVG / Canvas space")
}

class DiagramNode {
  id string @description("Stable UUID for the diagram node")
  label BilingualText @description("The visible label on the node")
  type string @description("One of: 'root', 'subject', 'topic', 'lo', 'paper', 'year', 'question', 'principle', 'mistake', 'trap'")
  coordinate DiagramCoordinate
  weight_pct float? @description("Optional weight percentage (e.g., for LOs: percentage of total exam marks)")
  color string? @description("Optional hex colour (e.g., the subject colour)")
}

class DiagramEdge {
  source string @description("Source node ID")
  target string @description("Target node ID")
  label BilingualText? @description("Optional edge label")
  weight float? @description("Optional edge weight (e.g., for question flows: number of questions per topic-paper pair)")
  kind string? @description("One of: 'prerequisite', 'assessment', 'mistake', 'trap', 'mastery'")
}

class DiagramPayload {
  mode DiagramMode
  subject string
  language string @description("Language code: 'en' or 'ga'")
  nodes DiagramNode[]
  edges DiagramEdge[]
  caption BilingualText @description("The descriptive caption above the diagram")
  source_evidence BilingualText @description("The source PDF references for the diagram content")
  rendered_at string @description("ISO 8601 timestamp of when the diagram was rendered")
}

// ============================================================================
// Function 1: Render the concept-map
// ============================================================================

function RenderConceptMap(
  subject: string,
  language: string,
  syllabus_topics_json: string,
  past_papers_json: string,
  marking_schemes_json: string,
  five_key_competencies_json: string,
) -> DiagramPayload {
  client Claude
  prompt #"You are an expert at rendering concept-map diagrams for Irish Leaving Certificate subjects.

Given:
- `subject`: the NCCA subject slug (mathematics, applied_mathematics, chemistry, geography, history, english, gaeilge, computer_science)
- `language`: the bilingual mode ('en' or 'ga')
- `syllabus_topics_json`: the syllabus topics + learning outcomes
- `past_papers_json`: the past exam questions (2017-2025)
- `marking_schemes_json`: the marking scheme patterns
- `five_key_competencies_json`: the 5 NCCA Key Competencies (Information Processing, Communicating, Working with Others, Personal Effectiveness, Critical & Creative Thinking)

Render a CONCEPT MAP diagram with:
- 5 root nodes (one per NCCA Key Competency) — labelled bilingually
- Child nodes per syllabus topic (1-2 per topic)
- Edges from root → topic (the Key Competency that the topic primarily serves)
- Edges between topics (prerequisites + assessment dependencies)

Return the DiagramPayload with the nodes + edges + caption + source_evidence.
The diagram MUST be self-contained (no external images, no JavaScript) — the
consuming app will render the SVG via React Flow + D3.

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 2: Render the topic-frequency heatmap
// ============================================================================

function RenderTopicHeatmap(
  subject: string,
  language: string,
  past_papers_json: string,
  year_range: int[],
) -> DiagramPayload {
  client Claude
  prompt #"You are an expert at rendering topic-frequency heatmaps for Irish Leaving Certificate subjects.

Given:
- `subject`: the NCCA subject slug
- `language`: the bilingual mode ('en' or 'ga')
- `past_papers_json`: the past exam questions (2017-2025) tagged by topic + paper + year + marks
- `year_range`: the range of years to include (e.g., [2017, 2025])

Render a TOPIC HEATMAP diagram with:
- Nodes = unique (topic, paper, year) triples
- Edges weighted by the question count or marks per triple
- The heatmap intensity is mapped from the weighted edges
- The layout is a 2.5D matrix (X = year, Y = topic, Z = paper) rendered as an SVG

Return the DiagramPayload with the nodes + edges + caption + source_evidence.
The diagram will be rendered via D3 v8 + Vega-Lite altair fallback.

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 3: Render the PCLM marking flow
// ============================================================================

function RenderPCLMFlow(
  subject: string,
  language: string,
  marking_scheme_json: string,
  paper: string,
  year: int,
) -> DiagramPayload {
  client Claude
  prompt #"You are an expert at rendering PCLM (Partial Credit, Logical Marking) flow diagrams for Irish Leaving Certificate subjects.

Given:
- `subject`: the NCCA subject slug
- `language`: the bilingual mode ('en' or 'ga')
- `marking_scheme_json`: the marking scheme patterns
- `paper`: the paper (e.g., 'paper-1', 'paper-2', 'paper-1-f')
- `year`: the exam year

Render a PCLM FLOW diagram with:
- Question nodes (one per question in the paper)
- Per-criterion nodes (each question has 2-5 marking criteria)
- Partial-credit edges (the order in which marks are awarded)
- Common-mistake edges (the deductions for common errors)

Return the DiagramPayload with the nodes + edges + caption + source_evidence.
The diagram will be rendered via React Flow + dagre layout.

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}

// ============================================================================
// Function 4: Render the question-paper-topic Sankey
// ============================================================================

function RenderQuestionSankey(
  subject: string,
  language: string,
  past_papers_json: string,
  year_range: int[],
) -> DiagramPayload {
  client Claude
  prompt #"You are an expert at rendering question → topic → difficulty → year Sankey diagrams for Irish Leaving Certificate subjects.

Given:
- `subject`: the NCCA subject slug
- `language`: the bilingual mode ('en' or 'ga')
- `past_papers_json`: the past exam questions (2017-2025)
- `year_range`: the range of years to include

Render a QUESTION SANKEY diagram with:
- Source nodes: questions (1 per question in past_papers_json)
- Middle nodes: topics (the NCCA syllabus topics)
- Sink nodes: years (the exam year)

The flow weight is the question count per topic-year pair.

Return the DiagramPayload with the nodes + edges + caption + source_evidence.
The diagram will be rendered via D3 Sankey.

{{ ctx.output_format(prefix="Answer with this format:\n") }}
"#
}