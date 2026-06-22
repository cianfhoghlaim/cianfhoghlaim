// BAML Schema for Curriculum Concept Extraction
// Extracts structured educational concepts from Irish Leaving Certificate syllabi

// Learning outcome from curriculum
class LearningOutcome {
  code string @description("Learning outcome code, e.g., LO1.1, LO2.3")
  description string @description("Full text of the learning outcome")
  cognitive_level string @description("Bloom's taxonomy level: Knowledge, Understanding, Application, Analysis, Synthesis, Evaluation")
  visual_potential float @description("Score 0.0-1.0 indicating how well this can be visualized")
}

// Visual asset requirement for a concept
class VisualRequirement {
  type string @description("Type of diagram: molecular, process_flow, experimental_setup, graph, schematic, anatomical, map, timeline")
  description string @description("What the visual should show")
  complexity string @description("Complexity level: simple, moderate, complex")
  style_preference string? @description("Preferred style: photograph, digital_illustration, scientific_diagram, line_art")
}

// A curriculum concept that can be visualized
class CurriculumConcept {
  topic string @description("Main topic from the curriculum strand")
  subtopic string? @description("Sub-topic if applicable")
  title string @description("Concise title for the concept")
  description string @description("Detailed description of the concept")
  learning_outcomes LearningOutcome[] @description("Associated learning outcomes")
  visual_requirements VisualRequirement[] @description("Types of visuals needed")
  keywords string[] @description("Keywords for search and categorization")
  difficulty_level string @description("Level: foundation, ordinary, higher")
}

// Result of extracting concepts from a syllabus page
class ExtractionResult {
  concepts CurriculumConcept[] @description("List of extracted concepts")
  page_type string @description("Type of page: content, experiment, assessment, overview, appendix")
  strand_name string? @description("Curriculum strand if identifiable")
}

// Main extraction function
function ExtractCurriculumConcepts(
  syllabus_page: image,
  subject_context: string
) -> ExtractionResult {
  client Gemini
  prompt #"
    You are an expert curriculum analyst specializing in Irish Leaving Certificate education.

    Analyze this syllabus page for {{ subject_context }}.

    Extract all educational concepts that would benefit from visual educational assets.

    For each concept, identify:
    1. The main topic and any sub-topic
    2. Specific learning outcomes with their codes (if visible)
    3. What types of visuals would help students understand the concept
    4. The difficulty level (Foundation, Ordinary, or Higher)
    5. Keywords for categorization

    Focus on concepts that CAN be effectively visualized, such as:

    For Chemistry:
    - Molecular structures and bonding
    - Laboratory equipment and setups
    - Chemical reactions and processes
    - Periodic table relationships
    - Flame tests and color changes
    - Titration curves and graphs

    For Biology:
    - Cell structures and organelles
    - Organism anatomy
    - Ecological relationships
    - Physiological processes
    - Microscopy observations
    - Genetic diagrams

    For Geography:
    - Landforms and geological features
    - Weather patterns and climate
    - Population distributions
    - Urban development
    - Map interpretations
    - Environmental processes

    {{ syllabus_page }}

    Return structured data with all identified concepts.
    If no visualizable concepts are found on this page, return an empty concepts array.

    {{ ctx.output_format }}
  "#
}

// Function to identify key visual concepts from a topic description
function IdentifyVisualConcepts(
  topic_description: string,
  subject: string
) -> VisualRequirement[] {
  client Gemini
  prompt #"
    You are an educational content specialist.

    Given this curriculum topic for {{ subject }}:
    {{ topic_description }}

    Identify what types of visual educational assets would best help students understand this topic.

    For each visual, specify:
    1. Type of diagram (molecular, process_flow, experimental_setup, graph, etc.)
    2. What it should show
    3. Complexity level
    4. Preferred artistic style

    Return a list of visual requirements that would create a comprehensive learning resource.

    {{ ctx.output_format }}
  "#
}

// Function to generate a concept summary for search
function GenerateConceptSummary(
  concept: CurriculumConcept
) -> string {
  client Gemini
  prompt #"
    Create a concise, searchable summary of this educational concept:

    Topic: {{ concept.topic }}
    Title: {{ concept.title }}
    Description: {{ concept.description }}

    The summary should:
    - Be 2-3 sentences
    - Include key scientific terms
    - Mention what students should learn
    - Be suitable for semantic search

    Return only the summary text.
  "#
}
