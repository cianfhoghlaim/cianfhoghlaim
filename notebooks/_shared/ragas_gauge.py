"""RAGASGaugeWidget — the canonical anywidget for per-cohort RAGAS score visualisation.

Per the centralised-observability capability — the RAGAS score is the
canonical quality metric for the 4-path OCR ensemble output. This
widget renders it as a circular progress gauge with a colour band
(green ≥0.85 / yellow ≥0.70 / red <0.70) + a sparkline of the last 10
scores from the audit table.

Reference: openspec/specs/british-isles-education-pipeline-v3/spec.md
           Requirement "BIEP v3 MUST expose its 24 tables via schema_introspect"
"""
from __future__ import annotations

try:
    import anywidget
    import traitlets
    _ANYWIDGET_AVAILABLE = True
except ImportError:
    # anywidget + traitlets are only installed inside the marimo runtime
    # (per the PEP 723 inline deps). At module import time outside that
    # runtime (e.g. `from notebooks import ...`), the imports fail.
    # The class definition below is conditional on these imports being
    # available.
    anywidget = None  # type: ignore[assignment]
    traitlets = None  # type: ignore[assignment]
    _ANYWIDGET_AVAILABLE = False


# Canonical RAGAS thresholds
RAGAS_EXCELLENT_THRESHOLD = 0.85
"""The RAGAS score at which the cohort is considered excellent (green)."""

RAGAS_PASS_THRESHOLD = 0.70
"""The canonical RAGAS pass threshold for the BIEP v3 4-path OCR ensemble (yellow)."""


def ragas_color(score: float) -> str:
    """Return the colour band for a RAGAS score.

    - Green ≥0.85 (excellent)
    - Yellow ≥0.70 (pass)
    - Red <0.70 (fail)
    """
    if score >= RAGAS_EXCELLENT_THRESHOLD:
        return "#22c55e"  # green
    elif score >= RAGAS_PASS_THRESHOLD:
        return "#eab308"  # yellow
    else:
        return "#ef4444"  # red


def ragas_status_emoji(score: float) -> str:
    """Return the status emoji for a RAGAS score."""
    if score >= RAGAS_EXCELLENT_THRESHOLD:
        return "✅"
    elif score >= RAGAS_PASS_THRESHOLD:
        return "⚠️"
    else:
        return "❌"


if _ANYWIDGET_AVAILABLE:

    class RAGASGaugeWidget(anywidget.AnyWidget):
        """The canonical RAGAS gauge widget for the BIEP jurisdiction dashboards.

    Renders a circular progress gauge + colour band + sparkline of the
    last N RAGAS scores from the audit table. The widget is fully
    reactive — when the `score` or `history` traitlets change, the
    gauge re-renders automatically.

    Usage in a marimo notebook:
    ```python
    from notebooks._shared.ragas_gauge import RAGASGaugeWidget
    gauge = mo.ui.anywidget(
        RAGASGaugeWidget(
            score=0.82,
            history=[0.78, 0.79, 0.82],
            cohort_slug="ireland_lc_mathematics_higher_en",
        )
    )
    gauge
    ```

    The widget renders:
    - A circular SVG gauge with the score as a fraction of the circle
    - A colour band (green/yellow/red) based on the score
    - A sparkline of the last N scores below the gauge
    - The cohort slug as the title
    """

    # Inputs (traitlets) — `sync=True` means the JS frontend sees the
    # value changes immediately.
    score = traitlets.Float(0.0).tag(sync=True)
    """The current RAGAS score (0.0 to 1.0)."""

    history = traitlets.List([]).tag(sync=True)
    """The last N RAGAS scores (for the sparkline). Empty list = no sparkline."""

    cohort_slug = traitlets.Unicode("").tag(sync=True)
    """The cohort slug (for the title)."""

    color = traitlets.Unicode("#22c55e").tag(sync=True)
    """The computed colour band (auto-updated by `_update_color` observer)."""

    @traitlets.observe("score")
    def _update_color(self, change: dict) -> None:
        """Auto-update the colour band when the score changes."""
        s = change["new"]
        self.color = ragas_color(s)

    @traitlets.validate("score")
    def _validate_score(self, proposal: dict) -> float:
        """Validate that the score is in [0.0, 1.0]."""
        v = proposal["value"]
        if v < 0.0:
            return 0.0
        elif v > 1.0:
            return 1.0
        return v

    def _repr_html_(self) -> str:
        """Render the widget as HTML for the notebook output."""
        score = self.score
        color = ragas_color(score)
        status_emoji = ragas_status_emoji(score)
        score_pct = score * 100

        # Build the SVG circle (radius=40, stroke-width=10)
        # The progress arc starts at -90° (12 o'clock) and goes clockwise.
        circumference = 2 * 3.14159 * 40
        offset = circumference * (1 - score)

        svg = f"""
        <svg width="120" height="120" viewBox="0 0 120 120"
             xmlns="http://www.w3.org/2000/svg"
             style="display: block; margin: 0 auto;">
          <!-- Background circle -->
          <circle cx="60" cy="60" r="40" fill="none"
                  stroke="#e5e7eb" stroke-width="10" />
          <!-- Progress arc -->
          <circle cx="60" cy="60" r="40" fill="none"
                  stroke="{color}" stroke-width="10"
                  stroke-dasharray="{circumference:.2f}"
                  stroke-dashoffset="{offset:.2f}"
                  transform="rotate(-90 60 60)"
                  stroke-linecap="round" />
          <!-- Score text -->
          <text x="60" y="55" text-anchor="middle"
                font-family="sans-serif" font-size="20" font-weight="bold"
                fill="#1f2937">
            {score_pct:.0f}
          </text>
          <text x="60" y="75" text-anchor="middle"
                font-family="sans-serif" font-size="12"
                fill="#6b7280">
            RAGAS
          </text>
        </svg>
        """

        # Build the sparkline (if history is non-empty)
        sparkline = ""
        if self.history:
            values = list(self.history)
            n = len(values)
            if n >= 2:
                # Normalize values to [0, 100] for the sparkline
                min_v = min(values)
                max_v = max(values)
                if max_v > min_v:
                    normalized = [(v - min_v) / (max_v - min_v) * 100 for v in values]
                else:
                    normalized = [50.0] * n

                # Build the SVG polyline
                width = 200
                height = 40
                step = width / (n - 1) if n > 1 else 0
                points = " ".join(
                    f"{i * step:.1f},{height - (v / 100 * height):.1f}"
                    for i, v in enumerate(normalized)
                )

                sparkline = f"""
                <svg width="{width}" height="{height + 20}" viewBox="0 0 {width} {height + 20}"
                     xmlns="http://www.w3.org/2000/svg"
                     style="display: block; margin: 10px auto 0;">
                  <text x="0" y="12" font-family="sans-serif" font-size="10"
                        fill="#6b7280">
                    History (last {n})
                  </text>
                  <polyline points="{points}" fill="none"
                            stroke="{color}" stroke-width="2"
                            stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                """

        # The full widget HTML
        return f"""
        <div style="
            border: 2px solid {color};
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            font-family: sans-serif;
            background: white;
            max-width: 320px;
            margin: 0 auto;
        ">
          <div style="
              font-size: 12px;
              font-weight: 600;
              color: #6b7280;
              margin-bottom: 8px;
              text-transform: uppercase;
              letter-spacing: 0.05em;
          ">
            {self.cohort_slug or "Cohort RAGAS Score"}
          </div>
          {svg}
          <div style="
              font-size: 14px;
              font-weight: 600;
              color: {color};
              margin-top: 4px;
          ">
            {status_emoji} {score:.3f}
          </div>
          {sparkline}
        </div>
        """

else:

    class RAGASGaugeWidget:  # type: ignore[no-redef]
        """Stub class — anywidget is not installed in this runtime.

        The real RAGASGaugeWidget is only available inside marimo's
        PEP 723 venv (which installs anywidget + traitlets). This stub
        prevents ``from notebooks._shared.ragas_gauge import RAGASGaugeWidget``
        from raising ImportError when the notebooks package is imported
        from outside the marimo runtime (e.g. from CLI scripts or tests).
        """

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                "RAGASGaugeWidget requires anywidget + traitlets, which are "
                "only installed inside the marimo PEP 723 runtime. "
                "Run via `uv run marimo edit <notebook>.py` or "
                "`python <notebook>.py` (which uses uv to install the deps)."
            )


# Convenience: __all__
__all__ = [
    "RAGASGaugeWidget",
    "ragas_color",
    "ragas_status_emoji",
    "RAGAS_EXCELLENT_THRESHOLD",
    "RAGAS_PASS_THRESHOLD",
]