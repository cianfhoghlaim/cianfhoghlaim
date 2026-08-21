## MODIFIED Requirements

### Requirement: DuckLake namespace root is `cianfhoghlaim`, not `oideachais`

The system SHALL use `cianfhoghlaim` (not `oideachais`) as the root
namespace across the entire Cianfhoghlaim platform — DuckLake
namespaces, LanceDB tables, BAML schemas, Dagster asset keys, openspec
specs, the web app directory, and Python module names.

The canonical shape SHALL be:
```
cianfhoghlaim.<domain>.<jurisdiction>.<stage>[.<board>].<subject>[.<variant>]
```

#### Scenario: All namespaces use `cianfhoghlaim` root

- **WHEN** `grep -rn "oideachais\." baml_src/british_isles/ dlt/british_isles/
   cocoindex_flows/subjects/ cocoindex_flows/british_isles/ dlt/common/ motherduck/
   orchestration/ web/apps/cianfhoghlaim-web/ web/hono-api/ openspec/specs/
   openspec/changes/ .agents/ AGENTS.md README.md mise.toml docs/`
  runs after the migration
- **THEN** zero non-`_legacy`/non-`commonwealth`/non-`api_sources`/non-`archive` matches appear
- **AND** `dlt/common/destinations_cianfhoghlaim.py:DEFAULT_NAMESPACE == "cianfhoghlaim"`

#### Scenario: Web app dir is `cianfhoghlaim-web`

- **WHEN** the web app is inspected
- **THEN** the directory SHALL be `web/apps/cianfhoghlaim-web/` (NOT `web/apps/oideachais-web/`)
- **AND** `web/apps/cianfhoghlaim-web/package.json:name == "cianfhoghlaim-web"`