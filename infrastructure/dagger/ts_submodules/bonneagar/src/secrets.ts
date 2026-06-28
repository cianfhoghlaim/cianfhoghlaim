/**
 * Secrets Management Module
 *
 * 1Password integration for secret retrieval and .env generation.
 * Extends the existing OnePassword class with app-specific secret mappings.
 */

import { dag, Container, Secret, object, func } from "@dagger.io/dagger";

export interface SecretMapping {
  envVar: string;
  opPath: string; // 1Password path: vault/item/field
  required: boolean;
}

/**
 * Secret mappings per app
 * Format: vault/item/field
 */
export const APP_SECRETS: Record<string, SecretMapping[]> = {
  // =============================================================================
  // ML Infrastructure Secrets (shared across all apps)
  // =============================================================================
  "ml-common": [
    // LiteLLM Gateway
    { envVar: "LITELLM_API_KEY", opPath: "cianfhoghlaim/litellm/api_key", required: false },
    { envVar: "LITELLM_MASTER_KEY", opPath: "cianfhoghlaim/litellm/master_key", required: false },

    // Langfuse Observability
    { envVar: "LANGFUSE_PUBLIC_KEY", opPath: "cianfhoghlaim/langfuse/public_key", required: true },
    { envVar: "LANGFUSE_SECRET_KEY", opPath: "cianfhoghlaim/langfuse/secret_key", required: true },
    { envVar: "LANGFUSE_HOST", opPath: "cianfhoghlaim/langfuse/host", required: false },

    // Vector Databases
    { envVar: "LANCEDB_API_KEY", opPath: "cianfhoghlaim/lancedb/api_key", required: false },
    { envVar: "QDRANT_API_KEY", opPath: "cianfhoghlaim/qdrant/api_key", required: false },
    { envVar: "FALKORDB_PASSWORD", opPath: "cianfhoghlaim/falkordb/password", required: false },

    // AI Memory
    { envVar: "COGNEE_API_KEY", opPath: "cianfhoghlaim/cognee/api_key", required: false },
    { envVar: "LETTA_API_KEY", opPath: "cianfhoghlaim/letta/api_key", required: false },

    // Cloud LLM Providers (used by LiteLLM)
    { envVar: "ANTHROPIC_API_KEY", opPath: "cianfhoghlaim/anthropic/api_key", required: false },
    { envVar: "GEMINI_API_KEY", opPath: "cianfhoghlaim/google/gemini_api_key", required: false },
    { envVar: "Z_API_KEY", opPath: "cianfhoghlaim/z-ai/api_key", required: false },
    { envVar: "HF_TOKEN", opPath: "cianfhoghlaim/huggingface/token", required: false },

    // MLflow
    { envVar: "MLFLOW_TRACKING_TOKEN", opPath: "cianfhoghlaim/mlflow/tracking_token", required: false },
  ],

  // =============================================================================
  // App-specific Secrets
  // =============================================================================
  "aleyum-portal": [
    { envVar: "DATABASE_URL", opPath: "cianfhoghlaim/aleyum-portal/database_url", required: true },
    { envVar: "POCKETID_CLIENT_ID", opPath: "cianfhoghlaim/pocketid/aleyum_client_id", required: true },
    { envVar: "POCKETID_CLIENT_SECRET", opPath: "cianfhoghlaim/pocketid/aleyum_client_secret", required: true },
    { envVar: "POCKETID_ISSUER", opPath: "cianfhoghlaim/pocketid/issuer", required: true },
    { envVar: "BETTER_AUTH_SECRET", opPath: "cianfhoghlaim/aleyum-portal/auth_secret", required: true },
  ],
  crypteolas: [
    { envVar: "POCKETID_CLIENT_ID", opPath: "cianfhoghlaim/pocketid/crypteolas_client_id", required: true },
    { envVar: "POCKETID_CLIENT_SECRET", opPath: "cianfhoghlaim/pocketid/crypteolas_client_secret", required: true },
    { envVar: "POCKETID_ISSUER", opPath: "cianfhoghlaim/pocketid/issuer", required: true },
    { envVar: "BETTER_AUTH_SECRET", opPath: "cianfhoghlaim/crypteolas/auth_secret", required: true },
  ],
  tuath: [
    { envVar: "POCKETID_CLIENT_ID", opPath: "cianfhoghlaim/pocketid/tuath_client_id", required: true },
    { envVar: "POCKETID_CLIENT_SECRET", opPath: "cianfhoghlaim/pocketid/tuath_client_secret", required: true },
    { envVar: "POCKETID_ISSUER", opPath: "cianfhoghlaim/pocketid/issuer", required: true },
    { envVar: "BETTER_AUTH_SECRET", opPath: "cianfhoghlaim/tuath/auth_secret", required: true },
  ],
  "oideachais-api": [
    { envVar: "ANTHROPIC_API_KEY", opPath: "cianfhoghlaim/anthropic/api_key", required: true },
    { envVar: "LANGFUSE_PUBLIC_KEY", opPath: "cianfhoghlaim/langfuse/public_key", required: false },
    { envVar: "LANGFUSE_SECRET_KEY", opPath: "cianfhoghlaim/langfuse/secret_key", required: false },
    { envVar: "LANGFUSE_HOST", opPath: "cianfhoghlaim/langfuse/host", required: false },
  ],
  "oideachais-web": [
    { envVar: "POCKETID_CLIENT_ID", opPath: "cianfhoghlaim/pocketid/oideachais_client_id", required: true },
    { envVar: "POCKETID_CLIENT_SECRET", opPath: "cianfhoghlaim/pocketid/oideachais_client_secret", required: true },
    { envVar: "POCKETID_ISSUER", opPath: "cianfhoghlaim/pocketid/issuer", required: true },
    { envVar: "BETTER_AUTH_SECRET", opPath: "cianfhoghlaim/oideachais/auth_secret", required: true },
  ],
};

@object()
export class SecretsManager {
  /**
   * Create a 1Password CLI container
   */
  private opContainer(opToken: Secret, connectHost: string): Container {
    return dag
      .container()
      .from("1password/op:2")
      .withSecretVariable("OP_CONNECT_TOKEN", opToken)
      .withEnvVariable("OP_CONNECT_HOST", connectHost);
  }

  /**
   * Get a single secret from 1Password
   */
  @func()
  async getSecret(
    opToken: Secret,
    connectHost: string,
    opPath: string
  ): Promise<Secret> {
    const value = await this.opContainer(opToken, connectHost)
      .withExec(["op", "read", "op://" + opPath])
      .stdout();

    const secretName = opPath.replace(/\//g, "-").replace(/[^a-zA-Z0-9-]/g, "");
    return dag.setSecret(secretName, value.trim());
  }

  /**
   * Generate .env file content for an app
   */
  @func()
  async generateEnvFile(
    opToken: Secret,
    connectHost: string,
    appName: string,
    port?: number
  ): Promise<string> {
    const mappings = APP_SECRETS[appName];
    if (!mappings) {
      return "# No secrets configured for " + appName + "\n";
    }

    const lines: string[] = [
      "# Generated .env for " + appName,
      "# Auto-generated by Dagger secrets module",
      "",
    ];

    if (port) {
      lines.push("PORT=" + port);
      lines.push("AUTH_BASE_URL=http://localhost:" + port);
      lines.push("");
    }

    for (const mapping of mappings) {
      try {
        const value = await this.opContainer(opToken, connectHost)
          .withExec(["op", "read", "op://" + mapping.opPath])
          .stdout();
        lines.push(mapping.envVar + "=" + value.trim());
      } catch (e) {
        if (mapping.required) {
          lines.push("# ERROR: Failed to fetch " + mapping.envVar);
        }
      }
    }

    return lines.join("\n");
  }

  /**
   * Load all secrets for an app into environment variables on a container
   */
  @func()
  async applySecretsToContainer(
    container: Container,
    opToken: Secret,
    connectHost: string,
    appName: string
  ): Promise<Container> {
    const mappings = APP_SECRETS[appName] || [];

    for (const mapping of mappings) {
      try {
        const secret = await this.getSecret(opToken, connectHost, mapping.opPath);
        container = container.withSecretVariable(mapping.envVar, secret);
      } catch (e) {
        if (mapping.required) {
          throw new Error("Required secret " + mapping.envVar + " not found");
        }
      }
    }

    return container;
  }

  /**
   * Validate that all required secrets exist for an app
   */
  @func()
  async validateSecrets(
    opToken: Secret,
    connectHost: string,
    appName: string
  ): Promise<{ valid: boolean; missing: string[] }> {
    const mappings = APP_SECRETS[appName] || [];
    const missing: string[] = [];

    for (const mapping of mappings) {
      if (mapping.required) {
        try {
          await this.opContainer(opToken, connectHost)
            .withExec(["op", "read", "op://" + mapping.opPath])
            .stdout();
        } catch (e) {
          missing.push(mapping.envVar);
        }
      }
    }

    return { valid: missing.length === 0, missing };
  }

  /**
   * List all apps and their secret requirements
   */
  @func()
  listAppSecrets(): string {
    const lines: string[] = ["App Secret Requirements:", ""];

    for (const [appName, mappings] of Object.entries(APP_SECRETS)) {
      lines.push(appName + ":");
      for (const mapping of mappings) {
        const required = mapping.required ? "[REQUIRED]" : "[OPTIONAL]";
        lines.push("  " + required + " " + mapping.envVar + " <- " + mapping.opPath);
      }
      lines.push("");
    }

    return lines.join("\n");
  }

  /**
   * Apply ML infrastructure secrets to a container
   * Uses the "ml-common" secret mappings
   */
  @func()
  async applyMLSecretsToContainer(
    container: Container,
    opToken: Secret,
    connectHost: string
  ): Promise<Container> {
    return this.applySecretsToContainer(container, opToken, connectHost, "ml-common");
  }

  /**
   * Generate .env file with ML infrastructure secrets
   */
  @func()
  async generateMLEnvFile(
    opToken: Secret,
    connectHost: string
  ): Promise<string> {
    return this.generateEnvFile(opToken, connectHost, "ml-common");
  }

  /**
   * Apply both app-specific and ML secrets to a container
   */
  @func()
  async applyAllSecretsToContainer(
    container: Container,
    opToken: Secret,
    connectHost: string,
    appName: string,
    includeMLSecrets: boolean = true
  ): Promise<Container> {
    // Apply app-specific secrets
    let result = await this.applySecretsToContainer(container, opToken, connectHost, appName);

    // Apply ML infrastructure secrets if requested
    if (includeMLSecrets) {
      result = await this.applySecretsToContainer(result, opToken, connectHost, "ml-common");
    }

    return result;
  }
}
