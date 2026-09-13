## ADDED Requirements

### Requirement: Bria Fibo Enabled

The system SHALL have `local/image/fibo: true` in `deployment-choice.yaml`
once the Familiar Dynamic NFT System change is archived.

#### Scenario: Fibo invocation works
- **WHEN** the user invokes `model_for("image_gen", "default")`
- **THEN** the function returns `"fibo"`

#### Scenario: Fibo slot in registry
- **WHEN** the user queries `MODEL_REGISTRY.filter_models("image_gen")`
- **THEN** the result SHALL include the `fibo` entry with `enabled: true`