## REMOVED Requirements

### Requirement: Phase 1 complete — 9 requirements all functional end-to-end

**Reason**: This Requirement was the deliberate retirement marker
the spec was already serving as; it stays as the single remaining
requirement after this change archives the other 3.

### Requirement: Leabharlann cognify (updated from "3 corpora" to "6 sub-corpora")

**Reason**: Consolidated into `cianfhoghlaim-cognify-knowledge-graph`
as the new Requirement "Leabharlann cognify covers 6 sub-corpora
(updated scope)".

### Requirement: Cross-archive edges (FalkorDB) (updated ownership boundary)

**Reason**: Consolidated into `cianfhoghlaim-cognify-knowledge-graph`
as the new Requirement "Cross-archive FalkorDB edges have documented
ownership boundaries".

### Requirement: PlanetScale Postgres Centralisation (cianfhoghlaim-cognify-knowledge-graph)

**Reason**: PlanetScale PG migration is owned by
`planetscale-postgres-data-strategy` (R7), not this spec.

**Migration**: After archive, `oideachais-cognify-knowledge-graph` is
a single-requirement retirement marker pointing at
`cianfhoghlaim-cognify-knowledge-graph`.