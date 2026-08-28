# bonneagar-subapp-carveout Specification

## Status: SUPERSEDED (2026-08-28) — carveout rejected in favour of the mirror model

## Purpose

This capability was created by archiving change
`2026-08-26-bonneagar-carveout-v1`, which proposed carving `bonneagar/`
out as an independent sibling repo and subtree-mounting it back into
cianfhoghlaim as a TIER 3 subapp.

**The carveout was never implemented, and on 2026-08-28 it was decided
against.** This spec is retained to record that decision rather than
leave a falsely-satisfied contract in the spec set.

## Why it was recorded as complete but was not

The archived change ticked all three of its tasks and all three
acceptance criteria, but none of the artefacts existed:

| Claimed | Actual on 2026-08-28 |
|:--|:--|
| `bonneagar/kcg_subapp_manifest.yaml` exists | No manifest at any path; the schema is also now named `subapp_manifest.yaml` |
| `github.com/cianmacandeisigh/bonneagar` exists | Does not exist. The bonneagar repo is under the `cianfhoghlaim` org |
| The 59 inbound refs rewritten to the facade URI | Not rewritten — and there are ~780 referencing files, not 59 (503 under `openspec/`, 166 under `docs/`, 60 under `scripts/`) |

The "59 inbound refs" estimate was low by an order of magnitude, which
is the main reason the carveout is not worth its cost.

## The decision

`bonneagar/` SHALL remain **in-tree and canonical** in the cianfhoghlaim
monorepo. `github.com/cianfhoghlaim/bonneagar` SHALL be a **one-way
published mirror** of it, force-updated by `mise run bonneagar:mirror`.

This is the opposite ownership direction to a subapp carveout, so
`bonneagar/` deliberately does **not** carry a `subapp_manifest.yaml`.
The sister-repo manifests (`tuatha`, `ciandlithe`, `cianchosaint`,
`ciancheiltis`, `gemini_hackathon`) declare `upstream_repo` — the
subapp's own repo being upstream of the parent's copy. For bonneagar the
parent is upstream and the remote is downstream, so a manifest of that
shape would assert the reverse of the truth and would make
`scripts/sync/sync_subapps.py` treat the mirror as a source of inbound
changes.

## Requirements

### Requirement: bonneagar is not a subapp

The system SHALL NOT treat `bonneagar/` as a TIER 3 subapp. It SHALL NOT
carry a `subapp_manifest.yaml`, and SHALL NOT be mounted under
`subapps/`.

#### Scenario: the subapp sync runs

- **WHEN** `scripts/sync/sync_subapps.py` enumerates `subapps/*/subapp_manifest.yaml`
- **THEN** `bonneagar` SHALL NOT appear among the results
- **AND** no openspec changes SHALL be mirrored to `openspec/changes/from-bonneagar/`

#### Scenario: a developer asks where bonneagar's source of truth is

- **WHEN** the developer reads the constellation table in `README.md`
- **THEN** `bonneagar/` SHALL be identified as in-tree and canonical
- **AND** `github.com/cianfhoghlaim/bonneagar` SHALL be identified as a mirror

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the
  "Bonneagar is in-tree and canonical; the standalone repo is a mirror"
  Requirement, which is the live contract
- [`sync-subapps`](../sync-subapps/spec.md) — the subapp model that
  bonneagar is explicitly outside of
