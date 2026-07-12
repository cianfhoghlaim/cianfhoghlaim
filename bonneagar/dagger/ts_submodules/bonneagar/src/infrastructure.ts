/**
 * Infrastructure Deployment Pipeline
 *
 * Unified deployment automation for deploying complete infrastructure to any domain:
 * - Periphery agents to all servers
 * - Public key registration in Komodo
 * - Pangolin labels generation
 * - Stack deployments
 *
 * Usage:
 *   dagger call infrastructure deploy-to-domain --base-domain="example.com" --servers='[...]'
 *   dagger call infrastructure verify-all
 */

import {
  dag,
  Container,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import { Periphery, type ServerConfig, type DeployResult } from "./periphery.js";
import { PangolinLabels, type ResourceConfig } from "./pangolin-labels.js";
import { Komodo } from "./komodo.js";

/** Result of the full deployment */
export interface DeploymentResult {
  id: string;
  success: boolean;
  domain: string;
  peripheryResults: DeployResult[];
  labelsGenerated: boolean;
  stacksDeployed: string[];
  totalDuration: number;
  startedAt: string;
  completedAt: string;
}

/** Verification result for all infrastructure */
export interface InfrastructureHealth {
  healthy: boolean;
  servers: Array<{
    name: string;
    peripheryHealthy: boolean;
    komodoConnected: boolean;
    error?: string;
  }>;
  services: Array<{
    name: string;
    url: string;
    healthy: boolean;
    statusCode?: number;
    error?: string;
  }>;
  timestamp: string;
}

@object()
export class Infrastructure {
  @field()
  baseDomain: string;

  @field()
  komodoUrl: string;

  @field()
  opConnectHost: string;

  constructor(
    baseDomain: string = "cianfhoghlaim.ie",
    komodoUrl: string = "https://komodo.cianfhoghlaim.ie",
    opConnectHost: string = "http://132.145.27.89:8080"
  ) {
    this.baseDomain = baseDomain;
    this.komodoUrl = komodoUrl;
    this.opConnectHost = opConnectHost;
  }

  /**
   * Deploy complete infrastructure to a domain
   */
  @func()
  async deployToDomain(
    sshKey: Secret,
    komodoPasskey: Secret,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    serversJson: string,
    stacksJson: string = "[]",
    dryRun: boolean = false
  ): Promise<string> {
    const startTime = new Date();
    const servers: ServerConfig[] = JSON.parse(serversJson);
    const stacks: string[] = JSON.parse(stacksJson);

    console.log(`=== ${dryRun ? "DRY RUN" : "DEPLOYING"} TO ${this.baseDomain} ===`);
    console.log(`Servers: ${servers.length}`);
    console.log(`Stacks: ${stacks.length}`);
    console.log("");

    const peripheryResults: DeployResult[] = [];
    const stacksDeployed: string[] = [];

    if (dryRun) {
      console.log("DRY RUN: Would deploy to the following servers:");
      for (const server of servers) {
        console.log(`  - ${server.name} (${server.connectionMode})`);
      }
      console.log("");
      console.log("DRY RUN: Would deploy the following stacks:");
      for (const stack of stacks) {
        console.log(`  - ${stack}`);
      }

      return JSON.stringify({
        id: `dry-run-${startTime.toISOString().replace(/[:.]/g, "-")}`,
        success: true,
        domain: this.baseDomain,
        peripheryResults: [],
        labelsGenerated: false,
        stacksDeployed: [],
        totalDuration: 0,
        startedAt: startTime.toISOString(),
        completedAt: new Date().toISOString(),
        dryRun: true,
      });
    }

    // Step 1: Deploy Periphery to all servers
    console.log("Step 1: Deploying Periphery agents...");
    const periphery = new Periphery(
      sshKey,
      komodoPasskey,
      `wss://komodo.${this.baseDomain}:9120`
    );

    for (const server of servers) {
      console.log(`  Deploying to ${server.name}...`);
      try {
        const resultStr = await periphery.deploySingle(
          server.name,
          server.host,
          server.user,
          server.connectionMode,
          server.dockerNetwork || "pangolin"
        );
        const result: DeployResult = JSON.parse(resultStr);
        peripheryResults.push(result);

        // Step 2: Register public key in Komodo (if successful)
        if (result.success && result.publicKey) {
          console.log(`  Registering ${server.name} in Komodo...`);
          await periphery.registerInKomodo(
            server.name,
            result.publicKey,
            result.address || `https://${server.host}:8120`,
            komodoApiKey,
            komodoApiSecret,
            this.komodoUrl
          );
        }
      } catch (error) {
        peripheryResults.push({
          serverName: server.name,
          success: false,
          error: error instanceof Error ? error.message : "Unknown error",
          duration: 0,
        });
      }
    }

    // Step 3: Generate Pangolin labels
    console.log("Step 2: Generating Pangolin labels...");
    const labels = new PangolinLabels(this.baseDomain);
    const blueprint = labels.generateInfrastructureBlueprint();
    console.log("  Blueprint generated for default services");

    // Step 4: Deploy stacks via Komodo
    console.log("Step 3: Deploying stacks via Komodo...");
    const komodo = new Komodo(this.komodoUrl, komodoApiKey, komodoApiSecret);

    for (const stack of stacks) {
      try {
        console.log(`  Deploying ${stack}...`);
        await komodo.deployStack(stack);
        stacksDeployed.push(stack);
      } catch (error) {
        console.log(
          `  Failed to deploy ${stack}: ${error instanceof Error ? error.message : "Unknown"}`
        );
      }
    }

    const endTime = new Date();

    const result: DeploymentResult = {
      id: `deploy-${startTime.toISOString().replace(/[:.]/g, "-")}`,
      success: peripheryResults.every((r) => r.success),
      domain: this.baseDomain,
      peripheryResults,
      labelsGenerated: true,
      stacksDeployed,
      totalDuration: endTime.getTime() - startTime.getTime(),
      startedAt: startTime.toISOString(),
      completedAt: endTime.toISOString(),
    };

    return JSON.stringify(result, null, 2);
  }

  /**
   * Verify all infrastructure health
   */
  @func()
  async verifyAll(
    komodoApiKey: Secret,
    komodoApiSecret: Secret
  ): Promise<string> {
    const serverResults: Array<{
      name: string;
      peripheryHealthy: boolean;
      komodoConnected: boolean;
      error?: string;
    }> = [];

    const serviceResults: Array<{
      name: string;
      url: string;
      healthy: boolean;
      statusCode?: number;
      error?: string;
    }> = [];

    // Check core services
    const services = [
      { name: "Komodo", url: `https://komodo.${this.baseDomain}/health` },
      { name: "Forgejo", url: `https://git.${this.baseDomain}/api/v1/version` },
      { name: "PocketID", url: `https://auth.${this.baseDomain}/healthz` },
      { name: "Pangolin", url: `https://pangolin.${this.baseDomain}/api/v1/` },
    ];

    for (const svc of services) {
      try {
        const result = await dag
          .container()
          .from("curlimages/curl:8.11.1")
          .withExec([
            "curl",
            "-sf",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            svc.url,
          ])
          .stdout();

        const statusCode = parseInt(result.trim());
        serviceResults.push({
          name: svc.name,
          url: svc.url,
          healthy: statusCode >= 200 && statusCode < 400,
          statusCode,
        });
      } catch (error) {
        serviceResults.push({
          name: svc.name,
          url: svc.url,
          healthy: false,
          error: error instanceof Error ? error.message : "Unknown error",
        });
      }
    }

    // Get server list from Komodo
    const komodo = new Komodo(this.komodoUrl, komodoApiKey, komodoApiSecret);
    try {
      const serversData = await komodo.listServers();
      const serversList = JSON.parse(serversData);

      if (Array.isArray(serversList)) {
        for (const server of serversList) {
          const name = server.name || server.id;
          serverResults.push({
            name,
            peripheryHealthy: server.status === "Ok" || server.status === "online",
            komodoConnected: server.reachable !== false,
          });
        }
      }
    } catch (error) {
      console.log(`Failed to get server list: ${error}`);
    }

    const health: InfrastructureHealth = {
      healthy:
        serviceResults.every((s) => s.healthy) &&
        serverResults.every((s) => s.peripheryHealthy),
      servers: serverResults,
      services: serviceResults,
      timestamp: new Date().toISOString(),
    };

    return JSON.stringify(health, null, 2);
  }

  /**
   * Generate inventory JSON from current servers
   */
  @func()
  async generateInventory(
    komodoApiKey: Secret,
    komodoApiSecret: Secret
  ): Promise<string> {
    const komodo = new Komodo(this.komodoUrl, komodoApiKey, komodoApiSecret);

    try {
      const serversData = await komodo.listServers();
      const serversList = JSON.parse(serversData);

      const inventory: ServerConfig[] = [];

      if (Array.isArray(serversList)) {
        for (const server of serversList) {
          const name = server.name || server.id;
          const address = server.address || "";

          // Determine connection mode from address
          const connectionMode: "core_to_periphery" | "periphery_to_core" =
            address.includes("komodo-periphery") || address.includes("localhost")
              ? "core_to_periphery"
              : "periphery_to_core";

          // Extract host from address
          const hostMatch = address.match(/https?:\/\/([^:/]+)/);
          const host = hostMatch ? hostMatch[1] : address;

          inventory.push({
            name,
            host:
              connectionMode === "core_to_periphery"
                ? "132.145.27.89" // Default for same-network
                : host,
            user: "ubuntu", // Default user
            connectionMode,
            peripheryAddress: address,
            dockerNetwork: "pangolin",
          });
        }
      }

      return JSON.stringify(inventory, null, 2);
    } catch (error) {
      return JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }

  /**
   * Create a new Infrastructure instance for a different domain
   */
  @func()
  forDomain(baseDomain: string): Infrastructure {
    return new Infrastructure(
      baseDomain,
      `https://komodo.${baseDomain}`,
      this.opConnectHost
    );
  }

  /**
   * Deploy Periphery to a new server and register it
   */
  @func()
  async addServer(
    sshKey: Secret,
    komodoPasskey: Secret,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    serverName: string,
    sshHost: string,
    sshUser: string,
    connectionMode: string = "periphery_to_core"
  ): Promise<string> {
    console.log(`Adding server ${serverName} (${connectionMode})...`);

    const periphery = new Periphery(
      sshKey,
      komodoPasskey,
      `wss://komodo.${this.baseDomain}:9120`
    );

    // Deploy Periphery
    const deployResult = await periphery.deploySingle(
      serverName,
      sshHost,
      sshUser,
      connectionMode
    );

    const result: DeployResult = JSON.parse(deployResult);

    if (result.success && result.publicKey) {
      // Register in Komodo
      const registerResult = await periphery.registerInKomodo(
        serverName,
        result.publicKey,
        result.address || `https://${sshHost}:8120`,
        komodoApiKey,
        komodoApiSecret,
        this.komodoUrl
      );

      return JSON.stringify({
        ...result,
        registered: true,
        registrationResult: JSON.parse(registerResult),
      });
    }

    return deployResult;
  }
}
