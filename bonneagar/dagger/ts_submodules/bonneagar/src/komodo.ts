/**
 * Komodo SDK Wrapper Module
 *
 * Provides programmatic access to Komodo Core API for:
 * - Git provider management
 * - Stack deployment
 * - Procedure execution
 * - Resource sync triggers
 * - Server management
 *
 * API Reference: https://komo.do/docs/api
 * Rust SDK: https://crates.io/crates/komodo_client
 */

import {
  dag,
  Container,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

@object()
export class Komodo {
  @field()
  coreUrl: string;

  @field()
  apiKey: Secret;

  @field()
  apiSecret: Secret;

  constructor(coreUrl: string, apiKey: Secret, apiSecret: Secret) {
    this.coreUrl = coreUrl;
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
  }

  /**
   * Get a curl container with Komodo auth configured
   */
  private curlContainer(): Container {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withSecretVariable("KOMODO_API_KEY", this.apiKey)
      .withSecretVariable("KOMODO_API_SECRET", this.apiSecret);
  }

  /**
   * Execute a Komodo API request
   */
  private async apiCall(
    path: string,
    requestType: string,
    params: object
  ): Promise<string> {
    const body = JSON.stringify({ type: requestType, params });
    return this.curlContainer()
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.coreUrl}${path}" \
          -H "Content-Type: application/json" \
          -H "X-Api-Key: $KOMODO_API_KEY" \
          -H "X-Api-Secret: $KOMODO_API_SECRET" \
          -d '${body}'`,
      ])
      .stdout();
  }

  /**
   * Read operation (GET-like)
   */
  @func()
  async read(requestType: string, params: object = {}): Promise<string> {
    return this.apiCall("/read", requestType, params);
  }

  /**
   * Write operation (POST/PUT-like)
   */
  @func()
  async write(requestType: string, params: object = {}): Promise<string> {
    return this.apiCall("/write", requestType, params);
  }

  /**
   * Execute operation (trigger actions)
   */
  @func()
  async execute(requestType: string, params: object = {}): Promise<string> {
    return this.apiCall("/execute", requestType, params);
  }

  // ==========================================================================
  // Git Provider Management
  // ==========================================================================

  /**
   * Create a Git provider account (for Forgejo, GitHub, GitLab, etc.)
   */
  @func()
  async createGitProvider(
    domain: string,
    username: string,
    token: Secret
  ): Promise<string> {
    return this.curlContainer()
      .withSecretVariable("GIT_TOKEN", token)
      .withExec([
        "sh",
        "-c",
        `curl -sf -X POST "${this.coreUrl}/write" \
          -H "Content-Type: application/json" \
          -H "X-Api-Key: $KOMODO_API_KEY" \
          -H "X-Api-Secret: $KOMODO_API_SECRET" \
          -d '{"type":"CreateGitProviderAccount","params":{"domain":"${domain}","username":"${username}","token":"'"$GIT_TOKEN"'"}}'`,
      ])
      .stdout();
  }

  /**
   * List configured Git providers
   */
  @func()
  async listGitProviders(): Promise<string> {
    return this.read("ListGitProviders", {});
  }

  // ==========================================================================
  // Stack Management
  // ==========================================================================

  /**
   * Deploy a stack by name
   */
  @func()
  async deployStack(stackName: string): Promise<string> {
    return this.execute("DeployStack", { stack: stackName });
  }

  /**
   * Start a stack by name
   */
  @func()
  async startStack(stackName: string): Promise<string> {
    return this.execute("StartStack", { stack: stackName });
  }

  /**
   * Stop a stack by name
   */
  @func()
  async stopStack(stackName: string): Promise<string> {
    return this.execute("StopStack", { stack: stackName });
  }

  /**
   * Restart a stack by name
   */
  @func()
  async restartStack(stackName: string): Promise<string> {
    return this.execute("RestartStack", { stack: stackName });
  }

  /**
   * Get stack details
   */
  @func()
  async getStack(stackName: string): Promise<string> {
    return this.read("GetStack", { stack: stackName });
  }

  /**
   * List all stacks
   */
  @func()
  async listStacks(): Promise<string> {
    return this.read("ListStacks", {});
  }

  // ==========================================================================
  // Procedure Management
  // ==========================================================================

  /**
   * Run a procedure by name
   */
  @func()
  async runProcedure(procedureName: string): Promise<string> {
    return this.execute("RunProcedure", { procedure: procedureName });
  }

  /**
   * Get procedure details
   */
  @func()
  async getProcedure(procedureName: string): Promise<string> {
    return this.read("GetProcedure", { procedure: procedureName });
  }

  /**
   * List all procedures
   */
  @func()
  async listProcedures(): Promise<string> {
    return this.read("ListProcedures", {});
  }

  // ==========================================================================
  // Resource Sync Management
  // ==========================================================================

  /**
   * Trigger a resource sync
   */
  @func()
  async runSync(syncName: string): Promise<string> {
    return this.execute("RunSync", { sync: syncName });
  }

  /**
   * Get sync details
   */
  @func()
  async getSync(syncName: string): Promise<string> {
    return this.read("GetResourceSync", { sync: syncName });
  }

  /**
   * List all resource syncs
   */
  @func()
  async listSyncs(): Promise<string> {
    return this.read("ListResourceSyncs", {});
  }

  // ==========================================================================
  // Server Management
  // ==========================================================================

  /**
   * List all servers
   */
  @func()
  async listServers(): Promise<string> {
    return this.read("ListServers", {});
  }

  /**
   * Get server details
   */
  @func()
  async getServer(serverName: string): Promise<string> {
    return this.read("GetServer", { server: serverName });
  }

  /**
   * Get server stats
   */
  @func()
  async getServerStats(serverName: string): Promise<string> {
    return this.read("GetServerStats", { server: serverName });
  }

  // ==========================================================================
  // Build Management
  // ==========================================================================

  /**
   * Run a build by name
   */
  @func()
  async runBuild(buildName: string): Promise<string> {
    return this.execute("RunBuild", { build: buildName });
  }

  /**
   * List all builds
   */
  @func()
  async listBuilds(): Promise<string> {
    return this.read("ListBuilds", {});
  }

  // ==========================================================================
  // Health & Diagnostics
  // ==========================================================================

  /**
   * Check Komodo Core health
   */
  @func()
  async health(): Promise<string> {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withExec(["curl", "-sf", `${this.coreUrl}/health`])
      .stdout();
  }

  /**
   * Get Komodo version
   */
  @func()
  async version(): Promise<string> {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withExec(["curl", "-sf", `${this.coreUrl}/version`])
      .stdout();
  }
}
