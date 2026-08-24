"""celtic_history_research/celtic_mythology stub DLT resource.

GATED for the downstream theming change. Yields zero rows.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt


@dlt.resource(
    name="celtic_mythology_stub",
    write_disposition="merge",
    primary_key=("work", "source_url", "source_timestamp"),
)
def celtic_mythology_stub() -> Iterator[dict[str, Any]]:
    """Celtic-history stub. Yields zero rows."""
    return
    yield  # noqa: unreachable


__all__ = ["celtic_mythology_stub"]
