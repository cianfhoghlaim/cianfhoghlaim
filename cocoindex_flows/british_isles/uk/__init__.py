"""cocoindex_flows.british_isles.uk — ciancheiltis umbrella CocoIndex App home.

Phase 1 of the ciancheiltis umbrella (Wales / en-cy). This package
houses the CocoIndex v1 App that embeds bilingual en-cy government
pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks``.

The R1-R4 conformance contract (per the
``oideachais-cocoindex-v1`` skill + the
``openspec/specs/ciancheiltis/spec.md`` R1-R4 section) is enforced by
``orchestration/components/layer3_model_lifecycle.py:_check_module_r1_to_r4``.
Every App in this sub-tree MUST:

- **R1** — import ``from ._lifespan import shared_lifespan`` (this file's sibling)
- **R2** — import the canonical ``ContextKey``s (``LANCE_DB``, ``EMBEDDER``,
  ``RESOLVED_FILE_REGISTRY``) from ``._lifespan``
- **R3** — declare ``coco.App(...)`` at module scope + wrap every flow as
  ``@coco.fn(memo=True, deps=[...])``
- **R4** — mount each LanceDB table via
  ``lancedb.mount_table_target(..., conformance_required=True)``

The shared embedder is ``BAAI/bge-m3`` (1024-d, multilingual — supports
CY/GA/GD/GV per the umbrella spec § R2).

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/``.
"""
