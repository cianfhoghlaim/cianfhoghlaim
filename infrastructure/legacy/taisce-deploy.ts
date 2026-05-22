import { KomodoClient, Types } from "komodo_client";
import { OnePasswordConnect, OPConnect, FullItem } from "@infisical/connect";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import {
  TAISCE_STACKS,
  TaisceStackDefinition,
  TAISCE_BASE_DIR,
  getStacksByOrder,
  getStackByName,
  validateDependencies,
} from "./lib/taisce-stacks";

// =============================================================================
// CONFIGURATION
// =============================================================================

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  komodo: {
    url: process.env.KOMODO_HOST || "https://komodo.cianfhoghlaim.ie",
    vault: process.env.OP_VAULT || "dev-baile",
    credentialItem: "komodo",
  },
  opConnect: {
    host: process.env.INFISICAL_HOST || "http://132.145.27.89:8080",
    tokenFile: process.env.INFISICAL_TOKEN_FILE || path.join(__dirname, "croí/op/connect_token"),
  },
  taisce: {
    localDir: path.join(__dirname, "croí/taisce"),
    remoteDir: TAISCE_BASE_DIR,
  },
};

// =============================================================================
// INFISICAL CONNECT CLIENT
// =============================================================================

let opClient: OPConnect | null = null;

function getOPConnectToken(): string {
  if (process.env.INFISICAL_TOKEN) {
    return process.env.INFISICAL_TOKEN;
  }
  try {
    return fs.readFileSync(CONFIG.opConnect.tokenFile, "utf-8").trim();
  } catch (err) {
    throw new Error(
      `Could not read Infisical token. Set INFISICAL_TOKEN env var or ensure ${CONFIG.opConnect.tokenFile} exists.`
    );
  }
}

function getOPClient(): OPConnect {
  if (!opClient) {
    const token = getOPConnectToken();
    opClient = OnePasswordConnect({
      serverURL: CONFIG.opConnect.host,
      token,
    });
  }
  return opClient;
}

function getFieldValue(item: FullItem, fieldLabel: string): string | undefined {
  const field = item.fields?.find(
    (f) => f.label?.toLowerCase() === fieldLabel.toLowerCase()
  );
  return field?.value;
}

// =============================================================================
// KOMODO CLIENT INITIALIZATION
// =============================================================================

async function getKomodoClient(): Promise<ReturnType<typeof KomodoClient>> {
  const op = getOPClient();
  const vault = await op.getVaultByTitle(CONFIG.komodo.vault);
  const item = await op.getItemByTitle(vault.id!, CONFIG.komodo.credentialItem);

  const username = getFieldValue(item, "username") || getFieldValue(item, "init_username");
  const password = getFieldValue(item, "password") || getFieldValue(item, "init_password");

  if (!username || !password) {
    throw new Error("Could not retrieve Komodo credentials from Infisical");
  }

  const loginResponse = await fetch(`${CONFIG.komodo.url}/auth/LoginLocalUser`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!loginResponse.ok) {
    throw new Error(`Komodo login failed: ${await loginResponse.text()}`);
  }

  const { jwt } = (await loginResponse.json()) as Types.JwtResponse;
  return KomodoClient(CONFIG.komodo.url, { type: "jwt", params: { jwt } });
}

// =============================================================================
// SERVER HELPERS
// =============================================================================

async function getServerId(
  komodo: ReturnType<typeof KomodoClient>,
  serverName: string
): Promise<string> {
  const servers = await komodo.read("ListServers", {});
  const server = servers.find((s) => s.name === serverName);
  if (!server) {
    throw new Error(`Server '${serverName}' not found in Komodo`);
  }
  return server.id;
}

// =============================================================================
// STACK MANAGEMENT
// =============================================================================

async function createOrUpdateStack(
  komodo: ReturnType<typeof KomodoClient>,
  stackDef: TaisceStackDefinition
): Promise<Types.Stack> {
  const existingStacks = await komodo.read("ListStacks", {});
  const existing = existingStacks.find((s) => s.name === stackDef.name);

  const serverId = await getServerId(komodo, stackDef.server);

  const stackConfig: Types._PartialStackConfig = {
    server_id: serverId,
    run_directory: path.join(CONFIG.taisce.remoteDir, "compose"),
    file_paths: [stackDef.composeFile],
    environment: stackDef.envVars || {},
    extra_args: stackDef.profiles?.map((p) => `--profile ${p}`).join(" ") || "",
    send_alerts: true,
  };

  if (existing) {
    console.log(`  Updating stack '${stackDef.name}'...`);
    return await komodo.write("UpdateStack", {
      id: existing.id,
      config: stackConfig,
    });
  } else {
    console.log(`  Creating stack '${stackDef.name}'...`);
    return await komodo.write("CreateStack", {
      name: stackDef.name,
      config: stackConfig,
    });
  }
}

async function deployStack(
  komodo: ReturnType<typeof KomodoClient>,
  stackName: string,
  options: { waitForCompletion?: boolean } = {}
): Promise<Types.Update | void> {
  console.log(`  Deploying stack '${stackName}'...`);

  try {
    if (options.waitForCompletion) {
      const result = await komodo.execute("DeployStack", {
        stack: stackName,
        stop_time: 300, // 5 minute timeout
      });
      console.log(`    Deployed: ${stackName}`);
      return result;
    } else {
      return await komodo.execute("DeployStack", {
        stack: stackName,
      });
    }
  } catch (err) {
    console.error(`    Failed to deploy ${stackName}: ${(err as Error).message}`);
    throw err;
  }
}

async function deployStacksInOrder(
  komodo: ReturnType<typeof KomodoClient>,
  stacks: TaisceStackDefinition[]
): Promise<void> {
  const orderGroups = getStacksByOrder();
  const sortedOrders = Array.from(orderGroups.keys()).sort((a, b) => a - b);

  for (const order of sortedOrders) {
    const group = orderGroups.get(order)!;
    // Filter to only stacks we're deploying
    const toDeployInGroup = group.filter((s) => stacks.some((st) => st.name === s.name));

    if (toDeployInGroup.length === 0) continue;

    console.log(`\nDeploying order ${order}: ${toDeployInGroup.map((s) => s.name).join(", ")}`);

    // Deploy stacks in same order group sequentially for now
    // (parallel deployment can cause issues with shared resources)
    for (const stack of toDeployInGroup) {
      await deployStack(komodo, stack.name, { waitForCompletion: true });
    }

    console.log(`  Order ${order} complete.`);
  }
}

// =============================================================================
// TEMPLATE SYNC
// =============================================================================

async function syncTemplates(stackDef: TaisceStackDefinition): Promise<void> {
  if (stackDef.secretTemplates.length === 0) {
    return;
  }

  console.log(`  Syncing templates for '${stackDef.name}'...`);

  for (const templateFile of stackDef.secretTemplates) {
    const localPath = path.join(
      CONFIG.taisce.localDir,
      "templates",
      stackDef.templateDir,
      templateFile
    );

    if (!fs.existsSync(localPath)) {
      console.warn(`    Warning: Template file not found: ${localPath}`);
      continue;
    }

    console.log(`    Template: ${templateFile}`);
  }
}

async function syncAllTemplates(): Promise<void> {
  console.log("\nSyncing secret templates...");

  for (const stackDef of TAISCE_STACKS) {
    await syncTemplates(stackDef);
  }

  // Also sync common templates
  const commonDir = path.join(CONFIG.taisce.localDir, "templates", "common");
  if (fs.existsSync(commonDir)) {
    const commonFiles = fs.readdirSync(commonDir);
    console.log(`  Common templates: ${commonFiles.join(", ")}`);
  }
}

// =============================================================================
// CLI COMMANDS
// =============================================================================

const commands: Record<string, (arg?: string) => Promise<void>> = {
  /**
   * Full setup: create all stacks, sync templates, and deploy
   */
  async setup(): Promise<void> {
    console.log("╔════════════════════════════════════════════════════════════╗");
    console.log("║          TAISCE STACK DEPLOYMENT SETUP                     ║");
    console.log("╚════════════════════════════════════════════════════════════╝\n");

    // Validate dependencies
    const validation = validateDependencies();
    if (!validation.valid) {
      console.error("Dependency validation failed:");
      for (const error of validation.errors) {
        console.error(`  - ${error}`);
      }
      process.exit(1);
    }

    const komodo = await getKomodoClient();

    // Step 1: Create/update all stacks
    console.log("Step 1: Creating/updating stack definitions...");
    for (const stackDef of TAISCE_STACKS) {
      await createOrUpdateStack(komodo, stackDef);
    }

    // Step 2: Sync templates
    console.log("\nStep 2: Syncing secret templates...");
    await syncAllTemplates();

    // Step 3: Deploy in order
    console.log("\nStep 3: Deploying stacks...");
    await deployStacksInOrder(komodo, TAISCE_STACKS);

    console.log("\n✓ Taisce stack deployment complete!");
  },

  /**
   * Deploy a single stack by name
   */
  async deploy(stackName?: string): Promise<void> {
    if (!stackName) {
      console.error("Usage: bun run taisce-deploy.ts deploy <stack-name>");
      process.exit(1);
    }

    const stackDef = getStackByName(stackName);
    if (!stackDef) {
      console.error(`Unknown stack: ${stackName}`);
      console.error(`Available stacks: ${TAISCE_STACKS.map((s) => s.name).join(", ")}`);
      process.exit(1);
    }

    const komodo = await getKomodoClient();

    // Sync templates first
    await syncTemplates(stackDef);

    // Deploy
    await deployStack(komodo, stackName, { waitForCompletion: true });
    console.log(`\n✓ Stack '${stackName}' deployed.`);
  },

  /**
   * Show status of all stacks
   */
  async status(): Promise<void> {
    console.log("╔════════════════════════════════════════════════════════════╗");
    console.log("║          TAISCE STACK STATUS                               ║");
    console.log("╚════════════════════════════════════════════════════════════╝\n");

    const komodo = await getKomodoClient();
    const stacks = await komodo.read("ListStacks", {});

    const orderGroups = getStacksByOrder();
    const sortedOrders = Array.from(orderGroups.keys()).sort((a, b) => a - b);

    for (const order of sortedOrders) {
      const group = orderGroups.get(order)!;
      console.log(`\n[Order ${order}]`);

      for (const stackDef of group) {
        const stack = stacks.find((s) => s.name === stackDef.name);
        const status = stack ? (stack.info?.state || "Unknown") : "Not Created";
        const locket = stackDef.requiresLocket ? " [Locket]" : "";
        const statusIcon = status === "Running" ? "🟢" : status === "Not Created" ? "⚪" : "🔴";
        console.log(`  ${statusIcon} ${stackDef.name}${locket}: ${status}`);
        console.log(`     ${stackDef.description}`);
      }
    }
  },

  /**
   * Sync templates only (no deployment)
   */
  async "sync-templates"(): Promise<void> {
    await syncAllTemplates();
    console.log("\n✓ Templates synced.");
  },

  /**
   * List all stacks
   */
  async list(): Promise<void> {
    console.log("Taisce Stacks:\n");

    const orderGroups = getStacksByOrder();
    const sortedOrders = Array.from(orderGroups.keys()).sort((a, b) => a - b);

    for (const order of sortedOrders) {
      const group = orderGroups.get(order)!;
      console.log(`Order ${order}:`);

      for (const stackDef of group) {
        const locket = stackDef.requiresLocket ? " [Locket]" : "";
        const deps = stackDef.dependencies.length > 0 ? ` (depends: ${stackDef.dependencies.join(", ")})` : "";
        console.log(`  - ${stackDef.name}${locket}${deps}`);
        console.log(`    ${stackDef.description}`);
      }
      console.log();
    }
  },

  /**
   * Create stacks in Komodo without deploying
   */
  async create(): Promise<void> {
    console.log("Creating stack definitions in Komodo...\n");

    const komodo = await getKomodoClient();

    for (const stackDef of TAISCE_STACKS) {
      await createOrUpdateStack(komodo, stackDef);
    }

    console.log("\n✓ Stack definitions created.");
  },

  /**
   * Destroy all stacks (in reverse order)
   */
  async destroy(): Promise<void> {
    console.log("WARNING: This will destroy all taisce stacks.\n");

    const komodo = await getKomodoClient();

    // Destroy in reverse order
    const reversed = [...TAISCE_STACKS].sort((a, b) => b.order - a.order);

    for (const stackDef of reversed) {
      console.log(`Destroying ${stackDef.name}...`);
      try {
        await komodo.execute("DestroyStack", { stack: stackDef.name });
        console.log(`  Destroyed.`);
      } catch (err) {
        console.warn(`  Warning: ${(err as Error).message}`);
      }
    }

    console.log("\n✓ All stacks destroyed.");
  },

  /**
   * Validate stack definitions
   */
  async validate(): Promise<void> {
    console.log("Validating stack definitions...\n");

    const validation = validateDependencies();

    if (validation.valid) {
      console.log("✓ All stack dependencies are valid.");
    } else {
      console.error("Validation errors:");
      for (const error of validation.errors) {
        console.error(`  - ${error}`);
      }
      process.exit(1);
    }

    // Check template files exist
    let templateErrors = 0;
    for (const stackDef of TAISCE_STACKS) {
      for (const templateFile of stackDef.secretTemplates) {
        const localPath = path.join(
          CONFIG.taisce.localDir,
          "templates",
          stackDef.templateDir,
          templateFile
        );
        if (!fs.existsSync(localPath)) {
          console.error(`  Missing template: ${localPath}`);
          templateErrors++;
        }
      }
    }

    if (templateErrors > 0) {
      console.error(`\n${templateErrors} template file(s) missing.`);
      process.exit(1);
    }

    console.log("✓ All template files exist.");
  },

  /**
   * Show help
   */
  async help(): Promise<void> {
    console.log("Taisce Stack Deployment Tool\n");
    console.log("Usage: bun run taisce-deploy.ts <command> [args]\n");
    console.log("Commands:");
    console.log("  setup            Create all stacks, sync templates, and deploy");
    console.log("  deploy <name>    Deploy a single stack");
    console.log("  status           Show status of all stacks");
    console.log("  list             List all stack definitions");
    console.log("  create           Create stack definitions without deploying");
    console.log("  sync-templates   Sync secret templates only");
    console.log("  validate         Validate stack definitions and templates");
    console.log("  destroy          Destroy all stacks (reverse order)");
    console.log("  help             Show this help message");
    console.log("\nEnvironment variables:");
    console.log("  KOMODO_HOST            Komodo URL (default: https://komodo.cianfhoghlaim.ie)");
    console.log("  INFISICAL_HOST        Infisical URL (default: http://132.145.27.89:8080)");
    console.log("  INFISICAL_TOKEN       Infisical token");
    console.log("  INFISICAL_TOKEN_FILE  Path to token file (default: croí/op/connect_token)");
  },
};

// =============================================================================
// CLI ENTRY POINT
// =============================================================================

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const command = process.argv[2] || "help";
  const arg = process.argv[3];

  const fn = commands[command];
  if (!fn) {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'bun run taisce-deploy.ts help' for available commands");
    process.exit(1);
  }

  fn(arg)
    .then(() => process.exit(0))
    .catch((err: Error) => {
      console.error("Error:", err.message);
      process.exit(1);
    });
}
