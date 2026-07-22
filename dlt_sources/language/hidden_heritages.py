"""
Culture IE source: hidden_heritages_source

Split from celtic/duchas_images.py in Phase 3D.
"""

from __future__ import annotations
import dlt


import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt_sources
from dlt.sources import DltResource

try:
    from dlt.sources.incremental import Incremental  # noqa: F401
except ImportError:
    pass  # dlt.sources.incremental moved; use dlt.sources.incremental.IncrementalCursorProvider instead

try:
    from dlt_sources.common.http_client import doras_client, duchas_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


def hidden_heritages_source(
    language: str = "ga",
    collection: str = "nfc",
    max_tales: int = 100,
) -> Iterator[DltResource]:
    """
    DLT source for HiddenHeritages.ai transcribed manuscripts.

    Collections:
    - nfc: National Folklore Collection
    - sss: School of Scottish Studies

    Args:
        language: Language filter (ga, gd, en)
        collection: Collection (nfc, sss)
        max_tales: Maximum tales to fetch

    Yields:
        DLT resources for tales and transcriptions
    """

    @dlt.resource(
        name="tales",
        write_disposition="merge",
        primary_key="tale_id",
    )
    def tales() -> Iterator[dict[str, Any]]:
        """HiddenHeritages tales with HTR transcriptions."""
        # HiddenHeritages.ai API endpoints

        try:
            # Use Firecrawl agent for discovery if available
            api_key = os.getenv("FIRECRAWL_API_KEY")
            if api_key:
                from firecrawl import FirecrawlApp

                app = FirecrawlApp(api_key=api_key)

                result = app.agent(
                    prompt=f"Find tales from the {collection.upper()} collection "
                    f"in {language} language. Extract tale ID, title, "
                    "transcription text, and image URLs.",
                    urls=[f"https://hiddenheritages.ai/{collection}"],
                    schema={
                        "type": "object",
                        "properties": {
                            "tales": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tale_id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "transcription": {"type": "string"},
                                        "image_url": {"type": "string"},
                                        "collector": {"type": "string"},
                                        "informant": {"type": "string"},
                                        "location": {"type": "string"},
                                        "date": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                )

                for tale in result.get("data", {}).get("tales", [])[:max_tales]:
                    yield {
                        "tale_id": tale.get("tale_id", ""),
                        "title": tale.get("title", ""),
                        "transcription": tale.get("transcription", ""),
                        "image_url": tale.get("image_url", ""),
                        "collector": tale.get("collector", ""),
                        "informant": tale.get("informant", ""),
                        "location": tale.get("location", ""),
                        "date": tale.get("date", ""),
                        "language": language,
                        "collection": collection,
                        "source": "hiddenheritages.ai",
                        "fetched_at": datetime.now(UTC).isoformat(),
                    }
            else:
                # Fallback: direct scraping
                yield {
                    "tale_id": "placeholder",
                    "title": "",
                    "transcription": "",
                    "language": language,
                    "collection": collection,
                    "source": "hiddenheritages.ai",
                    "status": "firecrawl_not_available",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            yield {
                "tale_id": "error",
                "error": str(e),
                "language": language,
                "collection": collection,
                "source": "hiddenheritages.ai",
                "fetched_at": datetime.now(UTC).isoformat(),
            }

    yield tales
