# `spaces-cicd-pipeline` capability spec

> A reusable GitHub Actions workflow under `infrastructure/ci/` that any
> Space under `spaces/*/` can call via a single `uses:` reference to publish
> a directory to a Hugging Face Space.

## ADDED Requirements

### Requirement: Reusable Spaces sync workflow
The system SHALL provide a reusable GitHub Actions workflow at
`infrastructure/ci/spaces-sync.yml` that any Space can call via a single
`uses: ./infrastructure/ci/spaces-sync.yml` reference to publish a directory
to a Hugging Face Space.

#### Scenario: Gradio Space sync
- **GIVEN** a Space at `spaces/my_space/` with `sdk: gradio` in its `README.md` frontmatter
- **AND** `HF_TOKEN` and `HF_USERNAME` are configured as repo secrets/vars
- **WHEN** a push to `main` modifies any file under `spaces/my_space/`
- **THEN** the workflow SHALL install dependencies from
  `spaces/my_space/requirements.txt`
- **AND** SHALL upload the directory to
  `huggingface.co/spaces/$HF_USERNAME/my_space` via the `huggingface_hub` Python API
- **AND** the HF Space SHALL rebuild and become live within 90 seconds

#### Scenario: Static dashboard sync (subtree push)
- **GIVEN** a Space at `spaces/my_space/` with a `dashboard/` subdir
- **AND** the `static_space` input is set to a HF Space slug
- **WHEN** a push to `main` modifies any file under `spaces/my_space/dashboard/`
- **THEN** the workflow SHALL run
  `git subtree split --prefix spaces/my_space/dashboard main`
- **AND** SHALL force-push the resulting commit to
  `huggingface.co/spaces/$HF_USERNAME/$static_space`

#### Scenario: Workflow is path-filtered
- **GIVEN** the workflow is configured for `spaces/an_scrudu/`
- **WHEN** a commit touches only `spaces/anam_sruth/tuatha/`
- **THEN** the workflow SHALL NOT trigger for the an_scrudu Space

#### Scenario: Failure surfaces a readable error
- **GIVEN** the HF token is missing or expired
- **WHEN** the workflow runs
- **THEN** the workflow SHALL fail with exit code 1
- **AND** the error message SHALL include the resolved `HF_USERNAME` and the
  target Space slug

#### Scenario: Docker SDK support (deferred to follow-up)
- **GIVEN** a Space at `spaces/my_space/` with a `Dockerfile`
- **WHEN** a push to `main` modifies any file under `spaces/my_space/`
- **THEN** the workflow SHALL `docker build` the Space
- **AND** SHALL push the image to `huggingface.co/spaces/$HF_USERNAME/my_space`
  via the HF Docker registry
- **NOTE** This scenario is documented but the implementation is deferred to
  the follow-up commit that adds `infrastructure/ci/test_spaces_sync.py`.
