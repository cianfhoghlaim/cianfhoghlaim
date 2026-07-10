# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 4: The 3 real CocoIndex+BAML integration patterns.

Walks through the 3 v1 CocoIndex Apps that integrate with BAML:

1. `upstream_api_surface` — `ExtractCocoIndexApiChange` (the API
   changelog monitor for cocoindex / dlthub / motherduck / lancedb)
2. `upstream_blog_monitor` — `ExtractBlogPostMetadata` (the blog
   post monitor for upstream package blogs)
3. `docs_skills_consolidation` — `ExtractDocSkillTag` + `ExtractTriples`
   (the docs/skills knowledge graph builder, using
   `baml/processing/docs_skills_extraction.baml` shipped in commit
   `93df30ebb`)

Demonstrates:
- The lazy-import pattern (`from baml_client.sync_client import b as baml_sync`)
- The `coco.use_context(BAML_CLIENT_UPSTREAM)` provider
- The fallback-stub for when BAML isn't generated
- The `try / except ImportError` graceful-degradation pattern

Source of truth:
- `cianfhoghlaim/cocoindex/upstream_api_surface.py`
- `cianfhoghlaim/cocoindex/upstream_blog_monitor.py`
- `cianfhoghlaim/cocoindex/docs_skills_consolidation.py`
- `cianfhoghlaim/baml/processing/docs_skills_extraction.baml` (the
  `ExtractDocSkillTag` + `ExtractTriples` BAML source, created in
  commit `93df30ebb`)

Cross-references:
- `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1 skill router
- `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
- `openspec/specs/upstream-package-monitoring/spec.md`
- `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/`

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/04_cocoindex_baml_integration
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/04_cocoindex_baml_integration
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
    # Tutorial 4 — The 3 real CocoIndex+BAML integration patterns

    The Cianfhoghlaim platform has 3 v1 CocoIndex Apps that integrate
    with BAML (per the 4-rule R1+R2+R3+R4 v1 conformance contract; see
    `.agents/skills/cocoindex/SKILL.md`):

    | App | BAML function | Purpose |
    |:--|:--|:--|
    | `upstream_api_surface` | `ExtractCocoIndexApiChange` | Watches cocoindex / dlthub / motherduck / lancedb changelogs |
    | `upstream_blog_monitor` | `ExtractBlogPostMetadata` | Watches upstream package blogs |
    | `docs_skills_consolidation` | `ExtractDocSkillTag` + `ExtractTriples` | Builds the docs/skills knowledge graph |

    All 3 follow the **same 4-step pattern**:
    1. Declare `BAML_CLIENT_<name>` as a `coco.ContextKey` (R2-exempt)
    2. Lazy-import `baml_sync` inside the lifespan builder
    3. Use `coco.use_context(BAML_CLIENT_<name>)` to fetch the
       per-app client inside the `@coco.fn` decorator
    4. Emit the extraction result to LanceDB + FalkorDB
    """
    )
    return


@app.cell
def _section_lazy_import(mo):
    mo.md(
        """
    ## 1. The lazy-import pattern (graceful-degradation)

    All 3 apps lazy-import the BAML sync client inside the lifespan
    builder, with a `try / except ImportError` fallback. This lets
    the apps be imported (and AST-parsed) even when the baml-py
    client hasn't been generated yet (e.g. in CI before
    `baml-cli generate` runs).

    ### Pattern (from `upstream_api_surface.py` lines 158-170):

    ```python
    async def _provide_baml_client(builder: coco.AppBuilder) -> None:
        try:
            from baml_client.sync_client import b as baml_sync
            builder.provide(BAML_CLIENT_UPSTREAM, baml_sync)
        except ImportError:
            logger.warning("baml_client_not_available_skipping_extraction")
            builder.provide(BAML_CLIENT_UPSTREAM, None)
    ```
    """
    )
    return


@app.cell
def _section_context_key(mo):
    mo.md(
        """
    ## 2. The `BAML_CLIENT_*` ContextKey (R2-exempt)

    Each app declares a `BAML_CLIENT_<name>` `coco.ContextKey` as an
    **R2-exempt** additional key. The exemption comment is mandatory
    (per the v1 conformance contract R2):

    ### Pattern (from `upstream_api_surface.py` lines 138-145):

    ```python
    # R2-exempt: BAML_CLIENT_UPSTREAM is the pre-initialised BAML
    # client for the `upstream_monitoring.baml` schema. Pre-init
    # avoids re-generating the client on every CocoIndex run.
    BAML_CLIENT_UPSTREAM = coco.ContextKey[Any](
        "oideachais_baml_client_upstream"
    )
    ```

    The 3 apps declare:
    - `BAML_CLIENT_UPSTREAM` (in `upstream_api_surface.py`)
    - `BAML_CLIENT_BLOG` (in `upstream_blog_monitor.py`)
    - `BAML_CLIENT_DOCS_SKILLS` (in `docs_skills_consolidation.py`)
    """
    )
    return


@app.cell
def _section_use_context(mo):
    mo.md(
        """
    ## 3. The `coco.use_context(BAML_CLIENT_*)` provider

    Inside the `@coco.fn(memo=True)` decorator, the BAML client is
    fetched via `coco.use_context(...)`. If the client is `None`
    (the graceful-degradation case), the function emits a stub row
    and returns:

    ### Pattern (from `upstream_api_surface.py` lines 207-225):

    ```python
    @coco.fn(memo=True)
    async def extract_cocoindex_api_chunk(chunk: ChangeChunk) -> Row:
        baml_sync = coco.use_context(BAML_CLIENT_UPSTREAM)
        if baml_sync is None:
            return Row(
                url=chunk.url,
                severity="UNKNOWN",
                error="baml_client_not_available",
            )
        change = baml_sync.ExtractCocoIndexApiChange(chunk_text=chunk.text)
        return Row(
            url=chunk.url,
            severity=change.severity,
            description=change.description,
        )
    ```
    """
    )
    return


@app.cell
def _section_apps(mo):
    mo.md(
        """
    ## 4. The 3 apps in detail

    ### 4.1 `upstream_api_surface` — `ExtractCocoIndexApiChange`

    - **BAML source:** `baml/processing/upstream_monitoring.baml`
      (the `ExtractCocoIndexApiChange` function)
    - **LanceDB target:** `upstream_api_chunks` (HNSW on `embedding`)
    - **FalkorDB target:** `upstream_packages_graph` (nodes +
      `api_change_edge` edges)
    - **Trigger:** Firecrawl monitor (daily check) +
      `upstream_breaking_change_sensor` Dagster sensor (polls the
      graph and fires Slack alerts on `severity="BREAKING"`)
    - **Cost:** ~50 changelog entries/day × ~2K tokens = 100K tokens/day

    ### 4.2 `upstream_blog_monitor` — `ExtractBlogPostMetadata`

    - **BAML source:** `baml/processing/upstream_monitoring.baml`
      (the `ExtractBlogPostMetadata` function)
    - **LanceDB target:** `upstream_blog_chunks` (HNSW on `embedding`)
    - **FalkorDB target:** `upstream_packages_graph` (nodes +
      `blog_post_edge` edges)
    - **Trigger:** n8n workflow `upstream-blog-monitor.json`
      forwards Firecrawl `monitor.page` webhook payloads to a local
      mirror at `${OIDEACHAIS_UPSTREAM_PAYLOADS_ROOT:-stedding/upstream_blog_payloads/}`
    - **Cost:** ~20 blog posts/day × ~3K tokens = 60K tokens/day

    ### 4.3 `docs_skills_consolidation` — `ExtractDocSkillTag` + `ExtractTriples`

    - **BAML source:** `baml/processing/docs_skills_extraction.baml`
      (the `ExtractDocSkillTag` + `ExtractTriples` functions, created
      in commit `93df30ebb` per the `2026-07-11-baml-cocoindex-modernization-v1`
      Phase A3)
    - **LanceDB target:** `docs_skills_chunks` (HNSW on `embedding`)
    - **FalkorDB target:** `docs_skills_graph` (tag nodes +
      `tagged_with` edges + `Triple` edges)
    - **Trigger:** scheduled CocoIndex run (daily at 02:00 UTC)
    - **Cost:** ~150 docs × ~1.5K tokens = 225K tokens/day
    """
    )
    return


@app.cell
def _section_fallback(mo):
    mo.md(
        """
    ## 5. The fallback-stub pattern (when BAML isn't generated)

    The 3 apps handle the case where `baml_client` isn't importable
    (e.g. before `baml-cli generate` runs, or in CI without the
    generated client):

    ```python
    try:
        from baml_client.sync_client import b as baml_sync
        builder.provide(BAML_CLIENT_DOCS_SKILLS, baml_sync)
    except ImportError:
        logger.warning("baml_client_not_available_skipping_extraction")
        builder.provide(BAML_CLIENT_DOCS_SKILLS, None)
    ```

    And inside the `@coco.fn`:

    ```python
    @coco.fn(memo=True)
    async def extract_doc_skill_tag(doc: DocChunk) -> Row:
        baml_sync = coco.use_context(BAML_CLIENT_DOCS_SKILLS)
        if baml_sync is None:
            return Row(
                doc_id=doc.doc_id,
                tags=[],
                triples=[],
                error="baml_client_not_available",
            )
        tags = baml_sync.ExtractDocSkillTag(chunk_text=doc.text)
        triples = baml_sync.ExtractTriples(chunk_text=doc.text)
        return Row(
            doc_id=doc.doc_id,
            tags=tags.tags,
            triples=[(t.subject, t.predicate, t.object) for t in triples.triples],
        )
    ```

    **This pattern lets the 3 apps be deployed to CI (where
    `baml-py` may not be installed) AND to production (where it is).**
    """
    )
    return


@app.cell
def _section_smoke(mo):
    mo.md(
        """
    ## 6. Smoke-test the 3 CocoIndex+BAML apps

    ```bash
    cd cianfhoghlaim
    uv run python -c "
    # Verify the 3 apps import + declare the right ContextKeys
    from cianfhoghlaim.cocoindex import (
        upstream_api_surface,
        upstream_blog_monitor,
        docs_skills_consolidation,
    )
    print('BAML_CLIENT_UPSTREAM:', upstream_api_surface.BAML_CLIENT_UPSTREAM)
    print('BAML_CLIENT_BLOG:', upstream_blog_monitor.BAML_CLIENT_BLOG)
    print('BAML_CLIENT_DOCS_SKILLS:', docs_skills_consolidation.BAML_CLIENT_DOCS_SKILLS)
    "
    ```

    **Expected:** all 3 ContextKeys are exported. If `baml-py` is not
    installed, the lifespan builder logs a warning and provides `None`
    for each key (the apps still run, but the extraction is a stub).
    """
    )
    return


@app.cell
def _next_steps(mo):
    mo.md(
        """
    ## Next steps

    - See `05_post_v4_duplicate_audit_and_migration.py` for the
      interactive 42-renames audit notebook
    - See Tutorial 3 for the side-by-side vision model comparison
    - See Tutorial 1 §4 for the `image` first-class type syntax

    **Cross-references:**
    - `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1 skill
      router (the 4-rule R1+R2+R3+R4 conformance contract)
    - `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
    - `openspec/specs/upstream-package-monitoring/spec.md` — the
      upstream package monitoring capability spec
    - `openspec/specs/british-isles-education-pipeline/spec.md` — the
      6 LC priority subjects pipeline (uses the 3 apps)
    - `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`
      — this tutorial track's parent capability spec
    """
    )
    return


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run the tutorial as a CLI script from any cwd."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="04_cocoindex_baml_integration.py",
        description=__doc__,
    )
    parser.add_argument(
        "--app",
        type=str,
        choices=[
            "upstream_api_surface",
            "upstream_blog_monitor",
            "docs_skills_consolidation",
            "all",
        ],
        default="all",
        help="Which CocoIndex+BAML app to walk through (default: all 3)",
    )
    args = parser.parse_args(argv)
    print("[04_cocoindex_baml_integration] Tutorial 4 — CocoIndex+BAML integration")
    print(f"  App: {args.app}")
    print("  3 real patterns: upstream_api_surface, upstream_blog_monitor,")
    print("                   docs_skills_consolidation")
    print("  Key concepts: lazy-import, ContextKey, use_context, fallback-stub")
    print("  Run: uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/04_cocoindex_baml_integration")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
