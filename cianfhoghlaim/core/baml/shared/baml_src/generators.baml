// BAML Shared Generators Configuration for cianfhoghlaim.
//
// Single source of truth for the Python + TypeScript client codegen
// targets. All 4 quadrants' BAML files generate their clients from
// these settings, replacing the 4 per-quadrant `generators.baml`
// files (2 of which were `0.74.0`, 2 of which were empty).
//
// Run after any .baml change:
//   cd cianfhoghlaim/core/baml && baml-cli generate
//
// Per the 2026-06 polyglot BAML pattern, the Python target is the
// Pydantic v2 model (consumed by Dagster + DLT + the Honcho API)
// and the TypeScript target is the Zod-compatible interface
// (consumed by TanStack AI + oRPC + the croilar-portal UI).

generator lang_py {
  output_type python/pydantic
  output_dir "../baml_client"
  version "0.76.2"
  default_client_mode async
}

generator lang_ts {
  output_type typescript
  output_dir "../baml_client_ts"
  version "0.76.2"
  default_client_mode async
}
