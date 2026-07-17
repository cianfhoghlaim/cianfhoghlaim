# Per-Domain BAML Merger Plan

> **Per Plan v6 Phase F3 (merge 6 BAML source trees into 1).**
> **Per user constraint ("1 wait")** - this is the per-domain subplan, not the full merger (wait means defer the pyproject merger).

## 1. Current BAML source trees (6 redundant)

| Tree | Path | Notes |
|---|---|---|
| `_catalog/` | `core/baml/_catalog/` | Lookup tables (BAML sidekick) |
| `_croilar_baml/` | `core/baml/_croilar_baml/` | Croilar-specific |
| `_croilar_src/` | `core/baml/_croilar_src/` | Croilar implementation |
| `_meaisinfhoghlaim_src/` | `core/baml/_meaisinfhoghlaim_src/` | Meaisínfhoghlaim |
| `_cianfhoghlaim_src/` | `core/baml/_cianfhoghlaim_src/` | Oideachais (largest) |
| `_tuatha_src/` | `core/baml/_tuatha_src/` | Tuatha |

## 2. Per-domain merger plan

### Domain 1: shared/ (cross-cutting functions)
- Move `core/baml/_catalog/` → `core/baml/shared/catalog/`
- Move all `core/baml/_*/shared/` files → `core/baml/shared/`
- This is the FIRST step (lowest risk, foundation)

### Domain 2: _cianfhoghlaim_src/ → cianfhoghlaim/ (the largest)
- Move all `.baml` files from `core/baml/_cianfhoghlaim_src/` to `core/baml/cianfhoghlaim/`
- Update all `import` statements
- This is the SECOND step (per-domain, the largest)

### Domain 3: _meaisinfhoghlaim_src/ → meaisinfhoghlaim/
- Move to `core/baml/meaisinfhoghlaim/`
- Update imports

### Domain 4: _tuatha_src/ → tuatha/
- Move to `core/baml/tuatha/`
- Update imports

### Domain 5: _croilar_src/ + _croilar_baml/ → croilar/
- Merge the 2 croilar trees into 1: `core/baml/croilar/`
- This consolidates duplicated croilar code

### Domain 6: clients.baml (the SHARED single source of truth)
- ONE `core/baml/clients.baml` with all 9 named clients
- This was Wave 1's R1 - move all 6 `clients.baml` copies into 1
- Replace all inline `client "anthropic/..."` calls (8 occurrences) with `client ExtractEnStrong`

## 3. Per-domain validation criteria

For each domain:
1. ✅ BAML CLI compiles (`baml-cli generate`)
2. ✅ All generated Python types in correct locations
3. ✅ All existing BAML function imports work
4. ✅ All BAML tests pass (per-domain test files)
5. ✅ Type checking (mypy) passes

## 4. Total timeline

- 6 domains × ~1 week each = 6 weeks
- With 1-person squad: 6 weeks sequential
- With 2-person squad: 3 weeks parallel

## 5. Dependencies

- Requires Plan v5 Phase B (P0 + P1 including BAML 0.223.0 upgrade) DONE
- Requires P1-1 (BAML inline client fix) DONE
- Can run in parallel with other Phase F tasks

## 6. Risk per domain

| Domain | Risk | Reason |
|---|---|---|
| shared/ | LOW | No business logic, just utilities |
| cianfhoghlaim/ | HIGH | Largest tree, most usage |
| meaisinfhoghlaim/ | MED | Has agent fleet integration |
| tuatha/ | LOW | Smaller surface |
| croilar/ | LOW | Smaller surface |
| clients.baml | HIGH | Affects EVERY domain |

## 7. Order recommendation

**shared/ FIRST, clients.baml LAST** (because clients.baml affects every domain). The 4 domain merges (oideachais, meaisinfhoghlaim, tuatha, croilar) can happen in parallel.

## 8. Why we WAIT on the full pyproject merger

Per user "1 wait" - the user wants to delay the pyproject merger because:
- Multiple domain teams are still using their own pyproject
- Wait for all 5 web apps to be on shared deps (Phase F8)
- Wait for BAML 0.223 upgrade to complete
- Wait for audit feedback from production deploy

The full rewrite (Plan v6 Phase F) requires the pyproject merger, but we wait until the per-domain merges are stable.

## 9. Pre-merge checklist

Before BAML merger starts:
- [ ] All P0 + P1 fixes DONE (BAML 0.223 + FalkorDB vector.so + Garage v2.3.0 + Dagster DltLoadCollectionComponent pattern)
- [ ] All 9 BAML clients defined in single `clients.baml`
- [ ] 8 inline `client "anthropic/..."` calls removed
- [ ] All 5 web apps using shared BAML types
- [ ] Staging environment has the new structure deployed
- [ ] 1-week production shadow run shows identical outputs
