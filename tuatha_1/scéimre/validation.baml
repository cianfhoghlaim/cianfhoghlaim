// BAML Schema for Image Quality Validation
// Validates generated educational images against curriculum requirements

// Validation scores
class ValidationScores {
  scientific_accuracy float @description("Score 0.0-1.0: Is the science correct?")
  educational_clarity float @description("Score 0.0-1.0: Is it easy to understand?")
  visual_quality float @description("Score 0.0-1.0: Is it professional and appropriate?")
  concept_alignment float @description("Score 0.0-1.0: Does it match the concept?")
  safety_compliance float @description("Score 0.0-1.0: Are safety requirements met?")
  overall_score float @description("Weighted average of all scores")
}

// Issue identified in the image
class ValidationIssue {
  category string @description("Issue category: accuracy, clarity, quality, alignment, safety")
  severity string @description("Severity: minor, moderate, critical")
  description string @description("Description of the issue")
  location string? @description("Where in the image the issue appears")
}

// Suggested refinement
class RefinementSuggestion {
  aspect string @description("What aspect to refine")
  current_state string @description("Current state of that aspect")
  suggested_change string @description("What should be changed")
  fibo_parameter string? @description("Which FIBO parameter to adjust")
}

// Complete validation result
class ValidationResult {
  scores ValidationScores @description("Numerical scores")
  passes_threshold bool @description("Whether image passes quality threshold")
  issues ValidationIssue[] @description("List of identified issues")
  suggestions RefinementSuggestion[] @description("Suggested improvements")
  summary string @description("Brief summary of validation")
}

// Validate generated educational image
function ValidateEducationalImage(
  generated_image: image,
  concept_title: string,
  concept_description: string,
  visual_requirement: string,
  subject: string,
  fibo_prompt_used: string
) -> ValidationResult {
  client Gemini
  prompt #"
    You are a quality assessor for educational visual content.

    Evaluate this generated image for the Irish Leaving Certificate {{ subject }} curriculum.

    INTENDED CONCEPT:
    Title: {{ concept_title }}
    Description: {{ concept_description }}

    VISUAL REQUIREMENT:
    {{ visual_requirement }}

    FIBO PROMPT USED:
    {{ fibo_prompt_used }}

    GENERATED IMAGE:
    {{ generated_image }}

    Evaluate the image on these criteria:

    1. SCIENTIFIC ACCURACY (0.0-1.0)
       - Are scientific concepts correctly represented?
       - Are proportions, structures, and relationships accurate?
       - Would a science teacher approve this for classroom use?

    2. EDUCATIONAL CLARITY (0.0-1.0)
       - Is the main concept clearly visible and understandable?
       - Could a student learn from this image?
       - Is there visual clutter or confusion?

    3. VISUAL QUALITY (0.0-1.0)
       - Is the image professional and well-rendered?
       - Are colors, lighting, and composition appropriate?
       - Is it suitable for textbook/exam use?

    4. CONCEPT ALIGNMENT (0.0-1.0)
       - Does the image match what was requested?
       - Are all required elements present?
       - Does it address the learning outcome?

    5. SAFETY COMPLIANCE (0.0-1.0)
       - For lab scenes: Is proper safety equipment shown?
       - Are there any unsafe practices depicted?
       - Is the content appropriate for students?

    Calculate overall_score as weighted average:
    - Scientific accuracy: 30%
    - Educational clarity: 25%
    - Concept alignment: 25%
    - Visual quality: 10%
    - Safety compliance: 10%

    The image passes if overall_score >= 0.7

    Identify any issues with their severity (minor/moderate/critical).
    Provide specific suggestions for refinement if needed.

    {{ ctx.output_format }}
  "#
}

// Quick validation check (faster, less detailed)
function QuickValidate(
  generated_image: image,
  concept_title: string,
  subject: string
) -> bool {
  client Gemini
  prompt #"
    Quickly evaluate if this educational image for {{ subject }} is acceptable.

    Concept: {{ concept_title }}
    Image: {{ generated_image }}

    Answer TRUE if:
    - The image is scientifically reasonable
    - The concept is recognizable
    - The quality is acceptable for educational use
    - There are no major issues

    Answer FALSE if:
    - There are obvious scientific errors
    - The concept is not clear
    - The quality is poor
    - There are safety concerns

    Return only true or false.
  "#
}

// Suggest specific FIBO refinements based on issues
function SuggestFiboRefinements(
  issues: ValidationIssue[],
  current_fibo_prompt: string
) -> string[] {
  client Gemini
  prompt #"
    Based on these validation issues:
    {{ issues }}

    And the current FIBO prompt:
    {{ current_fibo_prompt }}

    Suggest specific textual refinement instructions that can be passed
    to FIBO's refine mode to fix the issues.

    Each suggestion should be a clear, actionable instruction like:
    - "Add safety goggles and lab coat to the person"
    - "Make the molecular bonds more visible"
    - "Increase lighting brightness for clarity"
    - "Add scale reference to the diagram"

    Return a list of refinement instructions.

    {{ ctx.output_format }}
  "#
}

// Compare generated image to source curriculum page
function CompareToSource(
  generated_image: image,
  source_page_image: image,
  concept_title: string
) -> float {
  client Gemini
  prompt #"
    Compare the generated educational image to the source curriculum page.

    CONCEPT: {{ concept_title }}

    SOURCE PAGE:
    {{ source_page_image }}

    GENERATED IMAGE:
    {{ generated_image }}

    Score how well the generated image represents concepts from the source page.

    Consider:
    - Does it capture the same scientific concepts?
    - Is it appropriate for the same learning level?
    - Would it complement the source material?

    Return a similarity score from 0.0 (completely unrelated) to 1.0 (perfect match).
  "#
}
