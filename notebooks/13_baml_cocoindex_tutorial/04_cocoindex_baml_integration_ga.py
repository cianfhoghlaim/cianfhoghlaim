# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 4 (Gaeilge): The 3 CocoIndex+BAML integration patterns on GA content.

Companion to `04_cocoindex_baml_integration.py`. Demonstrates the
Gaeilge (Irish) language path through the same 3 CocoIndex+BAML
integration patterns:

1. `upstream_api_surface` — `ExtractCocoIndexApiChange` (the API
   changelog monitor for cocoindex / dlthub / motherduck / lancedb)
2. `upstream_blog_monitor` — `ExtractBlogPostMetadata` (the blog
   post monitor for upstream package blogs)
3. `docs_skills_consolidation` — `ExtractDocSkillTag` + `ExtractTriples`
   (the docs/skills knowledge graph builder)

The GA counterpart focuses on the **3 patterns applied to GA
content**:
- Pattern 1: extract GA-language API changelog entries
- Pattern 2: extract GA-language blog post metadata
- Pattern 3: extract GA-language doc/skill tags + triples

**GA-specific patterns:**
- Pattern 1 demo: a `BilingualText` extraction of a `cocoindex`
  changelog entry that has both EN + GA release notes
- Pattern 2 demo: extracting metadata from a `dlthub` blog post
  that was authored in Irish (the GA agent's canonical output)
- Pattern 3 demo: a tag like `gaeilge-extraction` + a triple like
  `(ExtractBilingualText, uses, BilingualText)` from the Gaeilge
  skill graph

Cross-references:
- `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1 skill router
- `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
- `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/` —
  this openspec change

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/04_cocoindex_baml_integration_ga
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/04_cocoindex_baml_integration_ga
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
    # Tutorial 4 (GA) — The 3 CocoIndex+BAML integration patterns on GA content

    The GA counterpart of Tutorial 4. Exercises the same 3 CocoIndex+BAML
    integration patterns (`upstream_api_surface`, `upstream_blog_monitor`,
    `docs_skills_consolidation`) but applies them to **Gaeilge content**.

    **What you'll learn:**
    1. The lazy-import pattern (same as English) + the bilingual
       `ExtractBilingualText` call inside the `@coco.fn` decorator
    2. The `BAML_CLIENT_*` ContextKey (same R2-exempt comment)
    3. The `coco.use_context(BAML_CLIENT_*)` provider + the bilingual
       extraction call
    4. The fallback-stub pattern with a bilingual `BilingualText` stub row
    """
    )
    return


@app.cell
def _section_pattern1_lazy_import(mo):
    mo.md(
        """
    ## 1. Pattern 1 — `upstream_api_surface` on GA API changelogs

    The `upstream_api_surface` CocoIndex App runs the
    `ExtractCocoIndexApiChange` BAML function on every changelog entry.
    For the GA path, the input chunk is a bilingual EN+GA release-note
    and the function is `ExtractBilingualText` (which returns the
    canonical `BilingualText` shape).

    ### Lazy-import pattern (same as English):

    ```python
    async def _provide_baml_client(builder: coco.AppBuilder) -> None:
        try:
            from baml_client.sync_client import b as baml_sync
            builder.provide(BAML_CLIENT_UPSTREAM, baml_sync)
        except ImportError:
            logger.warning("baml_client_not_available_skipping_extraction")
            builder.provide(BAML_CLIENT_UPSTREAM, None)
    ```

    ### GA-specific `@coco.fn` body:

    ```python
    @coco.fn(memo=True)
    async def extract_cocoindex_api_chunk_ga(chunk: ChangeChunk) -> Row:
        baml_sync = coco.use_context(BAML_CLIENT_UPSTREAM)
        if baml_sync is None:
            return Row(
                url=chunk.url,
                severity="UNKNOWN",
                language="ga",
                error="baml_client_not_available",
            )
        # Bilingual extraction — returns BilingualText
        bilingual = baml_sync.ExtractBilingualText(content=chunk.text)
        # Also extract the EN/GA structured change metadata
        change_en = baml_sync.ExtractCocoIndexApiChange(chunk_text=bilingual.text_en or "")
        change_ga = baml_sync.ExtractCocoIndexApiChange(chunk_text=bilingual.text_ga or "")
        return Row(
            url=chunk.url,
            severity=change_en.severity,  # canonical: EN
            description_en=change_en.description,
            description_ga=change_ga.description,
        )
    ```
    """
    )
    return


@app.cell
def _section_pattern2_blog(mo):
    mo.md(
        """
    ## 2. Pattern 2 — `upstream_blog_monitor` on GA blog posts

    The `upstream_blog_monitor` CocoIndex App runs
    `ExtractBlogPostMetadata` on every blog post payload from the
    Firecrawl monitor. For the GA path, the blog post was authored in
    Irish (the GA agent's canonical output) and the function returns
    metadata with both EN + GA title + summary.

    ### ContextKey (R2-exempt):

    ```python
    # R2-exempt: BAML_CLIENT_BLOG is the pre-initialised BAML client
    # for the `upstream_monitoring.baml` schema.
    BAML_CLIENT_BLOG = coco.ContextKey[Any](
        "oideachais_baml_client_blog"
    )
    ```

    ### GA-specific `@coco.fn` body:

    ```python
    @coco.fn(memo=True)
    async def extract_blog_post_ga(post: BlogPostPayload) -> Row:
        baml_sync = coco.use_context(BAML_CLIENT_BLOG)
        if baml_sync is None:
            return Row(
                post_url=post.url,
                title_en=None,
                title_ga=None,
                error="baml_client_not_available",
            )
        # Extract bilingual metadata (title + summary + tags)
        meta_en = baml_sync.ExtractBlogPostMetadata(post_text=post.text_en)
        meta_ga = baml_sync.ExtractBlogPostMetadata(post_text=post.text_ga)
        return Row(
            post_url=post.url,
            title_en=meta_en.title,
            title_ga=meta_ga.title,
            summary_en=meta_en.summary,
            summary_ga=meta_ga.summary,
            tags=list(set(meta_en.tags + meta_ga.tags)),
        )
    ```
    """
    )
    return


@app.cell
def _section_pattern3_docs_skills(mo):
    mo.md(
        """
    ## 3. Pattern 3 — `docs_skills_consolidation` on GA docs/skills

    The `docs_skills_consolidation` CocoIndex App runs both
    `ExtractDocSkillTag` AND `ExtractTriples` on every doc chunk.
    For the GA path, the doc chunk is an Irish-language skill or
    documentation page, and the tag set includes GA-specific tags
    (`gaeilge-extraction`, `bilingual-content`, `extract-strand-ga`,
    etc.).

    ### GA-specific `@coco.fn` body:

    ```python
    @coco.fn(memo=True)
    async def extract_doc_skill_tag_ga(doc: DocChunk) -> Row:
        baml_sync = coco.use_context(BAML_CLIENT_DOCS_SKILLS)
        if baml_sync is None:
            return Row(
                doc_id=doc.doc_id,
                language="ga",
                tags=[],
                triples=[],
                error="baml_client_not_available",
            )
        tags = baml_sync.ExtractDocSkillTag(chunk_text=doc.text)
        triples = baml_sync.ExtractTriples(chunk_text=doc.text)
        # Tag the GA-specific triples for downstream filter
        ga_triples = [
            (t.subject, t.predicate, t.object)
            for t in triples.triples
            if "ExtractGael" in t.subject or "ExtractBilingualText" in t.subject
        ]
        return Row(
            doc_id=doc.doc_id,
            language="ga",
            tags=tags.tags,
            triples=ga_triples,
        )
    ```

    **GA-specific output:** the `ga_triples` filter pulls out triples
    whose subject is a Gaeilge-specific BAML function (e.g.
    `(ExtractGaelGaStatement, returns, string[])` or
    `(ExtractBilingualText, uses, BilingualText)`). These triples
    feed into the `docs_skills_graph` FalkorDB graph and the
    `oideachais.gaeilge_skill_graph` LanceDB HNSW index.
    """
    )
    return


@app.cell
def _section_fallback_stub(mo):
    mo.md(
        """
    ## 4. The fallback-stub pattern (bilingual)

    Same `try / except ImportError` graceful-degradation as the English
    pattern, but the stub row carries the bilingual shape:

    ```python
    @coco.fn(memo=True)
    async def extract_doc_skill_tag_ga(doc: DocChunk) -> Row:
        baml_sync = coco.use_context(BAML_CLIENT_DOCS_SKILLS)
        if baml_sync is None:
            return Row(
                doc_id=doc.doc_id,
                language="ga",
                tags=[],
                triples=[],
                text_en=None,
                text_ga=None,
                error="baml_client_not_available",
            )
        # ... (real extraction path as above)
    ```

    The `language: "ga"` field is the discriminant that downstream
    consumers use to filter GA-only rows.
    """
    )
    return


@app.cell
def _section_outro(mo):
    mo.md(
        """
    ## Next steps

    - **Tutorial 5 (GA)** — `05_post_v4_duplicate_audit_and_migration_ga.py`
      audits the bilingual BAML additions in the same way as the English
      audit notebook

    For the canonical English-language walkthrough of all 3 apps, see
    `04_cocoindex_baml_integration.py`.
    """
    )
    return


if __name__ == "__main__":
    app.run()