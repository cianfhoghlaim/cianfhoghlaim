# Lakehouse — OrbStack Docker Recovery Runbook

> **Per the 2026-10-30-lakehouse-bridge-bring-up-v1 umbrella** of
> `openspec/plans/2026-10-30-platform-reset-saga-v1.md` (Umbrella 3 of 4).
> Closes Stage 8 fresh-slate handoff Gap 4 (the 12 lakehouse services
> down on `bunchloch` because the OrbStack Docker daemon socket is
> missing).
>
> **The ONLY blocker** for the 12 down services is operator-side
> OrbStack recovery. The 3 `scripts/lakehouse/` bring-up scripts +
> the 16-service compose file at `bonnegar/stacks/lakehouse/compose.yaml`
> are all ready to run as soon as Docker is reachable.

## Symptoms (how you know OrbStack is broken)

```bash
$ docker ps
Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

OR

```bash
$ docker info
Server: ERROR: failed to detect docker info
```

OR

```bash
$ mise run core:lakehouse:health
  CHECK 1: lakehouse-postgres is reachable
  [FAIL] TCP+auth to lakehouse-postgres:5433: ...
  [FAIL] (everything skipped — stub mode)
```

## Step 1 — Verify the OrbStack installation

```bash
# 1a. Confirm OrbStack is installed
ls /Applications/OrbStack.app 2>&1 || /usr/bin/ls ~/.orbstack/

# 1b. Confirm the OrbStack CLI is on PATH
which orbctl 2>&1
```

If OrbStack isn't installed at all, download it from <https://orbstack.dev/> and reinstall.

## Step 2 — Restart OrbStack

```bash
# 2a. Quit the OrbStack app (AppleScript is the most reliable on macOS)
osascript -e 'quit app "OrbStack"'

# 2b. Wait a moment
sleep 2

# 2c. Restart it
open -a OrbStack
# OR: orbstack  # if the CLI is on PATH

# 2d. Wait for OrbStack to be ready (the menu bar icon stops spinning)
sleep 5
```

## Step 3 — Verify the Docker socket

```bash
# 3a. Check the OrbStack-managed socket exists
ls -la ~/.orbstack/run/docker.sock
# Expected: srw-rw----  1 cian  staff  0 Oct 11 10:30 /Users/cianmac/.orbstack/run/docker.sock

# 3b. Confirm the standard /var/run/docker.sock symlink points to OrbStack
ls -la /var/run/docker.sock
# Expected: lrwxr-xr-x  1 root  wheel  38 Oct 11 10:30 /var/run/docker.sock -> /Users/cianmac/.orbstack/run/docker.sock
```

If the symlink in 3b is missing or points to the wrong target:

```bash
sudo ln -sf ~/.orbstack/run/docker.sock /var/run/docker.sock
```

## Step 4 — Verify the Docker context

```bash
# 4a. List the contexts
docker context ls
# Expected: NAME        DESCRIPTION   DOCKER ENDPOINT                ...
#           default *   OrbStack       unix:///Users/.../docker.sock
#           desktop                                          ...
#           orbstack                                         ...

# 4b. If the default is not orbstack, switch
docker context use orbstack
```

## Step 5 — Smoke test Docker

```bash
# 5a. Confirm docker is reachable
docker info | head -n 5
# Expected: Server Version: 24+ ... Storage Driver: overlay2 ...

# 5b. Run a hello-world
docker run --rm hello-world
# Expected: "Hello from Docker!" + a paragraph about the image
```

## Step 6 — Run the lakehouse bring-up

```bash
# 6a. The operator-side bring-up (12 services in dependency order)
mise run core:lakehouse:up
# OR: bash scripts/lakehouse/up_lakehouse_bridge.sh

# Expected: 12 services brought up over ~60s

# 6b. Initialize the 14 DuckLake databases
bash scripts/lakehouse/init_lakehouse_postgres.sh
# Expected: "✓ Lakehouse PostgreSQL initialized" + the 14 databases listed

# 6c. Verify
mise run core:lakehouse:health
# Expected: 6 per-language tables present, all checks pass
```

## Troubleshooting

### Symptom: `Cannot connect to the Docker daemon` after restarting OrbStack

**Cause**: OrbStack didn't start the dockerd socket.

**Fix**:
```bash
# Check OrbStack logs
tail -n 50 ~/.orbstack/log/orbstack.log

# Restart with verbose
osascript -e 'quit app "OrbStack"' && sleep 2 && open -a OrbStack --args --verbose
```

### Symptom: `permission denied` on `/var/run/docker.sock`

**Cause**: The `docker` CLI needs to be in the `docker` group (macOS usually has it; OrbStack may not).

**Fix**:
```bash
sudo chmod 666 /var/run/docker.sock
# OR: add yourself to the docker group
sudo dscl . -append /Groups/docker GroupMembership $(whoami)
```

### Symptom: lakehouse services up but `ducklake_cianfhoghlaim` namespace missing

**Cause**: `init_lakehouse_postgres.sh` hasn't been run (or was run before the compose stack was up).

**Fix**:
```bash
# Ensure the 12 services are up
mise run core:lakehouse:up
# Then run the init
bash scripts/lakehouse/init_lakehouse_postgres.sh
```

### Symptom: `verify_bridge.py` says `No module named 'psycopg2'`

**Cause**: The Python venv is missing the `psycopg2-binary` dep.

**Fix**:
```bash
uv pip install --python ./.venv/bin/python psycopg2-binary
```

## After OrbStack is recovered

Run `mise run core:lakehouse:health` once a day to confirm the 12 services are still green. The `lakehouse_health` marimo notebook (`notebooks/dashboards/lakehouse_health.py`) renders the status in a visual dashboard.

## See also

- `openspec/plans/2026-10-30-platform-reset-saga-v1.md` — the parent saga
- `openspec/changes/2026-10-30-lakehouse-bridge-bring-up-v1/` — this change folder
- `scripts/lakehouse/up_lakehouse_bridge.sh` — the bring-up script
- `scripts/lakehouse/init_lakehouse_postgres.sh` — the DB init
- `scripts/lakehouse/verify_bridge.py` — the smoke test
- `notebooks/dashboards/lakehouse_health.py` — the marimo dashboard
- `docs/lakehouse/` — historical smoke-test reports
- `bonneagar/stacks/lakehouse/compose.yaml` — the 16-service compose file
