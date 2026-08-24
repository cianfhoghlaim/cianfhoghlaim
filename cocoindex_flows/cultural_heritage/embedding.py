"""cultural_heritage.embedding — re-export shim.

The actual CocoIndex v1 App is `culture_heritage_embedding_app` from
`cocoindex_flows.portfolio.culture_heritage_embedding`. This submodule
shim lets `orchestration/defs/3_model_lifecycle/cocoindex_v1/culture_heritage_embedding/defs.yaml`
import it as `from cocoindex_flows.cultural_heritage.embedding import
culture_heritage_embedding_app`.

The re-export is named `culture_heritage_embedding_app` to match what
the defs.yaml expects (via _find_app's `name == app_name` fallback).

`culture_heritage_embedding_app_main` is a NESTED function inside
`_make_app()` and is NOT importable as a module-level symbol. It's
intentionally NOT re-exported here.
"""
from __future__ import annotations

from cocoindex_flows.portfolio.culture_heritage_embedding import (
    culture_heritage_embedding_app,
)
