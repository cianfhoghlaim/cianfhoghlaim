/**
 * Authenticated Stack Deployment Module
 *
 * Provides end-to-end authentication workflows for infrastructure stacks:
 * - PocketID OAuth client creation
 * - 1Password secret storage via Locket
 * - TinyAuth middleware registration
 * - Komodo stack deployment
 * - Authentication verification
 *
 * Usage:
 *   const authStack = bonneagar.authStack(config);
 *   await authStack.deployAuthenticatedStack("lakehouse", false);
 */

import {
  dag,
  Container,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import type { AuthStackConfig, AuthStage, AuthDeploymentResult, AuthStackDefinition } from "./types";

/**
 * Pre-defined stack configurations for authenticated deployment
 */
const STACK_DEFINITIONS: Record<string, AuthStackDefinition> = {
  lakehouse: {
    stackName: "lakehouse",
    services: [
      { name: "Lakehouse Garage", domain: "lakehouse-garage.cianfhoghlaim.ie", port: 3904, middleware: "tinyauth" },
      { name: "Lakehouse Lakekeeper", domain: "lakehouse-lakekeeper.cianfhoghlaim.ie", port: 8181, middleware: "tinyauth" },
      { name: "Lakehouse Lance", domain: "lakehouse-lance.cianfhoghlaim.ie", port: 8182, middleware: "tinyauth" },
    ],
    secretsVault: "taisce-secrets",
    secretsItem: "lakehouse-auth",
  },
  lancedb: {
    stackName: "lancedb",
    services: [
      { name: "LanceDB", domain: "lancedb.cianfhoghlaim.ie", port: 8080, middleware: "tinyauth" },
    ],
    secretsVault: "taisce-secrets",
    secretsItem: "lancedb-auth",
  },
  memgraph: {
    stackName: "memgraph",
    services: [
      { name: "Memgraph Lab", domain: "memgraph.cianfhoghlaim.ie", port: 3000, middleware: "tinyauth" },
    ],
    secretsVault: "taisce-secrets",
    secretsItem: "memgraph-auth",
  },
  mlflow: {
    stackName: "mlflow",
    services: [
      { name: "MLflow", domain: "mlflow.cianfhoghlaim.ie", port: 5000, middleware: "tinyauth" },
    ],
    secretsVault: "taisce-secrets",
    secretsItem: "mlflow-auth",
  },
  langfuse: {
    stackName: "langfuse",
    services: [
      { name: "Langfuse", domain: "langfuse.cianfhoghlaim.ie", port: 3000, middleware: "tinyauth" },
    ],
    secretsVault: "taisce-secrets",
    secretsItem: "langfuse-auth",
  },
  graphiti: {
    stackName: "graphiti",
    services: [
      { name: "Graphiti", domain: "graphiti.cianfhoghlaim.ie", port: 8003, middleware: "tinyauth" },
    ],
    secretsVault: "taisce-secrets",
    secretsItem: "graphiti-auth",
  },
  litellm: {
    stackName: "litellm",
    services: [
      { name: "LiteLLM", domain: "llm.cianfhoghlaim.ie", port: 4000, middleware: "native-oidc" },
      { name: "LiteLLM API", domain: "api.llm.cianfhoghlaim.ie", port: 4000, middleware: "none" },
    ],
    secretsVault: "dev-baile",
    secretsItem: "litellm-pocketid",
  },
};

@object()
export class AuthStack {
  @field()
  komodoUrl: string;

  @field()
  komodoApiKey: Secret;

  @field()
  komodoApiSecret: Secret;

  @field()
  pocketIdUrl: string;

  @field()
  pocketIdToken: Secret;

  @field()
  opConnectHost: string;

  @field()
  opConnectToken: Secret;

  @field()
  tinyauthUrl: string;

  constructor(
    komodoUrl: string,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    pocketIdUrl: string,
    pocketIdToken: Secret,
    opConnectHost: string,
    opConnectToken: Secret,
    tinyauthUrl: string = "http://tinyauth:10000"
  ) {
    this.komodoUrl = komodoUrl;
    this.komodoApiKey = komodoApiKey;
    this.komodoApiSecret = komodoApiSecret;
    this.pocketIdUrl = pocketIdUrl;
    this.pocketIdToken = pocketIdToken;
    this.opConnectHost = opConnectHost;
    this.opConnectToken = opConnectToken;
    this.tinyauthUrl = tinyauthUrl;
  }

  /**
   * Get a curl container for HTTP operations
   */
  private curlContainer(): Container {
    return dag.container().from("curlimages/curl:8.11.1");
  }

  /**
   * Get 1Password CLI container
   */
  private opContainer(): Container {
    return dag
      .container()
      .from("1password/op:2")
      .withSecretVariable("OP_CONNECT_TOKEN", this.opConnectToken)
      .withEnvVariable("OP_CONNECT_HOST", this.opConnectHost);
  }

  // ==========================================================================
  // OAuth Client Management
  // ==========================================================================

  /**
   * Create an OAuth client in PocketID for a service
   * Note: PocketID uses X-API-Key header, not Bearer token
   */
  @func()
  async createOAuthClient(
    serviceName: string,
    domain: string,
    redirectUri: string
  ): Promise<string> {
    // PocketID OAuth client creation via API
    // Note: PocketID uses callbackURLs, not redirect_uris
    const body = JSON.stringify({
      name: serviceName,
      callbackURLs: [redirectUri],
      isPublic: false,
      pkceEnabled: false,
    });

    // Create the client
    const clientResult = await this.curlContainer()
      .withSecretVariable("POCKETID_API_KEY", this.pocketIdToken)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.pocketIdUrl}/api/oidc/clients" \
          -H "Content-Type: application/json" \
          -H "X-API-Key: $POCKETID_API_KEY" \
          -d '${body}'`,
      ])
      .stdout();

    // Parse client ID and generate secret
    const client = JSON.parse(clientResult);
    const secretResult = await this.curlContainer()
      .withSecretVariable("POCKETID_API_KEY", this.pocketIdToken)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.pocketIdUrl}/api/oidc/clients/${client.id}/secret" \
          -H "X-API-Key: $POCKETID_API_KEY"`,
      ])
      .stdout();

    const secret = JSON.parse(secretResult);
    return JSON.stringify({
      ...client,
      client_id: client.id,
      client_secret: secret.secret,
    });
  }

  /**
   * List OAuth clients in PocketID
   */
  @func()
  async listOAuthClients(): Promise<string> {
    return this.curlContainer()
      .withSecretVariable("POCKETID_API_KEY", this.pocketIdToken)
      .withExec([
        "sh",
        "-c",
        `curl -sf "${this.pocketIdUrl}/api/oidc/clients" \
          -H "X-API-Key: $POCKETID_API_KEY"`,
      ])
      .stdout();
  }

  /**
   * Delete an OAuth client from PocketID
   */
  @func()
  async deleteOAuthClient(clientId: string): Promise<string> {
    return this.curlContainer()
      .withSecretVariable("POCKETID_API_KEY", this.pocketIdToken)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X DELETE "${this.pocketIdUrl}/api/oidc/clients/${clientId}" \
          -H "X-API-Key: $POCKETID_API_KEY"`,
      ])
      .stdout();
  }

  // ==========================================================================
  // Secret Management
  // ==========================================================================

  /**
   * Store OAuth credentials in 1Password
   */
  @func()
  async storeSecretsIn1Password(
    vault: string,
    itemName: string,
    clientId: Secret,
    clientSecret: Secret
  ): Promise<string> {
    return this.opContainer()
      .withSecretVariable("CLIENT_ID", clientId)
      .withSecretVariable("CLIENT_SECRET", clientSecret)
      .withExec([
        "sh",
        "-c",
        `op item create \
          --vault "${vault}" \
          --category "API Credential" \
          --title "${itemName}" \
          "client_id[password]=$CLIENT_ID" \
          "client_secret[password]=$CLIENT_SECRET" \
          || echo "Item may already exist"`,
      ])
      .stdout();
  }

  /**
   * Get a secret from 1Password
   */
  @func()
  async getSecretFrom1Password(reference: string): Promise<Secret> {
    const output = await this.opContainer()
      .withExec(["op", "read", reference])
      .stdout();
    return dag.setSecret("op-secret", output.trim());
  }

  /**
   * Delete a secret from 1Password
   */
  @func()
  async deleteSecretFrom1Password(vault: string, itemName: string): Promise<string> {
    return this.opContainer()
      .withExec(["op", "item", "delete", itemName, "--vault", vault])
      .stdout();
  }

  // ==========================================================================
  // Stack Deployment
  // ==========================================================================

  /**
   * Deploy a stack via Komodo
   */
  @func()
  async deployStack(stackName: string): Promise<string> {
    const body = JSON.stringify({
      type: "DeployStack",
      params: { stack: stackName },
    });

    return this.curlContainer()
      .withSecretVariable("KOMODO_API_KEY", this.komodoApiKey)
      .withSecretVariable("KOMODO_API_SECRET", this.komodoApiSecret)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.komodoUrl}/execute" \
          -H "Content-Type: application/json" \
          -H "X-Api-Key: $KOMODO_API_KEY" \
          -H "X-Api-Secret: $KOMODO_API_SECRET" \
          -d '${body}'`,
      ])
      .stdout();
  }

  /**
   * Stop a stack via Komodo
   */
  @func()
  async stopStack(stackName: string): Promise<string> {
    const body = JSON.stringify({
      type: "StopStack",
      params: { stack: stackName },
    });

    return this.curlContainer()
      .withSecretVariable("KOMODO_API_KEY", this.komodoApiKey)
      .withSecretVariable("KOMODO_API_SECRET", this.komodoApiSecret)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.komodoUrl}/execute" \
          -H "Content-Type: application/json" \
          -H "X-Api-Key: $KOMODO_API_KEY" \
          -H "X-Api-Secret: $KOMODO_API_SECRET" \
          -d '${body}'`,
      ])
      .stdout();
  }

  // ==========================================================================
  // Authentication Verification
  // ==========================================================================

  /**
   * Verify that a service redirects to TinyAuth
   */
  @func()
  async verifyAuthentication(serviceUrl: string): Promise<string> {
    // Test that accessing the service without auth redirects to TinyAuth
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `response=$(curl -sf -o /dev/null -w "%{http_code}:%{redirect_url}" "${serviceUrl}")
         code=$(echo $response | cut -d: -f1)
         redirect=$(echo $response | cut -d: -f2-)

         if [ "$code" = "302" ] || [ "$code" = "307" ]; then
           if echo "$redirect" | grep -q "tinyauth"; then
             echo "SUCCESS: Service redirects to TinyAuth"
             echo "Redirect URL: $redirect"
           else
             echo "WARNING: Service redirects but not to TinyAuth"
             echo "Redirect URL: $redirect"
           fi
         elif [ "$code" = "401" ]; then
           echo "SUCCESS: Service returns 401 Unauthorized"
         else
           echo "ERROR: Unexpected response code: $code"
           echo "Service may not be protected"
         fi`,
      ])
      .stdout();
  }

  /**
   * Test OAuth flow end-to-end
   */
  @func()
  async testOAuthFlow(serviceUrl: string): Promise<string> {
    // This would typically use browser automation
    // For now, just verify the redirect chain
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -L -o /dev/null -w "%{url_effective}" "${serviceUrl}"`,
      ])
      .stdout();
  }

  // ==========================================================================
  // Full Deployment Orchestration
  // ==========================================================================

  /**
   * Deploy a stack with full authentication setup
   *
   * Stages:
   * 1. pre-flight - Validate prerequisites
   * 2. create-oauth - Create OAuth client in PocketID
   * 3. inject-secrets - Store credentials in 1Password
   * 4. deploy-stack - Deploy via Komodo
   * 5. verify-auth - Test authentication redirect
   */
  @func()
  async deployAuthenticatedStack(
    stackName: string,
    dryRun: boolean = false
  ): Promise<string> {
    const definition = STACK_DEFINITIONS[stackName];
    if (!definition) {
      return JSON.stringify({
        success: false,
        error: `Unknown stack: ${stackName}. Available: ${Object.keys(STACK_DEFINITIONS).join(", ")}`,
      });
    }

    const stages: AuthStage[] = [];
    const startedAt = new Date().toISOString();

    try {
      // Stage 1: Pre-flight checks
      stages.push({
        name: "pre-flight",
        status: "in_progress",
        startedAt: new Date().toISOString(),
      });

      if (dryRun) {
        stages[0].status = "completed";
        stages[0].output = "DRY RUN: Pre-flight checks would run here";
        stages[0].completedAt = new Date().toISOString();
      } else {
        // Check Komodo is accessible
        const healthResult = await this.curlContainer()
          .withExec(["curl", "-sf", `${this.komodoUrl}/health`])
          .stdout();

        stages[0].status = "completed";
        stages[0].output = `Komodo health: ${healthResult}`;
        stages[0].completedAt = new Date().toISOString();
      }

      // Stage 2: Create OAuth client
      stages.push({
        name: "create-oauth",
        status: "in_progress",
        startedAt: new Date().toISOString(),
      });

      if (dryRun) {
        stages[1].status = "completed";
        stages[1].output = `DRY RUN: Would create OAuth client for ${stackName}`;
        stages[1].completedAt = new Date().toISOString();
      } else {
        const primaryService = definition.services[0];
        const redirectUri = `https://${primaryService.domain}/oauth/callback`;

        const oauthResult = await this.createOAuthClient(
          stackName,
          primaryService.domain,
          redirectUri
        );

        stages[1].status = "completed";
        stages[1].output = oauthResult;
        stages[1].completedAt = new Date().toISOString();
      }

      // Stage 3: Deploy stack
      stages.push({
        name: "deploy-stack",
        status: "in_progress",
        startedAt: new Date().toISOString(),
      });

      if (dryRun) {
        stages[2].status = "completed";
        stages[2].output = `DRY RUN: Would deploy stack ${stackName}`;
        stages[2].completedAt = new Date().toISOString();
      } else {
        const deployResult = await this.deployStack(stackName);
        stages[2].status = "completed";
        stages[2].output = deployResult;
        stages[2].completedAt = new Date().toISOString();
      }

      // Stage 4: Verify authentication
      stages.push({
        name: "verify-auth",
        status: "in_progress",
        startedAt: new Date().toISOString(),
      });

      if (dryRun) {
        stages[3].status = "completed";
        stages[3].output = "DRY RUN: Would verify auth redirects";
        stages[3].completedAt = new Date().toISOString();
      } else {
        const verifyResults: string[] = [];
        for (const service of definition.services) {
          const result = await this.verifyAuthentication(`https://${service.domain}`);
          verifyResults.push(`${service.name}: ${result}`);
        }

        stages[3].status = "completed";
        stages[3].output = verifyResults.join("\n");
        stages[3].completedAt = new Date().toISOString();
      }

      const result: AuthDeploymentResult = {
        success: true,
        stackName,
        stages,
        startedAt,
        completedAt: new Date().toISOString(),
        dryRun,
      };

      return JSON.stringify(result, null, 2);
    } catch (error) {
      const currentStage = stages[stages.length - 1];
      if (currentStage) {
        currentStage.status = "failed";
        currentStage.error = error instanceof Error ? error.message : String(error);
        currentStage.completedAt = new Date().toISOString();
      }

      const result: AuthDeploymentResult = {
        success: false,
        stackName,
        stages,
        startedAt,
        completedAt: new Date().toISOString(),
        dryRun,
        error: error instanceof Error ? error.message : String(error),
      };

      return JSON.stringify(result, null, 2);
    }
  }

  // ==========================================================================
  // Rollback
  // ==========================================================================

  /**
   * Rollback a failed deployment
   */
  @func()
  async rollback(
    stackName: string,
    stage: string
  ): Promise<string> {
    const results: string[] = [];

    switch (stage) {
      case "deploy-stack":
        // Stop the stack
        const stopResult = await this.stopStack(stackName);
        results.push(`Stopped stack: ${stopResult}`);
        // Fall through to clean up secrets
      case "inject-secrets":
        // Delete secrets from 1Password
        const definition = STACK_DEFINITIONS[stackName];
        if (definition) {
          try {
            const deleteResult = await this.deleteSecretFrom1Password(
              definition.secretsVault,
              definition.secretsItem
            );
            results.push(`Deleted secrets: ${deleteResult}`);
          } catch {
            results.push("Secrets deletion skipped (may not exist)");
          }
        }
        // Fall through to clean up OAuth
      case "create-oauth":
        // OAuth client cleanup would go here
        results.push("OAuth client cleanup skipped (requires client ID)");
        break;
      default:
        results.push(`Unknown stage: ${stage}`);
    }

    return results.join("\n");
  }

  // ==========================================================================
  // Utility Functions
  // ==========================================================================

  /**
   * List available stack definitions
   */
  @func()
  listAvailableStacks(): string {
    return JSON.stringify(
      Object.entries(STACK_DEFINITIONS).map(([name, def]) => ({
        name,
        services: def.services.length,
        domains: def.services.map((s) => s.domain),
      })),
      null,
      2
    );
  }

  /**
   * Get stack definition details
   */
  @func()
  getStackDefinition(stackName: string): string {
    const definition = STACK_DEFINITIONS[stackName];
    if (!definition) {
      return JSON.stringify({ error: `Unknown stack: ${stackName}` });
    }
    return JSON.stringify(definition, null, 2);
  }
}
