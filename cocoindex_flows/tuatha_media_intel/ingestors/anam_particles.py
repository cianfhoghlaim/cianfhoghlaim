"""ANAM particle cross-source joiner — CocoIndex v1 App.

Reads rows from the 3 source tables (hades_boons, comic_particles,
gba_magic) via DuckDB federation (per the lance_scan() pattern in the
lancedb skill), runs the BAML MapToAnamParticle function on each, and
writes the canonical ANAM particle row to cianfhoghlaim.tuatha.anam_particles.

This is the dataset that feeds the 2D TanStack Start client + the Celtic
deity mapping in tuatha/subjects/character.py.

shippable=false invariant: description-only rows. ANAM color/motion
must be derivable from the description fields alone.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Annotated, Any

import cocoindex as coco
from cocoindex.connectors import lancedb
from numpy.typing import NDArray

from .._shared import EMBEDDER, LANCE_DB, shared_lifespan

TABLE_NAME = "cianfhoghlaim.tuatha.anam_particles"

# The 3 source tables to join from. Update on schema change.
SOURCE_TABLES = [
    "cianfhoghlaim.tuatha.hades.boons",
    "cianfhoghlaim.tuatha.comic.particles",
    "cianfhoghlaim.tuatha.gba.magic",
]


@dataclass
class AnamParticleRow:
    anam_id: str
    source: str
    source_id: str
    celtic_deity: str
    anam_color_hex: str
    anam_motion: str
    description_en: str
    description_ga: str | None
    bias_mode: str
    run_id: str
    generated_at: str
    embedding: Annotated[NDArray, EMBEDDER]


async def _baml_map_to_anam(
    source: str, source_payload: dict[str, Any], bias_mode: str
) -> dict[str, Any]:
    from baml_client.sync_client import b  # type: ignore[import-not-found]

    result = b.MapToAnamParticle(
        source=source,
        source_payload=json.dumps(source_payload, default=str),
        bias_mode=bias_mode,
    )
    desc_ga = result.description_ga if hasattr(result, "description_ga") else None
    return {
        "anam_id": result.anam_id,
        "source": result.source.value
        if hasattr(result.source, "value")
        else str(result.source),
        "source_id": result.source_id,
        "celtic_deity": (
            result.celtic_deity.value
            if hasattr(result.celtic_deity, "value")
            else str(result.celtic_deity)
        ),
        "anam_color_hex": result.anam_color_hex,
        "anam_motion": result.anam_motion,
        "description_en": result.description_en,
        "description_ga": desc_ga,
        "bias_mode": bias_mode,
        "run_id": result.run_id,
        "generated_at": result.generated_at,
    }


async def _cross_linguistic_anam(
    anam_en: str, target_lang: str
) -> str | None:
    """Optional translation pass — currently only Irish is targeted."""
    from baml_client.sync_client import b  # type: ignore[import-not-found]

    if target_lang not in {"ga", "irish", "Gaeilge"}:
        return None
    return b.ExtractCrossLinguisticAnamDescription(
        anam_en=anam_en, target_lang="Gaeilge"
    )


async def _baml_translate_ga(anam_en: str) -> str | None:
    return await _cross_linguistic_anam(anam_en, "ga")


@coco.fn(memo=True)
async def process_source_row(
    source: str,
    row: dict[str, Any],
    bias_mode: str,
    table: lancedb.TableTarget,
) -> None:
    """Per source row: BAML MapToAnamParticle → anam row.

    `source` is one of "hades" | "comic" | "gba" | "manual".
    """
    anam = await _baml_map_to_anam(source=source, source_payload=row, bias_mode=bias_mode)
    desc_ga = await _baml_translate_ga(anam["description_en"])
    combined = (
        f"{anam['celtic_deity']}: {anam['anam_motion']} | "
        f"{anam['description_en']}"
        + (f" | {desc_ga}" if desc_ga else "")
    )
    vec = await coco.use_context(EMBEDDER).embed(combined)
    table.declare_row(
        row=AnamParticleRow(
            anam_id=anam["anam_id"],
            source=anam["source"],
            source_id=anam["source_id"],
            celtic_deity=anam["celtic_deity"],
            anam_color_hex=anam["anam_color_hex"],
            anam_motion=anam["anam_motion"],
            description_en=anam["description_en"],
            description_ga=desc_ga,
            bias_mode=bias_mode,
            run_id=anam["run_id"],
            generated_at=anam["generated_at"],
            embedding=vec,
        )
    )


@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            AnamParticleRow, primary_key=["anam_id"]
        ),
    )
    table.declare_vector_index(column="embedding")
    table.declare_fts_index(
        column="description_en", language="English", with_position=True
    )

    # Federate the 3 source tables via DuckDB + lance_scan() — see the
    # lancedb skill "Ibis + DuckDB lance_scan()" for the canonical pattern.
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL lance; LOAD lance;")
    source_summaries: list[dict[str, Any]] = []
    for src in SOURCE_TABLES:
        con.execute(
            f"CREATE OR REPLACE VIEW src_{src.split('.')[-2]}_{src.split('.')[-1]} "
            f"AS SELECT * FROM lance_scan('s3://garage/lance/{src}')"
        )
        rows = con.execute(
            f"SELECT * FROM src_{src.split('.')[-2]}_{src.split('.')[-1]} "
            f"LIMIT 1000"
        ).fetchall()
        cols = [d[0] for d in con.description]
        for r in rows:
            source_summaries.append({c: v for c, v in zip(cols, r)})

    # Bias mode is per source — see comic/source.yaml for the legal_notes
    # bias that description_heavy is used for comics.
    bias_by_source = {
        "hades.boons": "balanced",
        "comic.particles": "description_heavy",
        "gba.magic": "color_heavy",
    }

    for src_short, bias in bias_by_source.items():
        matching = [
            s for s in source_summaries if s.get("__source_table", "").endswith(src_short)
        ]
        for row in matching:
            row["__source_table"] = src_short
            await coco.use_context(EMBEDDER)  # warm the embedder
            await process_source_row(
                source=src_short.split(".")[0],
                row=row,
                bias_mode=bias,
                table=table,
            )


anam_particles_app = coco.App(
    coco.AppConfig(name="tuatha_anam_particles"),
    app_main,
    lifespan=shared_lifespan,
)


if __name__ == "__main__":
    import cocoindex as _ci

    _ci.init()
    anam_particles_app.update()
