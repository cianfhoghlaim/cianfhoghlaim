# Spec Delta: tuatha-ragas

## ADDED Requirements

### Requirement: The anam_color_anchor metric asserts ΔE ≤ 8 between source and derived colors

The system SHALL register a `anam_color_anchor` metric that computes the
CIE76 ΔE between every `source.color_hex` and the corresponding
`anam_particles.anam_color_hex`. The metric SHALL pass when every row
has ΔE ≤ 8 (the threshold for "perceptually anchored but allowed to
drift toward the ANAM palette").

#### Scenario: An hallucinated color is rejected by the asset_check

- **WHEN** the `anam_particles` table has any row where the derived
  `anam_color_hex` is more than ΔE 8 away from its source `color_hex`
- **THEN** the RAGAS asset_check SHALL fail with severity=WARN (or ERROR).
