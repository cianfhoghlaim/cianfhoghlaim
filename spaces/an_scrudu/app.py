"""
spaces/an_scrudu/app.py
Space 1: An Scrudu - Past Paper Heatmap.

BAML extracts marking schemes from Irish Leaving Cert past papers,
returns a topic heatmap (Talamh / Earth), and emits a PCLM-XML +
PDF for download.

Gradio components:
  - Top: file upload + sample-picker
  - Middle: extracted metadata card
  - Left: topic heatmap (HTML/CSS, emerald gradient)
  - Right: PCLM preview + download button (XML + PDF)
  - Footer: Anam Bonneagar
"""

from __future__ import annotations

import logging

import gradio as gr

from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
    translate,
    set_lang,
)
from spaces.an_scrudu.extraction import (
    CircularExtraction,
    get_sample,
)
from spaces.an_scrudu.heatmap import (
    render_heatmap,
    render_pclm_html,
)
from spaces.an_scrudu.pclm import (
    emit_pclm_pdf_bytes,
    emit_pclm_xml,
)


_log = logging.getLogger("an_scrudu.app")
set_lang("en")


def _on_extract(
    file_obj: gr.File | None,
    use_sample: bool,
) -> tuple[str, str, str, str]:
    """Extract a marking scheme and return the heatmap, PCLM preview, XML, and metadata.

    Returns:
        (heatmap_html, pclm_preview_html, pclm_xml, metadata_md)
    """
    if use_sample:
        filename, text = get_sample()
    elif file_obj is not None:
        # Read the uploaded file
        try:
            filename = file_obj.name.split("/")[-1] if hasattr(file_obj, "name") else "uploaded.txt"
            if filename.endswith(".pdf"):
                # No PDF parser in offline mode; show a friendly message
                return (
                    "",
                    "",
                    "",
                    f"**Note:** PDF parsing requires the `pypdf` package. "
                    f"File: {filename}. For the demo, click 'Use sample paper' "
                    f"to extract from the built-in LC Chemistry 2024 sample.",
                )
            with open(file_obj.name, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except (AttributeError, OSError) as e:
            return ("", "", "", f"**Error reading file:** {e}")
    else:
        return ("", "", "", "Upload a file or check 'Use sample paper'.")

    from spaces.an_scrudu.extraction import extract_circular
    ext = extract_circular(text, filename)

    heatmap_html = render_heatmap(ext)
    pclm_preview = render_pclm_html(ext)
    pclm_xml = emit_pclm_xml(ext)

    metadata = (
        f"**{ext.subject} - {ext.issued_year}**\n\n"
        f"- **{translate('space1.heatmap_caption')}**\n"
        f"- Source: `{ext.source_model}`\n"
        f"- Confidence: `{ext.extraction_confidence:.2f}`\n"
        f"- Total: {ext.total_marking_points} marks across {len(ext.topics)} topics"
    )

    return (heatmap_html, pclm_preview, pclm_xml, metadata)


def _on_download_pdf(file_obj: gr.File | None, use_sample: bool) -> str:
    """Generate a PDF for download. Returns a file path."""
    if use_sample:
        filename, text = get_sample()
    elif file_obj is not None and not file_obj.name.endswith(".pdf"):
        filename = file_obj.name.split("/")[-1]
        with open(file_obj.name, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    else:
        # Use the sample as a fallback
        filename, text = get_sample()

    from spaces.an_scrudu.extraction import extract_circular
    ext = extract_circular(text, filename)
    pdf_bytes = emit_pclm_pdf_bytes(ext)
    out_path = f"/tmp/{filename.rsplit('.', 1)[0]}_pclm.pdf"
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    return out_path


def build_app() -> gr.Blocks:
    with gr.Blocks(theme=apply_celtic_theme(), css=GRADIO_CSS, title="An Scrudu") as demo:
        gr.Markdown(
            f"""# {translate("space1.title")}
### *{translate("space1.subtitle")}*

Element: **Talamh** (Earth) - the curriculum map. Use a sample paper
or upload your own (plain text). The 3-tier HF Inference fallback
(Qwen 7B -> Llama 8B -> Gemma 9b) extracts the marking scheme. If all
3 models fail, an offline regex fallback engages so the heatmap always
renders.""",
            elem_classes="elem-talamh",
        )

        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label=translate("space1.upload_label"),
                    file_types=[".txt", ".md"],
                )
                use_sample_check = gr.Checkbox(
                    label="Use sample paper (LC Chemistry 2024)",
                    value=True,
                )
                extract_btn = gr.Button(
                    translate("space1.extract_button"),
                    variant="primary",
                )
                download_pdf_btn = gr.Button(
                    "Download as PDF",
                    variant="secondary",
                )
                pdf_file = gr.File(label="Generated PDF", visible=False)
            with gr.Column(scale=3):
                metadata_md = gr.Markdown(
                    value="_Click 'Extract Marking Scheme' to begin._",
                    label="Extraction metadata",
                )
                heatmap_html = gr.HTML(
                    value=(
                        '<div style="padding:2em; color:#bcb8b0; '
                        'text-align:center; font-style:italic;">'
                        'Heatmap appears here after extraction.</div>'
                    ),
                    label=translate("space1.heatmap_caption"),
                )

        with gr.Row():
            pclm_preview_html = gr.HTML(
                value=(
                    '<div style="padding:2em; color:#bcb8b0; '
                    'text-align:center; font-style:italic;">'
                    'PCLM preview appears here.</div>'
                ),
                label="PCLM-XML preview",
            )
            pclm_xml = gr.Code(
                value="",
                language="xml",
                label="PCLM-XML (downloadable)",
            )

        # Wire events
        extract_btn.click(
            fn=_on_extract,
            inputs=[file_input, use_sample_check],
            outputs=[heatmap_html, pclm_preview_html, pclm_xml, metadata_md],
        )
        download_pdf_btn.click(
            fn=_on_download_pdf,
            inputs=[file_input, use_sample_check],
            outputs=[pdf_file],
        ).then(
            fn=lambda: gr.update(visible=True),
            inputs=[],
            outputs=[pdf_file],
        )

        render_anam_bonneagar_footer(
            space_id="cianfhoghlaim/an-scrudu",
            pobal_hp="Dublin 8 (-9.8 HP 2022)",
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
