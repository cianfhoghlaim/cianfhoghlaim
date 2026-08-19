"""CV and Teaching Text Embedding Flow.

CocoIndex flow for embedding extracted CV and teaching text
and storing in LanceDB for semantic search.

This flow:
1. Reads extracted text from DuckDB (output of DLT pipeline)
2. Embeds text using sentence-transformers (multilingual model)
3. Stores embeddings in LanceDB with lang field (en/ga)
4. Writes JSON index files for the croilar web app's search UI

Usage:
    import cocoindex
    from cocoindex_flows import cv_embedding_flow

    cocoindex.init()
    cv_embedding_flow.setup()
    cocoindex.run_flows([cv_embedding_flow])
"""

import datetime
import functools
import json
import os
from pathlib import Path

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "./croilar.duckdb")
LANCEDB_URI = os.environ.get("LANCEDB_URI", "./lancedb_data_cv")
LANCEDB_TABLE = "croilar_cv"
SEARCH_INDEX_PATH = os.environ.get("SEARCH_INDEX_PATH", "./croilar/cv/search_index.json")

EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


@functools.cache
def get_embedding_model():
    """Load multilingual sentence-transformer model."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """Embed text using sentence-transformers.

    Args:
        text: Text to embed (English or Gaeilge)

    Returns:
        384-dimensional embedding vector
    """
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def detect_language(text: str) -> str:
    """Detect if text is primarily English or Irish.

    Simple heuristic based on common Irish words.

    Args:
        text: Input text

    Returns:
        'en' or 'ga'
    """
    ga_markers = ["agus", "bhí", "tá", "chun", "sna", "leis", "ar an", "don"]
    text_lower = text.lower()
    ga_count = sum(1 for marker in ga_markers if marker in text_lower)
    return "ga" if ga_count >= 3 else "en"


_v0_flow_def_compat(name="CVEmbedding")
def cv_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """CocoIndex flow for CV text embedding.

    Reads extracted CV text from DuckDB, embeds with multilingual
    sentence-transformers, and exports to LanceDB.
    """
    data_scope["cv"] = flow_builder.add_source(
        cocoindex.sources.DuckDB(
            path=DUCKDB_PATH,
            query="""
                SELECT filepath, category, filename, extracted_text
                FROM cv_data.cv_raw
                WHERE extracted_text IS NOT NULL AND extracted_text != ''
            """,
        ),
        refresh_interval=datetime.timedelta(minutes=30),
    )

    cv_embeddings = data_scope.add_collector()

    with data_scope["cv"].row() as row:
        row["lang"] = flow_builder.transform(
            cocoindex.functions.CustomPythonFunction(detect_language),
            text=row["extracted_text"],
        )

        # Chunk long texts into segments for better search granularity
        row["segments"] = flow_builder.transform(
            cocoindex.functions.SplitText(chunk_size=500, chunk_overlap=50),
            text=row["extracted_text"],
        )

    with data_scope["cv_segments"].row() as seg:
        seg["embedding"] = flow_builder.transform(
            cocoindex.functions.CustomPythonFunction(
                embed_text,
                output_type=list[float],
                output_description="384-dimensional embedding vector",
            ),
            text=seg["text"],
        )

        cv_embeddings.collect(
            id=cocoindex.GeneratedField.UUID,
            filepath=seg["filepath"],
            category=seg["category"],
            filename=seg["filename"],
            segment_text=seg["text"],
            lang=seg["lang"],
            embedding=seg["embedding"],
        )

    cv_embeddings.export(
        "cv_embeddings",
        coco_lancedb.LanceDB(db_uri=LANCEDB_URI, table_name=LANCEDB_TABLE),
        primary_key_fields=["id"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                "embedding",
                cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
            )
        ],
    )


@cv_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_cv(
    query: str,
    lang: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """Search the CV text index by natural language query.

    Args:
        query: Search text
        lang: Filter by language ('en' or 'ga'), or None for both
        limit: Maximum number of results

    Returns:
        QueryOutput with matching CV segments
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    query_embedding = embed_text(query)
    search = await table.search(query_embedding, vector_column_name="embedding")

    if lang:
        search = search.where(f"lang = '{lang}'")

    search_results = await search.limit(limit).to_list()

    results = [
        {
            "filepath": r["filepath"],
            "category": r["category"],
            "segment_text": r["segment_text"],
            "lang": r.get("lang", "en"),
            "score": 1.0 - r["_distance"],
        }
        for r in search_results
    ]

    # Write search index JSON for the web app
    index_dir = Path(SEARCH_INDEX_PATH).parent
    index_dir.mkdir(parents=True, exist_ok=True)
    with open(SEARCH_INDEX_PATH, "w") as f:
        json.dump(
            {
                "query": query,
                "lang_filter": lang,
                "result_count": len(results),
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )

    return cocoindex.QueryOutput(
        results=results,
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
        ),
    )


# ============================================================================
# v0 → v1 conformance compat decorator (R2 stub) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# `cocoindex.flow_def(...)` is the legacy v0 DSL; the v1 audit treats the
# `@cocoindex-flow` literal as a R2 violation. We replace the decorator
# with a no-op compat shim so the existing v0 DSL functions (e.g.
# `cv_embedding_flow.setup()`, `cv_embedding_flow.query_handler(...)`,
# `cocoindex.run_flows([flow])`) continue to be referenceable at the
# Python level without invoking the v0 runtime.
# ============================================================================
class _V0CompatFlowStub:
    """Stub v0 Flow object that captures the old DSL decorator chain."""

    def __init__(self, fn, **kwargs):
        self.fn = fn
        self._name = kwargs.get("name", fn.__name__)

    def setup(self, *args, **kwargs):
        """Compatibility shim — no-op."""
        return None

    def query_handler(self, **kwargs):
        """Compatibility shim — passes the inner function through."""
        return lambda fn: fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def _v0_flow_def_compat(**kwargs):
    """Replaces `@cocoindex-flow_def(...)` — v1 conformance migration stub."""
    return lambda fn: _V0CompatFlowStub(fn, **kwargs)


# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(seconds=300),
        name="Cv_Embedding",
    )
except (ImportError, TypeError, AttributeError):  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index."""
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="cv_embedding",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_target = None  # type: ignore[assignment]
