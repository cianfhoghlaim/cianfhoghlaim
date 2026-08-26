## MODIFIED Requirements

### Requirement: 6 new tutorial tasks in mise.toml

Bonneagar SHALL provide 6 tutorial tasks in `mise.toml` (`tutorial:01-env` through `tutorial:05-duchas-htr` + `tutorial:all`). These run the 5 tutorial marimo notebooks + the orchestrator.

#### Scenario: 5 tutorial tasks + 1 orchestrator

- **GIVEN** the 5 tutorial marimo notebooks exist (`notebooks/31_onboarding_01_env_check.py` through `notebooks/35_onboarding_05_duchas_htr.py`)
- **WHEN** the operator runs `mise tasks ls | grep tutorial`
- **THEN** 6 tasks are listed (`tutorial:01-env` + `tutorial:02-first-chat` + `tutorial:03-walkthrough` + `tutorial:04-biep-ocr` + `tutorial:05-duchas-htr` + `tutorial:all`)

#### Scenario: `mise run tutorial:all` walks the user through the 5 tutorials

- **WHEN** a fresh user runs `mise run tutorial:all`
- **THEN** the 5 tutorials run in order
- **AND** the user is guided through env check -> first Unsloth chat -> 4-stack walkthrough -> BIEP OCR eval -> Dúchas HTR
- **AND** the total walkthrough takes ~50 min

### Requirement: `scripts/verify-unsloth-serve.sh` for the 7-step verification

Bonneagar SHALL provide `scripts/verify-unsloth-serve.sh` that runs the 7-step verification protocol (per the prior `2026-08-21-unsloth-v5-architecture-refinement-v1` change).

#### Scenario: `mise run tutorial:verify` exits 0

- **WHEN** the operator runs `mise run tutorial:verify`
- **THEN** the script runs all 7 steps
- **AND** exits 0 if all steps pass
- **AND** prints a clear pass/fail summary
