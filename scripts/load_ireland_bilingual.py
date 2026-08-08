"""Land the Ireland bilingual layer (téarma.ie + gaois.ie/logainm.ie) into
the local DuckLake bronze layer.

Per the local-lakehouse plan's Phase 5
(/Users/cianmacandeisigh/.claude/plans/after-recent-plans-and-enumerated-cosmos.md):
run the real, HTTP-backed sources in dlt_sources/language/ that most
directly serve the "Irish" (language, not just jurisdiction) priority —
tearma_source() (Foras na Gaeilge's official EN<->GA terminology bulk
export) and gaois_combined_source() (logainm.ie/ainm.ie/tearma.ie
combined via the GAOIS research-group APIs).

This also required fixing dlt_sources/language/__init__.py, which
imported from a package (dlt_sources.british_isles.ireland.culture) that
does not exist anywhere in the repo — a dormant, repo-wide-breaking bug
(the entire dlt_sources.language package, all 19 sources, was
unimportable) predating this session, unrelated to but discovered while
executing this plan.

Run: mise exec -- .venv/bin/python3 scripts/load_ireland_bilingual.py
"""

from __future__ import annotations

import dlt

from dlt_sources.language.tearma import tearma_source
from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

# gaois_combined_source() has a real dlt resource-reuse bug beyond what was
# fixed in this pass (missing imports + a wrong max_terms kwarg, both
# fixed) — it yields already-instantiated resources from 3 other
# @dlt.source-decorated functions (logainm_source/tearma_source/
# ainm_source), and dlt raises "Parametrized resource `placenames` is not
# callable" when one of those gets iterated a second time internally.
# Flagged as a follow-up, not fixed here — tearma_source() alone (the
# plan's stated priority for the Irish-language layer) is proven working
# and is what this script lands.


def main() -> int:
    pipeline = dlt.pipeline(
        pipeline_name="ireland_bilingual",
        destination=get_dlt_destination(use_ducklake=True),
        dataset_name="cianfhoghlaim.bronze.ireland_bilingual",
    )
    load_info = pipeline.run(tearma_source())
    print("=== tearma_source ===")
    print(load_info)

    with pipeline.sql_client() as client:
        for table in ("tearma_terms", "tearma_education"):
            try:
                (n,) = next(iter(client.execute_sql(f"SELECT COUNT(*) FROM {table}")))
                print(f"{table}: {n} rows")
            except Exception as e:
                print(f"{table}: (no table — {e})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
