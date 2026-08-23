## Implementation Tasks

- [x] 1. Fill in Purpose for `openspec/specs/drift-remediation/spec.md`. (verification-id: drift-purpose-filled)

- [x] 2. Fill in Purpose for `openspec/specs/dual-search-architecture/spec.md`. (verification-id: dual-search-purpose-filled)

- [x] 3. Fill in Purpose for `openspec/specs/centralize-cross-cutting-docs/spec.md`. (verification-id: cross-cutting-purpose-filled)

- [x] 4. Fill in Purpose for `openspec/specs/centralized-model-registry/spec.md`. (verification-id: model-registry-purpose-filled)

- [x] 5. Fill in Purpose for `openspec/specs/centralized-schema-registry/spec.md`. (verification-id: schema-registry-purpose-filled)

- [x] 6. Fill in Purpose for `openspec/specs/deployment-control-panel/spec.md`. (verification-id: control-panel-purpose-filled)

- [x] 7. Fill in Purpose for `openspec/specs/docs-informed-content-generation/spec.md`. (verification-id: docs-informed-purpose-filled)

- [x] 8. Fill in Purpose for `openspec/specs/integration-runtime-wiring/spec.md`. (verification-id: runtime-wiring-purpose-filled)

- [x] 9. Fill in Purpose for `openspec/specs/baml-quality-bulk-sweep/spec.md`. (verification-id: baml-quality-purpose-filled)

- [x] 10. Fill in Purpose for `openspec/specs/planetscale-postgres-data-strategy/spec.md`. (verification-id: planetscale-purpose-filled)

- [x] 11. Fill in Purpose for `openspec/specs/repo-hygiene-agent-routing/spec.md`. (verification-id: agent-routing-purpose-filled)

- [x] 12. Run canonical CI gates: `mise run core:typecheck` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1 --strict` passes
- [x] All 11 agent specs have non-TBD Purpose (1 more than planned since `meaisinfhoghlaim-ocr-htr` already had one)
- [x] Core CI gates pass

## Notes

- After this change, ~12 TBDs remain in the infra + oideachais batches (covered in 5.1.3 + 5.1.4).
- The decision to NOT yet wire `lint:spec:purpose` into `core:lint` until 5.1.3 + 5.1.4 land is deliberate: wiring it earlier would break CI for the unresolved TBDs.
- The plan documents this as a 3-step rollout: 5.1.2 (this change) → 5.1.3 → 5.1.4 → wire into `core:lint`.