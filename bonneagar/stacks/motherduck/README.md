# MotherDuck - Managed DuckLake Lakehouse (SaaS reference)

MotherDuck (https://motherduck.com) is the KCG canonical cloud-managed
DuckLake lakehouse. It is a **SaaS**, not a Docker container; there is
no local `docker compose up` to run.

## Connect from bunchloch

```bash
# Test the MotherDuck connection (delegates through the
# mise-hydrated $MOTHERDUCK_TOKEN env var; see `.infisical.env`)
uv run python -c "
import duckdb
con = duckdb.connect('md:cianfhoghlaim?motherduck_token=' + open(os.environ['MOTHERDUCK_TOKEN_FILE']).read().strip())
print(con.sql('SELECT schema_name FROM information_schema.schemata').fetchdf())
"

# Run a BIEP MotherDuck Flight
python ./flights/lc_syllabus_topics_flight.py
```

## KCG integration surface

| Surface | Where | What |
|:--|:--|:--|
| BIEP Dives (4) | `bonneagar/stacks/motherduck/dives/` | Saved MotherDuck Dives (lc_syllabus_topics, lc_exam_difficulty, lc_marking_complexity, gov_circulars_archive) |
| BIEP Flights | `bonneagar/stacks/motherduck/flights/` | Scheduled Python jobs that backfill BAML rows onto the `cianfhoghlaim.lc.*` schemas |
| CocoIndex vector targets | `bonneagar/stacks/lancedb/` | 7 v1 CocoIndex Apps fan out to BOTH MotherDuck (structured) AND LanceDB (vectors) |

## Bring-up token round-trip

1. Provision a service-account at https://app.motherduck.com/settings/service-accounts
2. Store the token in the `dev-baile` Infisical vault (`motherduck/token`)
3. `bun run secrets:init` to hydrate the local `.env`
4. Connect via the duckdb Python client (or the MotherDuck MCP server)

## No container to deploy

This `compose.yaml` is intentionally a no-op placeholder (it carries
no `services:`). It exists only to satisfy the
`bun run validate-stacks` GOLD_STANDARD gate. The MotherDuck service
itself is managed by the MotherDuck team at their edge.
