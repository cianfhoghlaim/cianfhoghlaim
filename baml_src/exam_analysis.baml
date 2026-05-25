// BAML Schema for Exam and Marking Scheme Analysis
// Used with Vision Language Models to extract structured data from exam papers

enum DiagramType {
  MOLECULAR
  EXPERIMENTAL_SETUP
  PROCESS_FLOW
  GEOGRAPHIC_MAP
  HISTORICAL_TIMELINE
  CELL_DIAGRAM
  MATHEMATICAL_PROOF
  SRAITH_PICTIUR
  OTHER
}

class VisualRequirement {
  diagram_type DiagramType
  description string
  mandatory_labels string[]
  complexity string @description("Simple, Moderate, or Complex")
}

class ExamQuestion {
  question_id string @description("e.g., '2026-BIOL-H-Q1'")
  subject string
  year int
  level string @description("Higher, Ordinary, Foundation")
  raw_text string @description("The text of the question")
  marks_available int
  topics string[] @description("Curriculum topics covered")
  requires_diagram bool
  visual_requirements VisualRequirement[]
}

class MarkingSchemeRubric {
  question_id string
  subject string
  marking_logic string @description("e.g., 'SRPs (2 marks per point)', 'PCLM matrix', 'Step-by-step breakdown'")
  mandatory_keywords string[]
  common_pitfalls string[]
  full_marks_criteria string
}

class StudyGuideline {
  subject string
  topic string
  core_concept string
  exam_strategy string @description("How to tackle this topic in an exam context")
  recommended_visuals VisualRequirement[]
  related_questions string[] @description("List of related ExamQuestion IDs")
}

// Functions to extract these from text/images using VLMs

function ExtractExamQuestion(page_content: image | string) -> ExamQuestion {
  client "openai/gpt-4o" // Defaulting to a VLM-capable model
  prompt #"
    Analyze the following exam paper page and extract the exam question details.
    
    {{ page_content }}
    
    {{ ctx.output_format }}
  "#
}

function ExtractMarkingScheme(page_content: image | string) -> MarkingSchemeRubric {
  client "openai/gpt-4o"
  prompt #"
    Analyze the following marking scheme page and extract the grading rubric.
    Focus on mandatory keywords, SRPs (Significant Relevant Points), or PCLM where applicable.
    
    {{ page_content }}
    
    {{ ctx.output_format }}
  "#
}

function GenerateStudyGuideline(topic: string, syllabus_text: string, marking_schemes: string) -> StudyGuideline {
  client "openai/gpt-4o"
  prompt #"
    You are an expert Leaving Certificate examiner and teacher.
    Generate a study guideline for the topic: {{ topic }}
    
    Syllabus context:
    {{ syllabus_text }}
    
    Marking Scheme context:
    {{ marking_schemes }}
    
    {{ ctx.output_format }}
  "#
}
