# Spec Delta: tuatha-platform

## ADDED Requirements

### Requirement: Modal burst-training handoff

The system SHALL support handing off ML training jobs that
exceed MacBook M4 capacity (>13B parameter models, multi-GPU
training, or full-corpus processing) to Modal's H100 GPU pool,
with the trained artifacts synced back to Garage S3 for
llama-swap local serving.

#### Scenario: Modal H100 training handoff

- **GIVEN** a BAML extraction / Unsloth / TRL training script
  configured for local execution on `bunchloch` (M4 Mac)
- **WHEN** the training run is wrapped in a Modal decorator
  (`@app.function(gpu="H100", timeout=7200)`) and executed
  via `modal run --detach training.py`
- **THEN** Modal SHALL provision an H100, execute the
  training, and upload the resulting model artifacts to the
  configured S3 bucket
- **AND** the artifacts SHALL be downloadable back to
  `bunchloch` for llama-swap serving

### Requirement: Babylon.js game client (3D)

The system SHALL provide a Babylon.js-based 3D game client
at `sruth/tuatha/game/` for the Celtic Educational MMO, rendering
interactive 3D learning environments (mathematical concepts
spatially, Celtic language family tree, gamified study areas)
via WebGL + WebGPU with Havok physics, particle systems, and
GLTF 2.0 asset loading.

#### Scenario: 3D scene renders

- **GIVEN** a student launches the Tuatha MMO client at
  `sruth/tuatha/game/`
- **WHEN** the Babylon.js Engine + Scene + ArcRotateCamera
  initialise and the GLTFLoader loads the scene assets
- **THEN** the 3D classroom / mathematical-concept / Celtic-language
  scene SHALL render at ≥60 fps on a modern GPU
- **AND** the Convex real-time state sync SHALL drive NPC
  positions, BAML-extracted dialogue, and Dagster-pipeline
  asset updates

## REMOVED Requirements

(None.)
