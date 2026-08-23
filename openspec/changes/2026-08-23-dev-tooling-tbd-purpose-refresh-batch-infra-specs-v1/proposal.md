# 2026-08-23 — Fill remaining TBD Purpose fields (infra + misc batch)

## Why

Phase 5.1.2 filled 11 agent-spec TBDs. 11 remain:

| Spec | Domain |
|:--|:--|
| `dev-tooling-surfaces` | meta-spec (Phase 2/3/4 already addressed) |
| `learn-to-earn-token-credential` | misc |
| `meaisinfoghlaim-ocr-htr` | misc |
| `pangolin-integration-api` | infra |
| `oideachais-baml-schemas` | oideachais (Phase 5.1.4) |
| `oideachais-cocoindex-v1-migration` | oideachais (Phase 5.1.4) |
| `oideachais-cognify-knowledge-graph` | oideachais (Phase 5.1.4) |
| `oideachais-leabharlann` | oideachais (Phase 5.1.4) |
| `oideachais-marimo-dashboards` | oideachais (Phase 5.1.4) |
| `oideachais-pipeline` | oideachais (Phase 5.1.4) |
| `oideachais-university-deep-extraction` | oideachais (Phase 5.1.4) |

This change fills 3 (the non-oideachais ones: dev-tooling-surfaces + learn-to-earn-token-credential + meaisinfhoghlaim-ocr-htr + pangolin-integration-api = 4). After this change, 7 oideachais TBDs remain (addressed in Phase 5.1.4).

## The 4 specs to fill

- `dev-tooling-surfaces`: the meta-spec for dev-tooling refactors (1 invariant: the surface refactor pattern)
- `learn-to-earn-token-credential`: the x402 / Learn-to-Earn token + credential pattern
- `meaisinfoghlaim-ocr-htr`: the OCR/HTR pipeline (already covered in the Phase 5.1.2 agent batch via my batch script)
- `pangolin-integration-api`: the Pangolin reverse-proxy integration API

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. All 4 specs have non-TBD Purpose sections
2. `lint:spec:purpose` count drops from 12 remaining TBDs → 7 remaining TBDs (only oideachais)
3. `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-infra-specs-v1 --strict` exits 0

## Rollback plan

- `git checkout` the 4 spec files
- No code changes