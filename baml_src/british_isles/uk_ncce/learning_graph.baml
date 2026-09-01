// BAML schema: UK NCCE Learning Graph Extractor
//
// Per the 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 change
// (Phase 4 of the cianfhoghlaim-nua v6 era plan). Lifted + OSS-ified
// from ~/dev/gemini_hackathon/baml_extracts/learning_graph.baml
// (the GCP-first sister repo).
//
// Powers the BIEP NCCE learning-graph showcase: 5 NCCE PDFs → row ×
// column learning graphs + 6 per-subject extractors + the pedagogy
// overlay + 48 cross-jurisdiction equivalencies.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src
//
// Reference:
//   openspec/changes/2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/
//   cocoindex_flows/uk_ncce/learning_graphs_app.py (the grid-aware PDF converter)
//   cocoindex_flows/_shared/_docling_grid_segmenter.py (row × column detector)

// ============================================================================
// Canonical enums
// ============================================================================

enum UKNCCEYearLevel {
  Y6
  Y7
  Y8
  Y9
  Y10
  Y11
}

enum UKNCCESubjectSlug {
  COMPUTER_SCIENCE
  MATHEMATICS
  ENGLISH
  GAEILGE
  GEOGRAPHY
}

enum LearningGraphSkillType {
  KNOWLEDGE      @description("Factual recall + comprehension")
  SKILL          @description("Procedural fluency")
  APPLICATION    @description("Real-world context application")
  REASONING      @description("Analysis + evaluation")
  CREATIVITY     @description("Synthesis + creation")
  META_COGNITION @description("Self-regulation + reflection")
}

enum LearningGraphPedagogyPrinciple {
  ACTIVE_LEARNING          @description("Hands-on participation over passive reception")
  SCAFFOLDING               @description("Successive approximations toward independence")
  DIFFERENTIATION           @description("Tailored support for diverse learners")
  FORMATIVE_ASSESSMENT      @description("Continuous low-stakes feedback loops")
  METACOGNITION             @description("Awareness + regulation of own learning")
  SPACED_PRACTICE           @description("Distributed retrieval over time")
  INTERLEAVING              @description("Mixed-topic practice vs blocked")
  DUAL_CODING               @description("Verbal + visual information pairing")
  RETRIEVAL_PRACTICE        @description("Active recall before re-teaching")
  ELABORATIVE_INTERROGATION @description("Why/how questioning for deeper encoding")
  CONCRETE_REPRESENTATIONAL @description("Concrete → abstract progression")
  WORKED_EXAMPLE_FADING     @description("Fully worked → partially worked → independent")
}

// ============================================================================
// Output classes (the canonical 11 OFFICIAL_DOC_COLUMNS schema)
// ============================================================================

class LearningGraphCell {
  row_index int @description("1-indexed grid row (skill dimension)")
  col_index int @description("1-indexed grid column (lesson dimension)")
  skill_type LearningGraphSkillType
  outcome_text string @description("What the student knows/can do at this intersection")
  pedagogy_principles LearningGraphPedagogyPrinciple[] @description("NCCE pedagogy principles applied at this cell")
  lo_code string? @description("Mapped to the cross-jurisdiction LO code where applicable")
}

class LearningGraphRow {
  row_index int
  skill_type LearningGraphSkillType
  skill_name string
  skill_description string
}

class LearningGraphColumn {
  col_index int
  lesson_number int @description("Lesson number within the unit")
  lesson_title string
  lesson_topic string
}

class LearningGraphPrerequisite {
  from_lo_code string
  to_lo_code string
  rationale string
}

class LearningGraph {
  subject UKNCCESubjectSlug
  year_level UKNCCEYearLevel
  title string @description("The NCCE learning-graph title")
  source_pdf string @description("Path to the canonical NCCE PDF")
  rows LearningGraphRow[]
  columns LearningGraphColumn[]
  cells LearningGraphCell[]
  prerequisites LearningGraphPrerequisite[]
  total_lessons int
  total_skills int
}

// ============================================================================
// 6 per-subject extractors (one per Phase 1 LC subject + chemistry)
// ============================================================================

function ExtractComputerScienceLearningGraph(
  pdf_text: string,
  year_level: UKNCCEYearLevel,
  source_pdf: string
) -> LearningGraph {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting UK NCCE Computing learning graphs from
    PDF text. The source is the canonical NCCE PDF for year level
    {{ year_level }}. Extract every cell of the row × column grid,
    every prerequisite arrow, and every pedagogy principle that applies.

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractMathematicsLearningGraph(
  pdf_text: string,
  year_level: UKNCCEYearLevel,
  source_pdf: string
) -> LearningGraph {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting UK NCCE Mathematics learning graphs
    from PDF text. The source is the canonical NCCE PDF for year level
    {{ year_level }}. Extract every cell of the row × column grid,
    every prerequisite arrow, and every pedagogy principle that applies.

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractEnglishLearningGraph(
  pdf_text: string,
  year_level: UKNCCEYearLevel,
  source_pdf: string
) -> LearningGraph {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting UK NCCE English learning graphs
    from PDF text. The source is the canonical NCCE PDF for year level
    {{ year_level }}. Extract every cell of the row × column grid,
    every prerequisite arrow, and every pedagogy principle that applies.

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractGaeilgeLearningGraph(
  pdf_text: string,
  year_level: UKNCCEYearLevel,
  source_pdf: string
) -> LearningGraph {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting UK NCCE Gaeilge learning graphs
    from PDF text. The source is the canonical NCCE PDF for year level
    {{ year_level }}. Extract every cell of the row × column grid,
    every prerequisite arrow, and every pedagogy principle that applies.

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractGeographyLearningGraph(
  pdf_text: string,
  year_level: UKNCCEYearLevel,
  source_pdf: string
) -> LearningGraph {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting UK NCCE Geography learning graphs
    from PDF text. The source is the canonical NCCE PDF for year level
    {{ year_level }}. Extract every cell of the row × column grid,
    every prerequisite arrow, and every pedagogy principle that applies.

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Pedagogy overlay (the 12 NCCE principles)
// ============================================================================

function ExtractNCCEPedagogyPrinciples(
  pdf_text: string,
  source_pdf: string
) -> PedagogyOverlay {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting the 12 NCCE pedagogy principles
    from the canonical NCCE pedagogy PDF. Return a PedagogyOverlay with
    each principle's description, justification, and 2-3 worked
    examples from the PDF.

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

class PedagogyPrincipleDetail {
  principle LearningGraphPedagogyPrinciple
  description string @description("2-3 sentence description")
  justification string @description("Why this principle matters for computing/maths/English")
  worked_examples string[] @description("2-3 worked examples from the source PDF")
}

class PedagogyOverlay {
  source_pdf string
  principles PedagogyPrincipleDetail[]
  total_principles int
}

// ============================================================================
// BAML test blocks (per the @assert requirement)
// ============================================================================

test ncce_cs_y8_python_sanity {
  functions [ExtractComputerScienceLearningGraph]
  args {
    pdf_text "NCCE Y8 Python: Variables → Functions → Classes. Skill rows: KNOWLEDGE, SKILL, APPLICATION. Cells describe what students learn in each lesson."
    year_level UKNCCEYearLevel.Y8
    source_pdf "/data/bi_ep/syllabi_raw/uk_ncce/curriculum/y8_python.pdf"
  }
}

test ncce_maths_y7_scratch_sanity {
  functions [ExtractMathematicsLearningGraph]
  args {
    pdf_text "NCCE Y7 Scratch: Patterns → Variables → Events. Skill rows: REASONING, SKILL. Cells describe learning outcomes."
    year_level UKNCCEYearLevel.Y7
    source_pdf "/data/bi_ep/syllabi_raw/uk_ncce/curriculum/y7_scratch.pdf"
  }
}

test ncce_pedagogy_sanity {
  functions [ExtractNCCEPedagogyPrinciples]
  args {
    pdf_text "NCCE pedagogy: 12 principles including Active Learning, Scaffolding, Formative Assessment."
    source_pdf "/data/bi_ep/syllabi_raw/uk_ncce/curriculum/pedagogy_principles.pdf"
  }
}