import { OnePasswordConnect, OPConnect, FullItem, Item } from "@1password/connect";
import { KomodoClient, Types } from "komodo_client";
import * as crypto from "crypto";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import { execSync, spawn } from "child_process";

// =============================================================================
// CONFIGURATION
// =============================================================================

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 1Password configuration
const OP_CONNECT_HOST = process.env.OP_CONNECT_HOST || "http://localhost:8080";
const OP_CONNECT_TOKEN_FILE = process.env.OP_CONNECT_TOKEN_FILE || "/etc/connect/token";
const OP_VAULT = process.env.OP_VAULT || "dev-baile";
const OP_ANSIBLE_ITEM = "ansible-automation"; // Item name for ansible secrets

// Komodo configuration
const KOMODO_URL = process.env.KOMODO_HOST || "https://komodo.local";
const KOMODO_VAULT_PASS_VAR = "VAULT_PASS"; // Komodo variable name for vault password

// Paths
const INVENTORY_PATH = path.join(__dirname, "ansible", "inventory", "komodo.yml");
const INVENTORY_TEMPLATE_PATH = path.join(__dirname, "ansible", "inventory", "komodo.yml.template");

// =============================================================================
// TYPES
// =============================================================================

interface AnsibleSecrets {
  vaultPassword: string;
  becomePass?: string;
  opConnectToken?: string;
}

interface BootstrapOptions {
  becomePass?: string;  // Optional - only needed if sudo requires password
  opConnectToken: string;
  peripheryCoreAddress?: string;
  opConnectHost?: string;
  force?: boolean;
}

// =============================================================================
// 1PASSWORD CONNECT CLIENT
// =============================================================================

let opClient: OPConnect | null = null;

/**
 * Read 1Password Connect token from file or environment
 */
function getOPConnectToken(): string {
  if (process.env.OP_CONNECT_TOKEN) {
    return process.env.OP_CONNECT_TOKEN;
  }
  try {
    return fs.readFileSync(OP_CONNECT_TOKEN_FILE, "utf-8").trim();
  } catch (err) {
    throw new Error(
      `Could not read 1Password Connect token. Set OP_CONNECT_TOKEN env var or ensure ${OP_CONNECT_TOKEN_FILE} exists.`
    );
  }
}

/**
 * Initialize the 1Password Connect client
 */
function getOPClient(): OPConnect {
  if (!opClient) {
    const token = getOPConnectToken();
    opClient = OnePasswordConnect({
      serverURL: OP_CONNECT_HOST,
      token,
    });
  }
  return opClient;
}

/**
 * Get a field value from a 1Password item
 */
function getFieldValue(item: FullItem, fieldLabel: string): string | undefined {
  const field = item.fields?.find(
    (f) => f.label?.toLowerCase() === fieldLabel.toLowerCase()
  );
  return field?.value;
}

/**
 * Get vault ID by name
 */
async function getVaultId(): Promise<string> {
  const op = getOPClient();
  const vault = await op.getVaultByTitle(OP_VAULT);
  if (!vault.id) {
    throw new Error(`Vault '${OP_VAULT}' not found or has no ID`);
  }
  return vault.id;
}

/**
 * Check if ansible-automation item exists in 1Password
 */
async function getAnsibleItem(): Promise<FullItem | null> {
  const op = getOPClient();
  const vaultId = await getVaultId();

  try {
    return await op.getItemByTitle(vaultId, OP_ANSIBLE_ITEM);
  } catch {
    return null;
  }
}

/**
 * Create or update the ansible-automation item in 1Password
 */
async function storeSecretsIn1Password(secrets: AnsibleSecrets): Promise<void> {
  const op = getOPClient();
  const vaultId = await getVaultId();

  const fields: Item["fields"] = [
    {
      id: "vault_password",
      label: "vault_password",
      value: secrets.vaultPassword,
      type: "CONCEALED",
    },
  ];

  if (secrets.becomePass) {
    fields.push({
      id: "become_pass",
      label: "become_pass",
      value: secrets.becomePass,
      type: "CONCEALED",
    });
  }

  if (secrets.opConnectToken) {
    fields.push({
      id: "op_connect_token",
      label: "op_connect_token",
      value: secrets.opConnectToken,
      type: "CONCEALED",
    });
  }

  const existingItem = await getAnsibleItem();

  if (existingItem && existingItem.id) {
    console.log(`  Updating existing '${OP_ANSIBLE_ITEM}' item in 1Password...`);
    await op.updateItem(vaultId, existingItem.id, {
      ...existingItem,
      fields,
    });
  } else {
    console.log(`  Creating '${OP_ANSIBLE_ITEM}' item in 1Password...`);
    await op.createItem(vaultId, {
      title: OP_ANSIBLE_ITEM,
      category: "API_CREDENTIAL",
      vault: { id: vaultId },
      tags: ["ansible", "automation", "infrastructure"],
      fields,
    });
  }
}

/**
 * Retrieve ansible secrets from 1Password
 */
async function getSecretsFrom1Password(): Promise<AnsibleSecrets | null> {
  const item = await getAnsibleItem();
  if (!item) {
    return null;
  }

  const vaultPassword = getFieldValue(item, "vault_password");
  if (!vaultPassword) {
    throw new Error("ansible-automation item exists but has no vault_password field");
  }

  return {
    vaultPassword,
    becomePass: getFieldValue(item, "become_pass"),
    opConnectToken: getFieldValue(item, "op_connect_token"),
  };
}

// =============================================================================
// PASSWORD GENERATION
// =============================================================================

/**
 * Generate a cryptographically secure random password
 */
function generatePassword(length: number = 64): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-";
  const randomBytes = crypto.randomBytes(length);
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars[randomBytes[i] % chars.length];
  }
  return result;
}

// =============================================================================
// KOMODO CLIENT
// =============================================================================

/**
 * Get Komodo credentials from 1Password
 */
async function getKomodoCredentials(): Promise<{ username: string; password: string }> {
  const op = getOPClient();
  const vaultId = await getVaultId();
  const item = await op.getItemByTitle(vaultId, "komodo");

  const username = getFieldValue(item, "username") || getFieldValue(item, "init_username");
  const password = getFieldValue(item, "password") || getFieldValue(item, "init_password");

  if (!username || !password) {
    throw new Error("Missing Komodo credentials in 1Password");
  }

  return { username, password };
}

/**
 * Login to Komodo and return a client
 */
async function loginToKomodo(): Promise<ReturnType<typeof KomodoClient>> {
  const { username, password } = await getKomodoCredentials();

  console.log(`  Logging in to Komodo at ${KOMODO_URL}...`);

  const loginResponse = await fetch(`${KOMODO_URL}/auth/LoginLocalUser`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!loginResponse.ok) {
    const error = await loginResponse.text();
    throw new Error(`Komodo login failed: ${loginResponse.status} - ${error}`);
  }

  const { jwt } = (await loginResponse.json()) as Types.JwtResponse;
  return KomodoClient(KOMODO_URL, { type: "jwt", params: { jwt } });
}

/**
 * Set or update a Komodo variable
 */
async function setKomodoVariable(
  komodo: ReturnType<typeof KomodoClient>,
  name: string,
  value: string,
  isSecret: boolean = true
): Promise<void> {
  console.log(`  Setting Komodo variable '${name}' (secret: ${isSecret})...`);

  // First, try to get existing variables to check if it exists
  const variables = await komodo.read("ListVariables", {});
  const existing = variables.find((v) => v.name === name);

  if (existing) {
    await komodo.write("UpdateVariableValue", {
      name,
      value,
    });
  } else {
    await komodo.write("CreateVariable", {
      name,
      value,
      description: `Ansible vault password for automation. Auto-generated by ansible.ts bootstrap.`,
      is_secret: isSecret,
    });
  }
}

// =============================================================================
// ANSIBLE VAULT ENCRYPTION
// =============================================================================

/**
 * Encrypt a string using ansible-vault via docker
 */
function encryptWithVault(value: string, vaultPassword: string, varName: string): string {
  // Write vault password to temp file
  const vaultPassFile = "/tmp/.ansible-vault-pass-temp";
  fs.writeFileSync(vaultPassFile, vaultPassword, { mode: 0o600 });

  try {
    // Use docker to run ansible-vault encrypt_string
    const result = execSync(
      `docker compose exec -T -e ANSIBLE_VAULT_PASSWORD_FILE=${vaultPassFile} ansible ` +
      `ansible-vault encrypt_string '${value.replace(/'/g, "'\\''")}' --name '${varName}'`,
      {
        cwd: __dirname,
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      }
    );

    return result.trim();
  } catch (err) {
    // If docker isn't available, use Python directly
    console.log("  Docker not available, trying local ansible-vault...");

    const result = execSync(
      `ansible-vault encrypt_string '${value.replace(/'/g, "'\\''")}' --name '${varName}' --vault-password-file ${vaultPassFile}`,
      {
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      }
    );

    return result.trim();
  } finally {
    // Clean up temp file
    try {
      fs.unlinkSync(vaultPassFile);
    } catch {}
  }
}

/**
 * Encrypt a string using ansible-vault (pure Node.js implementation for simple cases)
 * This creates a vault-encrypted string compatible with ansible-vault 1.1
 */
function encryptWithVaultPure(value: string, vaultPassword: string): string {
  // Generate random salt and IV
  const salt = crypto.randomBytes(32);
  const iv = crypto.randomBytes(16);

  // Derive key using PBKDF2
  const key = crypto.pbkdf2Sync(vaultPassword, salt, 10000, 32, "sha256");
  const hmacKey = crypto.pbkdf2Sync(vaultPassword, salt, 10000, 32, "sha256");

  // Pad the plaintext to AES block size
  const blockSize = 16;
  const padding = blockSize - (value.length % blockSize);
  const paddedValue = value + String.fromCharCode(padding).repeat(padding);

  // Encrypt with AES-256-CTR
  const cipher = crypto.createCipheriv("aes-256-ctr", key, iv);
  const encrypted = Buffer.concat([cipher.update(paddedValue, "utf-8"), cipher.final()]);

  // Create HMAC
  const hmac = crypto.createHmac("sha256", hmacKey);
  hmac.update(encrypted);
  const hmacDigest = hmac.digest();

  // Combine: salt + hmac + iv + ciphertext
  const combined = Buffer.concat([salt, hmacDigest, iv, encrypted]);

  // Format as hex lines (80 chars per line)
  const hexData = combined.toString("hex");
  const lines: string[] = [];
  for (let i = 0; i < hexData.length; i += 80) {
    lines.push(hexData.slice(i, i + 80));
  }

  return `$ANSIBLE_VAULT;1.1;AES256\n${lines.join("\n")}`;
}

// =============================================================================
// INVENTORY GENERATION
// =============================================================================

/**
 * Generate the inventory file with encrypted secrets
 */
function generateInventory(
  encryptedOpToken: string,
  options: {
    encryptedBecomePass?: string;  // Optional - only if sudo requires password
    peripheryCoreAddress?: string;
    opConnectHost?: string;
  } = {}
): string {
  const peripheryCoreAddress = options.peripheryCoreAddress || "wss://komodo.local";
  const opConnectHost = options.opConnectHost || "http://host.docker.internal:8080";

  // Indent the encrypted values properly for YAML
  const indentVault = (encrypted: string, spaces: number = 6) => {
    const lines = encrypted.split("\n");
    const header = lines[0]; // $ANSIBLE_VAULT;1.1;AES256
    const data = lines.slice(1).map(line => " ".repeat(spaces) + line).join("\n");
    return `!vault |\n${" ".repeat(spaces)}${header}\n${data}`;
  };

  // Only include become_pass if provided (for hosts that need sudo password)
  const becomePassSection = options.encryptedBecomePass
    ? `\n    # Become password (sudo) - ENCRYPTED WITH VAULT\n    # Only needed if sudo requires a password\n    ansible_become_pass: ${indentVault(options.encryptedBecomePass, 6)}\n`
    : `\n    # No become password configured - using passwordless sudo\n`;

  return `---
# =============================================================================
# KOMODO INVENTORY
# =============================================================================
# Inventory file for Komodo Periphery and Locket deployment.
#
# GENERATED BY: bun run ansible.ts bootstrap
# DO NOT EDIT ENCRYPTED VALUES MANUALLY - re-run bootstrap to update
#
# IMPORTANT: For best automation with Komodo Actions, name your inventory
# hosts EXACTLY the same as they appear in the Komodo UI.
# =============================================================================

all:
  # ---------------------------------------------------------------------------
  # HOSTS
  # ---------------------------------------------------------------------------
  hosts:
    # Names should match exactly what's shown in Komodo UI
    security.hetzner:
      ansible_host: 78.47.231.137
      ansible_user: root
    arm1.oci:
      ansible_host: 130.162.172.50
      ansible_user: ubuntu
    bunchloch:
      ansible_host: host.docker.internal
      ansible_user: cliste
      ansible_connection: ssh

  # ---------------------------------------------------------------------------
  # GLOBAL VARIABLES
  # ---------------------------------------------------------------------------
  vars:${becomePassSection}
    # SSH key (path inside the ansible container)
    ansible_ssh_private_key_file: /root/.ssh/id_ed25519

    # -------------------------------------------------------------------------
    # PERIPHERY CONFIGURATION (Global)
    # -------------------------------------------------------------------------
    # Connection to Komodo Core (outbound mode - periphery connects to core)
    periphery_core_address: "${peripheryCoreAddress}"
    periphery_mode: outbound
    periphery_server_enabled: false

    # -------------------------------------------------------------------------
    # LOCKET CONFIGURATION (Global)
    # -------------------------------------------------------------------------
    # Enable locket on all servers
    locket_enabled: true
    locket_provider: op-connect

    # 1Password Connect settings
    locket_op_connect_host: "${opConnectHost}"

    # 1Password Connect token - ENCRYPTED WITH VAULT
    locket_op_connect_token: ${indentVault(encryptedOpToken, 6)}

  # ---------------------------------------------------------------------------
  # HOST GROUPS
  # ---------------------------------------------------------------------------
  children:
    # All Komodo-managed hosts
    komodo:
      vars:
        # Environment variables for periphery systemd service
        periphery_agent_secrets:
          - name: "KOMODO_UID"
            value: "{{ ansible_facts.getent_passwd[periphery_user | default('root')].1 | default('0') }}"
          - name: "KOMODO_GID"
            value: "{{ ansible_facts.getent_passwd[periphery_user | default('root')].2 | default('0') }}"
          # Locket environment (for services that need it)
          - name: "OP_CONNECT_HOST"
            value: "{{ locket_op_connect_host }}"
          - name: "OP_CONNECT_TOKEN_FILE"
            value: "{{ locket_op_token_file | default('/etc/locket/op_token') }}"

      children:
        # ---------------------------------------------------------------------
        # CORE SERVERS
        # ---------------------------------------------------------------------
        # Servers running Komodo Core (also runs periphery + locket)
        core:
          hosts:
            bunchloch:

        # ---------------------------------------------------------------------
        # PERIPHERY SERVERS
        # ---------------------------------------------------------------------
        # Servers running Periphery + Locket (no core)
        periphery:
          hosts:
            security.hetzner:
            arm1.oci:
            bunchloch:

    # -------------------------------------------------------------------------
    # ENVIRONMENT GROUPS (Optional)
    # -------------------------------------------------------------------------
    production:

    staging:
      hosts:
        security.hetzner:
        arm1.oci:
        bunchloch:
      vars:
        periphery_log_level: debug
`;
}

// =============================================================================
// BOOTSTRAP WORKFLOW
// =============================================================================

/**
 * Full bootstrap workflow:
 * 1. Generate vault password
 * 2. Store secrets in 1Password
 * 3. Set Komodo VAULT_PASS variable
 * 4. Generate encrypted inventory
 */
async function bootstrap(options: BootstrapOptions): Promise<void> {
  console.log("╔════════════════════════════════════════════════════════════╗");
  console.log("║           ANSIBLE AUTOMATION BOOTSTRAP                     ║");
  console.log("╚════════════════════════════════════════════════════════════╝\n");

  // Check if already bootstrapped
  const existingSecrets = await getSecretsFrom1Password();
  if (existingSecrets && !options.force) {
    console.log("⚠️  Ansible automation is already bootstrapped!");
    console.log("   Use --force to regenerate the vault password and re-encrypt secrets.");
    console.log("\n   Existing vault password found in 1Password.");
    console.log("   To use it, run: bun run ansible.ts sync");
    return;
  }

  // Step 1: Generate vault password
  console.log("Step 1: Generating vault password...");
  const vaultPassword = generatePassword(64);
  console.log("  ✓ Generated 64-character vault password\n");

  // Step 2: Store in 1Password
  console.log("Step 2: Storing secrets in 1Password...");
  await storeSecretsIn1Password({
    vaultPassword,
    becomePass: options.becomePass,
    opConnectToken: options.opConnectToken,
  });
  console.log(`  ✓ Secrets stored in '${OP_VAULT}/${OP_ANSIBLE_ITEM}'\n`);

  // Step 3: Set Komodo variable
  console.log("Step 3: Setting Komodo VAULT_PASS variable...");
  try {
    const komodo = await loginToKomodo();
    await setKomodoVariable(komodo, KOMODO_VAULT_PASS_VAR, vaultPassword, true);
    console.log(`  ✓ Komodo variable '${KOMODO_VAULT_PASS_VAR}' set\n`);
  } catch (err) {
    console.log(`  ⚠️  Could not set Komodo variable: ${(err as Error).message}`);
    console.log("     You may need to set VAULT_PASS manually in Komodo UI.\n");
  }

  // Step 4: Encrypt secrets
  console.log("Step 4: Encrypting secrets with vault...");

  let encryptedBecomePass: string | undefined;
  if (options.becomePass) {
    encryptedBecomePass = encryptWithVaultPure(options.becomePass, vaultPassword);
    console.log("  ✓ Encrypted ansible_become_pass");
  } else {
    console.log("  ○ Skipping ansible_become_pass (passwordless sudo)");
  }

  const encryptedOpToken = encryptWithVaultPure(options.opConnectToken, vaultPassword);
  console.log("  ✓ Encrypted locket_op_connect_token\n");

  // Step 5: Generate inventory
  console.log("Step 5: Generating inventory file...");
  const inventory = generateInventory(encryptedOpToken, {
    encryptedBecomePass,
    peripheryCoreAddress: options.peripheryCoreAddress,
    opConnectHost: options.opConnectHost,
  });

  // Backup existing inventory
  if (fs.existsSync(INVENTORY_PATH)) {
    const backupPath = `${INVENTORY_PATH}.backup.${Date.now()}`;
    fs.copyFileSync(INVENTORY_PATH, backupPath);
    console.log(`  ✓ Backed up existing inventory to ${path.basename(backupPath)}`);
  }

  fs.writeFileSync(INVENTORY_PATH, inventory);
  console.log(`  ✓ Inventory written to ${INVENTORY_PATH}\n`);

  // Done!
  console.log("╔════════════════════════════════════════════════════════════╗");
  console.log("║                 BOOTSTRAP COMPLETE                         ║");
  console.log("╚════════════════════════════════════════════════════════════╝");
  console.log("\nSecrets stored in:");
  console.log(`  • 1Password: ${OP_VAULT}/${OP_ANSIBLE_ITEM}`);
  console.log(`  • Komodo:    Variable '${KOMODO_VAULT_PASS_VAR}'`);
  console.log(`  • Inventory: ${INVENTORY_PATH}`);
  console.log("\nNext steps:");
  console.log("  1. Review the generated inventory file");
  console.log("  2. Start the ansible container:");
  console.log("     docker compose up -d");
  console.log("  3. Test connectivity:");
  console.log("     docker compose exec ansible ansible all -i /ansible/inventory/komodo.yml -m ping");
  console.log("\nThe vault password will be automatically injected from:");
  console.log("  • Local: ANSIBLE_VAULT_PASSWORD env var or .env file");
  console.log("  • Komodo Actions: [[VAULT_PASS]] variable interpolation");
}

/**
 * Sync: Pull vault password from 1Password and update local .env
 */
async function sync(): Promise<void> {
  console.log("Syncing vault password from 1Password...\n");

  const secrets = await getSecretsFrom1Password();
  if (!secrets) {
    console.error("❌ No ansible-automation item found in 1Password.");
    console.error("   Run 'bun run ansible.ts bootstrap' first.");
    process.exit(1);
  }

  // Write to .env file
  const envPath = path.join(__dirname, ".env");
  let envContent = "";

  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, "utf-8");
    // Replace or add ANSIBLE_VAULT_PASSWORD
    if (envContent.includes("ANSIBLE_VAULT_PASSWORD=")) {
      envContent = envContent.replace(
        /ANSIBLE_VAULT_PASSWORD=.*/,
        `ANSIBLE_VAULT_PASSWORD=${secrets.vaultPassword}`
      );
    } else {
      envContent += `\nANSIBLE_VAULT_PASSWORD=${secrets.vaultPassword}\n`;
    }
  } else {
    envContent = `# Ansible Vault Password (synced from 1Password)\nANSIBLE_VAULT_PASSWORD=${secrets.vaultPassword}\n`;
  }

  fs.writeFileSync(envPath, envContent, { mode: 0o600 });
  console.log(`✓ Vault password written to ${envPath}`);
  console.log("\nYou can now run:");
  console.log("  docker compose up -d");
  console.log("  docker compose exec ansible ansible all -i /ansible/inventory/komodo.yml -m ping");
}

/**
 * Show current status
 */
async function status(): Promise<void> {
  console.log("Checking ansible automation status...\n");

  // Check 1Password
  console.log("1Password Connect:");
  try {
    const response = await fetch(`${OP_CONNECT_HOST}/heartbeat`);
    if (response.ok) {
      console.log(`  ✓ Connected to ${OP_CONNECT_HOST}`);
    } else {
      console.log(`  ✗ 1Password Connect returned ${response.status}`);
    }
  } catch (err) {
    console.log(`  ✗ Cannot reach ${OP_CONNECT_HOST}`);
  }

  // Check ansible-automation item
  console.log("\nAnsible Secrets (1Password):");
  try {
    const secrets = await getSecretsFrom1Password();
    if (secrets) {
      console.log(`  ✓ '${OP_ANSIBLE_ITEM}' item exists in '${OP_VAULT}' vault`);
      console.log(`    • vault_password: ${secrets.vaultPassword ? "✓ set" : "✗ missing"}`);
      console.log(`    • become_pass: ${secrets.becomePass ? "✓ set" : "✗ missing"}`);
      console.log(`    • op_connect_token: ${secrets.opConnectToken ? "✓ set" : "✗ missing"}`);
    } else {
      console.log(`  ✗ '${OP_ANSIBLE_ITEM}' item not found`);
      console.log("    Run 'bun run ansible.ts bootstrap' to create it");
    }
  } catch (err) {
    console.log(`  ✗ Error: ${(err as Error).message}`);
  }

  // Check Komodo
  console.log("\nKomodo:");
  try {
    const komodo = await loginToKomodo();
    console.log(`  ✓ Connected to ${KOMODO_URL}`);

    const variables = await komodo.read("ListVariables", {});
    const vaultPassVar = variables.find((v) => v.name === KOMODO_VAULT_PASS_VAR);
    if (vaultPassVar) {
      console.log(`  ✓ '${KOMODO_VAULT_PASS_VAR}' variable exists (secret: ${vaultPassVar.is_secret})`);
    } else {
      console.log(`  ✗ '${KOMODO_VAULT_PASS_VAR}' variable not found`);
    }
  } catch (err) {
    console.log(`  ✗ Error: ${(err as Error).message}`);
  }

  // Check local files
  console.log("\nLocal Files:");
  console.log(`  Inventory: ${fs.existsSync(INVENTORY_PATH) ? "✓ exists" : "✗ missing"}`);

  const envPath = path.join(__dirname, ".env");
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, "utf-8");
    const hasVaultPass = envContent.includes("ANSIBLE_VAULT_PASSWORD=");
    console.log(`  .env file: ✓ exists ${hasVaultPass ? "(has ANSIBLE_VAULT_PASSWORD)" : "(no ANSIBLE_VAULT_PASSWORD)"}`);
  } else {
    console.log("  .env file: ✗ missing");
  }
}

/**
 * Test ansible connectivity
 */
async function test(): Promise<void> {
  console.log("Testing ansible connectivity...\n");

  // Ensure vault password is available
  const secrets = await getSecretsFrom1Password();
  if (!secrets) {
    console.error("❌ No vault password found. Run 'bun run ansible.ts bootstrap' first.");
    process.exit(1);
  }

  // Run ansible ping
  try {
    execSync(
      `docker compose exec -e ANSIBLE_VAULT_PASSWORD='${secrets.vaultPassword}' ansible ` +
      `ansible all -i /ansible/inventory/komodo.yml -m ping`,
      {
        cwd: __dirname,
        stdio: "inherit",
      }
    );
  } catch (err) {
    console.error("\n❌ Ansible ping failed");
    process.exit(1);
  }
}

/**
 * Re-encrypt inventory with current vault password
 */
async function reencrypt(options: { becomePass?: string; opConnectToken?: string }): Promise<void> {
  console.log("Re-encrypting inventory secrets...\n");

  const secrets = await getSecretsFrom1Password();
  if (!secrets) {
    console.error("❌ No vault password found. Run 'bun run ansible.ts bootstrap' first.");
    process.exit(1);
  }

  const becomePass = options.becomePass || secrets.becomePass;
  const opConnectToken = options.opConnectToken || secrets.opConnectToken;

  if (!opConnectToken) {
    console.error("❌ Missing op_connect_token. Provide --op-token or ensure it's in 1Password.");
    process.exit(1);
  }

  // Update 1Password with new values if provided
  if (options.becomePass || options.opConnectToken) {
    await storeSecretsIn1Password({
      vaultPassword: secrets.vaultPassword,
      becomePass,
      opConnectToken,
    });
    console.log("✓ Updated secrets in 1Password\n");
  }

  // Re-encrypt
  let encryptedBecomePass: string | undefined;
  if (becomePass) {
    encryptedBecomePass = encryptWithVaultPure(becomePass, secrets.vaultPassword);
  }
  const encryptedOpToken = encryptWithVaultPure(opConnectToken, secrets.vaultPassword);

  // Generate new inventory
  const inventory = generateInventory(encryptedOpToken, { encryptedBecomePass });

  // Backup and write
  if (fs.existsSync(INVENTORY_PATH)) {
    const backupPath = `${INVENTORY_PATH}.backup.${Date.now()}`;
    fs.copyFileSync(INVENTORY_PATH, backupPath);
    console.log(`✓ Backed up existing inventory to ${path.basename(backupPath)}`);
  }

  fs.writeFileSync(INVENTORY_PATH, inventory);
  console.log(`✓ Inventory written to ${INVENTORY_PATH}`);
}

// =============================================================================
// CLI
// =============================================================================

function printHelp(): void {
  console.log(`
Ansible Automation Bootstrap Script

Usage: bun run ansible.ts <command> [options]

Commands:
  bootstrap    Generate vault password, store in 1Password/Komodo, create inventory
  sync         Pull vault password from 1Password and update local .env
  status       Show current configuration status
  test         Test ansible connectivity to all hosts
  reencrypt    Re-encrypt inventory with updated secrets
  help         Show this help message

Bootstrap Options:
  --op-token <token>            1Password Connect token (required)
  --become-pass <password>      Sudo password (optional - only if sudo requires password)
  --periphery-url <url>         Komodo Core WebSocket URL (default: wss://komodo.local)
  --op-connect-host <url>       1Password Connect host (default: http://host.docker.internal:8080)
  --force                       Force regeneration even if already bootstrapped

Re-encrypt Options:
  --op-token <token>            New 1Password Connect token (optional, uses stored value)
  --become-pass <password>      New sudo password (optional, uses stored value)

Environment Variables:
  OP_CONNECT_HOST               1Password Connect server URL
  OP_CONNECT_TOKEN              1Password Connect access token
  OP_CONNECT_TOKEN_FILE         Path to file containing 1Password Connect token
  OP_VAULT                      1Password vault name (default: dev-baile)
  KOMODO_HOST                   Komodo server URL

Examples:
  # Initial bootstrap (passwordless sudo)
  bun run ansible.ts bootstrap --op-token "your-op-connect-token"

  # Initial bootstrap (with sudo password)
  bun run ansible.ts bootstrap \\
    --op-token "your-op-connect-token" \\
    --become-pass "your-sudo-password"

  # Sync vault password to local .env
  bun run ansible.ts sync

  # Check status
  bun run ansible.ts status

  # Test connectivity
  bun run ansible.ts test

  # Update 1Password Connect token
  bun run ansible.ts reencrypt --op-token "new-op-token"
`);
}

function parseArgs(args: string[]): Record<string, string | boolean> {
  const result: Record<string, string | boolean> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith("--")) {
      const key = arg.slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith("--")) {
        result[key] = next;
        i++;
      } else {
        result[key] = true;
      }
    }
  }

  return result;
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const command = args[0] || "help";
  const options = parseArgs(args.slice(1));

  try {
    switch (command) {
      case "bootstrap": {
        const becomePass = options["become-pass"] as string | undefined;
        const opToken = options["op-token"] as string;

        if (!opToken) {
          console.error("❌ Missing required option: --op-token <token>");
          console.error("\nRun 'bun run ansible.ts help' for usage.");
          process.exit(1);
        }

        await bootstrap({
          becomePass,
          opConnectToken: opToken,
          peripheryCoreAddress: options["periphery-url"] as string,
          opConnectHost: options["op-connect-host"] as string,
          force: options["force"] === true,
        });
        break;
      }

      case "sync":
        await sync();
        break;

      case "status":
        await status();
        break;

      case "test":
        await test();
        break;

      case "reencrypt":
        await reencrypt({
          becomePass: options["become-pass"] as string,
          opConnectToken: options["op-token"] as string,
        });
        break;

      case "help":
      case "--help":
      case "-h":
        printHelp();
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.error("Run 'bun run ansible.ts help' for usage.");
        process.exit(1);
    }
  } catch (err) {
    console.error(`\n❌ Error: ${(err as Error).message}`);
    if (process.env.DEBUG) {
      console.error((err as Error).stack);
    }
    process.exit(1);
  }
}

// Run if executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}

// Export for use as module
export {
  bootstrap,
  sync,
  status,
  test,
  reencrypt,
  generatePassword,
  getSecretsFrom1Password,
  storeSecretsIn1Password,
};
