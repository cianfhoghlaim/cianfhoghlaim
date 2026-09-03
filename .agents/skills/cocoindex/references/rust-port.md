# Rust Port Reference

CocoIndex v1 has a Rust port of most Python flows. The Rust port
is in `cocoindex/rust/` and at the upstream
`docs/cocoindex/rust/` examples (deleted with the docs; the same
examples are in the upstream cocoindex repo).

## When to use the Rust port

- **Performance**: the Rust port is faster (no Python GIL, native
  memory layout for the Arrow types)
- **Single binary deploy**: a Rust app compiles to a single static
  binary (no Python runtime)
- **Edge / WASM**: CocoIndex Rust is the basis for the WASM build

For most KCG use cases, the Python v1 Apps are sufficient and the
ergonomics of `@coco.fn` + BAML are better.

## Module map (Rust port)

| Python | Rust |
|:--|:--|
| `import cocoindex as coco` | `use cocoindex::prelude::*` |
| `@coco.fn` | `#[coco::fn]` |
| `@coco.fn(memo=True)` | `#[coco::fn(memo)]` |
| `@coco.lifespan` | `#[coco::lifespan]` |
| `ContextKey[T]` | `ContextKey::new_with_state(...)` |
| `mount_table_target` | `mount_table_target!` macro |
| `mount_each(fn, items, target)` | `mount_each!` macro |
| `await coco.use_context(KEY)` | `coco::use_context(KEY)` |

## KCG example (Rust port)

- `cocoindex/rust/text_embedding/src/main.rs` —
  mirror of `cocoindex/leabharlann_embedding.py`
  (text embedding + LanceDB target)

## Running a Rust port

```bash
cd cocoindex/rust/text_embedding
cargo run -- index    # catch-up
cargo run -- query "irish gaelic"  # query
```
