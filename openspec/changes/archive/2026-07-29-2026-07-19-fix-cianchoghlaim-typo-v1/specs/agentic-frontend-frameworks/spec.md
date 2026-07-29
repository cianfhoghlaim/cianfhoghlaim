## MODIFIED Requirements
### Requirement: OpenChamber default theme
The canonical OpenChamber theme SHALL be `cianfhoghlaim-dark` (with the spelled-out `cianfhoghlaim` brand prefix).

#### Scenario: Compose + Komodo + .env.example use the correct theme name
- **WHEN** the OpenChamber stack declares its default theme
- **THEN** `OPENCHAMBER_THEME` SHALL default to `cianfhoghlaim-dark` in `compose.yaml`, `compose.dev.yaml`, `.env.example`, and the `openchamber-arm1-oci.toml` Komodo stack
