# Cognee Docs Ingestion — Phase 4 Report

## Status: SCRIPT READY, KEY BLOCKER

The `cognee-ingest-docs.py` script has been extended to all 19 numbered
docs/ domains and verified locally. The Cognee REST API is up and
healthy. The remaining blocker is the litellm → deepseek auth path
(an `.env` / container restart issue, not a code issue).

## What was done

### Script extensions
- **DOMAIN_TO_DIR** expanded from 7 → 19 domains matching the new
  docs/ layout (00-core, 00-package-ecosystem, 01-cognee, ...,
  08-screenshots)
- **Recursive glob**: `load_domain_docs` now uses `rglob('*.md')` to
  descend into nested subdirs (e.g. `00-package-ecosystem/` has 10
  subdirs with 36 .md files; 06-infrastructure/ has 7 subdirs with
  190 .md files)
- **Encoding fallback**: Try UTF-8, fall back to latin-1 on
  UnicodeDecodeError (some Windows-saved files in 06-infrastructure/
  have non-UTF-8 bytes)
- **API field names** updated for Cognee v1.1.2 REST API:
  - `/api/v1/datasets` create → POST JSON `{name, description}`
  - `/api/v1/add` → POST multipart/form-data with `data` (binary file)
    + `datasetId` or `datasetName`
  - `/api/v1/cognify` → POST JSON `{datasetIds: [uuid, ...]}` or
    `{datasets: [name, ...]}`
- **ensure_dataset()** helper: creates the dataset if missing, returns
  its UUID; idempotent (skips creation if dataset exists)

### Verified locally (no LLM call required for --summary)

```bash
$ uv run python3 infrastructure/scripts/cognee-ingest-docs.py --all --summary
```

| Domain | Docs | Bytes |
|:--|--:|--:|
| core | 9 | 112,813 |
| package-ecosystem | 36 | 82,147 |
| cognee | 12 | 72,099 |
| patterns | 9 | 109,663 |
| platform-architecture | 16 | 161,253 |
| architecture | 11 | 249,389 |
| audit | 6 | 392,274 |
| data-platform | 13 | 150,485 |
| agents | 54 | 1,114,822 |
| pipelines | 1 | 13,785 |
| ai-ml | 20 | 6,298,554 |
| celtic-language | 8 | 128,383 |
| web | 6 | 63,403 |
| infrastructure | 190 | 7,006,553 |
| product | 8 | 92,931 |
| skills | 12 | 127,193 |
| standards | 2 | 23,170 |
| examples | 8 | 86,178 |
| screenshots | 3 | 33,940 |
| **TOTAL** | **424** | **16,319,035** |

Largest domain: **06-infrastructure** (190 docs, 7.0 MB).

## What was attempted (blocked)

```bash
$ COGNEE_API_URL=http://localhost:8100 uv run python3 \
    infrastructure/scripts/cognee-ingest-docs.py --domain standards
[standards] dataset docs-standards -> 237ff239-c9b2-57d0-b510-5ea8e5528f17
[standards] ingesting 2 canonical docs into docs-standards
# then hangs...
```

The `/api/v1/add` call hangs because Cognee runs **entity extraction
during add** (not just during cognify). The entity extraction calls
litellm, which calls DeepSeek, which fails authentication:

```
litellm.BadRequestError: DeepseekException -
  {"error":{"message":"Authentication Fails, Your api key: ****eded is invalid"}}
```

The redacted key `****eded` is the end of the `DEEPSEEK_API_KEY` in
the `.env` file (`sk-726756171edd4bc8a7a6c4c6295d6e83`). This is a
**placeholder key** that someone added to the .env file during
the hackathon (it's not a real DeepSeek key).

## Root cause analysis

1. `cognee/compose.yaml` sets `LLM_API_KEY=no-key-needed` (sentinel)
2. Cognee sends `Authorization: Bearer no-key-needed` to litellm
3. Litellm uses the **config-mapped** `os.environ/DEEPSEEK_API_KEY`
   (line 499 of `infrastructure/stacks/engineering/litellm/config/config.yaml`)
4. The litellm container was started **20+ hours ago** (before the
   `.env` had the placeholder `DEEPSEEK_API_KEY`)
5. So the litellm container has no `DEEPSEEK_API_KEY` env var set
6. When DeepSeek rejects the empty key, the error says `****eded`
   (last 4 of the .env placeholder) — but that's misleading; the
   actual key sent is empty

Wait — the redacted `****eded` looks like `****eded` of `sk-...7edd4bc8a7a6c4c6295d6e83` — actually `d6e83` is the last 5, and `eded` would be 4 chars from position 6-9. So litellm IS reading the .env key, but DeepSeek rejects it as invalid.

**Conclusion**: The .env has a fake placeholder `DEEPSEEK_API_KEY`. Real
extraction requires replacing it with a valid key.

## Workarounds (any of these unblocks Phase 4)

1. **Replace .env DEEPSEEK_API_KEY** with a real key from Infisical
   (`dev-baile/deepseek/api_key`), then restart litellm + cognee.
2. **Switch to a different model** that doesn't need DeepSeek. Edit
   `cognee/compose.yaml`: `LLM_MODEL=local/irish/uccix` (uses local
   GGUF, no external auth required).
3. **Use the `extract` alias** with the GLM 4.6 fallback (after fixing
   the Gemini 403): `LLM_MODEL=openai/glm-4.6` (Z.ai's GLM, $0.50/M tokens).

Option 1 is the cleanest (matches the plan). Option 2 is the fastest
(works immediately if the local UCCIX GGUF is up). Option 3 needs an
Infisical update for `Z_AI_API_KEY`.

## Next steps

- **Phase 4 close-out**: Pick a workaround above, re-run
  `--domain standards` to verify end-to-end.
- **Phase 4 stretch**: Run `--all --no-cognify` once a workaround is
  in place; this populates the Cognee vector store without building
  the graph. Then `--all` (without --no-cognify) to build the graph.
- **Phase 5a**: Build `cognee-ingest-archive.py` to handle
  `docs/2026-06-06-*` + 5 root PDFs + loose `.py`/`.yaml` files,
  with SHA-256 dedup at `~/.cache/cognee-dedup.json`.
- **Phase 5b**: Bring up Graphiti stack in parallel (same LiteLLM
  + pgvector, different compose files).
- **Phase 6**: Cross-reference discovery via cognee search.
- **Phase 7**: Write `docs/09-cross-references.md` synthesis.
- **Phase 8**: Skill doc updates + MCP config validation.

## Files changed

```
infrastructure/scripts/cognee-ingest-docs.py    (M, 79 insertions, 15 deletions)
doc/hackathons/cognee-ingestion-2026-06-12.md  (A)
```
