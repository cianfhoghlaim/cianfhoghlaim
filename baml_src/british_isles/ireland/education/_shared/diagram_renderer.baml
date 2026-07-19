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
) -> DiagramPayload {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Function 2: Render the topic-frequency heatmap
// ============================================================================

function RenderTopicHeatmap(
  subject: string,
  language: string,
  past_papers_json: string,
  year_range: int[],
) -> DiagramPayload {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
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
) -> DiagramPayload {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Function 4: Render the question-paper-topic Sankey
// ============================================================================

function RenderQuestionSankey(
  subject: string,
  language: string,
  past_papers_json: string,
  year_range: int[],
) -> DiagramPayload {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}