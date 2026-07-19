## MODIFIED Requirements
### Requirement: Dagger module name + entry-point class
The dagger module SHALL live at `bonneagar/dagger/cianfhoghlaim_dagger/` (with the spelled-out `cianfhoghlaim` package directory name — NOT the historical `cianfhoghlaim_dagger/` typo).

The entry-point class SHALL be `CianfhoghlaimDagger` (PascalCase with the `f` present).

#### Scenario: pyproject.toml wires the correct module + class
- **WHEN** `bonneagar/dagger/pyproject.toml` declares the Dagger entry-point
- **THEN** `[project.entry-points."dagger.mod"] main_object` SHALL equal `"cianfhoghlaim_dagger:CianfhoghlaimDagger"`
- **AND** `[project] name` SHALL equal `"cianfhoghlaim-dagger"`
- **AND** `[tool.hatch.build.targets.wheel] packages` SHALL include `"cianfhoghlaim_dagger"`

### Requirement: dagger.json module name
`bonneagar/dagger/dagger.json` SHALL declare the module as `cianfhoghlaim_dagger`.

#### Scenario: dagger.json top-level name field uses the correct identifier
- **WHEN** `bonneagar/dagger/dagger.json` is read
- **THEN** the top-level `"name"` field SHALL equal `"cianfhoghlaim_dagger"`
- **AND** it SHALL NOT contain the legacy typo `cianfhoghlaim_dagger`
