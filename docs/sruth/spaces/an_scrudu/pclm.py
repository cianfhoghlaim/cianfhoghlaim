"""
spaces/an_scrudu/pclm.py
PCLM-PDF emitter for the extracted marking scheme.

PCLM (Paper Common Layout Markup) is a Department-of-Education-flavoured
XML schema used for Irish past papers. The Space emits a minimal
PCLM document from a CircularExtraction; the user can download it and
ingest it into the oideachais document_factory.

This is a *simplified* emitter, scoped to the Space demo. The full
PCLM schema in oideachais/document_factory/curriculum_document.py
has 4-5x more tags; we emit a subset that round-trips with the
extraction (topic_code, topic_label, marking_points, paper_section).
"""

from __future__ import annotations

import io
from xml.etree import ElementTree as ET

from spaces.an_scrudu.extraction import CircularExtraction


PCLM_NS = "https://oideachais.ie/pclm/1.0"


def emit_pclm_xml(extraction: CircularExtraction) -> str:
    """Emit a PCLM XML document for the given extraction.

    Returns the XML as a string (UTF-8, pretty-printed).
    """
    ET.register_namespace("", PCLM_NS)
    root = ET.Element(f"{{{PCLM_NS}}}examination")
    root.set("circular_number", str(extraction.circular_number))
    root.set("issued_year", str(extraction.issued_year))
    root.set("subject", extraction.subject)
    root.set("level", extraction.level)

    title = ET.SubElement(root, f"{{{PCLM_NS}}}title")
    title_en = ET.SubElement(title, f"{{{PCLM_NS}}}en")
    title_en.text = extraction.title_en
    if extraction.title_ga:
        title_ga = ET.SubElement(title, f"{{{PCLM_NS}}}ga")
        title_ga.text = extraction.title_ga

    issuing = ET.SubElement(root, f"{{{PCLM_NS}}}issuingBody")
    issuing.text = extraction.issuing_body

    scheme = ET.SubElement(root, f"{{{PCLM_NS}}}markingScheme")
    scheme.set("totalMarks", str(extraction.total_marking_points))
    scheme.set("durationMin", str(extraction.estimated_paper_duration_min))
    if extraction.has_orale:
        scheme.set("hasOrale", "true")
    if extraction.has_coursework:
        scheme.set("hasCoursework", "true")

    for topic in extraction.topics:
        t_elem = ET.SubElement(scheme, f"{{{PCLM_NS}}}topic")
        t_elem.set("code", topic.topic_code)
        t_elem.set("section", topic.paper_section)
        t_elem.set("marks", str(topic.marking_points))
        lbl = ET.SubElement(t_elem, f"{{{PCLM_NS}}}label")
        lbl.text = topic.topic_label

    excerpt = ET.SubElement(root, f"{{{PCLM_NS}}}excerpt")
    excerpt.text = extraction.raw_text_excerpt

    confidence = ET.SubElement(root, f"{{{PCLM_NS}}}extractionConfidence")
    confidence.text = f"{extraction.extraction_confidence:.3f}"

    source = ET.SubElement(root, f"{{{PCLM_NS}}}sourceModel")
    source.text = extraction.source_model

    # Pretty-print
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")


def emit_pclm_pdf_bytes(extraction: CircularExtraction) -> bytes:
    """Emit a minimal PDF containing the PCLM text. Pure-Python, no deps.

    This is a 1-page PDF with the headline data only. The full
    curriculum_document.py in oideachais/ emits multi-page PDFs with
    Cormorant Garamond typography; this emitter is a Space-scoped
    minimal version that works in any Gradio container.
    """
    text_lines: list[str] = [
        f"PCLM Marking Scheme - {extraction.subject} {extraction.issued_year}",
        "",
        f"Title: {extraction.title_en}",
        f"Issuing body: {extraction.issuing_body}",
        f"Level: {extraction.level}",
        f"Total marks: {extraction.total_marking_points}",
        f"Duration: {extraction.estimated_paper_duration_min} min",
        "",
        "Topics:",
    ]
    for t in extraction.topics:
        text_lines.append(
            f"  {t.topic_code} {t.topic_label} - {t.marking_points} marks ({t.paper_section})"
        )
    text_lines.extend(
        [
            "",
            f"Extraction confidence: {extraction.extraction_confidence:.2f}",
            f"Source model: {extraction.source_model}",
            "",
            "Excerpt:",
            extraction.raw_text_excerpt,
        ]
    )
    return _render_minimal_pdf(text_lines)


def _render_minimal_pdf(lines: list[str]) -> bytes:
    """Render a list of text lines as a 1-page PDF. Pure-Python."""
    # Build the content stream
    content_parts: list[str] = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
    for i, line in enumerate(lines):
        # Escape PDF text
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if i == 0:
            content_parts.append(f"({safe}) Tj")
        else:
            content_parts.append(f"T* ({safe}) Tj")
    content_parts.append("ET")
    content = "\n".join(content_parts).encode("latin-1", errors="replace")

    # Build the PDF objects
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 792] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    # Assemble the PDF
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for i, obj in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode())
        out.write(obj)
        out.write(b"\nendobj\n")
    xref_offset = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(b"trailer\n")
    out.write(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode())
    out.write(f"startxref\n{xref_offset}\n%%EOF\n".encode())
    return out.getvalue()
