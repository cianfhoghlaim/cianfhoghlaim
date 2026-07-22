/**
 * Komodo Periphery Deployment Module
 *
 * Provides automated deployment of Komodo Periphery agents across servers:
 * - Core→Periphery mode: Periphery listens, Core connects (same network)
 * - Periphery→Core mode: Periphery connects outbound (remote servers)
 * - Public key registration in Komodo Core
 * - Health verification
 *
 * Usage:
 *   dagger call periphery deploy-single --server-name="arm1-oci" --ssh-host="132.145.27.89" ...
 *   dagger call periphery deploy-all --inventory-path="./inventory.yml" ...
 */

import {
  dag,
  Container,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import { Komodo } from "./komodo.js";

/** Connection mode for Periphery agent */
export type ConnectionMode = "core_to_periphery" | "periphery_to_core";

/** Result of a deployment operation */
export interface DeployResult {
  serverName: string;
  success: boolean;
  publicKey?: string;
  address?: string;
  error?: string;
  duration: number;
}

/** Health check result */
export interface HealthResult {
  serverName: string;
  healthy: boolean;
  version?: string;
  uptime?: number;
  error?: string;
}

/** Server configuration from inventory */
export interface ServerConfig {
  name: string;
  host: string;
  user: string;
  connectionMode: ConnectionMode;
  peripheryAddress: string;
  dockerNetwork?: string;
}

@object()
export class Periphery {
  @field()
  sshKey: Secret;

  @field()
  komodoPasskey: Secret;

  @field()
  komodoAddress: string;

  @field()
  peripheryVersion: string;

  constructor(
    sshKey: Secret,
    komodoPasskey: Secret,
    komodoAddress: string = "wss://komodo.cianfhoghlaim.ie:9120",
    peripheryVersion: string = "2-dev"
  ) {
    this.sshKey = sshKey;
    this.komodoPasskey = komodoPasskey;
    this.komodoAddress = komodoAddress;
    this.peripheryVersion = peripheryVersion;
  }

  /**
   * Get SSH container for remote operations
   */
  private sshContainer(): Container {
    return dag
      .container()
      .from("alpine:3.19")
      .withExec(["apk", "add", "--no-cache", "openssh-client", "curl", "jq"])
      .withMountedSecret("/root/.ssh/id_ed25519", this.sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
      .withEnvVariable(
        "SSH_OPTS",
        "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
      );
  }

  /**
   * Execute SSH command on target host
   */
  private async sshExec(host: string, user: string, command: string): Promise<string> {
    return this.sshContainer()
      .withExec([
        "sh",
        "-c",
        `ssh $SSH_OPTS ${user}@${host} '${command}'`,
      ])
      .stdout();
  }

  /**
   * Deploy Periphery to a single server
   */
  @func()
  async deploySingle(
    serverName: string,
    sshHost: string,
    sshUser: string,
    connectionMode: string,
    dockerNetwork: string = "pangolin",
    peripheryRoot: string = "/etc/komodo"
  ): Promise<string> {
    const startTime = Date.now();
    const mode = connectionMode as ConnectionMode;

    try {
      // Stop existing container if running
      await this.sshExec(sshHost, sshUser, `
        docker stop komodo-periphery 2>/dev/null || true
        docker rm komodo-periphery 2>/dev/null || true
      `);

      // Ensure network exists
      await this.sshExec(sshHost, sshUser, `
        docker network create ${dockerNetwork} 2>/dev/null || true
      `);

      // Ensure root directory exists
      await this.sshExec(sshHost, sshUser, `
        mkdir -p ${peripheryRoot}
      `);

      // Build environment variables based on connection mode
      let envVars = "";
      if (mode === "periphery_to_core") {
        // Outbound mode: Periphery connects to Core
        envVars = `
          -e PERIPHERY_CORE_ADDRESSES="${this.komodoAddress}"
          -e PERIPHERY_CONNECT_AS="${serverName}"
          -e PERIPHERY_CORE_TLS_INSECURE_SKIP_VERIFY="true"
        `;
      }
      // For core_to_periphery mode, we don't set PERIPHERY_CORE_ADDRESSES
      // This makes Periphery listen for incoming connections

      // Get passkey value for docker run
      const passkeyValue = await dag
        .container()
        .from("alpine:3.19")
        .withSecretVariable("PASSKEY", this.komodoPasskey)
        .withExec(["sh", "-c", "echo $PASSKEY"])
        .stdout();

      // Deploy Periphery container
      const runCommand = `
        docker run -d \\
          --name komodo-periphery \\
          --restart unless-stopped \\
          --network ${dockerNetwork} \\
          -p 8120:8120 \\
          -v /var/run/docker.sock:/var/run/docker.sock \\
          -v /proc:/proc \\
          -v ${peripheryRoot}:${peripheryRoot} \\
          -e KOMODO_PASSKEY='${passkeyValue.trim()}' \\
          -e PERIPHERY_PASSKEYS='${passkeyValue.trim()}' \\
          -e PERIPHERY_STATS_POLL_INTERVAL="5s" \\
          ${envVars} \\
          ghcr.io/moghtech/komodo-periphery:${this.peripheryVersion}
      `;

      await this.sshExec(sshHost, sshUser, runCommand);

      // Wait for container to start
      await this.sshExec(sshHost, sshUser, "sleep 5");

      // Get public key from container logs
      const logs = await this.sshExec(sshHost, sshUser, `
        docker logs komodo-periphery 2>&1 | grep -oE 'MCow[A-Za-z0-9+/=]+' | head -1
      `);

      const publicKey = logs.trim();

      // Verify health
      const health = await this.sshExec(sshHost, sshUser, `
        curl -sf http://localhost:8120/health || echo 'unhealthy'
      `);

      const result: DeployResult = {
        serverName,
        success: !health.includes("unhealthy"),
        publicKey: publicKey || undefined,
        address:
          mode === "core_to_periphery"
            ? `https://komodo-periphery:8120`
            : `https://${sshHost}:8120`,
        duration: Date.now() - startTime,
      };

      return JSON.stringify(result, null, 2);
    } catch (error) {
      const result: DeployResult = {
        serverName,
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        duration: Date.now() - startTime,
      };
      return JSON.stringify(result, null, 2);
    }
  }

  /**
   * Deploy to all servers defined in a JSON config
   */
  @func()
  async deployAll(serversJson: string): Promise<string> {
    const servers: ServerConfig[] = JSON.parse(serversJson);
    const results: DeployResult[] = [];

    for (const server of servers) {
      const resultStr = await this.deploySingle(
        server.name,
        server.host,
        server.user,
        server.connectionMode,
        server.dockerNetwork || "pangolin"
      );
      results.push(JSON.parse(resultStr));
    }

    return JSON.stringify(
      {
        totalServers: servers.length,
        successful: results.filter((r) => r.success).length,
        failed: results.filter((r) => !r.success).length,
        results,
      },
      null,
      2
    );
  }

  /**
   * Register Periphery public key in Komodo Core
   */
  @func()
  async registerInKomodo(
    serverName: string,
    publicKey: string,
    address: string,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    coreUrl: string = "https://komodo.cianfhoghlaim.ie"
  ): Promise<string> {
    const komodo = new Komodo(coreUrl, komodoApiKey, komodoApiSecret);

    try {
      // First get the server to check if it exists
      const serverData = await komodo.getServer(serverName);
      const server = JSON.parse(serverData);

      // Update server with new public key and address
      const updateResult = await komodo.write("UpdateServer", {
        id: serverName,
        config: {
          address,
          attempted_public_key: publicKey,
        },
      });

      return JSON.stringify(
        {
          success: true,
          serverName,
          address,
          publicKey,
          updateResult: JSON.parse(updateResult),
        },
        null,
        2
      );
    } catch (error) {
      return JSON.stringify(
        {
          success: false,
          serverName,
          error: error instanceof Error ? error.message : "Unknown error",
        },
        null,
        2
      );
    }
  }

  /**
   * Verify Periphery connectivity and health
   */
  @func()
  async verify(
    serverName: string,
    sshHost: string,
    sshUser: string
  ): Promise<string> {
    try {
      // Check container is running
      const containerStatus = await this.sshExec(sshHost, sshUser, `
        docker inspect komodo-periphery --format='{{.State.Status}}' 2>/dev/null || echo 'not found'
      `);

      if (containerStatus.trim() !== "running") {
        return JSON.stringify({
          serverName,
          healthy: false,
          error: `Container status: ${containerStatus.trim()}`,
        } as HealthResult);
      }

      // Check health endpoint
      const health = await this.sshExec(sshHost, sshUser, `
        curl -sf http://localhost:8120/health || echo '{}'
      `);

      // Get container logs for version
      const logs = await this.sshExec(sshHost, sshUser, `
        docker logs komodo-periphery 2>&1 | grep -i version | head -1 || echo ''
      `);

      const result: HealthResult = {
        serverName,
        healthy: true,
        version: logs.trim() || this.peripheryVersion,
      };

      return JSON.stringify(result, null, 2);
    } catch (error) {
      return JSON.stringify({
        serverName,
        healthy: false,
        error: error instanceof Error ? error.message : "Unknown error",
      } as HealthResult);
    }
  }

  /**
   * Get Periphery logs from a server
   */
  @func()
  async getLogs(
    sshHost: string,
    sshUser: string,
    lines: number = 100
  ): Promise<string> {
    return this.sshExec(sshHost, sshUser, `
      docker logs --tail ${lines} komodo-periphery 2>&1
    `);
  }

  /**
   * Restart Periphery on a server
   */
  @func()
  async restart(sshHost: string, sshUser: string): Promise<string> {
    await this.sshExec(sshHost, sshUser, "docker restart komodo-periphery");

    // Wait for restart
    await this.sshExec(sshHost, sshUser, "sleep 5");

    // Get new public key (regenerated on restart)
    const logs = await this.sshExec(sshHost, sshUser, `
      docker logs komodo-periphery 2>&1 | grep -oE 'MCow[A-Za-z0-9+/=]+' | head -1
    `);

    return JSON.stringify({
      success: true,
      newPublicKey: logs.trim(),
      message:
        "Periphery restarted. IMPORTANT: Update public key in Komodo Core.",
    });
  }

  /**
   * Stop and remove Periphery from a server
   */
  @func()
  async remove(sshHost: string, sshUser: string): Promise<string> {
    await this.sshExec(sshHost, sshUser, `
      docker stop komodo-periphery 2>/dev/null || true
      docker rm komodo-periphery 2>/dev/null || true
    `);

    return JSON.stringify({
      success: true,
      message: "Periphery container removed",
    });
  }
}
