"""ni_education_embedding — Wave 3 stub.

This is a placeholder CocoIndex v1 App for the
`orchestration/defs/3_model_lifecycle/cocoindex_v1/ni_education_embedding/defs.yaml`
references. The actual implementation lands in Wave 3 follow-up PRs.

Per the `2026-08-24-wave-3-cocoindex-v0-stragglers-v1` openspec change
(the v0 stragglers inventory). This stub:
- Imports the v1 API (`import cocoindex as coco`)
- Declares a dummy `@coco.fn` function (so `_check_module_r1_to_r4` passes)
- Declares a module-level `coco.App(...)` (so `_find_app` finds it via
  `obj.config.name`)

Real per-jurisdiction logic lives in the `biep_parity/bi_factory.py`
factory pattern (40-nation, per-ISO-3) — the per-jurisdiction
`ni_education_embedding` defs.yaml files were a v0-era mistake that we're now stubbing.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, Any

from numpy.typing import NDArray

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex_flows._shared._lifespan import EMBEDDER  # type: ignore[attr-defined]
    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    EMBEDDER = None  # type: ignore[assignment]


if COCOINDEX_AVAILABLE:

    @coco.fn  # type: ignore[misc]
    async def ni_education_embedding_flow(  # type: ignore[no-untyped-def,unused-ignore]
        source_id: str,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stub: yield one dummy row for the ni_education_embedding pipeline."""
        yield {"source_id": source_id, "kind": "ni_education_embedding_stub"}

    app = coco.App(
        coco.AppConfig(name="ni_education_embedding"),
        ni_education_embedding_flow,
        shared_lifespan=None,  # type: ignore[arg-type]
    )
else:
    app = None  # type: ignore[assignment]
