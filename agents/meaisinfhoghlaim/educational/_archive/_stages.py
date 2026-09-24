"""Stage <-> floor mapping (separated to break the circular import)."""
from agents.meaisinfhoghlaim._shared import EducationStage, STAGE_TO_FLOOR as _SHARED


stage_to_floor = _SHARED


__all__ = ["stage_to_floor"]
