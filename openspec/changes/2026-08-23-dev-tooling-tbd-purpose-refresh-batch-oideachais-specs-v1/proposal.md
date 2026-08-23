# 2026-08-23 — Fill 8 oideachais-spec TBD Purpose fields + wire lint:spec:purpose to core:lint

## Why

Phase 5.1.2 + 5.1.3 filled 14 TBDs. 8 remain, all oideachais specs:

- `oideachais-baml-schemas`
- `oideachais-cocoindex-v1-migration`
- `oideachais-cognify-knowledge-graph`
- `oideachais-leabharlann`
- `oideachais-marimo-dashboards`
- `oideachais-pipeline`
- `oideachais-university-deep-extraction`

(Note: `meaisinfoghlaim-ocr-htr` was filled in Phase 5.1.2 batch; the user's plan counted it as oideachais but it's actually a meaisinfhoghlaim spec.)

After this change, **all TBDs are filled** and `lint:spec:purpose` can be wired into `core:lint` as a real CI gate.

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. All 7 oideachais specs (8 minus the meaisinfhoghlaim one that was filled in 5.1.2) have non-TBD Purpose sections
2. `lint:spec:purpose` exits 0 (all TBDs filled)
3. `lint:spec:purpose` is added to `core:lint` depends (final wiring)
4. `core:lint` exits 0
5. `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-oideachais-specs-v1 --strict` exits 0

## Rollback plan

- `git checkout` the 7 oideachais spec files
- Remove `lint:spec:purpose` from `core:lint` depends