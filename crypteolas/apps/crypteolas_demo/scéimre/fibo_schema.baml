// BAML Schema for FIBO JSON Generation
// Translates curriculum concepts into FIBO-compatible structured prompts

// Object in the scene
class FiboObject {
  description string @description("Visual description of the object")
  location string? @description("Position: center, left, right, foreground, background")
  relationship string? @description("Relationship to other objects")
  relative_size string? @description("Size: small, medium, large")
  shape_and_color string? @description("Shape and color details")
  texture string? @description("Surface texture description")
  appearance_details string? @description("Additional visual details")
  number_of_objects int? @description("Count if multiple similar objects")
  orientation string? @description("Orientation or angle")
  action string? @description("Action if dynamic")
}

// Lighting configuration
class FiboLighting {
  conditions string @description("Lighting type: bright daylight, studio, natural, diffused, laboratory")
  direction string? @description("Light direction: front-lit, backlit, side-lit, evenly lit")
  shadows string? @description("Shadow style: soft, harsh, none, subtle")
  color_temperature string? @description("Temperature: warm, cool, neutral")
}

// Aesthetic configuration
class FiboAesthetics {
  composition string @description("Composition style: centered, rule of thirds, symmetrical")
  color_scheme string @description("Color palette: monochromatic, complementary, educational, scientific")
  mood_atmosphere string @description("Mood: educational, professional, engaging, clinical")
}

// Camera/photographic settings
class FiboPhotographicCharacteristics {
  depth_of_field string @description("DOF: shallow, deep, moderate")
  focus string @description("Focus style: sharp focus on subject, selective focus")
  camera_angle string @description("Angle: eye-level, low angle, high angle, overhead, macro")
  lens_focal_length string @description("Lens: wide, standard, telephoto, macro")
}

// Text overlay configuration
class FiboTextRender {
  text string @description("Text content to render")
  location string @description("Position of text")
  style string? @description("Text style: label, annotation, title")
}

// Complete FIBO prompt structure
class FiboPrompt {
  short_description string @description("Conceptual anchor of the image in 1-2 sentences")
  objects FiboObject[] @description("List of objects in the scene")
  background_setting string @description("Background environment description")
  lighting FiboLighting @description("Lighting configuration")
  aesthetics FiboAesthetics @description("Aesthetic settings")
  photographic_characteristics FiboPhotographicCharacteristics @description("Camera settings")
  style_medium string @description("Artistic medium: photograph, digital_illustration, scientific_diagram, line_art, 3d_render")
  text_render FiboTextRender[]? @description("Optional text overlays")
  context string @description("Educational context for the image")
  artistic_style string @description("Overall artistic style")
}

// Subject-specific color palettes
class SubjectColorPalette {
  primary string @description("Primary color hex code")
  secondary string @description("Secondary color hex code")
  accent string @description("Accent color hex code")
  background string @description("Background color hex code")
}

// Generate FIBO prompt from curriculum concept
function GenerateFiboPrompt(
  concept_title: string,
  concept_description: string,
  visual_requirement_type: string,
  visual_requirement_description: string,
  subject: string,
  style_preference: string,
  target_audience: string
) -> FiboPrompt {
  client Gemini
  prompt #"
    You are an expert educational content designer specializing in scientific visualizations
    for the Irish Leaving Certificate curriculum.

    Generate a detailed FIBO JSON prompt to create an educational image for:

    SUBJECT: {{ subject }}
    CONCEPT: {{ concept_title }}
    DESCRIPTION: {{ concept_description }}

    VISUAL REQUIREMENT:
    Type: {{ visual_requirement_type }}
    Details: {{ visual_requirement_description }}

    STYLE: {{ style_preference }}
    AUDIENCE: {{ target_audience }}

    Create a FIBO prompt that:
    1. Is scientifically accurate and educationally appropriate
    2. Uses clear, professional visual style suitable for exams
    3. Includes appropriate objects, lighting, and composition
    4. Avoids any unsafe or inappropriate content
    5. Uses colors and style appropriate for {{ subject }}

    Subject-specific guidelines:

    CHEMISTRY:
    - Use laboratory/clinical lighting
    - Include proper safety equipment (goggles, lab coat) for experiments
    - Show accurate molecular structures and bond angles
    - Use clean white/light gray backgrounds for clarity
    - Primary colors: Blue (#2196F3), Green (#4CAF50), Orange (#FF9800)

    BIOLOGY:
    - Use natural or soft lighting
    - Show accurate anatomical/cellular details
    - Include scale references where appropriate
    - Primary colors: Green (#4CAF50), Light green (#8BC34A), Orange (#FF5722)

    GEOGRAPHY:
    - Use appropriate lighting for landscapes or maps
    - Include accurate geological/geographical features
    - Show proper scales and orientations
    - Primary colors: Brown (#795548), Blue (#2196F3), Orange (#FF9800)

    {{ ctx.output_format }}
  "#
}

// Refine an existing FIBO prompt based on feedback
function RefineFiboPrompt(
  original_prompt: FiboPrompt,
  refinement_instruction: string
) -> FiboPrompt {
  client Gemini
  prompt #"
    You have an existing FIBO prompt for an educational image.

    CURRENT PROMPT:
    {{ original_prompt }}

    REFINEMENT REQUESTED:
    {{ refinement_instruction }}

    Modify the FIBO prompt to address the refinement while:
    1. Maintaining scientific accuracy
    2. Keeping the educational focus
    3. Preserving good composition and lighting
    4. Only changing what's necessary

    Return the complete updated FIBO prompt.

    {{ ctx.output_format }}
  "#
}

// Generate FIBO prompt for a specific diagram type
function GenerateDiagramPrompt(
  diagram_type: string,
  subject_matter: string,
  labels: string[],
  style: string
) -> FiboPrompt {
  client Gemini
  prompt #"
    Generate a FIBO prompt for a {{ diagram_type }} diagram showing:

    {{ subject_matter }}

    The diagram should include labels for:
    {{ labels }}

    Style: {{ style }}

    Create a clean, educational diagram suitable for:
    - Textbook illustrations
    - Exam papers
    - Study materials
    - Classroom presentations

    Use appropriate scientific conventions and symbols.

    {{ ctx.output_format }}
  "#
}

// Translate natural language to FIBO JSON
function NaturalLanguageToFibo(
  natural_prompt: string,
  subject: string
) -> FiboPrompt {
  client Gemini
  prompt #"
    Convert this natural language description into a structured FIBO prompt:

    "{{ natural_prompt }}"

    Subject area: {{ subject }}

    The FIBO prompt should:
    1. Capture all details from the natural language description
    2. Add appropriate educational styling
    3. Use subject-appropriate colors and lighting
    4. Be suitable for generating a professional educational asset

    {{ ctx.output_format }}
  "#
}
