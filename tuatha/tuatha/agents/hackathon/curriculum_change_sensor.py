"""tuatha.agents.hackathon.curriculum_change_sensor — the Curriculum Change Detection Sensor.

Dagster sensor that watches the NCCA + AQA + SQA + WJEC + CCEA
+ IoM websites and fires the SequentialAgent on changes.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="curriculum_change_sensor",
    module_slug="curriculum_change_sensor",
    display_name="Curriculum Change Sensor",
    baml_prefix="CurrChgSens",
    langfuse_trace_name="agent.curriculum_change_sensor.<verb>",
    cognee_dataset="oideachais_curriculum_change_sensor",
    letta_agent_id="kcg-curriculum-change-sensor-agent",
)

config = TuathaConfig.from_env()


curriculum_change_sensor_agent = LlmAgent(
    name="curriculum_change_sensor_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Curriculum Change Detection Sensor. Dagster sensor that "
        "watches the NCCA + AQA + SQA + WJEC + CCEA + IoM websites "
        "and fires the SequentialAgent on changes."
    ),
    instruction=(
        "You are the Curriculum Change Sensor. You watch the "
        "6-jurisdiction curriculum websites for syllabus changes. "
        "When a change is detected, you fire the SequentialAgent "
        "to update the per-jurisdiction syllabus DLT sources + "
        "the per-subject BAML contracts + the per-subject agents."
    ),
    output_key="curriculum_change_sensor_response",
)


__all__ = ["_wire", "config", "curriculum_change_sensor_agent"]
