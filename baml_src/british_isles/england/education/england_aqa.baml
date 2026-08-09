// Real BAML extraction prompt for the AQA qualification spec (per C4).
//
// Replaces the "Auto-generated extraction prompt" stub with a real
// AQA-specific prompt. The other 3 functions (ExtractOCRQualSpec,
// ExtractEdexcelQualSpec, ExtractUKQualSpec) already have real prompts
// per the BIEP v3 spec.

function ExtractAQAQualSpec(text: string, subject: string) -> AQAQualSpec {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert AQA qualification specification extractor for the subject `{{ subject }}`.

    Extract from the AQA spec text:
    - `spec_id`: AQA spec code (e.g. "7402" for A-Level Chemistry, "8462" for GCSE Combined Science)
    - `qualification_level`: "GCSE" | "A-Level" | "AS-Level"
    - `subject`: the subject name (as listed by AQA)
    - `version`: spec version string (e.g. "v1.4")
    - `first_teaching`: year (e.g. "2016")
    - `first_award`: year (e.g. "2018")
    - `units`: array of {code, title, learning_objectives: [{code, text, blooms_level}], assessment_weight_pct: float}
    - `assessment_objectives`: array of {code, description, weight_pct}
    - `tiered`: bool (whether the spec has Higher + Foundation tiers)
    - `tiers`: array of {name, allowed_units}

    Note: AQA spec codes start with "7401" (Physics), "7402" (Chemistry), "7404" (Maths),
    "7405" (English Lang), "7407" (English Lit), "7408" (Biology), "7437" (History),
    "7037" (Geography), "7517" (Computer Science), etc.

    Subject-specific guidance:
    {% if subject == "chemistry" %}
    - A-Level Chemistry (7402) has 3 papers: Inorganic + Physical (Paper 1), Organic + Analysis (Paper 2), Synoptic (Paper 3)
    - GCSE Chemistry (8462) has Foundation + Higher tiers
    {% elif subject == "mathematics" %}
    - A-Level Maths (7357) has Pure + Statistics + Mechanics papers
    - GCSE Maths (8300) has Foundation + Higher tiers (grades 1-9)
    {% elif subject == "english" %}
    - A-Level English Lang (7702) has 2 papers + coursework
    - GCSE English Lang (8700) has 2 papers (Explorations + Writers' Viewpoints)
    {% endif %}

    {{ ctx.output_format }}

    AQA SPEC TEXT:
    {{ text }}
  "#
}

class AQAQualSpec {
  spec_id string
  qualification_level string
  subject string
  version string
  first_teaching int
  first_award int
  units AQAUnit[]
  assessment_objectives AQAAssessmentObjective[]
  tiered bool
  tiers AQATier[]
}

class AQAUnit {
  code string
  title string
  learning_objectives AQALearningObjective[]
  assessment_weight_pct float
}

class AQALearningObjective {
  code string
  text string
  blooms_level string
}

class AQAAssessmentObjective {
  code string
  description string
  weight_pct float
}

class AQATier {
  name string
  allowed_units string[]
}
