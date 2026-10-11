# baml-repair-follow-up Specification

## Purpose
The 4 platform-reset saga umbrellas (PRs #209-#212) shipped on
2026-10-30. Umbrella 2 (`2026-10-30-biep-tertiary-baml-repair-v1`,
PR #210) reduced the BAML `baml-cli generate` error count from 21
to 3. The remaining 3 are a `baml-py 0.226.1` parser bug that cannot
be fixed in code (proven by 6+ minimal repros in fresh test dirs).

This spec captures the diagnosis + the 2 follow-up paths + the
honest scope: this change is doc-only. The actual BAML build fix
is the next-saga's job (either a `baml-py >= 0.30+` major bump
or a vendored baml-py fork with a targeted parser patch).

Per the 2026-10-30-baml-repair-follow-up-v1 change (deferred
follow-up to the 4 platform-reset umbrellas).

## ADDED Requirements

### Requirement: The 3 errors are diagnosed and reproducible

The system MUST document the 3 remaining BAML `baml-cli generate`
errors and prove via minimal repros that the errors are parser bugs
(not code issues). The repros MUST use a fresh test dir (no other
BAML files) + the real `baml_src/clients.baml` (so the named
clients are defined) + a single test.baml file.

#### Scenario: A developer re-runs the diagnosis
- **GIVEN** a developer with `baml-cli 0.226.1`
- **WHEN** they copy `baml_src/clients.baml` to a fresh test dir + create
  a single test.baml with `function TestFunc1() -> string { client Primary; prompt #"test" }`
- **THEN** the `baml-cli generate` fails with the same error:
  "This line is invalid. It does not start with any known Baml schema keyword."
- **AND** the test passes (the parser is broken in isolation; not
  specific to the 3 affected files)

### Requirement: The 2 follow-up paths are documented

The change's `proposal.md` MUST document:
- **Path A**: `baml-py >= 0.30+` major bump (the upstream fix; risk: HIGH;
  requires updating the BAML CLI binary too)
- **Path B**: vendor a baml-py fork with a targeted parser fix (the
  surgical fix; risk: MEDIUM; long-term maintenance commitment)

For each path, the proposal MUST include:
- The exact `pyproject.toml` change
- The exact `uv pip install` command
- The risk assessment (breaking changes, regression potential)
- The estimated time + the number of files affected

#### Scenario: The next-saga team picks a path
- **GIVEN** a future operator has read the proposal
- **WHEN** they choose Path A (the upstream fix) or Path B (the surgical fix)
- **THEN** they have a clear plan + a clear risk profile + a clear
  estimate to start the work
- **AND** the validation (baml-cli generate exits 0) is the headline
  success metric for either path

### Requirement: No code changes ship in this change

The system MUST ship this change with **zero code edits** to the
BAML surface. The working tree MUST be at the same 4-error baseline
that Umbrella 2 left it in. The change is a doc-only seed for the
next saga.

#### Scenario: An operator runs baml-cli generate after this change
- **GIVEN** a fresh clone of main after this change lands
- **WHEN** `./.venv/bin/baml-cli generate --from ./baml_src` runs
- **THEN** the error count is exactly 4 (same as the pre-change baseline)
- **AND** the 3 errors are the same 3 (no new errors introduced; no
  errors fixed)

### Requirement: `baml-py` 0.22x is the ceiling for the current BAML CLI

The system MUST keep the BAML CLI on the 0.22x series (currently
0.226.1). Upgrading the BAML CLI binary to 0.30+ without also
upgrading baml-py to 0.30+ is unsupported (the CLI 0.30+ requires
baml-py 0.30+; the CLI 0.22x is paired with baml-py 0.22x).

#### Scenario: An operator tries a mismatched bump
- **GIVEN** a developer has baml-py 0.30+ installed but baml-cli 0.226.1
- **WHEN** they run `baml-cli generate`
- **THEN** the CLI errors with an incompatible-version message
- **AND** the developer must pin both to the same 0.30+ line (Path A)
  or keep both on 0.22x (the current state)

## Reference

- The saga plan: `openspec/plans/2026-10-30-platform-reset-saga-v1.md`
- The 4 platform-reset umbrellas: PRs #209, #210, #211, #212
- The saga-closure follow-on: PR #213
- The 3 unfixable errors' original F1 entry: `openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/tasks.md`
- The PyPI baml-py versions: `https://pypi.org/pypi/baml-py/`
