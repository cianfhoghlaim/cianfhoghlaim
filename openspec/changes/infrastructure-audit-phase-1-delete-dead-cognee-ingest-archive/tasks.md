# Tasks: Delete dead `infrastructure/scripts/cognee-ingest-archive.py`

## 1. Validate change

- [x] 1.1 Run `openspec validate infrastructure-audit-phase-1-delete-dead-cognee-ingest-archive --strict`

## 2. Delete dead script

- [x] 2.1 Delete `infrastructure/scripts/cognee-ingest-archive.py` (434 lines)

## 3. Verify

- [x] 4.1 Confirm `cognee-ingest-docs.py` (the active sibling) is unchanged
- [x] 4.2 Run `mise run lint:skills` (must remain 123/123)

## 4. Spec delta + audit trail

- [x] 5.1 Add 1 ADDED Requirement to `openspec/specs/indexing-and-cognition/spec.md`: no-dead-cognee-ingest-archive-script

## 5. Commit + push + archive

- [x] 6.1 `git add` only the deleted file + the spec delta
- [x] 6.2 Commit (refactor)
- [x] 6.3 Push
- [x] 6.4 `openspec archive infrastructure-audit-phase-1-delete-dead-cognee-ingest-archive --yes`
- [x] 6.5 Commit (spec delta + archive)
- [x] 6.6 Push