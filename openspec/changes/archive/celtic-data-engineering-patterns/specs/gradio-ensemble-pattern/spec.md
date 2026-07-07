# `gradio-ensemble-pattern` capability spec

> Codifies the Gradio ensemble UI pattern (one `Interface` with one
> `output` Textbox per model) demonstrated by the prior-art
> `spaces/anti-phish/6_Gradio_Front_End.ipynb` (cell 8), plus the HF Hub
> model publish pattern (`foghlaimeoir/phishing-DistilBERT`).

## ADDED Requirements

### Requirement: Ensemble Gradio helper
The system SHALL provide `sruth/meaisinfhoghlaim/pipelines/ensemble_gradio.py`
exposing `build_ensemble_interface(models, examples, title)` that returns a
`gradio.Interface` with one output Textbox per model.

#### Scenario: Multi-model Gradio Interface
- **GIVEN** 3 models (sklearn pickle, HF pipeline, regex fallback) are passed in
- **WHEN** `build_ensemble_interface(models={...}, examples=[...], title="...")` is called
- **THEN** the returned Interface SHALL have 1 input textbox
- **AND** SHALL have N output Textboxes (one per model, N=3 in this case)
- **AND** SHALL NOT enable `allow_flagging`

#### Scenario: Examples are populated
- **GIVEN** `examples=["example 1", "example 2"]`
- **WHEN** the Interface is launched
- **THEN** the examples SHALL appear in the Gradio Examples component
- **AND** clicking an example SHALL populate the input textbox

### Requirement: HF Hub push helper
The system SHALL provide `spaces/_common/hf_hub_push.py` exposing
`push_model_to_hub(local_dir, repo_id, commit_message)` that uploads a local
directory to a HF Hub model repo using `huggingface_hub.HfApi.upload_folder`.

#### Scenario: Upload a fine-tuned model
- **GIVEN** `local_dir=Path("models/phishing-distilbert")` contains weights + tokenizer
- **AND** `repo_id="cianfhoghlaim/phishing-distilbert"`
- **WHEN** `push_model_to_hub(local_dir, repo_id, "Initial upload")` is called
- **THEN** the directory SHALL be uploaded to
  `huggingface.co/cianfhoghlaim/phishing-distilbert`
- **AND** a commit SHALL be created with the given message
- **AND** the function SHALL return the commit SHA

#### Scenario: Token from env
- **GIVEN** `HF_TOKEN` is set in the env
- **WHEN** `push_model_to_hub` is called
- **THEN** the helper SHALL use the env token
- **AND** SHALL NOT require a `token=` kwarg

### Requirement: Spaces can publish via the reusable workflow
Every Space under `spaces/*/.github/workflows/sync.yml` SHALL use the
reusable workflow from `infrastructure/ci/spaces-sync.yml` rather than
inlining the `git subtree split` + `git push` logic.

#### Scenario: Deployed Space uses the reusable workflow
- **GIVEN** `spaces/an_scrudu/.github/workflows/sync.yml` exists
- **THEN** it SHALL contain exactly one `uses:` line referencing
  `./infrastructure/ci/spaces-sync.yml`
- **AND** it SHALL NOT contain raw `git push` commands
