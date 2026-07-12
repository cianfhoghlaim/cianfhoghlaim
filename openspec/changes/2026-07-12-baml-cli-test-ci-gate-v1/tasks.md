# Tasks: baml-cli test CI gate

## 1. Inspect existing BAML test blocks

- [x] 1.1 Inspect `baml/clients.baml` route tests.
- [x] 1.2 Inspect `baml/processing/docs_skills_extraction.baml` smoke test.
- [x] 1.3 Count all `test` blocks under `baml/**/*.baml`.
  - Result: 37 total test blocks across 13 `.baml` files.

## 2. Verify local `baml:test` entrypoint

- [x] 2.1 Confirm `baml-cli test` is available in the uv environment.
- [x] 2.2 Add missing `mise run baml:test` task that runs `uv run baml-cli test`.
- [x] 2.3 Repoint `cic:baml:test` to the canonical `baml:test` task.
- [x] 2.4 Run `mise run baml:test` locally and document current failure mode.
  - Result: BAML CLI starts and validates the project, then fails on pre-existing non-v0.223 BAML syntax in out-of-scope schema files before test execution.

## 3. Create GitHub Actions workflow

- [x] 3.1 Add `.github/workflows/baml-test.yaml`.
- [x] 3.2 Trigger on pull requests and pushes targeting `pick-4-biep-v1` and `main`.
- [x] 3.3 Add `workflow_dispatch` for manual runs.
- [x] 3.4 Install Python, uv, mise, and package dependencies.
- [x] 3.5 Run `mise run baml:test` from `cianfhoghlaim/`.

## 4. Make the workflow a hard gate

- [x] 4.1 Let the `Run baml-cli test` step fail the job on non-zero exit.
- [x] 4.2 Upload captured CLI output to `baml-test-results` with `if: always()`.
- [x] 4.3 Add an optional PR failure comment using `peter-evans/create-or-update-comment@v4`.

## 5. Validate

- [x] 5.1 Validate `.github/workflows/baml-test.yaml` as YAML.
- [x] 5.2 Add OpenSpec spec delta for `oideachais-baml-schemas`.
- [x] 5.3 Run `openspec validate 2026-07-12-baml-cli-test-ci-gate-v1 --strict`.
