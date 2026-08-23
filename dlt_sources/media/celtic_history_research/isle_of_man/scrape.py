"""celtic_history_research/isle_of_man stub DLT resource.

GATED for the downstream theming change. Yields zero rows.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt


@dlt.resource(
    name="isle_of_man_stub",
    write_disposition="merge",
    primary_key=("work", "source_url", "source_timestamp"),
)
def isle_of_man_stub() -> Iterator[dict[str, Any]]:
    """Celtic-history stub. Yields zero rows."""
    return
    yield  # noqa: unreachable


__all__ = ["isle_of_man_stub"]
