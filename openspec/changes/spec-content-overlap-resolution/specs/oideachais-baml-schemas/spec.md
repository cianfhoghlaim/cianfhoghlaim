## REMOVED Requirements

### Requirement: BAML surface compiles cleanly across the 8 jurisdiction packs

**Reason**: Consolidated into `cianfhoghlaim-baml-schemas` as the new
Requirement "BAML surface compiles cleanly across the 8 jurisdiction
packs".

### Requirement: All 50 pre-existing BAML `field: type` errors resolved

**Reason**: Consolidated into `cianfhoghlaim-baml-schemas` as the new
Requirement "All 50 pre-existing BAML `field: type` errors resolved".

### Requirement: NCCA strand/outcome catalog supports runtime TypeBuilder mutation

**Reason**: TypeBuilder mutation is owned by the canonical
`cianfhoghlaim-baml-schemas` spec's existing dynamic-schema section.

### Requirement: baml-cli test CI hard gate

**Reason**: CI gate is owned by the canonical
`cianfhoghlaim-baml-schemas` spec's existing CI section.

### Requirement: baml_client regenerates with 0 errors in the processing cluster

**Reason**: Client regeneration is owned by the canonical
`cianfhoghlaim-baml-schemas` spec's existing client-regen section.

### Requirement: (all remaining requirements are similarly consolidated into `cianfhoghlaim-baml-schemas`)

**Migration**: After archive, `oideachais-baml-schemas` is a single-
requirement retirement marker pointing at
`cianfhoghlaim-baml-schemas`.