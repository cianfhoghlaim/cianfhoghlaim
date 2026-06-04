/**
 * Pangolin Deployment Orchestration Module
 *
 * Provides complete platform deployment from fresh server to production state:
 * - 10-stage deployment pipeline
 * - Browser automation integration for manual UI steps
 * - 1Password Connect for secrets management
 * - Komodo integration for stack deployment
 *
 * Usage:
 *   dagger call pangolin-deployment --target-host="ubuntu@server" --domain="example.com" deploy-full
 *   dagger call pangolin-deployment deploy-from --stage=5
 *   dagger call pangolin-deployment verify
 */

import {
  dag,
  Container,
  Directory,
  Secret,
  object,
  func,
  field,
} from "@dagger.io/dagger";

import type {
  StageResult,
  DeploymentResult,
  VerificationResult,
  SiteConfig,
  OLMClientConfig,
  ServiceHealth,
  SSLHealth,
  CrowdSecHealth,
  TunnelHealth,
} from "./types";

import { STAGES } from "./types";
import { PangolinApi } from "./pangolin-api";
import { Komodo } from "./komodo";

@object()
export class PangolinDeployment {
  @field()
  targetHost: string;

  @field()
  domain: string;

  @field()
  opConnectHost: string;

  @field()
  browserServerUrl: string;

  @field()
  orgId: string;

  @field()
  sshKey: Secret;

  @field()
  opConnectToken: Secret;

  constructor(
    targetHost: string,
    domain: string,
    sshKey: Secret,
    opConnectToken: Secret,
    opConnectHost: string = "http://132.145.27.89:8080",
    browserServerUrl: string = "http://localhost:3001",
    orgId: string = "cianfhoghlaim"
  ) {
    this.targetHost = targetHost;
    this.domain = domain;
    this.sshKey = sshKey;
    this.opConnectToken = opConnectToken;
    this.opConnectHost = opConnectHost;
    this.browserServerUrl = browserServerUrl;
    this.orgId = orgId;
  }

  // ===========================================================================
  // Private Helper Methods
  // ===========================================================================

  /**
   * Get a base SSH container for remote operations
   */
  private sshContainer(): Container {
    return dag
      .container()
      .from("alpine:3.19")
      .withExec(["apk", "add", "--no-cache", "openssh-client", "curl", "jq"])
      .withMountedSecret("/root/.ssh/id_ed25519", this.sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
      .withEnvVariable("SSH_OPTS", "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null");
  }

  /**
   * Execute SSH command on target host
   */
  private async sshExec(command: string): Promise<string> {
    return this.sshContainer()
      .withExec([
        "sh",
        "-c",
        `ssh $SSH_OPTS ${this.targetHost} '${command}'`,
      ])
      .stdout();
  }

  /**
   * Execute SCP to copy files to target host
   */
  private async scpCopy(localPath: string, remotePath: string): Promise<string> {
    return this.sshContainer()
      .withExec([
        "sh",
        "-c",
        `scp $SSH_OPTS ${localPath} ${this.targetHost}:${remotePath}`,
      ])
      .stdout();
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

  /**
   * Read secret from 1Password
   */
  private async readSecret(reference: string): Promise<string> {
    return this.opContainer()
      .withExec(["op", "read", reference])
      .stdout();
  }

  /**
   * Create a StageResult
   */
  private createStageResult(
    stage: string,
    success: boolean,
    output: string,
    options?: { skipped?: boolean; error?: string; duration?: number; humanApproved?: boolean }
  ): StageResult {
    return {
      stage,
      success,
      output,
      ...options,
    };
  }

  /**
   * Check if a service is healthy
   */
  private async checkServiceHealth(name: string, url: string): Promise<ServiceHealth> {
    const startTime = Date.now();
    try {
      const result = await dag
        .container()
        .from("curlimages/curl:8.11.1")
        .withExec(["curl", "-sf", "-o", "/dev/null", "-w", "%{http_code}", url])
        .stdout();

      const statusCode = parseInt(result.trim());
      return {
        name,
        url,
        healthy: statusCode >= 200 && statusCode < 400,
        statusCode,
        responseTime: Date.now() - startTime,
      };
    } catch (error) {
      return {
        name,
        url,
        healthy: false,
        error: error instanceof Error ? error.message : "Unknown error",
        responseTime: Date.now() - startTime,
      };
    }
  }

  // ===========================================================================
  // Stage 1: Server Initialization
  // ===========================================================================

  /**
   * Initialize server with Docker and required directories
   */
  @func()
  async initServer(dryRun: boolean = false): Promise<StageResult> {
    const stage = "initServer";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(stage, true, "DRY RUN: Would initialize server", { skipped: true });
    }

    try {
      // Check SSH connectivity
      await this.sshExec("echo 'SSH connection successful'");

      // Install Docker if not present
      await this.sshExec(`
        if ! command -v docker &> /dev/null; then
          curl -fsSL https://get.docker.com | sh
          sudo usermod -aG docker $USER
        fi
      `);

      // Create directory structure
      await this.sshExec(`
        sudo mkdir -p /opt/pangolin/{config,data}
        sudo mkdir -p /opt/komodo/{config,stacks}
        sudo mkdir -p /opt/forgejo/{config,data}
        sudo chown -R $USER:$USER /opt/{pangolin,komodo,forgejo}
      `);

      // Verify Docker is running
      const dockerVersion = await this.sshExec("docker --version");

      return this.createStageResult(
        stage,
        true,
        `Server initialized. Docker: ${dockerVersion.trim()}`,
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 2: 1Password Connect Deployment
  // ===========================================================================

  /**
   * Deploy 1Password Connect for secrets management
   */
  @func()
  async deployOpConnect(
    credentials: Secret,
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "deployOpConnect";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(stage, true, "DRY RUN: Would deploy 1Password Connect", { skipped: true });
    }

    try {
      // Deploy 1Password Connect stack
      await this.sshExec(`
        mkdir -p /opt/op-connect
        cat > /opt/op-connect/docker-compose.yml << 'EOF'
version: '3.9'
services:
  connect-api:
    image: 1password/connect-api:latest
    ports:
      - "8080:8080"
    volumes:
      - /opt/op-connect/1password-credentials.json:/home/opuser/.op/1password-credentials.json:ro
      - op-data:/home/opuser/.op/data
    restart: unless-stopped

  connect-sync:
    image: 1password/connect-sync:latest
    volumes:
      - /opt/op-connect/1password-credentials.json:/home/opuser/.op/1password-credentials.json:ro
      - op-data:/home/opuser/.op/data
    restart: unless-stopped

volumes:
  op-data:
EOF
      `);

      // Copy credentials file
      const credentialsJson = await dag.container()
        .from("alpine:3.19")
        .withMountedSecret("/creds.json", credentials)
        .withExec(["cat", "/creds.json"])
        .stdout();

      await this.sshExec(`echo '${credentialsJson}' > /opt/op-connect/1password-credentials.json`);
      await this.sshExec("chmod 600 /opt/op-connect/1password-credentials.json");

      // Start the stack
      await this.sshExec("cd /opt/op-connect && docker compose up -d");

      // Wait for health
      await this.sshExec("sleep 10");
      const health = await this.sshExec("curl -sf http://localhost:8080/health || echo 'unhealthy'");

      return this.createStageResult(
        stage,
        health.includes("unhealthy") === false,
        `1Password Connect deployed. Health: ${health.trim()}`,
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 3: Pangolin Core Stack
  // ===========================================================================

  /**
   * Deploy Pangolin core stack (9 services)
   */
  @func()
  async deployPangolinCore(
    pangolinDir: Directory,
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "deployPangolinCore";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(stage, true, "DRY RUN: Would deploy Pangolin core stack", { skipped: true });
    }

    try {
      // Get secrets from 1Password
      const serverSecret = await this.readSecret("op://dev-baile/pangolin/server_secret");
      const postgresPassword = await this.readSecret("op://dev-baile/pangolin/postgres_password");
      const cfApiToken = await this.readSecret("op://dev-baile/cloudflare/api_token");

      // Copy Pangolin directory to target
      const composeContent = await pangolinDir.file("compose.yaml").contents();
      await this.sshExec(`mkdir -p /opt/pangolin && cat > /opt/pangolin/compose.yaml << 'COMPOSEEOF'
${composeContent}
COMPOSEEOF`);

      // Create .env file with secrets
      await this.sshExec(`cat > /opt/pangolin/.env << 'ENVEOF'
SERVER_SECRET=${serverSecret.trim()}
POSTGRES_PASSWORD=${postgresPassword.trim()}
CF_DNS_API_TOKEN=${cfApiToken.trim()}
POCKET_ID_URL=https://auth.${this.domain}
TINYAUTH_URL=https://tinyauth.${this.domain}
ENVEOF`);

      // Copy config directory
      const configFiles = await pangolinDir.directory("config").entries();
      await this.sshExec("mkdir -p /opt/pangolin/config");
      for (const entry of configFiles) {
        const content = await pangolinDir.file(`config/${entry}`).contents();
        await this.sshExec(`cat > /opt/pangolin/config/${entry} << 'CFGEOF'
${content}
CFGEOF`);
      }

      // Deploy the stack
      await this.sshExec("cd /opt/pangolin && docker compose up -d");

      // Wait for Pangolin to be healthy
      await this.sshExec("sleep 30");
      const health = await this.sshExec("docker exec pangolin curl -sf http://localhost:3001/api/v1/ || echo 'unhealthy'");

      return this.createStageResult(
        stage,
        !health.includes("unhealthy"),
        `Pangolin core deployed. Health: ${health.trim().substring(0, 100)}`,
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 4: PocketID Admin Setup (Browser - Human in Loop)
  // ===========================================================================

  /**
   * Setup PocketID admin account (requires human approval for WebAuthn)
   */
  @func()
  async setupPocketIdAdmin(dryRun: boolean = false): Promise<StageResult> {
    const stage = "setupPocketIdAdmin";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would request human approval for PocketID admin setup",
        { skipped: true }
      );
    }

    try {
      // Check if already configured
      const healthCheck = await dag
        .container()
        .from("curlimages/curl:8.11.1")
        .withExec(["curl", "-sf", `https://auth.${this.domain}/healthz`])
        .stdout();

      if (healthCheck.includes("ok")) {
        return this.createStageResult(
          stage,
          true,
          "PocketID already configured",
          { skipped: true, duration: Date.now() - startTime }
        );
      }

      // Request human approval via browser automation API
      const approvalRequest = {
        task: "PocketID Admin Setup",
        instructions: [
          `Navigate to https://auth.${this.domain}/setup`,
          "Create admin account with passkey",
          "Complete WebAuthn registration",
          "Click 'Complete Setup'",
        ],
        url: `https://auth.${this.domain}/setup`,
        timeout: 300,
      };

      // Call browser automation service for human-in-the-loop
      const result = await dag
        .container()
        .from("curlimages/curl:8.11.1")
        .withExec([
          "curl",
          "-sf",
          "-X", "POST",
          `${this.browserServerUrl}/api/approval/request`,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify(approvalRequest),
        ])
        .stdout();

      const approval = JSON.parse(result);

      return this.createStageResult(
        stage,
        approval.approved,
        approval.approved ? "PocketID admin setup completed" : "Human approval denied or timed out",
        { humanApproved: approval.approved, duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 5: OAuth Client Creation (Browser - Automated)
  // ===========================================================================

  /**
   * Create OAuth client for TinyAuth in PocketID (automated browser)
   */
  @func()
  async createOAuthClient(dryRun: boolean = false): Promise<StageResult> {
    const stage = "createOAuthClient";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would create OAuth client via browser automation",
        { skipped: true }
      );
    }

    try {
      // Use Stagehand for automated browser interaction
      const automationRequest = {
        url: `https://auth.${this.domain}/admin`,
        actions: [
          { type: "navigate", url: `https://auth.${this.domain}/admin/oidc-clients` },
          { type: "click", selector: "button:contains('Add Client')" },
          { type: "fill", selector: "input[name='name']", value: "TinyAuth" },
          { type: "fill", selector: "input[name='redirectUri']", value: `https://tinyauth.${this.domain}/api/oauth/callback/pocketid` },
          { type: "fill", selector: "input[name='scopes']", value: "openid email profile groups" },
          { type: "click", selector: "button:contains('Save')" },
          { type: "extract", schema: { clientId: "string", clientSecret: "string" } },
        ],
      };

      const result = await dag
        .container()
        .from("curlimages/curl:8.11.1")
        .withExec([
          "curl",
          "-sf",
          "-X", "POST",
          `${this.browserServerUrl}/api/automate`,
          "-H", "Content-Type: application/json",
          "-d", JSON.stringify(automationRequest),
        ])
        .stdout();

      const credentials = JSON.parse(result);

      // Store credentials in 1Password
      await this.opContainer()
        .withExec([
          "op", "item", "edit", "pocketid-tinyauth",
          "--vault", "dev-baile",
          `client_id=${credentials.clientId}`,
          `client_secret=${credentials.clientSecret}`,
        ])
        .stdout();

      // Update TinyAuth environment
      await this.sshExec(`
        cd /opt/pangolin
        sed -i 's/POCKETID_CLIENT_ID=.*/POCKETID_CLIENT_ID=${credentials.clientId}/' .env
        sed -i 's/POCKETID_CLIENT_SECRET=.*/POCKETID_CLIENT_SECRET=${credentials.clientSecret}/' .env
        docker compose restart tinyauth
      `);

      return this.createStageResult(
        stage,
        true,
        `OAuth client created. Client ID: ${credentials.clientId}`,
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 6: CrowdSec Bouncer Key Generation
  // ===========================================================================

  /**
   * Generate CrowdSec bouncer key for Traefik
   */
  @func()
  async generateCrowdSecKey(dryRun: boolean = false): Promise<StageResult> {
    const stage = "generateCrowdSecKey";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would generate CrowdSec bouncer key",
        { skipped: true }
      );
    }

    try {
      // Generate bouncer key
      const bouncerKey = await this.sshExec(
        "docker exec crowdsec cscli bouncers add traefik-bouncer -o raw"
      );

      // Store in 1Password
      await this.opContainer()
        .withExec([
          "op", "item", "edit", "crowdsec",
          "--vault", "dev-baile",
          `bouncer_key=${bouncerKey.trim()}`,
        ])
        .stdout();

      // Update Pangolin .env
      await this.sshExec(`
        cd /opt/pangolin
        sed -i 's/CROWDSEC_BOUNCER_KEY=.*/CROWDSEC_BOUNCER_KEY=${bouncerKey.trim()}/' .env
        docker compose restart traefik
      `);

      return this.createStageResult(
        stage,
        true,
        "CrowdSec bouncer key generated and configured",
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 7: Komodo Core + Periphery
  // ===========================================================================

  /**
   * Deploy Komodo Core and Periphery
   */
  @func()
  async deployKomodo(
    komodoDir: Directory,
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "deployKomodo";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would deploy Komodo Core and Periphery",
        { skipped: true }
      );
    }

    try {
      // Copy Komodo compose files
      const coreCompose = await komodoDir.file("core.compose.yaml").contents();
      const peripheryCompose = await komodoDir.file("periphery.compose.yaml").contents();

      await this.sshExec(`cat > /opt/komodo/core.compose.yaml << 'COMPOSEEOF'
${coreCompose}
COMPOSEEOF`);

      await this.sshExec(`cat > /opt/komodo/periphery.compose.yaml << 'COMPOSEEOF'
${peripheryCompose}
COMPOSEEOF`);

      // Generate Komodo secrets
      const apiKey = await dag
        .container()
        .from("alpine:3.19")
        .withExec(["sh", "-c", "cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 32 | head -n 1"])
        .stdout();

      const apiSecret = await dag
        .container()
        .from("alpine:3.19")
        .withExec(["sh", "-c", "cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 64 | head -n 1"])
        .stdout();

      // Create Komodo .env
      await this.sshExec(`cat > /opt/komodo/.env << 'ENVEOF'
KOMODO_HOST=https://komodo.${this.domain}
KOMODO_API_KEY=${apiKey.trim()}
KOMODO_API_SECRET=${apiSecret.trim()}
ENVEOF`);

      // Store in 1Password
      await this.opContainer()
        .withExec([
          "op", "item", "create",
          "--vault", "dev-baile",
          "--category", "API Credential",
          "--title", "komodo",
          `api_key=${apiKey.trim()}`,
          `api_secret=${apiSecret.trim()}`,
        ])
        .stdout();

      // Deploy Komodo Core
      await this.sshExec("cd /opt/komodo && docker compose -f core.compose.yaml up -d");

      // Wait and deploy Periphery
      await this.sshExec("sleep 20");
      await this.sshExec("cd /opt/komodo && docker compose -f periphery.compose.yaml up -d");

      // Verify health
      const health = await this.sshExec(`curl -sf https://komodo.${this.domain}/health || echo 'unhealthy'`);

      return this.createStageResult(
        stage,
        !health.includes("unhealthy"),
        `Komodo deployed. Health: ${health.trim()}`,
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 8: Forgejo + GitOps Setup
  // ===========================================================================

  /**
   * Deploy Forgejo and configure GitOps
   */
  @func()
  async deployForgejo(
    forgejoDir: Directory,
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "deployForgejo";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would deploy Forgejo and configure GitOps",
        { skipped: true }
      );
    }

    try {
      // Copy Forgejo compose
      const composeContent = await forgejoDir.file("compose.yaml").contents();
      await this.sshExec(`mkdir -p /opt/forgejo && cat > /opt/forgejo/compose.yaml << 'COMPOSEEOF'
${composeContent}
COMPOSEEOF`);

      // Generate admin credentials
      const adminPassword = await dag
        .container()
        .from("alpine:3.19")
        .withExec(["sh", "-c", "cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 24 | head -n 1"])
        .stdout();

      // Create Forgejo .env
      await this.sshExec(`cat > /opt/forgejo/.env << 'ENVEOF'
FORGEJO_DOMAIN=git.${this.domain}
FORGEJO_ADMIN_USER=admin
FORGEJO_ADMIN_PASSWORD=${adminPassword.trim()}
ENVEOF`);

      // Deploy Forgejo
      await this.sshExec("cd /opt/forgejo && docker compose up -d");

      // Wait for Forgejo to start
      await this.sshExec("sleep 30");

      // Create admin user
      await this.sshExec(`docker exec forgejo forgejo admin user create \
        --username admin \
        --password '${adminPassword.trim()}' \
        --email admin@${this.domain} \
        --admin || true`);

      // Generate admin token
      const adminToken = await this.sshExec(`docker exec forgejo forgejo admin user generate-access-token \
        --username admin \
        --token-name "komodo-integration" \
        --scopes "all" 2>/dev/null | grep -oE '[a-f0-9]{40}' || echo 'token-generation-failed'`);

      // Store in 1Password
      await this.opContainer()
        .withExec([
          "op", "item", "create",
          "--vault", "dev-baile",
          "--category", "Login",
          "--title", "forgejo",
          `admin_password=${adminPassword.trim()}`,
          `admin_token=${adminToken.trim()}`,
        ])
        .stdout();

      // Verify health
      const health = await this.sshExec(`curl -sf https://git.${this.domain}/api/v1/version || echo 'unhealthy'`);

      return this.createStageResult(
        stage,
        !health.includes("unhealthy"),
        `Forgejo deployed. Version: ${health.trim()}`,
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 9: Pangolin Sites via Integration API
  // ===========================================================================

  /**
   * Create Pangolin sites via Integration API
   */
  @func()
  async createPangolinSites(
    pangolinToken: Secret,
    sites: string, // JSON array of SiteConfig
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "createPangolinSites";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would create Pangolin sites via API",
        { skipped: true }
      );
    }

    try {
      const siteConfigs: SiteConfig[] = JSON.parse(sites);
      const api = new PangolinApi(`https://api.${this.domain}`, pangolinToken);

      // Create organization if needed
      try {
        await api.createOrg(this.orgId, "Cianfhoghlaim", "10.100.0.0/16");
      } catch {
        // Organization may already exist
      }

      const results: string[] = [];

      for (const site of siteConfigs) {
        // Create site with defaults
        const siteResult = await api.createSiteWithDefaults(
          this.orgId,
          site.name,
          site.type as "newt" | "wireguard" | "local"
        );
        const siteData = JSON.parse(siteResult);

        // Store Newt credentials in 1Password
        if (site.type === "newt" && siteData.newtId && siteData.newtSecret) {
          await this.opContainer()
            .withExec([
              "op", "item", "create",
              "--vault", "dev-baile",
              "--category", "API Credential",
              "--title", `newt-${site.name.toLowerCase().replace(/\s+/g, "-")}`,
              `newt_id=${siteData.newtId}`,
              `newt_secret=${siteData.newtSecret}`,
            ])
            .stdout();
        }

        // Apply blueprint if specified
        if (site.blueprint) {
          const blueprintBase64 = Buffer.from(site.blueprint).toString("base64");
          await api.applyBlueprint(this.orgId, blueprintBase64);
        }

        results.push(`Created site: ${site.name} (${site.type})`);
      }

      return this.createStageResult(
        stage,
        true,
        results.join("\n"),
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 9b: OLM Client Creation via Integration API
  // ===========================================================================

  /**
   * Store OLM credentials in 1Password
   */
  private async storeOLMCredentials(
    itemTitle: string,
    olmId: string,
    olmSecret: string
  ): Promise<void> {
    await this.opContainer()
      .withExec([
        "op", "item", "create",
        "--vault", "dev-baile",
        "--category", "API Credential",
        "--title", itemTitle,
        `id=${olmId}`,
        `secret[password]=${olmSecret}`,
        "--tags", "olm,pangolin,automation"
      ])
      .stdout();
  }

  /**
   * Create OLM clients via Pangolin Integration API
   *
   * This method:
   * 1. Resolves Newt site names to IDs
   * 2. Creates OLM clients in Pangolin via API
   * 3. Stores credentials in 1Password
   * 4. Deploys OLM stacks via Komodo
   */
  @func()
  async createOLMClients(
    pangolinToken: Secret,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    clients: string, // JSON array of OLMClientConfig
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "createOLMClients";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would create OLM clients via API",
        { skipped: true }
      );
    }

    try {
      const clientConfigs: OLMClientConfig[] = JSON.parse(clients);
      const api = new PangolinApi(`https://api.${this.domain}`, pangolinToken);
      const komodo = new Komodo(`https://komodo.${this.domain}`, komodoApiKey, komodoApiSecret);

      // Get existing sites to resolve names → IDs
      const sitesJson = await api.listSites(this.orgId);
      const sites = JSON.parse(sitesJson);
      const siteNameToId = new Map<string, number>(
        sites.map((s: { name: string; id: number }) => [s.name, s.id])
      );

      const results: string[] = [];

      for (const config of clientConfigs) {
        // Resolve site names to IDs
        const siteIds: number[] = [];
        for (const siteName of config.siteNames) {
          const id = siteNameToId.get(siteName);
          if (!id) {
            throw new Error(`Site not found: ${siteName}. Ensure Newt site exists before creating OLM client.`);
          }
          siteIds.push(id);
        }

        // Create OLM client via Pangolin API
        const clientResultJson = await api.createOLMClientWithDefaults(
          this.orgId,
          config.name,
          siteIds
        );
        const clientData = JSON.parse(clientResultJson);

        // Store credentials in 1Password
        await this.storeOLMCredentials(
          config.name,
          clientData.olmId,
          clientData.secret
        );

        // Deploy OLM stack via Komodo
        const stackName = `olm-${config.server.replace(/\s+/g, "-").toLowerCase()}`;
        try {
          await komodo.deployStack(stackName);
          results.push(`✓ Created & deployed: ${config.name} → ${stackName}`);
        } catch (deployError) {
          results.push(`✓ Created ${config.name}, deploy pending: ${deployError instanceof Error ? deployError.message : "Unknown"}`);
        }

        // Apply TCP blueprint if specified
        if (config.blueprint) {
          const blueprintBase64 = Buffer.from(config.blueprint).toString("base64");
          await api.applyBlueprint(this.orgId, blueprintBase64);
          results.push(`  Applied blueprint for ${config.name}`);
        }
      }

      return this.createStageResult(
        stage,
        true,
        results.join("\n"),
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Stage 10: Application Stacks + Final Verification
  // ===========================================================================

  /**
   * Deploy application stacks via Komodo
   */
  @func()
  async deployAppStacks(
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    stacks: string, // JSON array of stack names
    dryRun: boolean = false
  ): Promise<StageResult> {
    const stage = "deployAppStacks";
    const startTime = Date.now();

    if (dryRun) {
      return this.createStageResult(
        stage,
        true,
        "DRY RUN: Would deploy application stacks via Komodo",
        { skipped: true }
      );
    }

    try {
      const stackNames: string[] = JSON.parse(stacks);
      const komodo = new Komodo(`https://komodo.${this.domain}`, komodoApiKey, komodoApiSecret);

      const results: string[] = [];

      for (const stackName of stackNames) {
        try {
          const result = await komodo.deployStack(stackName);
          results.push(`Deployed stack: ${stackName} - ${result}`);
        } catch (error) {
          results.push(`Failed to deploy ${stackName}: ${error instanceof Error ? error.message : "Unknown"}`);
        }
      }

      return this.createStageResult(
        stage,
        true,
        results.join("\n"),
        { duration: Date.now() - startTime }
      );
    } catch (error) {
      return this.createStageResult(
        stage,
        false,
        "",
        { error: error instanceof Error ? error.message : "Unknown error", duration: Date.now() - startTime }
      );
    }
  }

  // ===========================================================================
  // Orchestration Methods
  // ===========================================================================

  /**
   * Run full deployment pipeline
   */
  @func()
  async deployFull(
    pangolinDir: Directory,
    komodoDir: Directory,
    forgejoDir: Directory,
    opCredentials: Secret,
    pangolinToken: Secret,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    sites: string = "[]",
    stacks: string = "[]",
    dryRun: boolean = false
  ): Promise<string> {
    const startTime = new Date();
    const stages: StageResult[] = [];

    console.log(`=== ${dryRun ? "DRY RUN" : "FULL DEPLOYMENT"} ===`);
    console.log(`Target: ${this.targetHost}`);
    console.log(`Domain: ${this.domain}`);
    console.log("");

    // Stage 1: Server Initialization
    console.log("Stage 1: Initializing server...");
    stages.push(await this.initServer(dryRun));

    // Stage 2: 1Password Connect
    console.log("Stage 2: Deploying 1Password Connect...");
    stages.push(await this.deployOpConnect(opCredentials, dryRun));

    // Stage 3: Pangolin Core
    console.log("Stage 3: Deploying Pangolin Core...");
    stages.push(await this.deployPangolinCore(pangolinDir, dryRun));

    // Stage 4: PocketID Admin
    console.log("Stage 4: Setting up PocketID Admin...");
    stages.push(await this.setupPocketIdAdmin(dryRun));

    // Stage 5: OAuth Client
    console.log("Stage 5: Creating OAuth Client...");
    stages.push(await this.createOAuthClient(dryRun));

    // Stage 6: CrowdSec
    console.log("Stage 6: Generating CrowdSec Key...");
    stages.push(await this.generateCrowdSecKey(dryRun));

    // Stage 7: Komodo
    console.log("Stage 7: Deploying Komodo...");
    stages.push(await this.deployKomodo(komodoDir, dryRun));

    // Stage 8: Forgejo
    console.log("Stage 8: Deploying Forgejo...");
    stages.push(await this.deployForgejo(forgejoDir, dryRun));

    // Stage 9: Pangolin Sites
    console.log("Stage 9: Creating Pangolin Sites...");
    stages.push(await this.createPangolinSites(pangolinToken, sites, dryRun));

    // Stage 10: Application Stacks
    console.log("Stage 10: Deploying Application Stacks...");
    stages.push(await this.deployAppStacks(komodoApiKey, komodoApiSecret, stacks, dryRun));

    const endTime = new Date();
    const totalDuration = endTime.getTime() - startTime.getTime();

    const result: DeploymentResult = {
      id: `deploy-${startTime.toISOString().replace(/[:.]/g, "-")}`,
      success: stages.every((s) => s.success),
      stages,
      totalDuration,
      startedAt: startTime.toISOString(),
      completedAt: endTime.toISOString(),
    };

    return JSON.stringify(result, null, 2);
  }

  /**
   * Resume deployment from a specific stage
   */
  @func()
  async deployFrom(
    stage: number,
    pangolinDir: Directory,
    komodoDir: Directory,
    forgejoDir: Directory,
    opCredentials: Secret,
    pangolinToken: Secret,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    sites: string = "[]",
    stacks: string = "[]"
  ): Promise<string> {
    const startTime = new Date();
    const stages: StageResult[] = [];

    console.log(`=== RESUMING FROM STAGE ${stage} ===`);

    // Mark earlier stages as skipped
    for (let i = 0; i < stage; i++) {
      stages.push({
        stage: STAGES[i],
        success: true,
        output: "Skipped (resuming from later stage)",
        skipped: true,
      });
    }

    // Run remaining stages
    if (stage <= 0) stages.push(await this.initServer());
    if (stage <= 1) stages.push(await this.deployOpConnect(opCredentials));
    if (stage <= 2) stages.push(await this.deployPangolinCore(pangolinDir));
    if (stage <= 3) stages.push(await this.setupPocketIdAdmin());
    if (stage <= 4) stages.push(await this.createOAuthClient());
    if (stage <= 5) stages.push(await this.generateCrowdSecKey());
    if (stage <= 6) stages.push(await this.deployKomodo(komodoDir));
    if (stage <= 7) stages.push(await this.deployForgejo(forgejoDir));
    if (stage <= 8) stages.push(await this.createPangolinSites(pangolinToken, sites));
    if (stage <= 9) stages.push(await this.deployAppStacks(komodoApiKey, komodoApiSecret, stacks));

    const endTime = new Date();

    const result: DeploymentResult = {
      id: `deploy-resume-${startTime.toISOString().replace(/[:.]/g, "-")}`,
      success: stages.every((s) => s.success),
      stages,
      totalDuration: endTime.getTime() - startTime.getTime(),
      startedAt: startTime.toISOString(),
      completedAt: endTime.toISOString(),
    };

    return JSON.stringify(result, null, 2);
  }

  /**
   * Verify deployment health
   */
  @func()
  async verify(): Promise<string> {
    const services: ServiceHealth[] = [];

    // Check core services
    services.push(await this.checkServiceHealth("pangolin", `https://pangolin.${this.domain}/api/v1/`));
    services.push(await this.checkServiceHealth("pocketid", `https://auth.${this.domain}/healthz`));
    services.push(await this.checkServiceHealth("tinyauth", `https://tinyauth.${this.domain}/healthz`));
    services.push(await this.checkServiceHealth("komodo", `https://komodo.${this.domain}/health`));
    services.push(await this.checkServiceHealth("forgejo", `https://git.${this.domain}/api/v1/version`));

    // Check SSL
    let ssl: SSLHealth | undefined;
    try {
      const sslResult = await dag
        .container()
        .from("alpine:3.19")
        .withExec(["apk", "add", "--no-cache", "openssl"])
        .withExec([
          "sh",
          "-c",
          `echo | openssl s_client -servername ${this.domain} -connect ${this.domain}:443 2>/dev/null | openssl x509 -noout -dates -issuer`,
        ])
        .stdout();

      const expiryMatch = sslResult.match(/notAfter=(.+)/);
      const issuerMatch = sslResult.match(/issuer=(.+)/);

      if (expiryMatch) {
        const expiryDate = new Date(expiryMatch[1]);
        const daysUntilExpiry = Math.floor((expiryDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));

        ssl = {
          domain: this.domain,
          valid: daysUntilExpiry > 0,
          issuer: issuerMatch ? issuerMatch[1].trim() : undefined,
          expiresAt: expiryDate.toISOString(),
          daysUntilExpiry,
        };
      }
    } catch {
      ssl = { domain: this.domain, valid: false };
    }

    // Check CrowdSec
    let crowdsec: CrowdSecHealth | undefined;
    try {
      const bouncerList = await this.sshExec("docker exec crowdsec cscli bouncers list -o json");
      const bouncers = JSON.parse(bouncerList);
      crowdsec = {
        enabled: true,
        bouncerRegistered: bouncers.length > 0,
        decisionsCount: 0,
        alertsCount: 0,
      };
    } catch {
      crowdsec = { enabled: false, bouncerRegistered: false };
    }

    const result: VerificationResult = {
      healthy: services.every((s) => s.healthy),
      services,
      ssl,
      crowdsec,
      timestamp: new Date().toISOString(),
    };

    return JSON.stringify(result, null, 2);
  }

  /**
   * Rollback to a specific stage (stops services deployed after that stage)
   */
  @func()
  async rollback(stage: number): Promise<string> {
    const results: string[] = [];

    console.log(`=== ROLLING BACK TO STAGE ${stage} ===`);

    // Stop services in reverse order
    if (stage < 9) {
      results.push("Would stop application stacks");
    }
    if (stage < 8) {
      await this.sshExec("cd /opt/forgejo && docker compose down || true");
      results.push("Stopped Forgejo");
    }
    if (stage < 7) {
      await this.sshExec("cd /opt/komodo && docker compose -f periphery.compose.yaml down || true");
      await this.sshExec("cd /opt/komodo && docker compose -f core.compose.yaml down || true");
      results.push("Stopped Komodo");
    }
    if (stage < 2) {
      await this.sshExec("cd /opt/pangolin && docker compose down || true");
      results.push("Stopped Pangolin");
    }
    if (stage < 1) {
      await this.sshExec("cd /opt/op-connect && docker compose down || true");
      results.push("Stopped 1Password Connect");
    }

    return JSON.stringify({
      rolledBackTo: stage,
      actions: results,
      timestamp: new Date().toISOString(),
    }, null, 2);
  }
}
