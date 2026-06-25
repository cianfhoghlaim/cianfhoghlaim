"""
FIBO controls component for EduVision.

Provides UI controls for FIBO JSON-native image generation parameters.
"""

from typing import Optional
import gradio as gr


# FIBO parameter options
CAMERA_ANGLES = [
    "Eye Level",
    "Low Angle",
    "High Angle",
    "Overhead",
    "Macro",
    "Close-up",
    "Wide Shot",
]

DEPTH_OF_FIELD_OPTIONS = [
    "Deep (All in focus)",
    "Shallow (Bokeh)",
    "Moderate",
    "Selective Focus",
]

LIGHTING_CONDITIONS = [
    "Laboratory Bright",
    "Studio",
    "Natural",
    "Soft Diffused",
    "Dramatic",
    "Neutral",
]

STYLE_MEDIUMS = [
    "Digital Illustration",
    "Scientific Diagram",
    "Photography",
    "Line Art",
    "Infographic",
    "Educational Poster",
    "Textbook Illustration",
]

ASPECT_RATIOS = ["1:1", "16:9", "4:3", "3:2", "9:16"]

# Subject-specific style presets
SUBJECT_PRESETS = {
    "chemistry": {
        "style_medium": "Scientific Diagram",
        "lighting": "Laboratory Bright",
        "camera_angle": "Eye Level",
        "depth_of_field": "Deep (All in focus)",
        "color_palette": ["#1565C0", "#42A5F5", "#BBDEFB", "#FFFFFF", "#37474F"],
    },
    "biology": {
        "style_medium": "Digital Illustration",
        "lighting": "Soft Diffused",
        "camera_angle": "Macro",
        "depth_of_field": "Selective Focus",
        "color_palette": ["#2E7D32", "#66BB6A", "#C8E6C9", "#FFEB3B", "#FF5722"],
    },
    "geography": {
        "style_medium": "Infographic",
        "lighting": "Natural",
        "camera_angle": "Wide Shot",
        "depth_of_field": "Deep (All in focus)",
        "color_palette": ["#795548", "#4CAF50", "#2196F3", "#FFC107", "#9E9E9E"],
    },
}


def create_fibo_controls() -> dict:
    """
    Create Gradio controls for FIBO parameters.

    Returns:
        Dictionary of Gradio components
    """
    controls = {}

    with gr.Accordion("Camera Settings", open=True):
        controls["camera_angle"] = gr.Dropdown(
            choices=CAMERA_ANGLES,
            value="Eye Level",
            label="Camera Angle",
            info="Viewing perspective for the image",
        )
        controls["lens_focal_length"] = gr.Slider(
            minimum=14,
            maximum=200,
            value=50,
            step=1,
            label="Lens Focal Length (mm)",
            info="Affects perspective distortion",
        )
        controls["depth_of_field"] = gr.Dropdown(
            choices=DEPTH_OF_FIELD_OPTIONS,
            value="Deep (All in focus)",
            label="Depth of Field",
            info="Background blur effect",
        )

    with gr.Accordion("Lighting", open=True):
        controls["lighting_condition"] = gr.Dropdown(
            choices=LIGHTING_CONDITIONS,
            value="Laboratory Bright",
            label="Lighting Condition",
        )
        controls["lighting_direction"] = gr.Radio(
            choices=["Front", "Side", "Back", "Top", "Multi-directional"],
            value="Front",
            label="Light Direction",
        )
        controls["color_temperature"] = gr.Slider(
            minimum=2700,
            maximum=6500,
            value=5500,
            step=100,
            label="Color Temperature (K)",
            info="Warm (2700K) to Cool (6500K)",
        )

    with gr.Accordion("Style & Composition", open=True):
        controls["style_medium"] = gr.Dropdown(
            choices=STYLE_MEDIUMS,
            value="Digital Illustration",
            label="Style Medium",
        )
        controls["aspect_ratio"] = gr.Radio(
            choices=ASPECT_RATIOS,
            value="16:9",
            label="Aspect Ratio",
        )
        controls["composition_rule"] = gr.Dropdown(
            choices=["Rule of Thirds", "Center", "Golden Ratio", "Symmetrical"],
            value="Rule of Thirds",
            label="Composition Rule",
        )

    return controls


def build_fibo_json(
    title: str,
    description: str,
    camera_angle: str = "Eye Level",
    depth_of_field: str = "Deep (All in focus)",
    lighting: str = "Laboratory Bright",
    style: str = "Digital Illustration",
    aspect_ratio: str = "16:9",
    subject: str = "chemistry",
    lens_focal_length: int = 50,
    lighting_direction: str = "Front",
    color_temperature: int = 5500,
    composition_rule: str = "Rule of Thirds",
) -> dict:
    """
    Build FIBO-compatible JSON from UI parameters.

    Args:
        title: Concept title
        description: What the image should show
        camera_angle: Camera viewing angle
        depth_of_field: DOF setting
        lighting: Lighting condition
        style: Style medium
        aspect_ratio: Image aspect ratio
        subject: Subject for preset application
        lens_focal_length: Camera lens focal length
        lighting_direction: Direction of main light
        color_temperature: Light color temperature in Kelvin
        composition_rule: Composition guideline

    Returns:
        FIBO-compatible JSON dictionary
    """
    # Get subject preset for defaults
    preset = SUBJECT_PRESETS.get(subject.lower(), SUBJECT_PRESETS["chemistry"])

    # Map UI values to FIBO schema
    dof_map = {
        "Deep (All in focus)": "deep",
        "Shallow (Bokeh)": "shallow",
        "Moderate": "moderate",
        "Selective Focus": "selective",
    }

    lighting_map = {
        "Laboratory Bright": "bright_artificial",
        "Studio": "studio",
        "Natural": "natural_daylight",
        "Soft Diffused": "soft_diffused",
        "Dramatic": "dramatic",
        "Neutral": "neutral",
    }

    style_map = {
        "Digital Illustration": "digital_illustration",
        "Scientific Diagram": "scientific_diagram",
        "Photography": "photorealistic",
        "Line Art": "line_art",
        "Infographic": "infographic",
        "Educational Poster": "educational_poster",
        "Textbook Illustration": "textbook_illustration",
    }

    # Build FIBO JSON
    fibo_json = {
        "short_description": f"{title}: {description}",
        "objects": [
            {
                "class_label": title.lower().replace(" ", "_"),
                "instance_description": description,
                "relative_position": "center",
                "relative_scale": 0.7,
            }
        ],
        "background_setting": _get_background_for_subject(subject),
        "lighting": {
            "condition": lighting_map.get(lighting, "neutral"),
            "direction": lighting_direction.lower(),
            "color_temperature": color_temperature,
            "intensity": 0.8,
        },
        "aesthetics": {
            "color_palette": preset.get("color_palette", []),
            "style_keywords": [style.lower(), "educational", "clear", "accurate"],
        },
        "style_medium": style_map.get(style, "digital_illustration"),
        "photographic_characteristics": {
            "camera_angle": camera_angle.lower().replace(" ", "_"),
            "lens_focal_length": lens_focal_length,
            "depth_of_field": dof_map.get(depth_of_field, "deep"),
            "aspect_ratio": aspect_ratio,
        },
        "composition": {
            "rule": composition_rule.lower().replace(" ", "_"),
            "main_subject_position": "center",
        },
        "_metadata": {
            "subject": subject,
            "concept_title": title,
            "educational_context": True,
        },
    }

    return fibo_json


def _get_background_for_subject(subject: str) -> str:
    """Get appropriate background setting for subject."""
    backgrounds = {
        "chemistry": "Clean laboratory bench with neutral gray background",
        "biology": "Neutral backdrop with subtle organic texture",
        "geography": "Clean white or light gray background for diagrams",
    }
    return backgrounds.get(subject.lower(), "Neutral educational background")


def apply_subject_preset(subject: str) -> tuple:
    """
    Apply subject-specific presets to controls.

    Args:
        subject: Subject slug

    Returns:
        Tuple of preset values for Gradio update
    """
    preset = SUBJECT_PRESETS.get(subject.lower(), SUBJECT_PRESETS["chemistry"])

    return (
        preset.get("style_medium", "Digital Illustration"),
        preset.get("lighting", "Laboratory Bright"),
        preset.get("camera_angle", "Eye Level"),
        preset.get("depth_of_field", "Deep (All in focus)"),
    )


def get_fibo_schema_help() -> str:
    """Get help text explaining FIBO JSON schema."""
    return """
## FIBO JSON Schema

FIBO uses a structured JSON format for precise image control:

### Core Fields
- **short_description**: Brief description of the entire scene
- **objects**: List of objects with class labels and descriptions
- **background_setting**: Environmental context
- **lighting**: Lighting conditions and properties
- **style_medium**: Artistic style (diagram, illustration, photo, etc.)

### Photographic Characteristics
- **camera_angle**: Viewing perspective
- **lens_focal_length**: Affects perspective distortion
- **depth_of_field**: Background blur control
- **aspect_ratio**: Image dimensions

### Tips for Educational Images
1. Use clear, accurate labels for scientific concepts
2. Choose appropriate style for the subject matter
3. Ensure high contrast for visibility
4. Include relevant context without clutter
"""
