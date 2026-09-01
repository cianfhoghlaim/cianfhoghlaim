/**
 * STUB BAML TypeScript client for gcse/physics.
 * 
 * Per the 2026-08-26 build subagent report: the canonical BAML TypeScript
 * client cannot be regenerated because baml_src/ uses the deprecated
 * `catch_all` syntax (258 .baml files); regenerating requires a multi-day
 * .baml syntax migration (catch_all → fallback per BAML 0.222+) before
 * `baml-cli generate` will succeed.
 *
 * This stub unblocks typecheck for the 45 oideachais-dashboard Convex type
 * consumers (the type aliases are used only in type-position). Replace with
 * the regenerated `baml_client_ts/` output once the .baml catch_all migration
 * lands. See: openspec/changes/2026-08-26-baml-catchall-to-fallback-v1 (TBD).
 */

export type PhysicsSyllabus = unknown;
export type PhysicsPaper = unknown;
export type PhysicsMarkingScheme = unknown;
export type PhysicsTopics = unknown;
