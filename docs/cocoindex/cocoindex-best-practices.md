# CocoIndex Best Practices for Cianfhoghlaim/Tuath

> Synthesised from `cocoindex-code-mcp-server/` (56 internal docs) and the canonical CocoIndex examples in `cocoindex/examples/`. This is the **operational** summary for our projects; the source material remains in `cocoindex-code-mcp-server/` for deep dives.

Last synthesised: 2026-06-14

---

## 1. Dataflow model

CocoIndex is a **declarative dataflow** framework. You define transformations as a DAG using Python decorators; the system tracks lineage and incremental recomputation.

```python
import cocoindex

@cocoindex.flow_def(name="DocumentsToEmbeddings")
def documents_to_embeddings_flow(flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope):
    # 1. Source
    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(path="docs/")
    )

    # 2. Transform (chunk → embed)
    data_scope["chunks"] = data_scope["documents"].transform(
        cocoindex.functions.SplitRecursively(...),
        language="markdown"
    )
    data_scope["embeddings"] = data_scope["chunks"].transform(
        cocoindex.functions.SentenceTransformerEmbed(model="sentence-transformers/all-MiniLM-L6-v2")
    )

    # 3. Target
    data_scope["embeddings"].export(
        "embeddings",
        cocoindex.targets.Postgres(),
        primary_key_fields=["id"],
    )
```

**Key insight**: you describe the *desired state*, not the *transformation steps*. The engine decides what to recompute when sources change.

## 2. Code-aware chunking with Tree-sitter

For indexing source code (our use case: cianfhoghlaim codebase), CocoIndex integrates **Tree-sitter** for syntax-aware chunking. One function / one class / one block per chunk, not arbitrary line splits.

| Language | AST nodes used as chunk boundaries |
|----------|-------------------------------------|
| Python | function, class, method definitions |
| Rust | fn, impl, struct, trait, mod |
| TypeScript | function, class, interface, type |
| Markdown | section, code block, paragraph |

`cocoindex-code-mcp-server` ships reference implementations for ~20 languages. **Use this when indexing our own monorepo.**

## 3. Incremental processing — the killer feature

Two modes:

| Mode | CLI | Use case |
|------|-----|----------|
| **Batch** | `cocoindex update` | One-time index build; subsequent runs only re-process changed files |
| **Live** | `cocoindex update -L` | Long-lived watcher; polls source every N seconds, updates in real-time |

**Pattern for Cianfhoghlaim**: use live mode for `cognee/` and `sruth/` development (sources change frequently), batch mode for curriculum PDFs (sources are stable).

**No custom incremental code is needed** — CocoIndex tracks lineage via content fingerprints and reuses cached chunks/embeddings.

## 4. Multi-target architecture

A single flow can export to multiple targets simultaneously:

```python
data_scope["chunks"].export("lancedb_index", cocoindex.targets.LanceDB(uri="./.lancedb"))
data_scope["chunks"].export("postgres_index", cocoindex.targets.Postgres())
data_scope["chunks"].export("neo4j_graph", cocoindex.targets.Neo4j(), graph=True)
```

For our curriculum knowledge graph (Cognee + Graphiti + LanceDB), this means one flow, three sinks.

## 5. Hybrid search: pgvector vs Qdrant

The `docs/vectordb/hybrid-search-with-pgvector-vs-qdrant.md` analysis (from cocoindex-code-mcp-server) is worth reading for our hybrid search design. Key takeaway:

- **pgvector** is fine up to ~1M vectors; tight Postgres integration is the win
- **Qdrant** scales to billions; richer filtering, faster ANN at scale
- For Tuath's Irish curriculum corpus (estimated 100K-500K documents): **pgvector is the right choice** — keep the data plane simple, single Postgres, no extra service

## 6. The "Cianfhoghlaim-flavored" example: indexing our own monorepo

The `cocoindex-code-mcp-server` reference (56 docs) is the most directly applicable pattern. The `.agents/skills/ccc/` skill (CocoIndex Code Crawler) is built on top of this.

**For our project**: instead of a separate cocoindex-code-mcp-server deployment, we should embed the same architecture in our `sruth/tuath/code_index/` (next to `códeolas/`) — same Tree-sitter + LanceDB + MCP tool pattern, but pointing at *our* monorepo.

## 7. Performance numbers (from the docs)

- **Tree-sitter chunking**: ~50-200ms per 1K LOC
- **Sentence transformer embedding**: ~10-50ms per chunk (CPU) / ~2-5ms (GPU)
- **LanceDB upsert**: O(log N) with HNSW; sub-millisecond for 1M vectors
- **Live update poll**: configurable; recommended 10s for Google Drive, 60s for local FS

## 8. Anti-patterns to avoid

- ❌ **Don't** run the same flow twice in parallel — it'll produce duplicate rows unless you use a deterministic primary key
- ❌ **Don't** embed raw HTML — always clean to markdown/text first (CocoIndex's `HtmlToMarkdown` function)
- ❌ **Don't** store large blobs in the index — extract text/metadata only; large assets go in object storage (R2, S3)
- ❌ **Don't** rely on in-memory state — always re-derive from sources so flows are idempotent

---

## When to read the source material

- Building a new code RAG index → read `cocoindex-code-mcp-server/docs/cocoindex/{flow,embedding,search}.md`
- Setting up a custom Tree-sitter chunker → `cocoindex-code-mcp-server/docs/tree-sitter/error-nodes.md`
- Choosing between hybrid-search strategies → `cocoindex-code-mcp-server/docs/vectordb/hybrid-search-with-pgvector-vs-qdrant.md`
- Debugging a flow → `cocoindex-code-mcp-server/docs/claude/Flow-Debug.md`
- Understanding Flow internal types → `cocoindex-code-mcp-server/docs/cocoindex/flow-and-types.md`

The 56-doc source material in `cocoindex-code-mcp-server/` is preserved for deep dives; this summary is the 80/20 rule applied to operational use.
