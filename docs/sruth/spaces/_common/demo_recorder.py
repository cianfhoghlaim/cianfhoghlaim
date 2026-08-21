"""
spaces/_common/demo_recorder.py
Programmatic demo recording for the 4 Spaces.

The hackathon submission requires a demo video. Rather than manually
clicking through each Space, this module provides:
  - record_interaction: Capture a sequence of (component_id, value) tuples
  - render_storyboard: Compose a 16:9 storyboard PNG from a sequence
  - export_voiceover_script: Emit a VoiceOverScript.txt for human narration

Usage:
    from spaces._common.demo_recorder import (
        DemoSequence, record_interaction, render_storyboard,
    )
    seq = DemoSequence(title="An Scrudu", element="talamh")
    seq.add("input_pdf", "lc_chem_2024.pdf")
    seq.add("extract_btn.click", None)
    seq.add("output_heatmap", "...")
    render_storyboard(seq, "storyboard.png")
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Final


@dataclass
class DemoStep:
    """A single recorded interaction step."""

    timestamp: float
    component_id: str
    value: Any
    note: str = ""


@dataclass
class DemoSequence:
    """A full demo sequence for one Space."""

    title: str
    element: str  # talamh, uisce, tine, aer, anam
    steps: list[DemoStep] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    voiceover_lines: list[str] = field(default_factory=list)

    def add(
        self,
        component_id: str,
        value: Any,
        note: str = "",
    ) -> None:
        """Record a single interaction step."""
        elapsed = time.time() - self.started_at
        self.steps.append(
            DemoStep(
                timestamp=elapsed,
                component_id=component_id,
                value=value,
                note=note,
            )
        )

    def add_voiceover(self, line: str) -> None:
        """Add a voiceover line at the current timestamp."""
        self.voiceover_lines.append(line)

    @property
    def total_duration(self) -> float:
        """Estimated total duration in seconds (1 step ~= 3s)."""
        return max(len(self.steps) * 3.0, 15.0)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict (for JSON sidecar)."""
        return {
            "title": self.title,
            "element": self.element,
            "started_at": self.started_at,
            "total_duration_s": self.total_duration,
            "steps": [
                {
                    "timestamp": s.timestamp,
                    "component_id": s.component_id,
                    "value": repr(s.value)[:200],
                    "note": s.note,
                }
                for s in self.steps
            ],
            "voiceover_lines": self.voiceover_lines,
        }

    def save_json(self, path: str) -> None:
        """Write the sequence to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


_ELEMENT_TAGLINES: Final[dict[str, str]] = {
    "talamh": "Earth / Talamh - the curriculum map",
    "uisce": "Water / Uisce - the chemistry visual",
    "tine": "Fire / Tine - the OCR forge",
    "aer": "Air / Aer - the language carrier",
    "anam": "Spirit / Anam - the soulbound token",
}


def render_storyboard(seq: DemoSequence, output_path: str) -> str:
    """Render a 16:9 storyboard PNG from the sequence.

    This is a best-effort render - it produces a simple storyboard
    layout (title + 4-step summary) using PIL if available, or a
    plain-text fallback otherwise.

    Returns:
        The output_path on success, or "" if rendering failed.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except ImportError:
        return ""

    w, h = 1920, 1080
    bg = (29, 29, 47)
    gold = (204, 153, 102)
    bone = (216, 212, 204)
    bronze = (166, 124, 82)
    emerald = (40, 149, 94)
    azure = (30, 128, 198)
    amber = (214, 140, 28)
    indigo = (90, 79, 207)

    elem_color = {
        "talamh": emerald,
        "uisce": azure,
        "tine": amber,
        "aer": indigo,
        "anam": gold,
    }.get(seq.element, bone)

    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    draw.rectangle((20, 20, w - 20, h - 20), outline=bronze, width=4)

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 72)
        body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 32)
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 22)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = small_font = title_font

    draw.text((60, 60), seq.title, fill=gold, font=title_font)
    draw.text(
        (60, 160),
        _ELEMENT_TAGLINES.get(seq.element, ""),
        fill=elem_color,
        font=body_font,
    )

    summary_steps = seq.steps[:4]
    if not summary_steps:
        summary_steps = [
            DemoStep(0, "input", "demo.pdf", "user uploads sample"),
            DemoStep(5, "extract", "click", "user clicks extract"),
            DemoStep(15, "output", "heatmap.png", "Space returns heatmap"),
            DemoStep(25, "share", "social_card.png", "user shares card"),
        ]

    y = 280
    for i, step in enumerate(summary_steps, 1):
        draw.text(
            (60, y),
            f"Step {i} (t={step.timestamp:.1f}s)",
            fill=elem_color,
            font=body_font,
        )
        draw.text(
            (60, y + 40),
            f"  {step.component_id}: {str(step.value)[:80]}",
            fill=bone,
            font=small_font,
        )
        if step.note:
            draw.text(
                (60, y + 70),
                f"  ({step.note})",
                fill=bronze,
                font=small_font,
            )
        y += 130

    draw.text(
        (60, h - 220),
        "Voiceover (transcript):",
        fill=gold,
        font=body_font,
    )
    vo_text = "\n".join(seq.voiceover_lines[:3]) or (
        "Demonstration auto-narrated. See transcript for full text."
    )
    draw.multiline_text(
        (60, h - 180),
        vo_text[:600],
        fill=bone,
        font=small_font,
        spacing=4,
    )

    draw.text(
        (w - 460, h - 60),
        "Anam Bonneagar  *  cianfhoghlaim  *  Build Small 2026",
        fill=bronze,
        font=small_font,
    )

    img.save(output_path, "PNG", optimize=True)
    return output_path


def export_voiceover_script(seq: DemoSequence, path: str) -> str:
    """Export a human-readable voiceover script to a text file.

    The script includes:
      - Title + element
      - Estimated duration
      - Timestamp for each step
      - Voiceover lines (if added)
      - Suggested narrator cues (TONE: ... / [PAUSE])
    """
    lines: list[str] = [
        f"# Voiceover Script: {seq.title}",
        f"Element: {seq.element}",
        f"Estimated duration: {seq.total_duration:.0f} seconds",
        "",
        "## Beat-by-beat",
        "",
    ]
    for i, step in enumerate(seq.steps, 1):
        lines.append(f"[{step.timestamp:5.1f}s] Step {i}: {step.component_id}")
        if step.note:
            lines.append(f"           TONE: {step.note}")
        if step.value is not None:
            lines.append(f"           SAY: {str(step.value)[:120]}")
        lines.append("           [PAUSE 0.5s]")
        lines.append("")

    if seq.voiceover_lines:
        lines.append("## Pre-written voiceover lines")
        lines.append("")
        for line in seq.voiceover_lines:
            lines.append(f"- {line}")

    text = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
