# Self-Hosted Docker Dagster Deploy (canonical KCG pattern)

The KCG stack uses **self-hosted Docker** for the production Dagster
deploy (not Dagster+ Hybrid). The pattern is from the official
`docs/dagster/integrations/deploy/` example (deleted with the
`sync-skills-from-docs` change).

## 4-service topology

```yaml
# docker-compose.yml
version: "3.7"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: dagster
      POSTGRES_PASSWORD: dagster
      POSTGRES_DB: dagster
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dagster"]
      interval: 10s
      timeout: 5s
      retries: 5

  user_code:
    build:
      context: .
      dockerfile: Dockerfile_user_code
    command: dagster api grpc -h 0.0.0.0 -p 4000 -m dagster_module
    volumes:
      - ./dagster_module:/app/dagster_module
    environment:
      DAGSTER_POSTGRES_HOST: postgres
      DAGSTER_POSTGRES_USER: dagster
      DAGSTER_POSTGRES_PASSWORD: dagster
      DAGSTER_POSTGRES_DB: dagster

  webserver:
    build:
      context: .
      dockerfile: Dockerfile_dagster
    command: dagster-webserver -h 0.0.0.0 -p 3000
    ports:
      - "3000:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      DAGSTER_POSTGRES_HOST: postgres
      DAGSTER_POSTGRES_USER: dagster
      DAGSTER_POSTGRES_PASSWORD: dagster
      DAGSTER_POSTGRES_DB: dagster
    depends_on:
      postgres:
        condition: service_healthy

  daemon:
    build:
      context: .
      dockerfile: Dockerfile_dagster
    command: dagster-daemon run
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      DAGSTER_POSTGRES_HOST: postgres
      DAGSTER_POSTGRES_USER: dagster
      DAGSTER_POSTGRES_PASSWORD: dagster
      DAGSTER_POSTGRES_DB: dagster
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres-data:
```

## `dagster.yaml` (the daemon config)

```yaml
# dagster.yaml
scheduler:
  module: dagster.core.scheduler
  class: DagsterDaemonScheduler

run_coordinator:
  module: dagster.core.run_coordinator
  class: QueuedRunCoordinator

run_launcher:
  module: dagster_docker
  class: DockerRunLauncher
  config:
    env_vars:
      - DAGSTER_POSTGRES_HOST=postgres
      - DAGSTER_POSTGRES_USER=dagster
      - DAGSTER_POSTGRES_PASSWORD=dagster
      - DAGSTER_POSTGRES_DB=dagster
    network: dagster_network
    container_kwargs:
      volumes:
        - /tmp/dagster_tmp:/tmp/dagster_tmp
```

## `workspace.yaml`

```yaml
# workspace.yaml
load_from:
  - grpc_server:
      host: user_code
      port: 4000
      location_name: "cianfhoghlaim"
```

## `Dockerfile_dagster` (webserver + daemon)

```dockerfile
FROM python:3.12-slim

RUN pip install --no-cache-dir \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker

EXPOSE 3000
```

## `Dockerfile_user_code`

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dagster_module /app/dagster_module

ENV DAGSTER_HOME=/app/dagster_home
```

## KCG production usage

The KCG stack runs this same 4-service topology on `bunchloch` (M4
Mac) + `arm1-oci` (ARM). The Docker Compose file is at
`infrastructure/stacks/dagster/`, with:

- `compose.yaml` (the 4-service topology above)
- `sidecar.yaml` (Locket sidecar for secret injection)
- `secrets.env` (the Infisical reference template)
- `pangolin.yaml` (the Pangolin resource definitions)

## Legacy note

The `dagster.yaml` example above uses the **legacy** module paths
(`dagster.core.scheduler`, `DagsterDaemonScheduler`,
`QueuedRunCoordinator`, `DockerRunLauncher`). The modern path uses
`dg` CLI for project scaffolding. Both are supported in Dagster 1.x.

## Reference

- The full `deploy/` example (multiple files: `Dockerfile_dagster`,
  `Dockerfile_user_code`, `docker-compose.yml`, `dagster.yaml`,
  `workspace.yaml`, `definitions.py`, `from_source/`, `tests/`,
  `tox.ini`) was in `docs/dagster/integrations/deploy/` (deleted
  with the `sync-skills-from-docs` change). The same content is in
  the upstream Dagster docs at
  <https://docs.dagster.io/deployment/guides/docker>
- The `infrastructure-stacks` openspec spec for the
  6-file GOLD_STANDARD stack pattern
- The `dagster` skill's `references/deployment/config-files.md`
  for the Dagster+ Hybrid variant
