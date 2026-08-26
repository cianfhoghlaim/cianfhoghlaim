# Spec Delta: tuatha-anam-particles

## ADDED Requirements

### Requirement: The ANAM particle joiner maps every source row to a Tuatha Dé deity + ANAM color

The system SHALL run the BAML `MapToAnamParticle` function over every
row from the 3 source tables (hades.boons, comic.particles, gba.magic)
and emit a row into `cianfhoghlaim.tuatha.anam_particles` per source row.

The mapping SHALL pick one `celtic_deity` from the `CelticDeity` enum
based on the source god / character / element and SHALL derive an
`anam_color_hex` within the ANAM turquoise/blue palette.

#### Scenario: An Hades Zeus boon maps to Taranis

- **WHEN** a row in `hades.boons` has `god=Zeus` and `tier=Legendary`
- **THEN** the joiner SHALL emit an AnamParticle row with
  `celtic_deity=Taranis` and `anam_motion="thunder strike"`.
