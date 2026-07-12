# 2026-07-11-global-region-source-contract-v1

## Why

The Cianfhoghlaim data plane has grown organically since the
[lateralise-british-isles-domains](../archive/lateralise-british-isles-domains/)
change. Today the on-disk contract is inconsistent across regions and
across source families:

- `dlt/british_isles/<nation>/<domain>/<source>.py` (e.g.
  `dlt/british_isles/ireland/education/ncca.py`)
- `dlt/official_media/` (sibling region, no nation + domain layout)
- `dlt/language/` (regional cluster, no nation)
- per-subject LC6 sources (`dlt/british_isles/ireland/education/ncca_<subject>.py`)
- scaffolded cross-nation board sources
  (`dlt/british_isles/<nation>/education/<board>/syllabus_source.py`)

The British Isles cross-nation audit
([`docs/agents/cross-nation-content-audit.md`](../../../docs/agents/cross-nation-content-audit.md))
already deferred the next phase (Scotland / Wales / England / NI /
Crown Dependencies) to v2.

We are about to add two new regional directories —

- `dlt/european_union/` for EU institutional resources across all EU
  official languages (used for later alignment and data creation)
- `dlt/european_nations/` for one sub-directory per EU member state
  + Ukraine, mirroring the British Isles contract

— and we will then later add `dlt/commonwealth/` and `dlt/americas/`
(with California as the US sub-state example).

Before we add four more region trees, the canonical path + source-id +
partition contract must be **locked in writing** so we do not compound
the existing drift. The Phase 0 lockdown guarantees that the EU,
Commonwealth, and Americas work lands on a contract that:

1. matches the existing British Isles pattern (the on-disk state of
   truth for that region),
2. documents the new regions (EU institutional vs EU member states vs
   Commonwealth vs Americas), and
3. is enforceable via `dg check yaml` + a one-line `git grep`
   invariant.

## What changes

This is a **spec-only, no-code** change. It locks the canonical path
contract and the canonical `source_id` shape for any new region going
forward. The existing British Isles files are NOT renamed in this
change (per the "do not touch the legacy tree" hard rule below); only
the future global-expansion files MUST obey the new contract.

### 1. New umbrella spec `cross-region-pipeline`

Adds `openspec/specs/cross-region-pipeline/spec.md` as the umbrella
spec for the global expansion. It declares:

- the 5 regions (`british_isles`, `european_union`, `european_nations`,
  `commonwealth`, `americas`) + the optional `global_official` for
  universal institutions,
- the canonical DLT path contract,
- the canonical `source_id` shape,
- the canonical partition contract (the BC / EU / Commonwealth /
  Americas overlap on the `language` axis),
- the cross-nation BAML classifier (carried forward from
  `multi_nation_curriculum.baml`),
- the canonical DuckLake namespace shape.

The new spec is referenced from the existing
[`oideachais-pipeline`](../../specs/oideachais-pipeline/spec.md) +
[`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md)
specs (see §2 below).

### 2. Spec deltas

| File | Action | Why |
|:--|:--|:--|
| `openspec/specs/oideachais-pipeline/spec.md` | MODIFIED | Add the cross-region path contract as a new ADDED Requirement and reference the new umbrella spec |
| `openspec/specs/british-isles-education-pipeline/spec.md` | MODIFIED | Add a cross-reference that the British Isles path contract is one instance of the new global contract |
| `openspec/specs/cross-region-pipeline/spec.md` | NEW | The umbrella spec for the global expansion |

### 3. Hard-rule invariants (enforced by `dg check yaml` + grep)

| Invariant | Check |
|:--|:--|
| Every new DLT source for any of the 6 regions MUST live at `dlt/<region>/<jurisdiction>/<domain>/<source>.py` | `dg check yaml` on the new defs |
| Every new `source_id` MUST match `^[a-z0-9]+(\.[a-z0-9]+)+$` | `git grep -E 'source_id:\s*[^a-z0-9.]' openspec/changes/*/specs/ defs/` |
| Every new jurisdiction MUST be an ISO 3166-1 alpha-3 (3-letter) code in lowercase, OR one of the documented British Isles names (`ireland`, `england`, `scotland`, `wales`, `northern_ireland`, `jersey`, `guernsey`, `isle_of_man`) | `git grep -E 'nation:\s*[A-Z]' openspec/changes/*/specs/ defs/` |
| Every new EU-official-language resource MUST list its `language` partition as one of the 24 EU official language codes | grep on the defs.yaml |
| Every new CocoIndex v1 App MUST import `from ._lifespan import shared_lifespan` (the R1–R4 conformance contract) | `ccc:search "from ._lifespan import shared_lifespan"` |

## What does NOT change

- The existing 200+ files under `dlt/british_isles/`, `dlt/official_media/`,
  `dlt/language/`, `dlt/filesystem/` are NOT renamed. The new contract
  is forward-only.
- No new DLT sources, no new BAML files, no new Dagster assets, no new
  CocoIndex v1 Apps land in this change. Those land in Phase 1 +
  Phase 2 + Phase 4 + Phase 5 (the follow-on openspec changes).
- The legacy `sruth/<quadrant>/` paths referenced in the older
  `oideachais-pipeline/spec.md` scenarios are NOT modified in this
  change.

## Out of scope (deferred to follow-on changes)

- The 3 archived `lateralise-*` changes that pre-date this contract.
- The dead-code scaffolded board sources under
  `dlt/british_isles/<nation>/education/<board>/syllabus_source.py`
  (promoted in a separate change).
- The legacy `_crawl_source` private helper leakage (already in flight
  via `2026-07-15-pipeline-architecture-clarity-v1`).
- The missing `medicine/` and `statistics/` BAML sub-trees (added in
  the BAML phase of each follow-on change).

## Dependencies

```yaml
Blocked by: none
Blocked by (soft):
  - 2026-07-15-pipeline-architecture-clarity-v1
    (the canonical `site_crawler` primitive must land before any
     global-expansion source is implemented — this Phase 0 contract
     assumes the new primitive is the entry point for new sources)
  - 2026-07-09-2026-07-09-cross-nation-content-audit-v1
    (the British Isles v2 audit is the template for the new
     `cross-region-pipeline` spec)

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-11-global-region-source-contract-v1 --strict` passes
- `openspec/specs/cross-region-pipeline/spec.md` exists with at least 3
  Requirements + 3 Scenarios
- `openspec/specs/oideachais-pipeline/spec.md` carries the new
  `cross-region-pipeline` Requirement
- `openspec/specs/british-isles-education-pipeline/spec.md` carries
  the new cross-reference Requirement
- No new DLT / BAML / Dagster files are added (verified via
  `git diff --stat` against the base)
- Push target: `origin/main`

## Cross-references

- `openspec/specs/british-isles-education-pipeline/spec.md` — the
  British Isles v1 capspec (one instance of the new global contract)
- `openspec/specs/oideachais-pipeline/spec.md` — the parent Celtic
  education pipeline
- `openspec/specs/official-media-pipeline/spec.md` — the official-media
  capspec (sibling region, not yet under the new contract)
- `openspec/specs/oideachais-university-deep-extraction/spec.md` — the
  per-university deep-extraction spec (will reference the new contract)
- `docs/agents/cross-nation-content-audit.md` — the BIEP v2 audit
  template
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
