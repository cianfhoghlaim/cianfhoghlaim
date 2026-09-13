## ADDED Requirements

### Requirement: Zero `import dlt_sources` references under orchestration/defs

The `orchestration/defs/` tree in cianfhoghlaim SHALL contain
zero files that use the pre-v7 `import dlt_sources` statement
that resolves to the old domain path.

#### Scenario: grep returns zero matches

- **WHEN** an operator runs `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__`
- **THEN** the output MUST be empty
- **AND** the 3 known broken files MUST each have been migrated to the canonical dlt import path
