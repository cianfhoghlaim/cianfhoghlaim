# TypeScript Modern API

The LanceDB TypeScript SDK has had several API changes. The
**deprecated** `vectorSearch(...)` API has been replaced by the
modern `search(...)` API with explicit `queryType`. Always use the
modern API in new code.

## Install

```bash
bun add @lancedb/lancedb apache-arrow
# Optional: for embeddings + rerankers
bun add @lancedb/lancedb/embedding @lancedb/lancedb/rerankers
```

## Connection

```typescript
import * as lancedb from "@lancedb/lancedb";

// Local
const db = await lancedb.connect("data/my-database");

// Cloudflare R2
const db = await lancedb.connect("s3://my-bucket/lance", {
  storageOptions: {
    endpoint: "https://<accountid>.r2.cloudflarestorage.com",
    region: "auto",
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
});

// LanceDB Cloud
// .env: LANCEDB_URI=db://my-database, LANCEDB_API_KEY=...
const db = await lancedb.connect(process.env.LANCEDB_URI!, {
  apiKey: process.env.LANCEDB_API_KEY!,
  region: "eu-west-1",
});
```

## Embeddings registry

```typescript
import { embedding, rerankers } from "@lancedb/lancedb";

const registry = embedding.getRegistry();

// OpenAI
const openai = registry.get("openai");
const embedModel = openai.create({ model: "text-embedding-3-small" });

// HuggingFace transformers (browser / Node with onnxruntime-node)
const hf = registry.get("huggingface");
const hfModel = hf.create({ name: "Xenova/all-MiniLM-L6-v2" });
```

## Declarative schema with `LanceSchema`

```typescript
import { embedding } from "@lancedb/lancedb";
import { Utf8, Float32, FixedSizeList, Schema, Field } from "apache-arrow";

const model = embedding.getRegistry().get("openai").create({ model: "text-embedding-3-small" });

const schema = new Schema([
  new Field("id", new Utf8(), false),
  new Field("text", new Utf8(), false),
  new Field("vector", new FixedSizeList(model.ndims(), new Field("item", new Float32())), false),
]);

// Create a table
const table = await db.createTable({
  name: "documents",
  data: [
    { id: "1", text: "LanceDB is great", vector: Array.from(await model.embed("LanceDB is great")) },
    { id: "2", text: "Vector search is fast", vector: Array.from(await model.embed("Vector search is fast")) },
  ],
  schema,
  mode: "create",
});
```

## Vector search (modern API)

```typescript
// Query embedding
const queryVec = Array.from(await model.embed("machine learning"));

// Modern API: search(), not vectorSearch()
const results = await table
  .search(queryVec)
  .limit(10)
  .toArray();

// With filter
const filtered = await table
  .search(queryVec)
  .where("id > '1'")
  .limit(10)
  .toArray();
```

## Hybrid search with RRF

```typescript
import { rerankers } from "@lancedb/lancedb";

const hybrid = await table
  .search(queryType: "hybrid", queryVec, "machine learning")
  .rerank(rerankers.RRFReranker())
  .limit(10)
  .toArray();
```

## CrossEncoder reranker

```typescript
import { rerankers } from "@lancedb/lancedb";

const reranker = await rerankers.CrossEncoderReranker.create({
  name: "Xenova/ms-marco-MiniLM-L-6-v2",
});

const results = await table
  .search(queryVec)
  .rerank(reranker)
  .limit(10)
  .toArray();
```

## Migration from `vectorSearch()`

```typescript
// ❌ Deprecated
const results = await table.vectorSearch(queryVec).limit(10).toArray();

// ✅ Modern
const results = await table.search(queryVec).limit(10).toArray();
```

The `vectorSearch()` API will be removed in a future major version of
`@lancedb/lancedb`. Always use `search()` in new code.

## Reference

- The canonical `hybrid-search/` and `quickstart/` examples in the
  upstream lancedb/vectordb-recipes repo (deleted with
  `docs/lance/`) show the modern TS API in a Next.js + Bun context.
- LanceDB TS SDK docs: <https://lancedb.github.io/lancedb/js/>
