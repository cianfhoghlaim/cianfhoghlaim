"""
EduVision Gradio Application

Interactive UI for generating curriculum-aligned educational assets
using Bria FIBO for the Irish Leaving Certificate.
"""

import json
from pathlib import Path
from typing import Optional

import gradio as gr

from .components.subject_selector import load_subject_metadata, get_curriculum_tree
from .components.fibo_controls import create_fibo_controls, build_fibo_json
from .components.image_preview import generate_preview
from .components.asset_gallery import get_generated_assets, get_asset_attribution


# Theme configuration
THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="green",
)

# CSS styling
CUSTOM_CSS = """
.concept-card { border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin: 5px; }
.source-link { color: #1976d2; text-decoration: none; }
.validation-pass { color: #4caf50; font-weight: bold; }
.validation-fail { color: #f44336; font-weight: bold; }
"""


def create_app() -> gr.Blocks:
    """
    Create the EduVision Gradio application.

    Returns:
        Configured Gradio Blocks application
    """
    with gr.Blocks(title="EduVision - Irish LC Visual Assets") as app:
        # Header
        gr.Markdown("""
        # EduVision: Irish Leaving Certificate Visual Assets

        Generate curriculum-aligned educational images for Chemistry, Biology, and Geography
        using Bria FIBO's JSON-native image generation.

        Each generated asset includes **source attribution** linking to the curriculum specification.
        """)

        # State
        current_subject = gr.State("chemistry")
        current_concept = gr.State(None)
        current_fibo_json = gr.State({})

        # Subject selector row
        with gr.Row():
            subject_dropdown = gr.Dropdown(
                choices=["Chemistry", "Biology", "Geography"],
                value="Chemistry",
                label="Select Subject",
                interactive=True,
            )
            subject_info = gr.Markdown("Select a subject to begin")

        # Main tabs
        with gr.Tabs() as tabs:
            # Tab 1: Browse Syllabus
            with gr.Tab("Browse Syllabus", id="browse"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Curriculum Structure")
                        syllabus_tree = gr.JSON(
                            label="Syllabus Topics",
                            value={},
                        )
                        refresh_btn = gr.Button("Refresh Syllabus", variant="secondary")

                    with gr.Column(scale=2):
                        gr.Markdown("### Learning Outcomes")
                        learning_outcomes = gr.Dataframe(
                            headers=["Code", "Description", "Visual Potential"],
                            label="Select outcomes to visualize",
                            interactive=True,
                        )
                        select_outcome_btn = gr.Button("Select for Visualization", variant="primary")

            # Tab 2: Visual Concepts
            with gr.Tab("Visual Concepts", id="concepts"):
                with gr.Row():
                    concept_search = gr.Textbox(
                        label="Search Concepts",
                        placeholder="e.g., 'titration curve', 'cell membrane'",
                    )
                    search_btn = gr.Button("Search", variant="primary")

                concept_results = gr.Gallery(
                    label="Matching Concepts from Curriculum",
                    columns=4,
                    object_fit="contain",
                )

                with gr.Row():
                    concept_details = gr.JSON(
                        label="Selected Concept Details",
                        value={},
                    )
                    use_concept_btn = gr.Button("Use This Concept", variant="primary")

            # Tab 3: Generate Asset
            with gr.Tab("Generate Asset", id="generate"):
                with gr.Row():
                    # Left column: FIBO controls
                    with gr.Column(scale=1):
                        gr.Markdown("### Concept Description")
                        concept_title = gr.Textbox(
                            label="Title",
                            placeholder="e.g., Bunsen burner flame test",
                        )
                        concept_description = gr.Textbox(
                            label="Description",
                            placeholder="What should the image show?",
                            lines=3,
                        )

                        gr.Markdown("### Camera Settings")
                        camera_angle = gr.Dropdown(
                            choices=["Eye Level", "Low Angle", "High Angle", "Overhead", "Macro"],
                            value="Eye Level",
                            label="Camera Angle",
                        )
                        depth_of_field = gr.Dropdown(
                            choices=["Deep (All in focus)", "Shallow (Bokeh)", "Moderate"],
                            value="Deep (All in focus)",
                            label="Depth of Field",
                        )

                        gr.Markdown("### Lighting")
                        lighting_condition = gr.Dropdown(
                            choices=["Laboratory Bright", "Studio", "Natural", "Soft Diffused"],
                            value="Laboratory Bright",
                            label="Lighting Condition",
                        )

                        gr.Markdown("### Style")
                        style_medium = gr.Dropdown(
                            choices=["Digital Illustration", "Scientific Diagram", "Photography", "Line Art"],
                            value="Digital Illustration",
                            label="Style Medium",
                        )
                        aspect_ratio = gr.Radio(
                            choices=["1:1", "16:9", "4:3"],
                            value="16:9",
                            label="Aspect Ratio",
                        )

                        # JSON preview
                        with gr.Accordion("FIBO JSON Preview", open=False):
                            fibo_json_preview = gr.Code(
                                label="Generated JSON",
                                language="json",
                                interactive=False,
                            )

                    # Right column: Preview and generation
                    with gr.Column(scale=1):
                        gr.Markdown("### Generated Preview")
                        preview_image = gr.Image(
                            label="Preview",
                            type="pil",
                            interactive=False,
                        )
                        generation_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                        )

                        with gr.Row():
                            generate_btn = gr.Button("Generate", variant="primary")
                            refine_btn = gr.Button("Refine", variant="secondary")
                            save_btn = gr.Button("Save to Gallery", variant="secondary")

                        seed_input = gr.Number(
                            label="Seed (-1 for random)",
                            value=-1,
                            precision=0,
                        )

                        # Validation results
                        with gr.Accordion("Validation Results", open=True):
                            validation_score = gr.Number(
                                label="Overall Score",
                                interactive=False,
                            )
                            validation_details = gr.JSON(
                                label="Detailed Scores",
                                value={},
                            )

            # Tab 4: Asset Gallery
            with gr.Tab("Asset Gallery", id="gallery"):
                with gr.Row():
                    gallery_subject_filter = gr.Dropdown(
                        choices=["All", "Chemistry", "Biology", "Geography"],
                        value="All",
                        label="Filter by Subject",
                    )
                    gallery_refresh_btn = gr.Button("Refresh Gallery")

                asset_gallery = gr.Gallery(
                    label="Generated Assets",
                    columns=4,
                    object_fit="contain",
                )

                with gr.Row():
                    with gr.Column(scale=2):
                        selected_asset = gr.Image(
                            label="Selected Asset",
                            interactive=False,
                        )

                    with gr.Column(scale=1):
                        gr.Markdown("### Curriculum Attribution")
                        attribution_subject = gr.Textbox(
                            label="Subject",
                            interactive=False,
                        )
                        attribution_strand = gr.Textbox(
                            label="Strand/Topic",
                            interactive=False,
                        )
                        attribution_outcome = gr.Textbox(
                            label="Learning Outcome",
                            interactive=False,
                            lines=2,
                        )
                        attribution_link = gr.Markdown(
                            "**Specification Link:** [View PDF](#)"
                        )
                        similarity_score = gr.Number(
                            label="Similarity to Source",
                            interactive=False,
                        )

                        gr.Markdown("### Export")
                        export_png_btn = gr.Button("Export PNG + Metadata")
                        export_json_btn = gr.Button("Export FIBO JSON")

        # Event handlers
        def on_subject_change(subject: str):
            """Handle subject selection change."""
            subject_lower = subject.lower()
            metadata = load_subject_metadata(subject_lower)
            tree = get_curriculum_tree(subject_lower)

            info_text = f"""
            **{subject}** - Irish Leaving Certificate

            {metadata.get('description', 'No description available')[:200]}...

            - Bilingual: {'Yes' if metadata.get('metadata', {}).get('bilingual') else 'No'}
            - Has new specification: {'Yes' if metadata.get('metadata', {}).get('has_new_specification') else 'No'}
            """

            return subject_lower, info_text, tree

        subject_dropdown.change(
            fn=on_subject_change,
            inputs=[subject_dropdown],
            outputs=[current_subject, subject_info, syllabus_tree],
        )

        def on_generate_click(
            title, description, camera, dof, lighting, style, aspect, seed, subject
        ):
            """Handle generate button click."""
            fibo_json = build_fibo_json(
                title=title,
                description=description,
                camera_angle=camera,
                depth_of_field=dof,
                lighting=lighting,
                style=style,
                aspect_ratio=aspect,
                subject=subject,
            )

            # Generate image
            image, status, validation = generate_preview(
                fibo_json=fibo_json,
                seed=int(seed) if seed >= 0 else None,
            )

            json_str = json.dumps(fibo_json, indent=2)

            return (
                image,
                status,
                json_str,
                validation.get("scores", {}).get("overall", 0),
                validation.get("scores", {}),
            )

        generate_btn.click(
            fn=on_generate_click,
            inputs=[
                concept_title,
                concept_description,
                camera_angle,
                depth_of_field,
                lighting_condition,
                style_medium,
                aspect_ratio,
                seed_input,
                current_subject,
            ],
            outputs=[
                preview_image,
                generation_status,
                fibo_json_preview,
                validation_score,
                validation_details,
            ],
        )

        # Gallery events
        def on_gallery_refresh(subject_filter):
            """Refresh asset gallery."""
            subject = None if subject_filter == "All" else subject_filter.lower()
            assets = get_generated_assets(subject=subject)
            return [(a["image_path"], a["concept_title"]) for a in assets]

        gallery_refresh_btn.click(
            fn=on_gallery_refresh,
            inputs=[gallery_subject_filter],
            outputs=[asset_gallery],
        )

    return app


def launch_app(
    server_name: str = "0.0.0.0",
    server_port: int = 7860,
    share: bool = False,
):
    """
    Launch the EduVision Gradio application.

    Args:
        server_name: Server hostname
        server_port: Server port
        share: Whether to create a public share link
    """
    app = create_app()
    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        theme=THEME,
        css=CUSTOM_CSS,
    )


if __name__ == "__main__":
    launch_app()
