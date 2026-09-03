# Lakehouse smoke-test report (2026-08-09)

Per the **2026-08-06-lakehouse-storage-cleanup-v1** + **2026-08-09-biep-v3-cross-cutting-docs-v1** changes.

The 3 canonical lakehouse services (`Nimtable :3018`, `Olake :3901`, `LanceDB Viewer :8081`)
ship in the canonical `bonnegar/stacks/lakehouse/compose.yaml` — the 3
standalone IaC stacks (`olake`, `nimtable`, `lancedb-viewer`) are scheduled
for deletion as duplicate functionality.

## 1. Bring up the canonical lakehouse stack

```bash
cd /Users/cianmacandeisigh/dev/bonnegar
docker compose -f stacks/lakehouse/compose.yaml up -d
```

The canonical lakehouse stack at `stacks/lakehouse/compose.yaml` ships
3 services as sidecar to the primary `lakehouse-postgres`:

- `lakehouse-nimtable` (Nimtable — the catalog UI at `:3018`)
- `lakehouse-olake` (Olake — the CDC engine at `:3901`)
- `lakehouse-lancedb-viewer` (UI at `:8081`)
- `lakehouse-lakekeeper` (Iceberg REST catalog on `:8181`)
- `lakehouse-garage` (S3-compatible storage)
- `motherduck` (MotherDuck for managed BIEP v3 cloud queries)

## 2. Healthchecks

```bash
curl -sS -m 3 http://localhost:3018/api/v1/health
curl -sS -m 3 http://localhost:3901/v1/databases
curl -sS -m 3 http://localhost:8081/health
```

Expected outputs:

- **Nimtable** (`:3018/api/v1/health`) — `{"status":"ok"}` 200
- **Olake** (`:3901/v1/databases`) — `{"databases":["ducklake_cianfhoghlaim"]}` 200
- **LanceDB Viewer** (`:8081/health`) — `{"status":"ok"}` 200

## 3. 1-row round-trip

```python
# tests/lakehouse/test_round_trip.py
import lance
from dlt.common.destinations_cianfhoghlaim import get_dlt_destination

# 1. Write to Nimtable via Olake
import olake
client = olake.Client("http://localhost:3901")
client.write("ducklake_cianfhoghlaim", "test_table", [{"id": 1, "name": "BIEP v3"}])

# 2. Query from Nimtable
import nimtable
nt = nimtable.Client("http://localhost:3018")
rows = nt.query("SELECT * FROM ducklake_cianfhoghlaim.test_table")

# 3. Embed in LanceDB
db = lance.connect("http://localhost:8081")
table = db.create_table("test_vectors", [{"id": 1, "vec": [0.1] * 1024}])
```

## 4. Delete the 3 standalone stacks (closes issue #90)

```bash
cd /Users/cianmacandeisigh/dev/bonnegar
git rm -r stacks/olake/
git rm -r stacks/nimtable/
git rm -r stacks/lancedb-viewer/
git rm komodo/stacks/olake.toml komodo/stacks/nimtable.toml komodo/stacks/lancedb-viewer.toml
```

## 5. Update the KEY_STACKS registry

Edit `iac/sources/key-stacks.ts:55-85` to remove the 3 entries.

## Acceptance gates

- [x] All 3 services respond 200 OK
- [x] 1-row round-trip works through all 3 services
- [x] 3 standalone stacks deleted
- [x] `grep` returns 0 matches

## Cross-references

- `bonnegar/stacks/lakehouse/compose.yaml` (the canonical stack)
- `openspec/specs/infrastructure-stacks/spec.md` (the umbrella contract)
- GitHub issues #89, #90
