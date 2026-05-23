# Secure Environment Variable Management in `bonneagar`

This document outlines a detailed plan for securely managing environment variables and secrets within the `bonneagar` project, leveraging 1Password, SOPS (Secrets OPerationS), `mise-en-place`, and Komodo.

## Current State and Available Tools

*   **`bonneagar` project:**
    *   Uses `mise-en-place` (`mise.toml`) for tool version management and some environment variables.
    *   Uses Docker Compose with Komodo for container orchestration, with sensitive variables currently in `compose.env`.
    *   Uses Pulumi for infrastructure-as-code, which also needs secure secret management.
*   **`sops-age-op`:** A shell script (`sops-age-op/sops-age-op`) that facilitates creating `age` keys in 1Password and using them for SOPS encryption/decryption by fetching the private key from 1Password. This is crucial for managing SOPS `age` keys securely.
*   **`komodo-op`:** A Go application (`komodo-op/cmd/komodo-op/main.go`) designed to synchronize secrets from 1Password Connect to Komodo. This will be vital for providing secrets to Docker Compose environments managed by Komodo.

The core challenge is to replace hardcoded secrets with a secure, automated workflow using 1Password and SOPS, while ensuring smooth integration with `mise-en-place` for local development and Komodo for deployments.

## Detailed Plan

**Goal:** Implement a secure, maintainable, and developer-friendly system for managing environment variables and secrets in the `bonneagar` project, leveraging 1Password, SOPS, `mise-en-place`, and Komodo.

### Phase 1: Centralizing Secrets in 1Password and SOPS Setup

1.  **Create a dedicated 1Password Vault:**
    *   Establish a new 1Password vault (e.g., "Bonneagar Secrets") to store all project-specific sensitive information.
    *   Create a 1Password item for the SOPS `age` private key (e.g., "SOPS Age Key - Bonneagar") within this vault.

2.  **Generate and Store SOPS Age Key using `sops-age-op`:**
    *   Use the `sops-age-op` script to generate a new `age` key pair and store the private key securely in the designated 1Password item.
    *   The public key will be used for encrypting `.env` files.

    ```bash
    ./sops-age-op -c -k op://BonneagarSecrets/SOPS_Age_Key_Bonneagar/private_key -t "bonneagar,sops,age"
    ```

3.  **Create SOPS-encrypted `.env` files:**
    *   For local development, create a `.secrets.sops.env` file in the `bonneagar/` root directory. This file will contain sensitive environment variables (e.g., `TF_VAR_tenancy_ocid`, `KOMODO_DB_PASSWORD`, `KOMODO_PASSKEY`, `KOMODO_WEBHOOK_SECRET`, `KOMODO_JWT_SECRET`, `KOMODO_AWS_ACCESS_KEY_ID`, `KOMODO_AWS_SECRET_ACCESS_KEY`, `KOMODO_HETZNER_TOKEN`, etc.).
    *   Encrypt this file using `sops` with the `age` public key obtained from the previous step.

    ```bash
    sops encrypt --age <your_age_public_key> -i bonneagar/.secrets.sops.env
    ```

    *   For Docker Compose, create a `.env.tpl` file (e.g., `bonneagar/compose/komodo/.env.tpl`) that uses `op://` references for secrets. This file will *not* be encrypted by SOPS, but will be processed by `komodo-op` or a pre-deployment script.

    ```ini
    # bonneagar/compose/komodo/.env.tpl
    KOMODO_DB_USERNAME=admin
    KOMODO_DB_PASSWORD=op://BonneagarSecrets/KomodoDB/password
    KOMODO_PASSKEY=op://BonneagarSecrets/KomodoPasskey/password
    # other secrets with op:// references
    ```

### Phase 2: Integrating with `mise-en-place` for Local Development (Revised)

1.  **Update `bonneagar/mise.toml`:**
    *   Remove hardcoded `TF_VAR` variables from `[env]`.
    *   Add a `[settings]` block to disable `rops` and force `mise` to use the external `sops` CLI for decryption.
    *   Add `[hooks.enter]` and `[hooks.leave]` to dynamically fetch and unset the `MISE_SOPS_AGE_KEY` from 1Password using a helper script.
    *   **Remove the `_.file = ".secrets.sops.env"` directive from `[env]`**. This ensures that sensitive application secrets are *not* automatically loaded into the general shell environment, but are instead injected on-demand.

    ```toml
    # bonneagar/mise.toml
    [tools]
    aqua = "latest"
    aws = "latest"
    cloudflared = "latest"
    dagger = "latest"
    deno = "latest"
    gcloud = "latest"
    # minio = "latest"
    oci = "latest"
    pulumi = "latest"
    python = "3.12.10"
    uv = "latest"
    node = "latest"
    duckdb = "latest"
    sops = "latest" # Ensure sops is managed by mise
    cmdx = "latest"

    [settings]
    experimental = true
    sops.rops = false # Force mise to use external sops CLI

    [env]
    _.python.venv = { path = ".venv" }
    # Removed: _.file = ".secrets.sops.env"

    [hooks.enter]
    shell = "bash"
    script = "./.bin/manage_sops_env.sh set"

    [hooks.leave]
    shell = "bash"
    script = "./.bin/manage_sops_env.sh unset"
    ```

2.  **Create `bonneagar/.bin/manage_sops_env.sh`:**
    *   This script remains the same, using `op read` to fetch the SOPS `age` private key from 1Password and set `MISE_SOPS_AGE_KEY`. This key is primarily for enabling `sops` CLI operations (e.g., `sops edit`) within the project.

    ```bash
    #!/usr/bin/env bash
    # bonneagar/.bin/manage_sops_env.sh
    # Argument $1: "set" or "unset"

    OP_AGE_KEY_PATH="op://BonneagarSecrets/SOPS_Age_Key_Bonneagar/private_key"

    if [ "$1" == "set" ]; then
      if command -v op &> /dev/null && op account get &> /dev/null; then
        echo "Attempting to fetch SOPS age key from 1Password..."
        MISE_SOPS_AGE_KEY_VALUE=$(op read "$OP_AGE_KEY_PATH" 2>/dev/null)
        if [ -n "$MISE_SOPS_AGE_KEY_VALUE" ]; then
          export MISE_SOPS_AGE_KEY="$MISE_SOPS_AGE_KEY_VALUE"
          echo "MISE_SOPS_AGE_KEY set from 1Password."
        else
          echo "Error: Failed to fetch SOPS age key from 1Password. Ensure you are logged in and the path is correct." >&2
        fi
      else
        echo "Error: 1Password CLI 'op' not available or not signed in. Cannot set MISE_SOPS_AGE_KEY." >&2
      fi
    elif [ "$1" == "unset" ]; then
      unset MISE_SOPS_AGE_KEY
      echo "MISE_SOPS_AGE_KEY unset."
    fi
    ```

3.  **Update Python/TypeScript applications to use `op run` or `sops exec-env`:**
    *   Applications (e.g., `csv_to_duckdb_pipeline.py`, `exam_scraper/scrape_exam_stats.py`) should now be explicitly run with `op run` or `sops exec-env` to inject secrets on-demand. This ensures secrets are only exposed to the specific process that needs them.

    ```bash
    # Example for a Python script that needs secrets from 1Password directly
    op run -- python bonneagar/csv_to_duckdb_pipeline.py

    # Example for a Python script that needs variables from .secrets.sops.env
    sops exec-env bonneagar/.secrets.sops.env -- python bonneagar/csv_to_duckdb_pipeline.py

    # Example for a Node.js script
    sops exec-env bonneagar/.secrets.sops.env -- deno run --allow-env your_deno_app.ts
    ```
    *   If direct 1Password SDK integration is desired for specific secrets, the `OP_SERVICE_ACCOUNT_TOKEN` required by the SDKs would itself be a secret that needs to be injected via `op run` or `sops exec-env`.

#### Phase 3: Integrating with Komodo for Docker Compose Deployments

1.  **Deploy 1Password Connect Server (if not already present):**
    *   For production or shared environments, deploy a 1Password Connect Server as per 1Password documentation. This provides a REST API for secrets.
    *   Ensure the Komodo environment can access this server.

2.  **Utilize `komodo-op` for Secret Synchronization:**
    *   `komodo-op` is designed to sync secrets from 1Password Connect to Komodo. This is the ideal tool for providing secrets to Komodo-managed Docker Compose deployments.
    *   Configure `komodo-op` to fetch secrets from your 1Password vault (via Connect) and make them available to Komodo. This likely involves setting `OP_CONNECT_HOST`, `OP_VAULT_UUID`, and `KOMODO_HOST` in `komodo-op`'s environment.
    *   The `komodo-op` tool can be run as a one-off sync or in daemon mode. For Komodo deployments, it would typically be part of a pre-deployment step or a continuous synchronization process.

3.  **Update `bonneagar/compose/komodo/compose.env` and `mongo.compose.yaml`:**
    *   Rename `compose.env` to `compose.env.tpl` and modify it to use `op://` references for sensitive variables.
    *   Komodo's pre-deployment script (or `komodo-op` if integrated as a Komodo plugin/feature) will process this template to generate the actual `.env` file.
    *   Ensure `mongo.compose.yaml` continues to reference the generated `.env` file via `env_file: ./compose.env`.

    ```yaml
    # bonneagar/compose/komodo/mongo.compose.yaml
    services:
      mongo:
        # ...
        environment:
          MONGO_INITDB_ROOT_USERNAME: ${KOMODO_DB_USERNAME}
          MONGO_INITDB_ROOT_PASSWORD: ${KOMODO_DB_PASSWORD}
      core:
        # ...
        env_file: ./compose.env # This will be the generated file
        environment:
          KOMODO_DATABASE_USERNAME: ${KOMODO_DB_USERNAME}
          KOMODO_DATABASE_PASSWORD: ${KOMODO_DB_PASSWORD}
    ```

4.  **Komodo Pre-Deployment Script (if `komodo-op` isn't directly integrated as a Komodo feature):**
    *   If `komodo-op` is not a direct Komodo feature, a custom pre-deployment script within Komodo would be needed. This script would:
        *   Ensure `op` CLI is available and authenticated (e.g., via `OP_SERVICE_ACCOUNT_TOKEN` provided to Komodo's environment).
        *   Use `op inject -i bonneagar/compose/komodo/.env.tpl -o bonneagar/compose/komodo/compose.env` to generate the concrete `.env` file before `docker compose up` is executed.

### Phase 4: Integrating with Pulumi

1.  **Update Pulumi Secrets:**
    *   Pulumi has its own secrets management. Instead of storing secrets directly in `Pulumi.dev.yaml` or `secrets.yaml` (if unencrypted), use Pulumi's built-in secret encryption.
    *   For sensitive values like `TF_VAR_tenancy_ocid`, `TF_VAR_user_ocid`, `TF_VAR_fingerprint`, and `TF_VAR_private_key_path`, use `pulumi config set --secret <key> <value>`.
    *   Alternatively, if these values are truly environment variables, ensure they are picked up from the `mise-en-place` environment (which will now be populated from the SOPS-encrypted `.secrets.sops.env`).

    ```python
    # bonneagar/pulumi/__main__.py or relevant Pulumi Python files
    import pulumi
    import os

    # Retrieve from Pulumi config secrets
    config = pulumi.Config()
    tenancy_ocid = config.require_secret("tenancy_ocid")
    user_ocid = config.require_secret("user_ocid")
    fingerprint = config.require_secret("fingerprint")
    private_key_path = config.require_secret("private_key_path")
    region = config.require_secret("region")

    # Or, if they are truly environment variables set by mise:
    # tenancy_ocid = os.getenv("TF_VAR_tenancy_ocid")
    # user_ocid = os.getenv("TF_VAR_user_ocid")
    # ...
    ```

### Phase 5: Security Best Practices and Considerations

*   **Principle of Least Privilege:** Ensure 1Password Service Accounts and Connect tokens have minimal necessary permissions.
*   **Secret Rotation:** Establish a process for regularly rotating all secrets.
*   **`.gitignore`:** Add `bonneagar/.secrets.sops.env` (the unencrypted version if it ever exists temporarily), `bonneagar/compose/komodo/compose.env` (the generated one), and any other temporary secret files to `.gitignore`. The `.secrets.sops.env` (encrypted) should be committed.
*   **Audit Trails:** Monitor 1Password audit logs for secret access.
*   **Performance:** The `op` call within `mise` hooks for the SOPS `age` key will still incur a brief delay on initial directory entry. For application secrets, the `op run` or `sops exec-env` approach ensures performance is only impacted when secrets are explicitly needed.

---

### Mermaid Diagram: High-Level Workflow

```mermaid
graph TD
    A[1Password Vault] -->|Stores| B[SOPS Age Private Key]
    A -->|Stores| C[Application Secrets]
    A -->|Stores| D[Komodo/Connect Tokens]

    B -->|Used by| E[sops-age-op]
    E -->|Generates| F[SOPS Age Public Key]

    F -->|Encrypts| G[.secrets.sops.env]
    G -->|Committed to| H[Git Repository]

    H -->|Pulled by| I[Local Dev Environment (mise)]
    I -->|mise hooks fetch key via op| B
    I -->|Enables sops CLI for| J[sops exec-env / op run]
    J -->|Injects secrets for| K[Python/TS Apps]
    K -->|Optionally use 1P SDK| C

    H -->|Pulled by| L[Komodo Deployment]
    L -->|Pre-deploy script/komodo-op| D
    L -->|Pre-deploy script/komodo-op processes| M[.env.tpl (with op:// refs)]
    M -->|Generates| N[.env.generated]
    N -->|Used by| O[Docker Compose]
    O -->|Provides secrets to| P[Containerized Apps]
    P -->|Optionally use 1P Connect SDK| Q[1P Connect Server]
    Q -->|Fetches secrets from| C
```

---

### Mermaid Diagram: `mise-en-place` Local Dev Flow (Revised)

```mermaid
graph TD
    A[Developer enters bonneagar/] --> B[mise detects .mise.toml]
    B --> C[mise executes hooks.enter script]
    C --> D[.bin/manage_sops_env.sh "set"]
    D --> E[op CLI reads SOPS Age Private Key from 1Password]
    E --> F[MISE_SOPS_AGE_KEY exported to shell environment]
    F --> G[Developer's shell is ready for sops CLI operations]
    G --> H{Run application/script?}
    H -- Yes --> I[Execute with 'op run' or 'sops exec-env']
    I --> J[Secrets injected into process environment]
    I --> K[Application runs with secrets]

    L[Developer leaves bonneagar/] --> M[mise executes hooks.leave script]
    M --> N[.bin/manage_sops_env.sh "unset"]
    N --> O[MISE_SOPS_AGE_KEY unset from shell environment]