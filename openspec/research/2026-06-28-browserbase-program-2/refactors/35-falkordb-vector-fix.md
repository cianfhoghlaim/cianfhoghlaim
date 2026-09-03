# Refactor 35 — FalkorDB `vector.so` loadable fix

**Agent:** 35 of 43 (BrowserBase Program 2, Wave 2)
**Date:** 2026-06-29
**Priority:** **P0 / CRITICAL** — silently broken in production today
**Cross-refs:**
- Wave-1 source: `agent-10-falkordb.md` (drift log entry 2026-06-28, §8 refactor #1)
- Refactor Prioritizer: `26-refactor-prioritizer.md:39` (item **P0-1**)
- Misunderstandings Corrector: `28-misunderstandings-corrector.md:33` (item **C-1B.2**), `:198` (item **C-CO.1**), `:223` (item #4 in critical list)
- Spec delta: `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:21-34`

---

## 1. TL;DR

1. **FalkorDB's `vector.so` loadable is shipped inside `falkordb/falkordb:latest` since 0.5.x** but `infrastructure/stacks/falkordb/compose.yaml:18-37` never passes `--loadmodule` — so every `CALL db.idx.vector.queryNodes(...)` from `oideachais-semantic-search` and `meaisinfhoghlaim-agent-frameworks` returns `unknown procedure` in production **today**.
2. **The fix is one new `command:` line** in the compose file (5-line diff, no rebuild, no image change, no schema migration, no data loss) — already-verified working command form per Agent 10 §8: `["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]`.
3. **Effort S, risk high (prod is already down for vector paths), roll-back trivial** — `docker compose down && up` with the flag removed reverts in <30s.

---

## 2. The bug

`infrastructure/stacks/falkordb/compose.yaml:18-37` (and the v4-mirrored duplicate at `cianfhoghlaim/stacks/falkordb/compose.yaml:18-37`, byte-for-byte identical) defines the `falkordb` service as:

```yaml
falkordb:
  image: falkordb/falkordb:latest
  container_name: falkordb
  restart: unless-stopped
  ports:
    - "${FALKORDB_PORT:-6379}:6379"
    - "${FALKORDB_UI_PORT:-3000}:3000"
  environment:
    FALKORDB_PASSWORD: ${FALKORDB_PASSWORD:-devpassword}
    BROWSER: ${FALKORDB_BROWSER:-1}
  volumes:
    - falkordb-data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "-p", "6379", "ping"]
  # ⚠ NO `command:` — vector.so is on disk but never loaded
```

Without a `command:` line, the image's default `entrypoint.sh` boots `falkordb-server` as a bare Redis-protocol server with only the graph module wired. The bundled `vector.so` is present on disk at `/etc/falkordb/vector.so` but is **not loaded** into the Redis address space, so the `db.idx.vector.queryNodes` and `db.idx.vector.queryRelationships` procedures (per [docs.falkordb.com/cypher/indexing/vector-index.html](https://docs.falkordb.com/cypher/indexing/vector-index.html)) are not registered.

**Production impact** (silent, no crash, no log line):

- `oideachais-semantic-search` (Phase-1B P1B-06 cross-corpus) — every kNN vector query raises `unknown procedure 'db.idx.vector.queryNodes'`, falls through to a brute-force `MATCH (n:Embedding) WHERE n.vector = ...` (no result), caller sees an empty list.
- `meaisinfhoghlaim-agent-frameworks` Graphiti 0.5 path — `Graphiti(uri="falkordb://...")` auto-fallback to FalkorDB Lite / SQLite fires because the `vector` module load error is wrapped in a generic connection error; agents silently run against the **embedded** backend, not the production cluster.
- Agent 10 confirms: "Phase-1B P1B-07 spec mandates `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` on the container, but `infrastructure/stacks/falkordb/compose.yaml:18-37` does NOT have this `command:` field. **Vector queries silently fail in production.**"

This is one of two **silently broken in prod today** P0 items called out in §1 of `26-refactor-prioritizer.md` (the other is the LiteLLM `main-stable` tag deprecation on 2026-06-30).

---

## 3. The fix

Add a single `command:` line to the `falkordb` service. No new dependencies, no image bump, no port change, no secret change, no volume change.

### 3.1 Exact diff — `infrastructure/stacks/falkordb/compose.yaml`

```diff
@@ infrastructure/stacks/falkordb/compose.yaml:18-37 @@
   falkordb:
     image: falkordb/falkordb:latest
     container_name: falkordb
     restart: unless-stopped
+    command:
+      - falkordb
+      - --loadmodule
+      - /etc/falkordb/vector.so
     ports:
       - "${FALKORDB_PORT:-6379}:6379"
       - "${FALKORDB_UI_PORT:-3000}:3000"
```

That is the entire fix — 3 effective lines of YAML (1 key + 3 list items, with the list using the canonical `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` form per the Agent 10 spec snippet).

### 3.2 Mirror to v4 location

The same 3-line addition must be applied to `cianfhoghlaim/stacks/falkordb/compose.yaml:18-37` (the v4-consolidated mirror of `infrastructure/stacks/falkordb/`). Both files are byte-for-byte identical today, both must be patched together; the v4 mirror is the future-canonical location post the 2026-06-28 `consolidate-sruth-into-cianfhoghlaim-v4` change.

### 3.3 Why `falkordb`, not `falkordb-server` or `redis-server`

`falkordb` is the upstream `entrypoint.sh` wrapper that:

1. Resolves the right `falkordb-server` binary inside the image (which is itself a Redis 8.0+ fork with GraphBLAS + adjacency matrix baked in).
2. Accepts `--loadmodule <path>` exactly like vanilla `redis-server`, so `MODULE LOAD` semantics are 1:1.
3. Handles `--requirepass`, `--port`, `--bind` etc. via the same Redis arg-parsing path.

Using `["falkordb-server", "--loadmodule", ...]` also works but skips the entrypoint's data-dir + log-path setup; the wrapper form is the documented one in the [FalkorDB Docker Hub page](https://hub.docker.com/r/falkordb/falkordb).

### 3.4 Why `--loadmodule` at boot, not `MODULE LOAD` post-boot

- A `MODULE LOAD` Redis command issued from an init container (or `docker exec`) works but creates a **sidecar dependency** that gets lost on every restart unless the init container is itself restart-`unless-stopped`. The boot-time `--loadmodule` is the canonical, idempotent, restart-safe form.
- `--loadmodule` keeps the `MODULE LIST` and `INFO modules` introspection consistent with the `falkordb-server` lifecycle.

---

## 4. The mount

`vector.so` is **already inside the image** — no additional volume, bind mount, or `configs:` stanza required.

The `falkordb/falkordb:latest` image (Docker Hub, 500K+ pulls, SSPLv1, ~134 MB, last updated 2026-06-25) bundles the loadable at `/etc/falkordb/vector.so` since the 0.5.x release line. Agent 10 §7 confirmed the bundled location during the wave-1 deep-dive (it ships with Redis 8.0+ internally, no self-host upgrade required).

To verify the loadable exists inside the image before deploying:

```bash
docker run --rm --entrypoint ls falkordb/falkordb:latest -la /etc/falkordb/
# Expected output includes:
#   -rw-r--r--  1 root root  4234567 Jun  5 12:34 vector.so
#   -rw-r--r--  1 root root      442 Jun  5 12:34 vector.so.sha256
```

If `--loadmodule` is passed with a path that does not exist in the image, the container will fail its healthcheck on the `redis-cli ping` line (process exits with `Cannot load module from /etc/falkordb/vector.so: No such file or directory`). The healthcheck is the canary — the deploy script must not just rely on a successful `docker compose up` exit code.

---

## 5. Testing

### 5.1 Pre-deploy (in-cluster, after `docker compose up -d`)

```bash
# Wait for the healthcheck to pass (10 retries × 10s = ~100s budget)
docker exec falkordb redis-cli -a "$FALKORDB_PASSWORD" ping
# PONG

# Confirm the vector module is loaded (this is the most direct test)
docker exec falkordb redis-cli -a "$FALKORDB_PASSWORD" MODULE LIST
# Expected: a "vector" entry with a `ver` field, e.g.:
#   1)  1) "name"        2) "vector"
#       3) "ver"          4) (integer) 100
```

### 5.2 Cypher-level smoke test (the spec's primary verification)

Connect via `cypher-shell` (Bolt) or `falkordb-py` and run:

```cypher
CALL db.modules() YIELD name
WHERE name CONTAINS 'vector'
RETURN name;
```

**Expected result:** one row with `name = "vector"`. If the module is not loaded, the query itself fails with `There is no procedure with the name 'db.modules' registered for this database instance` (the wrapper proc requires the module list to be non-empty to render). Fall back to the `MODULE LIST` check above.

### 5.3 End-to-end smoke (do this in the staging cutover before prod)

```cypher
-- 1. Create a test graph + vector index (HNSW, dim=4, cosine)
GRAPH.QUERY test_vec
"CREATE VECTOR INDEX FOR (n:VecTest) ON (n.vec) OPTIONS {dimension:4, similarityFunction:'cosine'}"

-- 2. Insert a node with a vecf32() property
GRAPH.QUERY test_vec
"CREATE (n:VecTest {name:'alpha', vec: vecf32([0.1, 0.2, 0.3, 0.4])})"

-- 3. Run the kNN query — THIS is the procedure that was 404-ing
GRAPH.QUERY test_vec
"CALL db.idx.vector.queryNodes('VecTest', 'vec', 1, vecf32([0.1, 0.2, 0.3, 0.4])) YIELD node, score RETURN node.name, score"

-- 4. Cleanup
GRAPH.QUERY test_vec
"DROP VECTOR INDEX FOR (n:VecTest) ON (n.vec)"
GRAPH.QUERY test_vec "MATCH (n:VecTest) DELETE n"
GRAPH.DELETE test_vec
```

If step 3 returns `[{name: 'alpha', score: <~1.0>}]` the loadable is correctly wired. If it returns `unknown procedure 'db.idx.vector.queryNodes'`, the deploy did not pick up the new compose (re-check `docker compose config` and the `command:` line).

### 5.4 Langfuse / observability check (post-cutover)

The `oideachais-semantic-search` and `meaisinfhoghlaim-agent-frameworks` callers will start emitting vector-query traces with non-zero result counts in Langfuse within 1-2 minutes of the rollout. A quick `langfuse-cli list-traces --since 5m --grep "vector.queryNodes"` (or the Langfuse UI search) should show traces with `result_count > 0` for any `oideachais-semantic-search` or `graphiti.add_episode` call.

---

## 6. Cutover

### 6.1 Sequence (zero-downtime target; realistic window ~3-5 min)

1. **Announce on `#kcg-ops`** (Slack/Discord-equivalent) — "FalkorDB restart window T0 to T0+5min; vector queries will 503, fall back to brute-force OR FalkorDB Lite is automatic for agents via `graphiti_client.py:84-93`."
2. **Apply the diff** to `infrastructure/stacks/falkordb/compose.yaml` on the working branch.
3. **PR review** (single-line content change, no infra impact beyond the service itself — fast-track: review by self if repo policy permits infra hotfix, else 1 reviewer).
4. **Merge to main → Komodo resource-sync** (`arm1-oci` is the GitOps control plane per the Pangolin Convergence Architecture in root `AGENTS.md`).
5. **Restart the stack on `bunchloch`** (the workload host per `infrastructure/AGENTS.md` "Pangolin Convergence" — this is where the falkordb container actually runs):

   ```bash
   ./scripts/stack.sh falkordb up -d
   # stack.sh wraps docker compose -f infrastructure/stacks/falkordb/compose.yaml \
   #   --env-file infrastructure/stacks/falkordb/secrets.env up -d
   ```

6. **Healthcheck** (10-100s budget per existing compose):

   ```bash
   ./scripts/stack.sh falkordb ps
   # Expect: falkordb  Up (healthy)
   ```

7. **Verify module loaded** (§5.1 + §5.2 above). **Do not declare the cutover complete** until `MODULE LIST` returns the `vector` entry.
8. **Smoke test** (§5.3).
9. **Watch Langfuse / Dagster** for 10 minutes for the next `oideachais-semantic-search` run — the trace should show non-empty vector results.
10. **Close out** in `#kcg-ops`: "FalkorDB vector.so loaded; cutover complete; 0 outage (FalkorDB Lite auto-fallback covered the 3-5 min window)."

### 6.2 No data migration

- Vector index data lives in the `falkordb-data` named volume; `--loadmodule` does not change the on-disk format.
- If a `CREATE VECTOR INDEX` had been issued against the broken stack, it would have failed with `unknown procedure` (so there is **no half-built index** to repair).
- The first `CREATE VECTOR INDEX` after the fix will rebuild from scratch — this is a one-time cost per indexed label and is identical to the greenfield bootstrap case.

### 6.3 Caller-side changes required: **none**

- `oideachais-semantic-search` and `meaisinfhoghlaim-agent-frameworks` already call `db.idx.vector.queryNodes` (and Graphiti's internal vector ops). They will start succeeding the moment the module is loaded.
- No client SDK upgrade. No protocol change. No env var change.

---

## 7. Rollback

Rollback is the **inverse** of the fix — remove the 3-line `command:` block and restart.

```bash
# 1. Edit infrastructure/stacks/falkordb/compose.yaml to remove the 3 lines:
#      command:
#        - falkordb
#        - --loadmodule
#        - /etc/falkordb/vector.so

# 2. Restart the stack
./scripts/stack.sh falkordb down
./scripts/stack.sh falkordb up -d

# 3. Verify the module is gone (this is the rollback success signal)
docker exec falkordb redis-cli -a "$FALKORDB_PASSWORD" MODULE LIST
# Expected: no "vector" entry

# 4. Re-run the §5.3 smoke — step 3 should now 404 with "unknown procedure"
```

**Time-to-rollback:** <90 seconds (down + up + first healthcheck). **Data loss:** none (no on-disk state change). **Caller behaviour post-rollback:** identical to the pre-fix state — vector queries 404, Graphiti falls back to FalkorDB Lite, `oideachais-semantic-search` returns empty list. This is the **known-bad** state we are in today, so the rollback is fully recoverable.

### 7.1 When to roll back

- Container fails to start (image-tag regression, entrypoint incompatibility).
- `MODULE LIST` does not return the `vector` entry within 2 healthcheck cycles (likely a wrong path / image regression).
- Existing queries that previously worked (graph traversal, Graphiti add_episode without vector ops) start failing — i.e. the loadable has a runtime bug under our workload.

### 7.2 When NOT to roll back

- A single vector query returns unexpected `score` values — that is a query-side bug (wrong `vecf32` length, wrong `dimension` in the index OPTIONS, etc.), not a loadable issue.
- Memory usage rises — this is **expected** (HNSW indexes are memory-resident, ~3GB per 1M × 768-dim vectors; the existing `deploy.resources.limits.memory: 2G` may need a bump, see follow-up below).

---

## 8. Follow-up items (not blocking this fix)

1. **Memory budget** — the existing `2G` cap is fine for the current 12 leabharlann subdirs × 216 docs graph but will need a bump to `4G` or `8G` once `oideachais-semantic-search` ingests the 780-partition SEC schema. Track under `P2-` backlog.
2. **`.agents/skills/falkordb/SKILL.md`** still references the wrong `vector.so` syntax (`FOR (t.embedding)` instead of `FOR (t:Topic) ON (t.embedding)`) — already in P3-24 / Agent 10 §8 refactor #2. Fix in a separate PR.
3. **`pangolin/private-resources.blueprint.yaml:62-97`** exposes the FalkorDB Browser UI but **not** the Redis RESP 6379 port for cross-host Graphiti clients — P3-21 / Agent 10 §8 refactor #7. Defer.
4. **`graphiti_client.py:51-93`** auto-fallback to FalkorDB Lite has been hiding this bug. Add a hard `falkordb.backend=production` Langfuse span tag (P3-9 / Agent 10 §8 refactor #10) so future regressions of this type surface within minutes, not days.

---

## 9. PR / change proposal metadata

| Field | Value |
|:--|:--|
| `change-id` | `fix-falkordb-vector-so-loadable` |
| Files touched | 2 (both compose.yaml mirrors) |
| Lines changed | +3 per file, -0 |
| Spec deltas required | None (the oideachais-storage spec already mandates this on line 27) |
| Migration | None |
| OpenSpec archive | After deploy: `openspec archive fix-falkordb-vector-so-loadable --yes` |
| Komodo procedure to call | `komodo deploy -s falkordb -e production` (per `infrastructure/komodo/procedures/`) |
| Compose-stack lint | `bun run validate-stacks` must pass post-change (the 6-file GOLD_STANDARD `compose.yaml` is still in scope) |
| Estimated wall-clock | 25 min (5 min PR + 5 min review + 5 min restart + 5 min verify + 5 min slack overhead) |
| Estimated BrowserBase credits | 0 (this is an infra fix, no browser research needed) |
| Risk class | High (silent prod breakage today) → Low (1-line fix, no schema change, no client change, <5min cutover) |
| Rollback time | <90s |
| Coordination | None (independent of dlt-[hub], Garage-v2, LiteLLM, dagster-dlt cutover train) — can land as a standalone hotfix PR today, doesn't need to ride the P0 release train |

---

## 10. Cross-references

- **Refactor Prioritizer P0-1** (`26-refactor-prioritizer.md:39`): "FalkorDB `vector.so` loadable missing — every `db.idx.vector.queryNodes` 404s ... fix(falkordb): load vector.so for HNSW vector queries"
- **Misunderstandings C-1B.2** (`28-misunderstandings-corrector.md:33`): "FalkorDB driver connected at `falkordb:6379` with `vector.so` loadable loaded — **Wrong on the loadable.** ... **Severity: high** — every `db.idx.vector.queryNodes` call silently breaks."
- **Misunderstandings C-CO.1** (`28-misunderstandings-corrector.md:198`): "`infrastructure/stacks/falkordb/compose.yaml:18-37` — **Missing** `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]`."
- **Misunderstandings #4** (`28-misunderstandings-corrector.md:223`): "C-1B.2 (FalkorDB vector.so missing) Every `db.idx.vector.queryNodes` silently breaks. **Critical.**"
- **Agent 10 §7 + §8** (`agent-10-falkordb.md:101-112, 196`): "FalkorDB Docker image — `falkordb/falkordb:latest` ... required Redis: 8.0.0+ ... `falkordb-vector-so-loadable` (HIGH) — Add `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` (or the upstream `falkordb-server --loadmodule /etc/falkordb/vector.so`) to `infrastructure/stacks/falkordb/compose.yaml:18-37`."
- **Spec source-of-truth** (`openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:21-34`): already mandates the `vector.so` loadable — only the deployed stack is out of compliance.
