## REMOVED Requirements

### Requirement: BIEP v3 5-milestone sequential plan (M0-M4)

**Reason**: Consolidated into `british-isles-education-pipeline` as
the new Requirement "BIEP v3 5-milestone sequential plan (M0-M4)".

### Requirement: BIEP v3 6-deferred-jurisdiction plan (M5-M10)

**Reason**: Deferred M5-M10 is a roadmap item, not a current
capability; tracked in `openspec/plans/` instead of a spec.

### Requirement: BIEP v3 2-scanner-domain plan (filesystem + language)

**Reason**: Scanner-domain plan is owned by
`british-isles-education-pipeline`'s existing scanner section.

### Requirement: BIEP v3 4-cadence scheduling policy

**Reason**: Consolidated into `british-isles-education-pipeline` as
the new Requirement "BIEP v3 4-cadence scheduling policy".

### Requirement: BIEP v3 5-phase pattern

**Reason**: 5-phase pattern is owned by
`british-isles-education-pipeline`'s existing
5-phase-pattern section.

### Requirement: OCR completion webhook convention

**Reason**: Consolidated into `british-isles-education-pipeline` as
the new Requirement "OCR completion webhook convention".

### Requirement: Dagster ocr_completion_sensor

**Reason**: Sensor is owned by `british-isles-education-pipeline`'s
existing sensor section.

### Requirement: Foundation unblock (M0)

**Reason**: M0 foundation is owned by
`british-isles-education-pipeline`'s existing foundation section.

### Requirement: Snake_case file naming contract

**Reason**: Snake-case file naming is owned by the canonical
`pipeline-naming-taxonomy` spec.

### Requirement: Per-cohort 5-phase pattern

**Reason**: 5-phase pattern is owned by
`british-isles-education-pipeline`'s existing per-cohort section.

### Requirement: (all remaining requirements are similarly consolidated into `british-isles-education-pipeline`)

**Migration**: After archive, `british-isles-education-pipeline-v3`
is a single-requirement retirement marker pointing at
`british-isles-education-pipeline` (the v1 + v2 + v3 trilogy is
collapsed to v1 + v2; -v3 served its purpose as a milestone
tracker).