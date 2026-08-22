## ADDED Requirements

### Requirement: `iac:teardown-stack` per-host selective teardown

The system SHALL provide a new `iac:teardown-stack` command at
`bonneagar/iac/commands/teardown-stack.ts` that takes
per-host, selective teardown flags:

- `--host=<name>` — the target host (e.g. `arm1-oci` or `bunchloch`)
- `--keep=<comma-separated-list>` — the stack names that MUST
  NOT be torn down (e.g. `pangolin,infisical,komodo,forgejo`)
- `--exclude=<comma-separated-list>` — the stack names that
  MUST be torn down (used when you want to tear down
  everything except specific exceptions)
- `--include-volumes` — also `docker compose down -v` the
  named volumes
- `--force` — skip confirmation prompts
- `--dry-run` — print the planned actions without mutating
  state (the default for the first invocation)

The command SHALL be idempotent: re-running on a partially-torn-down
host is safe (delete-or-noop). The command SHALL preserve the
reverse-deploy order: stacks with `depends_on` relationships
to other stacks SHALL be torn down FIRST (the leaves of the
dependency tree), and stacks depended on by `kept` stacks
SHALL NOT be torn down (e.g. if `--keep=komodo` is passed,
then `komodo-periphery` on `bunchloch` SHALL be preserved
because it's a dependency of the Komodo Core on `arm1-oci`).

The command SHALL be registered in `bonneagar/iac/cli.ts` +
`bonneagar/package.json` `scripts` block as
`"iac:teardown-stack"` + aliased in `mise.toml` as
`mise run iac:teardown-stack`.

#### Scenario: Operator tears down the non-core subset on arm1-oci

- **WHEN** the operator runs
  `mise run iac:teardown-stack --host=arm1-oci
  --keep=pangolin,infisical,komodo,forgejo,tinyauth,pocket-id,backrest,beszel,dozzle,crowdsec,headplane,headscale,middleware-manager,garage
  --include-volumes --dry-run`
- **THEN** the command SHALL print the list of stacks that
  WOULD be torn down (88 stacks on `arm1-oci`)
- **AND** the command SHALL print the list of stacks that
  WOULD be preserved (14 stacks: the 12 core + headplane +
  headscale — the resource-sync-managed Headscale + UI
  companion)
- **AND** the command SHALL exit 0 without mutating state

#### Scenario: Operator tears down everything on bunchloch except Komodo Periphery + Newt

- **WHEN** the operator runs
  `mise run iac:teardown-stack --host=bunchloch
  --exclude=komodo-periphery,newt-bunchloch
  --include-volumes --force`
- **THEN** the command SHALL `docker compose down -v` every
  stack on `bunchloch` EXCEPT `komodo-periphery` and
  `newt-bunchloch` (which are dependencies of the arm1-oci
  control plane)
- **AND** the command SHALL write an audit record to
  `/tmp/iac-teardown-stack-{host}-{ts}.json` with the list
  of torn-down stacks + their container IDs
- **AND** the command SHALL exit 0 on success
- **AND** the local Infisical containers
  (`infisical-backend` + `infisical-db` + `infisical-redis`)
  on `bunchloch` SHALL also be torn down (per the env-var
  fallback pattern)

#### Scenario: Operator tries to tear down the Komodo Core dependency

- **GIVEN** the operator runs
  `mise run iac:teardown-stack --host=bunchloch --exclude=komodo-periphery`
- **AND** the `--keep=komodo` flag is NOT passed
- **WHEN** the command parses the dependency tree
- **THEN** the command SHALL refuse with exit 1 and the
  message
  `REFUSING TO TEAR DOWN: komodo-periphery is a dependency of
  the Komodo Core on arm1-oci. Pass --keep=komodo to preserve
  both.`
- **AND** the command SHALL NOT mutate state

#### Scenario: Operator re-runs on a partially-torn-down host

- **GIVEN** the operator previously ran
  `mise run iac:teardown-stack --host=bunchloch --exclude=komodo-periphery --force`
- **AND** 35 stacks were torn down successfully
- **WHEN** the operator re-runs the same command
- **THEN** the command SHALL be a no-op for the 35 already-torn-down
  stacks (the `docker compose down` call returns 0 because the
  compose dir still exists but the containers are gone)
- **AND** the command SHALL exit 0
- **AND** the audit record SHALL be appended (not overwritten)
  with the new run timestamp
