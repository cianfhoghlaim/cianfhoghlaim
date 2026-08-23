"""tuatha.agents.hackathon — the 4 BIEP hackathon features.

The canonical re-export surface. The 4 BIEP hackathon
features (per the
`2026-08-21-biiep-hackathon-agentic-educational-system-v1/`
change):

- `marking_grader_agent` — the Adaptive Marking Grader
- `adaptive_tutor_agent` — the Adaptive Tutor Chat
- `equivalency_generator_agent` — the Cross-Jurisdiction
  Equivalency Generator
- `curriculum_change_sensor_agent` — the Curriculum Change
  Detection Sensor
"""
from __future__ import annotations

try:
    from .adaptive_tutor import (  # type: ignore
        adaptive_tutor_agent,
    )
    from .curriculum_change_sensor import (  # type: ignore
        curriculum_change_sensor_agent,
    )
    from .equivalency_generator import (  # type: ignore
        equivalency_generator_agent,
    )
    from .marking_grader import (  # type: ignore
        marking_grader_agent,
    )

    AGENTS = {
        "marking_grader": marking_grader_agent,
        "adaptive_tutor": adaptive_tutor_agent,
        "equivalency_generator": equivalency_generator_agent,
        "curriculum_change_sensor": curriculum_change_sensor_agent,
    }
except ImportError:
    AGENTS = {}


__all__ = [
    "AGENTS",
    "adaptive_tutor_agent",
    "curriculum_change_sensor_agent",
    "equivalency_generator_agent",
    "marking_grader_agent",
]
