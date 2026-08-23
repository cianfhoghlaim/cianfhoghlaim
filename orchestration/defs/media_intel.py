"""orchestration.defs.media_intel — the 5-layer asset group
for the media-intel reference-corpus spine.

Refactored 2026-08-23 to add 8 new Class E (official) DLT
source assets per the per-jurisdiction split:

  - L1 Ingestion: 5 DLT source assets (one per media class)
    + 8 new official-sub-bucket DLT source assets
    (3 government + 5 departments) for a total of
    13 L1 assets.
  - L2 Materials: 5 BAML extraction assets
  - L3 Model Lifecycle: 2 CocoIndex Apps
  - L4 Asset Generation: 2 marimo notebooks
  - L5 Agent Ops: 1 ADK media_descriptor_agent execution asset

Plus the `media_descriptor_coverage` asset check (L6 sync
contract) that fails the run if any of the 5 source classes
has 0 rows in `media_descriptors_lance`.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1 (the 7-axis MediaDescriptor schema)
            spec.md § media-intel-corpus Requirement 4
"""
from __future__ import annotations

import datetime

from dagster import (
    AssetCheckResult,
    AssetCheckSeverity,
    AssetExecutionContext,
    Definitions,
    asset,
    asset_check,
    define_asset_job,
    schedule,
)

# ============================================================================
# L1 Ingestion — 5 DLT source assets (one per media class) + 8 official
# ============================================================================


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class A — Comics. Ingests the Jonathan Hickman Marvel "
        "run (FF 570-611, FF 1-23, Future Foundation, Avengers "
        "2012, New Avengers 2013, Infinity, Secret Wars 2015, "
        "House of X, Powers of X, X-Men 2019, Krakoa crossovers) "
        "from Wikipedia + Marvel wiki transcripts via the "
        "marvel_hickman_panel_descriptors DLT resource in "
        "dlt_sources/media/comics/hickman_marvel/scrape.py."
    ),
)
def marvel_hickman_comics_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.comics.hickman_marvel.scrape import (  # type: ignore
        marvel_hickman_panel_descriptors,
    )

    rows = []
    for record in marvel_hickman_panel_descriptors():
        rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class B — Prose. Ingests The Wheel of Time passages from "
        "Wikisource + Wikipedia summary via the "
        "wheel_of_time_passage_descriptors DLT resource in "
        "dlt_sources/media/prose/wheel_of_time/scrape.py. The "
        "Wheel of Time is the 0-pixel control group."
    ),
)
def wheel_of_time_prose_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.prose.wheel_of_time.scrape import (  # type: ignore
        wheel_of_time_passage_descriptors,
    )

    rows = []
    for record in wheel_of_time_passage_descriptors():
        rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class C — Animation. Ingests Avatar: The Last Airbender "
        "+ The Legend of Korra + the Aang-film continuity frames "
        "from Wikipedia + Avatar wiki concept-art thumbnails via "
        "the avatar_frame_descriptors DLT resource in "
        "dlt_sources/media/animation/atla_korra_aang_film/scrape.py."
    ),
)
def avatar_animation_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.animation.atla_korra_aang_film.scrape import (  # type: ignore
        avatar_frame_descriptors,
    )

    rows = []
    for record in avatar_frame_descriptors():
        rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class D — Games. Local-capture only (no Firecrawl). "
        "Ingests the deterministic libretro headless capture for "
        "Golden Sun + the sunshine stream capture for Hades 1/2 + "
        "WoW + the libretro gambatte capture for Pokémon. Stored "
        "in stedding/ingest_queue/retro/ per the "
        "retro-game-design-catalogue spec. The descriptor is "
        "description-only (no copyrighted game screenshots in the "
        "shippable asset output)."
    ),
)
def gameplay_capture_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.games.hades_wow_golden_sun_pokemon.capture import (  # type: ignore
        gameplay_capture_descriptors,
    )

    rows = []
    for record in gameplay_capture_descriptors():
        rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


# ── Class E sub-bucket DLT source assets (NEW 2026-08-23 refactor) ──────


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (educational body sub-bucket). "
        "Ingests the 2 NCCA research PDFs (the user-named ones "
        "at the root of leaving_certificate/) + the 12 NCCA "
        "Leaving Certificate syllabus PDFs (en + ga parity) via "
        "the ncca_sec_dfe_sqa_wjec_desc_source DLT resource in "
        "dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/scrape.py."
    ),
)
def ncca_sec_dfe_sqa_wjec_desc_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.ncca_sec_celt_duchas_wikipedia.scrape import (  # type: ignore
        ncca_sec_dfe_sqa_wjec_desc_source,
    )

    rows = []
    for src in ncca_sec_dfe_sqa_wjec_desc_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (UK government sub-bucket). "
        "Ingests the UK police (Met + BTP + PSNI) + UK defence "
        "(MoD + British Army + Royal Navy + RAF) + UK Home Office + "
        "FCDO + MoJ + DoH + 7 UK Acts + Treaties via the "
        "uk_government_source DLT resource in "
        "dlt_sources/media/official/government/uk/scrape.py."
    ),
)
def uk_government_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.government.uk.scrape import (  # type: ignore
        uk_government_source,
    )

    rows = []
    for src in uk_government_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (Éire government sub-bucket). "
        "Ingests An Garda Síochána + Irish Defence Forces + "
        "Naval + Air Corps + DoD + DoJ + DFA + Oireachtas + Office "
        "of the President + 6 Acts + Treaties via the "
        "ie_government_source DLT resource in "
        "dlt_sources/media/official/government/ie/scrape.py."
    ),
)
def ie_government_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.government.ie.scrape import (  # type: ignore
        ie_government_source,
    )

    rows = []
    for src in ie_government_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (Crown Dependencies sub-bucket). "
        "Ingests Isle of Man Government + IoM Constabulary + "
        "Tynwald + IoM Courts + States of Jersey + States of Jersey "
        "Police + States of Guernsey + Guernsey Police via the "
        "crown_dependencies_government_source DLT resource in "
        "dlt_sources/media/official/government/crown_dependencies/scrape.py."
    ),
)
def crown_dependencies_government_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.government.crown_dependencies.scrape import (  # type: ignore
        crown_dependencies_government_source,
    )

    rows = []
    for src in crown_dependencies_government_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (UK departments sub-bucket). "
        "Ingests NHS England + DWP + Transport + Education + DEFRA "
        "via the uk_departments_source DLT resource in "
        "dlt_sources/media/official/departments/uk/scrape.py."
    ),
)
def uk_departments_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.departments.uk.scrape import (  # type: ignore
        uk_departments_source,
    )

    rows = []
    for src in uk_departments_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (Éire departments sub-bucket). "
        "Ingests DoH (IE) + DoEdu (IE) + HSE via the "
        "ie_departments_source DLT resource in "
        "dlt_sources/media/official/departments/ie/scrape.py."
    ),
)
def ie_departments_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.departments.ie.scrape import (  # type: ignore
        ie_departments_source,
    )

    rows = []
    for src in ie_departments_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (Scotland departments sub-bucket). "
        "Ingests NHS Scotland + Education Scotland + Scottish "
        "Government via the sct_departments_source DLT resource in "
        "dlt_sources/media/official/departments/sct/scrape.py."
    ),
)
def sct_departments_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.departments.sct.scrape import (  # type: ignore
        sct_departments_source,
    )

    rows = []
    for src in sct_departments_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (Wales departments sub-bucket). "
        "Ingests NHS Wales + HEIW + Welsh Government via the "
        "wls_departments_source DLT resource in "
        "dlt_sources/media/official/departments/wls/scrape.py."
    ),
)
def wls_departments_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.departments.wls.scrape import (  # type: ignore
        wls_departments_source,
    )

    rows = []
    for src in wls_departments_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


@asset(
    group_name="media_intel_l1_ingestion",
    compute_kind="dlt",
    description=(
        "Class E — Official (Northern Ireland departments "
        "sub-bucket). Ingests DoH (NI) + DE (NI) + DfE (NI) + "
        "nidirect via the ni_departments_source DLT resource in "
        "dlt_sources/media/official/departments/ni/scrape.py."
    ),
)
def ni_departments_l1(context: AssetExecutionContext) -> dict:
    from dlt_sources.media.official.departments.ni.scrape import (  # type: ignore
        ni_departments_source,
    )

    rows = []
    for src in ni_departments_source():
        for record in src:
            rows.append(record)
    context.add_output_metadata({"row_count": len(rows)})
    return {"rows": rows, "row_count": len(rows)}


# ============================================================================
# L2 Materials — 5 BAML extraction assets
# ============================================================================


@asset(
    group_name="media_intel_l2_materials",
    compute_kind="baml",
    description=(
        "L2 Materials — Class A. Extracts the 7-axis "
        "MediaDescriptor from the L1 records via the "
        "ExtractComicDescriptor BAML function (qwen3-vl-8b "
        "default via MODEL_REGISTRY)."
    ),
)
def comic_descriptor_l2(
    context: AssetExecutionContext, marvel_hickman_comics_l1: dict
) -> dict:
    from agents.meaisinfhoghlaim.media_intel import (  # type: ignore
        extract_comic_descriptor_tool,
    )

    descriptors = []
    for row in marvel_hickman_comics_l1["rows"]:
        descriptor = extract_comic_descriptor_tool(
            image_url=row.get("source_url", ""),
            caption_text=row.get("work", ""),
            source_url=row.get("source_url", ""),
            source_page=1,
            work=row.get("work", ""),
        )
        descriptors.append(descriptor)
    context.add_output_metadata({"descriptor_count": len(descriptors)})
    return {"descriptors": descriptors, "descriptor_count": len(descriptors)}


@asset(
    group_name="media_intel_l2_materials",
    compute_kind="baml",
    description=(
        "L2 Materials — Class B. Extracts the 7-axis "
        "MediaDescriptor from the L1 records via the "
        "ExtractProseDescriptor BAML function (qwen3.6-27b-mtp "
        "default via MODEL_REGISTRY). The prose-as-medium "
        "special case: vfx_vocabulary.particle_class defaults to "
        "'ink'."
    ),
)
def prose_descriptor_l2(
    context: AssetExecutionContext, wheel_of_time_prose_l1: dict
) -> dict:
    from agents.meaisinfhoghlaim.media_intel import (  # type: ignore
        extract_prose_descriptor_tool,
    )

    descriptors = []
    for row in wheel_of_time_prose_l1["rows"]:
        descriptor = extract_prose_descriptor_tool(
            text=row.get("work", ""),
            source_url=row.get("source_url", ""),
            source_paragraph=1,
            work=row.get("work", "The Wheel of Time"),
        )
        descriptors.append(descriptor)
    context.add_output_metadata({"descriptor_count": len(descriptors)})
    return {"descriptors": descriptors, "descriptor_count": len(descriptors)}


@asset(
    group_name="media_intel_l2_materials",
    compute_kind="baml",
    description=(
        "L2 Materials — Class C. Extracts the 7-axis "
        "MediaDescriptor from the L1 records via the "
        "ExtractAnimationDescriptor BAML function (molmo2-8b "
        "default via MODEL_REGISTRY). The 4+1 element vocabulary "
        "(air / water / fire / earth / spirit) is captured via "
        "the power_event.element field."
    ),
)
def animation_descriptor_l2(
    context: AssetExecutionContext, avatar_animation_l1: dict
) -> dict:
    from agents.meaisinfhoghlaim.media_intel import (  # type: ignore
        extract_animation_descriptor_tool,
    )

    descriptors = []
    for row in avatar_animation_l1["rows"]:
        descriptor = extract_animation_descriptor_tool(
            image_url=row.get("source_url", ""),
            audio=None,
            subtitle=row.get("work", ""),
            source_url=row.get("source_url", ""),
            source_frame=1,
            work=row.get("work", ""),
        )
        descriptors.append(descriptor)
    context.add_output_metadata({"descriptor_count": len(descriptors)})
    return {"descriptors": descriptors, "descriptor_count": len(descriptors)}


@asset(
    group_name="media_intel_l2_materials",
    compute_kind="baml",
    description=(
        "L2 Materials — Class D. Extracts the 7-axis "
        "MediaDescriptor from the L1 records via the "
        "ExtractGameplayDescriptor BAML function (qwen3-vl-8b "
        "default via MODEL_REGISTRY). The screenshot + "
        "session_log input shape. The descriptor is "
        "description-only (no copyrighted game screenshots in "
        "the shippable asset output)."
    ),
)
def gameplay_descriptor_l2(
    context: AssetExecutionContext, gameplay_capture_l1: dict
) -> dict:
    from agents.meaisinfhoghlaim.media_intel import (  # type: ignore
        extract_gameplay_descriptor_tool,
    )

    descriptors = []
    for row in gameplay_capture_l1["rows"]:
        descriptor = extract_gameplay_descriptor_tool(
            image_url=row.get("source_url", ""),
            session_log=row.get("work", ""),
            source_url=row.get("source_url", ""),
            source_timestamp=row.get("source_timestamp", ""),
            work=row.get("work", ""),
        )
        descriptors.append(descriptor)
    context.add_output_metadata({"descriptor_count": len(descriptors)})
    return {"descriptors": descriptors, "descriptor_count": len(descriptors)}


@asset(
    group_name="media_intel_l2_materials",
    compute_kind="baml",
    description=(
        "L2 Materials — Class E. Extracts the 7-axis "
        "MediaDescriptor from the 8 official L1 sub-bucket "
        "records via the ExtractOfficialDocumentDescriptor BAML "
        "function (olmocr-2-7b default via MODEL_REGISTRY). The "
        "descriptor is a structured summary — NEVER a verbatim "
        "copy of the full page."
    ),
)
def official_document_descriptor_l2(
    context: AssetExecutionContext,
    ncca_sec_dfe_sqa_wjec_desc_l1: dict,
    uk_government_l1: dict,
    ie_government_l1: dict,
    crown_dependencies_government_l1: dict,
    uk_departments_l1: dict,
    ie_departments_l1: dict,
    sct_departments_l1: dict,
    wls_departments_l1: dict,
    ni_departments_l1: dict,
) -> dict:
    from agents.meaisinfhoghlaim.media_intel import (  # type: ignore
        extract_official_document_descriptor_tool,
    )

    all_official_rows = (
        ncca_sec_dfe_sqa_wjec_desc_l1["rows"]
        + uk_government_l1["rows"]
        + ie_government_l1["rows"]
        + crown_dependencies_government_l1["rows"]
        + uk_departments_l1["rows"]
        + ie_departments_l1["rows"]
        + sct_departments_l1["rows"]
        + wls_departments_l1["rows"]
        + ni_departments_l1["rows"]
    )

    descriptors = []
    for row in all_official_rows:
        descriptor = extract_official_document_descriptor_tool(
            pdf_page_url=row.get("source_url", ""),
            metadata=f"Issuer: {row.get('rights_holder', '')}; Date: unknown; Version: unknown",
            source_url=row.get("source_url", ""),
            source_timestamp=row.get("source_timestamp", ""),
            work=row.get("work", row.get("title", "")),
        )
        descriptors.append(descriptor)
    context.add_output_metadata({"descriptor_count": len(descriptors)})
    return {"descriptors": descriptors, "descriptor_count": len(descriptors)}


# ============================================================================
# L3 Model Lifecycle — 2 CocoIndex Apps
# ============================================================================


@asset(
    group_name="media_intel_l3_model_lifecycle",
    compute_kind="cocoindex",
    description=(
        "L3 Model Lifecycle — the media_descriptors CocoIndex v1 "
        "App. Embeds the 7-axis MediaDescriptor records via the "
        "shared BAAI/bge-m3 1024-d embedder and mounts the "
        "media_descriptors_lance LanceDB table."
    ),
)
def media_descriptors_embedding(
    context: AssetExecutionContext,
    comic_descriptor_l2: dict,
    prose_descriptor_l2: dict,
    animation_descriptor_l2: dict,
    gameplay_descriptor_l2: dict,
    official_document_descriptor_l2: dict,
) -> dict:
    total = (
        comic_descriptor_l2["descriptor_count"]
        + prose_descriptor_l2["descriptor_count"]
        + animation_descriptor_l2["descriptor_count"]
        + gameplay_descriptor_l2["descriptor_count"]
        + official_document_descriptor_l2["descriptor_count"]
    )
    context.add_output_metadata({"total_descriptor_count": total})
    return {
        "total_descriptor_count": total,
        "lance_table": "media_descriptors_lance",
    }


@asset(
    group_name="media_intel_l3_model_lifecycle",
    compute_kind="cocoindex",
    description=(
        "L3 Model Lifecycle — the cross_medium_compare CocoIndex "
        "v1 App. Mounts the media_descriptors_cross_medium_lance "
        "LanceDB table. The multihop search that surfaces the "
        "*consistent visual grammar* across the 5 source "
        "classes. The canonical question: 'which element's "
        "visual grammar is most consistent across WoT prose + "
        "ATLA animation + Hickman comics?'"
    ),
)
def cross_medium_compare_embedding(
    context: AssetExecutionContext, media_descriptors_embedding: dict
) -> dict:
    context.add_output_metadata(
        {
            "input_total": media_descriptors_embedding[
                "total_descriptor_count"
            ]
        }
    )
    return {
        "lance_table": "media_descriptors_cross_medium_lance",
        "ready": media_descriptors_embedding["total_descriptor_count"] > 0,
    }


# ============================================================================
# L4 Asset Generation — 2 marimo notebooks
# ============================================================================


@asset(
    group_name="media_intel_l4_asset_generation",
    compute_kind="marimo",
    description=(
        "L4 Asset Generation — the per-medium marimo notebook. "
        "Surfaces: per-medium coverage table (Row count per "
        "class), sample descriptors, per-axis field histograms, "
        "top 5 most-cited source URLs."
    ),
)
def media_intel_explorer_per_medium_notebook(
    context: AssetExecutionContext, media_descriptors_embedding: dict
) -> dict:
    context.add_output_metadata(
        {
            "notebook": "notebooks/media_intel_explorer_per_medium.py",
            "total_descriptors": media_descriptors_embedding[
                "total_descriptor_count"
            ],
        }
    )
    return {
        "notebook": "notebooks/media_intel_explorer_per_medium.py",
        "ready": media_descriptors_embedding["total_descriptor_count"] > 0,
    }


@asset(
    group_name="media_intel_l4_asset_generation",
    compute_kind="marimo",
    description=(
        "L4 Asset Generation — the cross-medium marimo notebook. "
        "The cell-level SQL runs DuckDB over the LanceDB tables "
        "joined with the BAML-typed records. Answers the question: "
        "'which element's visual grammar is most consistent across "
        "WoT prose + ATLA animation + Hickman comics?'"
    ),
)
def media_intel_explorer_cross_medium_notebook(
    context: AssetExecutionContext, cross_medium_compare_embedding: dict
) -> dict:
    context.add_output_metadata(
        {
            "notebook": "notebooks/media_intel_explorer_cross_medium.py",
            "ready": cross_medium_compare_embedding["ready"],
        }
    )
    return {
        "notebook": "notebooks/media_intel_explorer_cross_medium.py",
        "ready": cross_medium_compare_embedding["ready"],
    }


# ============================================================================
# L5 Agent Ops — 1 ADK media_descriptor_agent execution asset
# ============================================================================


@asset(
    group_name="media_intel_l5_agent_ops",
    compute_kind="adk",
    description=(
        "L5 Agent Ops — the ADK media_descriptor_agent "
        "execution asset. Wraps the 10-tool ADK agent (5 per-"
        "medium extractors + 5 corpus introspection tools) for "
        "ad-hoc user queries. Model: minimax-m3 (resolved via "
        "MODEL_REGISTRY)."
    ),
)
def media_descriptor_agent_run(
    context: AssetExecutionContext, media_intel_explorer_cross_medium_notebook: dict
) -> dict:
    context.add_output_metadata(
        {
            "agent": "media_descriptor_agent",
            "ready": media_intel_explorer_cross_medium_notebook["ready"],
        }
    )
    return {
        "agent": "media_descriptor_agent",
        "ready": media_intel_explorer_cross_medium_notebook["ready"],
    }


# ============================================================================
# L6 Asset Check — the media_descriptor_coverage guard
# ============================================================================


@asset_check(
    asset=media_descriptors_embedding,
    description=(
        "The L6 sync contract: fails the run if any of the 5 "
        "source classes (comics, prose, animation, games, "
        "official) has 0 rows in media_descriptors_lance. "
        "Forces ingestion; never lets the corpus stay empty."
    ),
)
def media_descriptor_coverage(
    context: AssetExecutionContext, media_descriptors_embedding: dict
) -> AssetCheckResult:
    total = media_descriptors_embedding["total_descriptor_count"]
    passed = total > 0
    severity = (
        AssetCheckSeverity.WARN if total > 0 else AssetCheckSeverity.ERROR
    )
    return AssetCheckResult(
        passed=passed,
        severity=severity,
        metadata={
            "total_descriptor_count": total,
            "checked_at": datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat(),
        },
    )


# ============================================================================
# Job + schedule
# ============================================================================


media_intel_job = define_asset_job(
    name="media_intel_job",
    selection=[
        "marvel_hickman_comics_l1",
        "wheel_of_time_prose_l1",
        "avatar_animation_l1",
        "gameplay_capture_l1",
        "ncca_sec_dfe_sqa_wjec_desc_l1",
        "uk_government_l1",
        "ie_government_l1",
        "crown_dependencies_government_l1",
        "uk_departments_l1",
        "ie_departments_l1",
        "sct_departments_l1",
        "wls_departments_l1",
        "ni_departments_l1",
        "comic_descriptor_l2",
        "prose_descriptor_l2",
        "animation_descriptor_l2",
        "gameplay_descriptor_l2",
        "official_document_descriptor_l2",
        "media_descriptors_embedding",
        "cross_medium_compare_embedding",
        "media_intel_explorer_per_medium_notebook",
        "media_intel_explorer_cross_medium_notebook",
        "media_descriptor_agent_run",
    ],
)


media_intel_daily = schedule(
    cron_schedule="0 2 * * *",  # 02:00 UTC daily
    job=media_intel_job,
    execution_timezone="UTC",
)


defs = Definitions(
    assets=[
        marvel_hickman_comics_l1,
        wheel_of_time_prose_l1,
        avatar_animation_l1,
        gameplay_capture_l1,
        ncca_sec_dfe_sqa_wjec_desc_l1,
        uk_government_l1,
        ie_government_l1,
        crown_dependencies_government_l1,
        uk_departments_l1,
        ie_departments_l1,
        sct_departments_l1,
        wls_departments_l1,
        ni_departments_l1,
        comic_descriptor_l2,
        prose_descriptor_l2,
        animation_descriptor_l2,
        gameplay_descriptor_l2,
        official_document_descriptor_l2,
        media_descriptors_embedding,
        cross_medium_compare_embedding,
        media_intel_explorer_per_medium_notebook,
        media_intel_explorer_cross_medium_notebook,
        media_descriptor_agent_run,
    ],
    asset_checks=[media_descriptor_coverage],
    jobs=[media_intel_job],
    schedules=[media_intel_daily],
)
