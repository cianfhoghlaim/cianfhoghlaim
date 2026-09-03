# Spec Delta: `croilar-persona-registry` (REMOVED)

## REMOVED Requirements

### Requirement: Persona Schema

**Reason**: The persona model conflated stream id with owner identity and blocked the new author-profile-consolidation, ResearchGate source, and DLT filesystem source work. The persona Zod schema is replaced by the new `croilar-stream-registry` capability's Pydantic models.

**Migration**: The legacy `personas/<id>.ts` files are migrated to `sruth/croilar/config/sources.yaml` `streams:` entries. The `getPersona("aleyum")` API is replaced by `get_stream("music")`. The `definePersona({...})` helper is removed entirely; the Stream registry is YAML-driven and validated by Pydantic.

### Requirement: Persona Registry

**Reason**: The persona lookup table was the central coupling point. Removing it eliminates a class of bugs where the persona id leaked into DLT defaults, BAML enums, and i18n imports.

**Migration**: The registry is replaced by `sruth/croilar/_shared/streams.py::get_stream` / `list_streams`. The 3 personas (`aleyum`, `cianfhoghlaim`, `carlcashman`) collapse to 2 streams (`music`, `teaching`) plus the new `cv` and `research` streams. `carlcashman` is removed with no replacement.

### Requirement: New Persona Addition

**Reason**: Adding a "persona" was a code change (new `personas/<id>.ts` + register in `_registry.ts`). The Stream registry is data-driven: adding a stream is a YAML change + a BAML schema change for new source types. The code path is more general and doesn't deserve a dedicated "add a stream" test scenario.

**Migration**: New streams are added by appending to `sruth/croilar/config/sources.yaml`. Validation is `openspec validate --strict` over the spec deltas, then `bun run turbo typecheck lint test` over the resulting code.
