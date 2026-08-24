"""celtic_history_research/tuatha_de_danann stub DLT resource.

GATED for the downstream theming change. Yields zero rows.

The user's own clippings at
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/tuatha_de_danann-wikipedia.md`
is the canonical source for the future theming change.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            spec.md § celtic-history-research
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt


@dlt.resource(
    name="tuatha_de_danann_stub",
    write_disposition="merge",
    primary_key=("work", "source_url", "source_timestamp"),
)
def tuatha_de_danann_stub() -> Iterator[dict[str, Any]]:
    """Celtic-history stub. Yields zero rows.

    GATED for the downstream theming change. The plugin
    registry handles the no-op (per the
    `media-intel-acquisition-plan` spec, Requirement 6).
    """
    return
    yield  # noqa: unreachable — but keeps the function a generator


__all__ = ["tuatha_de_danann_stub"]
