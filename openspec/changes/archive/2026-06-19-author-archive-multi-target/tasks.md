# Author-Archive v1: Multi-Target Implementation Tasks

## Stage 4 — Multi-target deployment (this change)

### 4.0 target_factory.py (DONE)

- [x] Create `sruth/oideachais/dlt_utils/target_factory.py`
- [x] Define the `Target` dataclass (frozen=True, hashable)
- [x] Define the 3 canonical instances: `DEV` (local DuckDB),
      `STAGING` (MotherDuck), `PROD` (DuckLake)
- [x] `get_target(name)` reads `OIDEACHAIS_TARGET` env var, default
      `"dev"`
- [x] `validate_target_secrets(target)` raises `EnvironmentError`
      for missing required env vars
- [x] `create_pipeline_for_target(target, pipeline_name, dataset_name)`
      + the 3 shortcut functions

### 4.1 make_target.sh CLI helper (DONE)

- [x] Create `sruth/oideachais/scripts/make_target.sh` (100 LOC, executable)
- [x] Resolves target from `$1` (default `dev`)
- [x] Sources the `.env` file (if present) with `set -a` / `set +a`
- [x] Exports `OIDEACHAIS_TARGET`
- [x] Pre-flight secret check for staging and prod
- [x] Execs the user-supplied command with the target env set
- [x] `--help` output with 3 examples

### 4.2 OpenSpec change (DONE — this commit)

- [x] Create `openspec/changes/author-archive-multi-target/` with
      proposal + tasks + 1 spec delta
- [ ] `openspec validate author-archive-multi-target --strict`

### 4.3 Tests (TODO)

- [ ] `sruth/oideachais/tests/test_target_factory.py` covering the 3
      targets, get_target with env var override, secret validation,
      and the 3 shortcut functions

## Validation

```bash
# 1. Validate OpenSpec change
openspec validate author-archive-multi-target --strict

# 2. Run the helper with no command (prints the resolved target)
./sruth/oideachais/scripts/make_target.sh dev

# 3. Run the helper with a Python command
./sruth/oideachais/scripts/make_target.sh dev python -c "
from oideachais.dlt_utils.target_factory import get_target
print('target =', get_target().name)
print('destination =', get_target().destination)
"

# 4. Run the unit tests
cd oideachais
pytest tests/test_target_factory.py -v

# 5. Test the secret validator
python -c "
import os
os.environ.pop('MOTHERDUCK_TOKEN', None)
from oideachais.dlt_utils.target_factory import STAGING, validate_target_secrets
try:
    validate_target_secrets(STAGING)
except EnvironmentError as e:
    print('OK: secret validator caught missing env:', e)
"
```

## Push status

This branch is **blocked by GitHub Push Protection** on a pre-existing
Cloudflare DNS API Token in `92de91dd6` (the ancestor of this
branch). The user must rotate the token (it's a real token, not a
false positive) and rebase the branch.
