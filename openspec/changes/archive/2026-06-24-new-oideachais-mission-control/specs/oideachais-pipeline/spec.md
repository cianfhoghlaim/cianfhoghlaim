## ADDED Requirements

### Requirement: oideachais Mission Control Space

The oideachais quadrant MUST provide a Mission Control HuggingFace Space at `spaces/oideachais_mission_control/` that surfaces the 5 educational stages (Aistear / Primary / JC / SC / Tertiary) as marimo notebooks over the canonical MotherDuck lakehouse. The Space MUST be wired to the canonical BAML extraction + Cognee cognify + MotherDuck Dive buttons per stage.

#### Scenario: User opens the Mission Control

- **WHEN** a user navigates to the oideachais_mission_control Space
- **THEN** they see 5 tabs (one per educational stage)
- **AND** each tab shows a marimo notebook backed by MotherDuck
- **AND** each tab has a Cognee cognify button + a BAML extraction button + a MotherDuck Dive button
