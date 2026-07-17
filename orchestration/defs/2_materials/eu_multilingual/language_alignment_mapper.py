"""Dagster L2 asset: map EU bilingual documents to British Isles corpus for alignment."""
from __future__ import annotations

from datetime import UTC, datetime

import dlt
from dagster import AssetExecutionContext, asset


@asset(
    group_name="2_materials_eu_multilingual",
    description=(
        "Map EU bilingual (en+ga) institutional documents to the "
        "British Isles Ireland + Northern Ireland corpus for cross-jurisdiction "
        "alignment via the en + ga language pair"
    ),
    compute_kind="python",
    deps=["english_coverage_monitor", "irish_coverage_monitor"],
)
def language_alignment_mapper(context: AssetExecutionContext) -> dict[str, int]:
    """Produce an alignment matrix linking EU bilingual docs to British Isles."""
    rows = [
        {
            "eu_institution": "eur_lex",
            "eu_language": "en",
            "bi_corpus_target": "ireland/courts_ie",
            "bi_language": "en",
            "alignment_strength": "high",
            "linked_at": datetime.now(UTC).isoformat(),
        },
        {
            "eu_institution": "eur_lex",
            "eu_language": "ga",
            "bi_corpus_target": "ireland/irish_statute_book",
            "bi_language": "ga",
            "alignment_strength": "high",
            "linked_at": datetime.now(UTC).isoformat(),
        },
        {
            "eu_institution": "eurydice",
            "eu_language": "en",
            "bi_corpus_target": "british_isles/ncca_gaeilge",
            "bi_language": "en",
            "alignment_strength": "high",
            "linked_at": datetime.now(UTC).isoformat(),
        },
        {
            "eu_institution": "eurydice",
            "eu_language": "ga",
            "bi_corpus_target": "british_isles/ncca_gaeilge",
            "bi_language": "ga",
            "alignment_strength": "high",
            "linked_at": datetime.now(UTC).isoformat(),
        },
        {
            "eu_institution": "eurostat",
            "eu_language": "en",
            "bi_corpus_target": "british_isles/cso_education",
            "bi_language": "en",
            "alignment_strength": "high",
            "linked_at": datetime.now(UTC).isoformat(),
        },
    ]

    @dlt.resource(
        name="eu_bi_alignment",
        write_disposition="merge",
        primary_key=["eu_institution", "eu_language", "bi_corpus_target"],
    )
    def eu_bi_alignment() -> list[dict]:
        return rows

    pipeline = dlt.pipeline(
        pipeline_name="language_alignment_mapper",
        destination="duckdb",
        dataset_name="cianfhoghlaim_multilingual",
    )
    load_info = pipeline.run(eu_bi_alignment())
    context.log.info(
        "language_alignment_completed",
        rows=len(rows),
        load_id=str(load_info.loads_ids[0]) if load_info.loads_ids else "",
    )
    return {"rows": len(rows)}


__all__ = ["language_alignment_mapper"]
