/**
 * GitOps Setup Pipeline Module
 *
 * Orchestrates the complete GitOps pipeline setup:
 * 1. Create renovate-bot user in Forgejo
 * 2. Generate access token for renovate-bot
 * 3. Set RENOVATE_TOKEN as Actions secret
 * 4. Configure webhooks (Forgejo → Komodo)
 * 5. Create Git Provider in Komodo
 * 6. Deploy Forgejo Runner stack
 * 7. Trigger resource sync
 * 8. Verify pipeline functionality
 */

import { dag, Secret, object, func, field } from "@dagger.io/dagger";
import { Forgejo } from "./forgejo";
import { Komodo } from "./komodo";

interface SetupResult {
  step: string;
  success: boolean;
  output: string;
  error?: string;
}

@object()
export class GitOpsSetup {
  /**
   * Run the complete GitOps setup pipeline
   */
  @func()
  async setupComplete(
    forgejoUrl: string,
    forgejoAdminToken: Secret,
    komodoUrl: string,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    webhookSecret: Secret,
    renovatePassword: Secret
  ): Promise<string> {
    const forgejo = new Forgejo(forgejoUrl, forgejoAdminToken);
    const komodo = new Komodo(komodoUrl, komodoApiKey, komodoApiSecret);
    const results: SetupResult[] = [];

    // Step 1: Create renovate-bot user
    try {
      const userResult = await forgejo.createUser(
        "renovate-bot",
        "renovate@cianfhoghlaim.ie",
        renovatePassword,
        false
      );
      results.push({
        step: "1. Create renovate-bot user",
        success: true,
        output: userResult,
      });
    } catch (e) {
      results.push({
        step: "1. Create renovate-bot user",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 2: Create access token for renovate-bot
    let tokenValue = "";
    try {
      const tokenResult = await forgejo.createAccessToken(
        "renovate-bot",
        "renovate-token",
        ["read:misc", "read:repository", "write:repository", "write:issue"]
      );
      // Parse token from JSON response
      const tokenJson = JSON.parse(tokenResult);
      tokenValue = tokenJson.sha1 || "";
      results.push({
        step: "2. Create access token",
        success: true,
        output: `Token created: ${tokenJson.name}`,
      });
    } catch (e) {
      results.push({
        step: "2. Create access token",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 3: Set RENOVATE_TOKEN secret in Forgejo Actions
    if (tokenValue) {
      try {
        const tokenSecret = dag.setSecret("renovate-token", tokenValue);
        const secretResult = await forgejo.setActionsSecret(
          "cliste",
          "bonneagar",
          "RENOVATE_TOKEN",
          tokenSecret
        );
        results.push({
          step: "3. Set RENOVATE_TOKEN secret",
          success: true,
          output: secretResult || "Secret set successfully",
        });
      } catch (e) {
        results.push({
          step: "3. Set RENOVATE_TOKEN secret",
          success: false,
          output: "",
          error: String(e),
        });
      }
    } else {
      results.push({
        step: "3. Set RENOVATE_TOKEN secret",
        success: false,
        output: "",
        error: "No token value available from step 2",
      });
    }

    // Step 4: Configure Komodo webhook
    try {
      const webhookResult = await forgejo.createWebhook(
        "cliste",
        "bonneagar",
        "https://komodo.cianfhoghlaim.ie/listener/github/procedure/auto-deploy-stacks/main",
        webhookSecret,
        ["push"],
        "main"
      );
      results.push({
        step: "4. Configure Komodo webhook",
        success: true,
        output: webhookResult,
      });
    } catch (e) {
      results.push({
        step: "4. Configure Komodo webhook",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 5: Create Git Provider in Komodo
    if (tokenValue) {
      try {
        const gitToken = dag.setSecret("forgejo-git-token", tokenValue);
        const providerResult = await komodo.createGitProvider(
          "git.cianfhoghlaim.ie",
          "cliste",
          gitToken
        );
        results.push({
          step: "5. Create Git Provider in Komodo",
          success: true,
          output: providerResult,
        });
      } catch (e) {
        results.push({
          step: "5. Create Git Provider in Komodo",
          success: false,
          output: "",
          error: String(e),
        });
      }
    } else {
      results.push({
        step: "5. Create Git Provider in Komodo",
        success: false,
        output: "",
        error: "No token value available from step 2",
      });
    }

    // Step 6: Deploy forgejo-runner stack via Komodo
    try {
      const deployResult = await komodo.deployStack("forgejo-runner");
      results.push({
        step: "6. Deploy forgejo-runner stack",
        success: true,
        output: deployResult,
      });
    } catch (e) {
      results.push({
        step: "6. Deploy forgejo-runner stack",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 7: Sync resources
    try {
      const syncResult = await komodo.runSync("storage-infrastructure");
      results.push({
        step: "7. Sync resources",
        success: true,
        output: syncResult,
      });
    } catch (e) {
      results.push({
        step: "7. Sync resources",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Format results
    return formatResults(results);
  }

  /**
   * Run only the Forgejo setup steps (steps 1-4)
   */
  @func()
  async setupForgejo(
    forgejoUrl: string,
    forgejoAdminToken: Secret,
    webhookSecret: Secret,
    renovatePassword: Secret
  ): Promise<string> {
    const forgejo = new Forgejo(forgejoUrl, forgejoAdminToken);
    const results: SetupResult[] = [];

    // Step 1: Create renovate-bot user
    try {
      const userResult = await forgejo.createUser(
        "renovate-bot",
        "renovate@cianfhoghlaim.ie",
        renovatePassword,
        false
      );
      results.push({
        step: "1. Create renovate-bot user",
        success: true,
        output: userResult,
      });
    } catch (e) {
      results.push({
        step: "1. Create renovate-bot user",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 2: Create access token
    let tokenValue = "";
    try {
      const tokenResult = await forgejo.createAccessToken(
        "renovate-bot",
        "renovate-token",
        ["read:misc", "read:repository", "write:repository", "write:issue"]
      );
      const tokenJson = JSON.parse(tokenResult);
      tokenValue = tokenJson.sha1 || "";
      results.push({
        step: "2. Create access token",
        success: true,
        output: `Token created: ${tokenJson.name}`,
      });
    } catch (e) {
      results.push({
        step: "2. Create access token",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 3: Set RENOVATE_TOKEN secret
    if (tokenValue) {
      try {
        const tokenSecret = dag.setSecret("renovate-token", tokenValue);
        const secretResult = await forgejo.setActionsSecret(
          "cliste",
          "bonneagar",
          "RENOVATE_TOKEN",
          tokenSecret
        );
        results.push({
          step: "3. Set RENOVATE_TOKEN secret",
          success: true,
          output: secretResult || "Secret set successfully",
        });
      } catch (e) {
        results.push({
          step: "3. Set RENOVATE_TOKEN secret",
          success: false,
          output: "",
          error: String(e),
        });
      }
    }

    // Step 4: Configure webhook
    try {
      const webhookResult = await forgejo.createWebhook(
        "cliste",
        "bonneagar",
        "https://komodo.cianfhoghlaim.ie/listener/github/procedure/auto-deploy-stacks/main",
        webhookSecret,
        ["push"],
        "main"
      );
      results.push({
        step: "4. Configure Komodo webhook",
        success: true,
        output: webhookResult,
      });
    } catch (e) {
      results.push({
        step: "4. Configure Komodo webhook",
        success: false,
        output: "",
        error: String(e),
      });
    }

    return formatResults(results);
  }

  /**
   * Run only the Komodo setup steps (steps 5-7)
   */
  @func()
  async setupKomodo(
    komodoUrl: string,
    komodoApiKey: Secret,
    komodoApiSecret: Secret,
    forgejoToken: Secret
  ): Promise<string> {
    const komodo = new Komodo(komodoUrl, komodoApiKey, komodoApiSecret);
    const results: SetupResult[] = [];

    // Step 5: Create Git Provider
    try {
      const providerResult = await komodo.createGitProvider(
        "git.cianfhoghlaim.ie",
        "cliste",
        forgejoToken
      );
      results.push({
        step: "5. Create Git Provider in Komodo",
        success: true,
        output: providerResult,
      });
    } catch (e) {
      results.push({
        step: "5. Create Git Provider in Komodo",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 6: Deploy forgejo-runner stack
    try {
      const deployResult = await komodo.deployStack("forgejo-runner");
      results.push({
        step: "6. Deploy forgejo-runner stack",
        success: true,
        output: deployResult,
      });
    } catch (e) {
      results.push({
        step: "6. Deploy forgejo-runner stack",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Step 7: Sync resources
    try {
      const syncResult = await komodo.runSync("storage-infrastructure");
      results.push({
        step: "7. Sync resources",
        success: true,
        output: syncResult,
      });
    } catch (e) {
      results.push({
        step: "7. Sync resources",
        success: false,
        output: "",
        error: String(e),
      });
    }

    return formatResults(results);
  }

  /**
   * Verify the GitOps pipeline is functioning
   */
  @func()
  async verify(
    forgejoUrl: string,
    forgejoAdminToken: Secret,
    komodoUrl: string,
    komodoApiKey: Secret,
    komodoApiSecret: Secret
  ): Promise<string> {
    const forgejo = new Forgejo(forgejoUrl, forgejoAdminToken);
    const komodo = new Komodo(komodoUrl, komodoApiKey, komodoApiSecret);
    const checks: SetupResult[] = [];

    // Check 1: Forgejo API health
    try {
      const forgejoHealth = await forgejo.health();
      checks.push({
        step: "Forgejo API",
        success: true,
        output: forgejoHealth,
      });
    } catch (e) {
      checks.push({
        step: "Forgejo API",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 2: Forgejo admin token valid
    try {
      const currentUser = await forgejo.getCurrentUser();
      checks.push({
        step: "Forgejo Admin Token",
        success: true,
        output: currentUser,
      });
    } catch (e) {
      checks.push({
        step: "Forgejo Admin Token",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 3: Komodo API health
    try {
      const komodoHealth = await komodo.health();
      checks.push({
        step: "Komodo API",
        success: true,
        output: komodoHealth,
      });
    } catch (e) {
      checks.push({
        step: "Komodo API",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 4: Komodo version
    try {
      const komodoVersion = await komodo.version();
      checks.push({
        step: "Komodo Version",
        success: true,
        output: komodoVersion,
      });
    } catch (e) {
      checks.push({
        step: "Komodo Version",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 5: List runners
    try {
      const runners = await forgejo.listRunners();
      const runnerJson = JSON.parse(runners);
      const onlineCount = runnerJson.filter(
        (r: { status?: string }) => r.status === "online"
      ).length;
      checks.push({
        step: "Forgejo Runners",
        success: onlineCount > 0,
        output: `${onlineCount} runner(s) online`,
      });
    } catch (e) {
      checks.push({
        step: "Forgejo Runners",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 6: List webhooks
    try {
      const webhooks = await forgejo.listWebhooks("cliste", "bonneagar");
      const webhookJson = JSON.parse(webhooks);
      checks.push({
        step: "Forgejo Webhooks",
        success: webhookJson.length > 0,
        output: `${webhookJson.length} webhook(s) configured`,
      });
    } catch (e) {
      checks.push({
        step: "Forgejo Webhooks",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 7: List Actions secrets
    try {
      const secrets = await forgejo.listActionsSecrets("cliste", "bonneagar");
      const secretsJson = JSON.parse(secrets);
      const hasRenovateToken = secretsJson.secrets?.some(
        (s: { name?: string }) => s.name === "RENOVATE_TOKEN"
      );
      checks.push({
        step: "Forgejo Actions Secrets",
        success: hasRenovateToken,
        output: hasRenovateToken
          ? "RENOVATE_TOKEN configured"
          : "RENOVATE_TOKEN missing",
      });
    } catch (e) {
      checks.push({
        step: "Forgejo Actions Secrets",
        success: false,
        output: "",
        error: String(e),
      });
    }

    // Check 8: Komodo stacks
    try {
      const stacks = await komodo.listStacks();
      checks.push({
        step: "Komodo Stacks",
        success: true,
        output: stacks,
      });
    } catch (e) {
      checks.push({
        step: "Komodo Stacks",
        success: false,
        output: "",
        error: String(e),
      });
    }

    return formatResults(checks);
  }

  /**
   * Register a Forgejo runner programmatically
   */
  @func()
  async registerRunner(
    forgejoUrl: string,
    forgejoAdminToken: Secret,
    runnerName: string = "forgejo-runner"
  ): Promise<string> {
    const forgejo = new Forgejo(forgejoUrl, forgejoAdminToken);

    // Get registration token
    const tokenStr = await forgejo.getRunnerRegistrationToken();
    const registrationToken = dag.setSecret("runner-token", tokenStr.trim());

    // Register runner
    const runner = await forgejo.registerRunner(
      runnerName,
      ["ubuntu-latest:docker://ghcr.io/catthehacker/ubuntu:runner-latest"],
      registrationToken
    );

    return `Runner ${runnerName} registration initiated`;
  }
}

/**
 * Format results array into readable output
 */
function formatResults(results: SetupResult[]): string {
  const lines: string[] = ["GitOps Setup Results", "=".repeat(50)];

  let successCount = 0;
  let failCount = 0;

  for (const result of results) {
    const status = result.success ? "✓" : "✗";
    lines.push(`${status} ${result.step}`);

    if (result.output) {
      lines.push(`  Output: ${result.output.substring(0, 100)}...`);
    }
    if (result.error) {
      lines.push(`  Error: ${result.error}`);
    }

    if (result.success) successCount++;
    else failCount++;
  }

  lines.push("=".repeat(50));
  lines.push(`Summary: ${successCount} passed, ${failCount} failed`);

  return lines.join("\n");
}
