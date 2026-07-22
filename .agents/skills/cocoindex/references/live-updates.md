# Live Updates in CocoIndex v1

CocoIndex v1 supports live updates via `cocoindex update -L <flow>`.
The flow must declare `live=True` on its source. When the source
files change (added / removed / mtime changed), CocoIndex re-runs
only the affected `@coco.fn(memo=True)` components.

## Minimal example

```python
import pathlib
import cocoindex as coco
from cocoindex.connectors import localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher

@coco.fn(memo=True)
async def process_file(file: FileLike, target) -> None:
    text = await file.read_text()
    target.declare_row(row=MyRecord(text=text, …))

@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    target = await postgres.mount_table_target(...)
    files = localfs.walk_dir(
        sourcedir, recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.md"]),
        live=True,  # ← required
    )
    await coco.mount_each(process_file, files.items(), target)
```

## Run

```bash
# Catch-up: scan source, sync, exit
cocoindex update main

# Live: catch up, then watch for changes
cocoindex update -L main
```

## Memoisation keys

`@coco.fn(memo=True)` memoises per component path. The component
path is derived from the function name + the source key. For
`localfs.walk_dir`, the source key is the file path (e.g.
`leabharlann/gaeilge/book1.pdf`). CocoIndex hashes `(function_name,
file_path, file_mtime)` to decide whether to re-run.

## Failure isolation

A file that fails BAML extraction is logged and skipped. The
flow continues. Check the asset check report for the count of
skipped files (see `orchestration/defs/docs_skills_assets.py`).

## Concurrency control

- `max_inflight_rows` on a source limits concurrent rows processed
- `max_inflight_bytes` limits concurrent bytes
- Global env vars: `COCOINDEX_SOURCE_MAX_INFLIGHT_ROWS`,
  `COCOINDEX_SOURCE_MAX_INFLIGHT_BYTES`

## KCG live-update patterns

- `cocoindex/docs_skills_consolidation.py` —
  live-walks `docs/` and `.agents/skills/`
- `cocoindex/codebase_indexing.py` — live-walks
  the repo (replacement for the legacy `ccc` CLI)
- `cocoindex/leabharlann_embedding.py` —
  live-walks `leabharlann/`
