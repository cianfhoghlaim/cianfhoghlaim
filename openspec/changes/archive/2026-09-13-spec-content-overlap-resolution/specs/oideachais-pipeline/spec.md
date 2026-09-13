## REMOVED Requirements

### Requirement: No legacy 972-LOC ie-namespace duplicate pairs remain in `dlt/british_isles/ireland/education/`

**Reason**: Content consolidated into `cianfhoghlaim-pipeline` as the
new Requirement "No legacy ie-namespace duplicate pairs remain". The
MD5 hash and the 11-importer invariant are now owned by the canonical
spec.

### Requirement: Canonical endpoint_recovery helper

**Reason**: Endpoint-recovery helper is owned by
`cianfhoghlaim-pipeline`'s dagster-bridge section; this
spec's requirement is duplicated.

### Requirement: EU pilot + Ukraine per-subject depth upgrade

**Reason**: Cross-reference stub (a duplicate of the canonical's
mention). The actual EU pilot + Ukraine upgrade content lives in
`european-nations-ukraine-pipeline`.

### Requirement: Americas pipeline cross-referenced from cianfhoghlaim-pipeline

**Reason**: Cross-reference stub. Consolidated into the new
cianfhoghlaim-pipeline Requirement "Cross-references section must
enumerate the regional pipelines".

### Requirement: Commonwealth pipeline cross-referenced from oideachais-pipeline

**Reason**: Same as above.

### Requirement: EU nations + Ukraine pipeline cross-referenced from cianfhoghlaim-pipeline

**Reason**: Same as above.

### Requirement: EU institutional pipeline cross-referenced from cianfhoghlaim-pipeline

**Reason**: Same as above.

### Requirement: Nigeria pipeline cross-referenced from oideachais-pipeline

**Reason**: Same as above.

### Requirement: Canada provinces cross-referenced from cianfhoghlaim-pipeline

**Reason**: Same as above.

### Requirement: British Isles parity pipeline cross-referenced from cianfhoghlaim-pipeline

**Reason**: Same as above.

### Requirement: EU full-depth expansion cross-referenced from cianfhoghlaim-pipeline

**Reason**: Same as above.

### Requirement: EU multilingual pipeline cross-referenced

**Reason**: Same as above.

### Requirement: PlanetScale Postgres Centralisation (cianfhoghlaim-pipeline)

**Reason**: PlanetScale PG migration is owned by
`planetscale-postgres-data-strategy` (R7), not this spec.

### Requirement: Gaois + Celtic language pipeline cross-referenced from cianfhoghlaim-pipeline

**Reason**: Cross-reference stub. The actual Celtic language pipeline
content lives in `celtic-language-pipeline`; consolidated into the
new cianfhoghlaim-pipeline Requirement "Cross-references section must
enumerate the regional pipelines".

**Migration**: This change archives `oideachais-pipeline` to a single-
requirement retirement marker (see the next change in
`oideachais-pipeline/spec.md` after archive). All cross-references in
skills/AGENTS.md/READMEs SHOULD point at `cianfhoghlaim-pipeline`
instead.