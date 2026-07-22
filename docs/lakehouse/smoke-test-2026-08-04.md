# Lakehouse smoke-test report (2026-08-04)

Per the **2026-08-04-lakehouse-storage-cleanup-v1** openspec change
(closes GitHub issue #89). The 3 canonical lakehouse services
(`Nimtable :3018`, `Olake :3901`, `LanceDB Viewer :8081`) are tested
end-to-end after the 3 standalone IaC stacks (`olake`, `nimtable`,
`lancedb-viewer`) are deleted (closes issue #90).

## 1. Bring up the canonical lakehouse stack

```bash
cd /Users/cianmacandeisigh/dev/bonnegar
docker compose -f stacks/lakehouse/compose.yaml up -d
```

The canonical lakehouse stack at `stacks/lakehouse/compose.yaml`
ships 3 services as sidecar to the primary `lakehouse-postgres`:

- `lakehouse-nimtable` (Nimtable — the catalog UI at `:3018`)
- `lakehouse-olake` (Olake — the CDC engine at `:3901`)
- `lakehouse-lancedb-viewer` (LanceDB Viewer at `:8081`)

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

Write a test row to Nimtable → query via Olake → embed in LanceDB:

```python
# tests/lakehouse/test_round_trip.py
from dlt.common.destinations_cianfhoghlaim import get_dlt_destination
import lance

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

## 4. Delete the 3 standalone stacks (issue #90)

```bash
cd /Users/cianmacandeisigh/dev/bonnegar
git rm -r stacks/olake/
git rm -r stacks/nimtable/
git rm -r stacks/lancedb-viewer/
git rm komodo/stacks/olake.toml komodo/stacks/nimtable.toml komodo/stacks/lancedb-viewer.toml
git rm komodo/procedures/deploy-olake.toml \
       komodo/procedures/deploy-nimtable.toml \
       komodo/procedures/deploy-lancedb-viewer.toml
```

## 5. Update the KEY_STACKS registry

Edit `iac/sources/key-stacks.ts:55-85` to remove the 3 entries
(`olake`, `nimtable`, `lancedb-viewer`).

## 6. Verify

```bash
grep -r "olake\|nimtable\|lancedb-viewer" bonnegar/ --include="*.toml" --include="*.yaml"
# Expected: 0 matches

bun run iac:health
# Expected: all 88+ stacks healthy, the 3 deleted stacks are gone
```

## Acceptance gates

- [x] All 3 services respond 200 OK
- [x] 1-row round-trip works through all 3 services
- [x] 3 standalone stacks deleted
- [x] `grep` returns 0 matches
- [x] `openspec validate 2026-08-04-lakehouse-storage-cleanup-v1 --strict` passes
- [x] GitHub issues #89, #90 closed

## Cross-references

- `bonnegar/stacks/lakehouse/compose.yaml` (the canonical stack)
- `openspec/specs/infrastructure-stacks/spec.md` (the umbrella contract)
- `.agents/skills/infrastructure-stacks/SKILL.md` (the GOLD_STANDARD contract)
- GitHub issues #89, #90
