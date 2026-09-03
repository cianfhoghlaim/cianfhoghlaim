# Dagger Pipelines — MODIFIED requirements for v5 (Bonneagar drift refactor)

## ADDED Requirements

### Requirement: iac-bootstrap Dagger Function

The Dagger module SHALL expose an `iac_bootstrap()` function
at `bonneagar/dagger/cianfhoghlaim_dagger/` that wraps
`bun run iac:bootstrap`. The function MUST take the 4 IaC
config values (Pangolin URL, Komodo URL, Infisical URL,
Pangolin org ID) as Dagger secret args + the 5 IaC auth
values (Komodo password, Pocket ID client_id +
client_secret, Infisical client_id + client_secret) as
Dagger secret args.

The function SHALL invoke the IaC inside a Bun container +
SHALL report the 8-phase progress as Dagger container logs
(one structured log line per phase, for observability via
Langfuse).

#### Scenario: iac-bootstrap succeeds in CI

- **GIVEN** a merge to `main` on
  `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway`
- **WHEN** the Dagger `iac_bootstrap` function runs in CI
- **THEN** the IaC `iac:bootstrap` SHALL complete all 8
  phases
- **AND** the CI SHALL exit 0 only if all 8 phases
  succeed
- **AND** the Dagger function SHALL emit a structured log
  line per phase

### Requirement: TypeScript Submodule Preservation

The `bonneagar/dagger/ts_submodules/bonneagar/` directory MUST
be preserved (not deleted) as the canonical TypeScript
implementation of the Dagger control-plane logic (per the v5
user decision: "we also use TS not Python only"). The
submodule README SHALL accurately document:

- The actual engine version (`v0.19.2` per the submodule's
  `dagger.json`)
- The actual entry point (the TS-side `Dagger` object)
- The actual file count (34 .ts files)
- The actual cross-module composition pattern (how the
  Python root invokes the TS submodule functions)
- The known limitations (deprecated decorators removed in
  Dagger v0.16.0; the submodule requires a Dagger v0.19+
  engine to compile via `dagger develop --codegen`)

The `bonneagar/dagger/README.md` (root) SHALL also be
rewritten to reflect the dual-language architecture (Python
+ TypeScript) and the actual state of the codebase.

#### Scenario: ts_submodules README reflects reality

- **WHEN** `cat bonneagar/dagger/ts_submodules/bonneagar/README.md`
- **THEN** the file count claim matches the actual
  `find bonneagar/dagger/ts_submodules/bonneagar/src -name '*.ts' | wc -l`
- **AND** the engine version matches
  `ts_submodules/bonneagar/dagger.json` line 3
- **AND** the cross-module composition is documented with
  at least one concrete example (`python` module calling
  into `ts_submodules/bonneagar/src/*.ts`)

#### Scenario: ts_submodules is not consumed by any code path

- **WHEN** `rg -n 'ts_submodules|Module\(|import_module' bonneagar/dagger/cianfhoghlaim_dagger/`
  is run
- **THEN** the Python module SHALL reference the TS
  submodule's directory at least once (in the docstring)
  but SHALL NOT have any runtime dependency on it (the
  cross-module composition is via `dagger -m bonneagar`,
  not via Python imports)

## Cross-references

- [`bonneagar-iac-merge`](../bonneagar-iac-merge/spec.md) —
  the IaC `iac:bootstrap` command this wraps
- [`bonneagar-komodo-gitops`](../bonneagar-komodo-gitops/spec.md) —
  the Komodo resource-sync pattern this wires in via
  Phase 7 of the 8-phase state machine
