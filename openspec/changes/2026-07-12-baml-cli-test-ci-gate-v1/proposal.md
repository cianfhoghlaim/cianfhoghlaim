# Proposal: baml-cli test CI gate

## Summary

Add a dedicated GitHub Actions workflow at `.github/workflows/baml-test.yaml` that runs the BAML test suite as a hard CI gate on every pull request and push targeting `pick-4-biep-v1` or `main`.

The workflow invokes the canonical mise task:

```bash
cd cianfhoghlaim
mise run baml:test
```

`baml:test` runs `uv run baml-cli test`, so the gate exercises every `test` block discovered by BAML under `cianfhoghlaim/baml/` (via the existing `baml_src -> baml/` project layout). The seeded tests include the 3 existing route tests in `cianfhoghlaim/baml/clients.baml` and the new `ExtractDocSkillTagSmokeTest` block in `cianfhoghlaim/baml/processing/docs_skills_extraction.baml` from commit `409898008`.

## Dependencies

Blocked by: none
Blocked by (soft): `2026-07-11-baml-cocoindex-modernization-v1` (this follow-up wires the CI gate deferred by that change)
Affected repos: cianfhoghlaim

## Current test inventory

The current branch contains 37 BAML `test` blocks:

| File | Test blocks |
|:--|--:|
| `cianfhoghlaim/baml/clients.baml` | 3 |
| `cianfhoghlaim/baml/education/cross_nation/isles_education.baml` | 2 |
| `cianfhoghlaim/baml/education/cross_nation/multi_nation_curriculum.baml` | 2 |
| `cianfhoghlaim/baml/education/stages/junior_cycle.baml` | 1 |
| `cianfhoghlaim/baml/education/stages/primary.baml` | 1 |
| `cianfhoghlaim/baml/education/statistics/education_statistics.baml` | 3 |
| `cianfhoghlaim/baml/education/university/university_extraction.baml` | 4 |
| `cianfhoghlaim/baml/processing/artwork_analysis.baml` | 2 |
| `cianfhoghlaim/baml/processing/author_archive.baml` | 10 |
| `cianfhoghlaim/baml/processing/docs_skills_extraction.baml` | 1 |
| `cianfhoghlaim/baml/processing/email.baml` | 4 |
| `cianfhoghlaim/baml/processing/portfolio_extraction.baml` | 2 |
| `cianfhoghlaim/baml/processing/style_transfer.baml` | 2 |

## Local verification note

`baml-cli test` is available in the uv environment, and this change adds the missing `mise run baml:test` task. The task is self-contained: it recreates the ignored `cianfhoghlaim/baml_src -> baml` symlink in fresh checkouts before invoking `baml-cli test --from cianfhoghlaim/baml_src`.

The local command currently reaches BAML validation and fails before executing tests because the branch still contains pre-existing non-v0.223 BAML syntax in several schema files (for example colon-style fields in `baml_src/education/lc_extraction/cross_linguistic.baml`, `baml_src/education/lc_extraction/syllabus_diagram.baml`, `baml_src/education/_shared/content_types.baml`, `baml_src/education/subjects/qpack_gaeilge.baml`, `baml_src/education/subjects/qpack_mathematics.baml`, and `baml_src/celtic/curriculum/celtic_curriculum.baml`, plus legacy function signatures in `baml_src/processing/portfolio_extraction.baml`, `baml_src/processing/named_entities.baml`, `baml_src/processing/game_content.baml`, `baml_src/processing/image_generation.baml`, `baml_src/processing/culture_extraction.baml`, and `baml_src/processing/ui_components.baml`). This change intentionally does not modify those schemas because the BIEP v1 extraction files are out of scope for this 2-3 hour CI-gate follow-up.

The CI gate is still wired as a hard gate: once those pre-existing BAML parse failures are resolved by the owning BIEP follow-up, this workflow will block PRs and pushes on any future `baml-cli test` regression.

## Changes

- Add `mise.toml` task `baml:test` → `uv run baml-cli test`.
- Keep `cic:baml:test` as an alias of `baml:test` so existing CIC naming remains aligned.
- Add `.github/workflows/baml-test.yaml` for PR, push, and manual workflow dispatch.
- Upload captured BAML CLI output as the `baml-test-results` artifact.
- Post a PR failure comment via `peter-evans/create-or-update-comment`, mirroring the CocoIndex conformance gate style from `.github/workflows/cocoindex-conformance.yaml`.
- Ignore `baml_client_tests/` local output directories.

## Out of scope

- No changes to the 7 `cianfhoghlaim/baml/education/lc_extraction/*.baml` files.
- No BAML duplicate renames.
- No streaming attribute work.
- No TypeBuilder/dynamic-schema implementation.
- No tutorial notebook work.
