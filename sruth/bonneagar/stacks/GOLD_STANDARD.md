# Locket / Pangolin / Komodo - Deployment Gold Standard

When converting a repository to our standard deployment format, generate the following 5 files in `sruth/bonneagar/stacks/<category>/<repo_name>/`:

## 1. compose.yaml
Base compose file containing the application services. It MUST NOT contain any Locket references natively. It should rely on environment variables (which will be supplied locally via `.env.local` or in production via Locket).
- Use `depends_on: locket: condition: service_healthy` only in the `sidecar.yaml` override, NOT here.

## 2. sidecar.yaml
The Locket sidecar definition and service override.
```yaml
services:
  locket:
    image: ghcr.io/bpbradley/locket:connect
    container_name: ${COMPOSE_PROJECT_NAME:-stack}-locket
    restart: unless-stopped
    user: "65532:65532"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    environment:
      INFISICAL_HOST: ${INFISICAL_HOST:-http://132.145.27.89:8080}
    command:
      - "--connect-host=${INFISICAL_HOST:-http://132.145.27.89:8080}"
      - "--connect-token=file:/run/secrets/infisical_secret"
      - "--map=/templates:/run/secrets/locket"
      - "--mode=${LOCKET_MODE:-watch}"
    secrets:
      - infisical_secret
    volumes:
      - ./secrets.env:/templates/secrets.env:ro
      - stack-secrets:/run/secrets/locket
    healthcheck:
      test: ["CMD", "/locket", "healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s
    networks:
      - stack

  # Replace 'main-service' with the actual name of the primary app container
  main-service:
    depends_on:
      locket:
        condition: service_healthy
    volumes:
      - stack-secrets:/run/secrets/locket:ro
    env_file:
      - /run/secrets/locket/secrets.env

secrets:
  infisical_secret:
    file: ${INFISICAL_TOKEN_FILE:-../../infisical_secret}

volumes:
  stack-secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: uid=65532,gid=65532,mode=700
```

## 3. secrets.env
Locket template file for Infisical:
```env
# Example
SERVICE_API_KEY={{ infisical://dev-baile/stack/api_key }}
```

## 4. pangolin.yaml
Pangolin auto-discovery labels for Komodo Core. Override the main service to add labels.
```yaml
services:
  main-service:
    labels:
      - "pangolin.public-resources.<repo_name>.name=<Repo Name>"
      - "pangolin.public-resources.<repo_name>.full-domain=<repo>.cianfhoghlaim.ie"
      - "pangolin.public-resources.<repo_name>.protocol=http"
      - "pangolin.public-resources.<repo_name>.targets[0].method=http"
      - "pangolin.public-resources.<repo_name>.targets[0].port=<Internal Port>"
```

## 5. blueprint.yaml
Pangolin routing blueprint.
```yaml
public-resources:
  <repo_name>:
    name: "<Repo Name>"
    full-domain: "<repo>.cianfhoghlaim.ie"
    protocol: "http"
    targets:
      - site: "arm1-oci"
        hostname: "<repo_name>-main"
        method: "http"
        port: <Internal Port>
```

When processing a repo:
1. Identify its services, ports, and required environment variables from its original `docker-compose.yml`.
2. Map required secrets into `secrets.env`.
3. Create the 5 standard files in the target directory.
