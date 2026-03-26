import { LocalWorkspace, LocalProgramArgs } from "@pulumi/pulumi/automation";
import { OnePasswordConnect, ItemBuilder, OPConnect } from "@1password/connect";
import { execSync, exec } from "child_process";
import * as path from "path";
import * as fs from "fs";

// Configuration - can be overridden via environment variables
const CONFIG = {
    stackName: process.env.PULUMI_STACK || "prod",
    // Use tenancy as compartment (no sub-compartments exist)
    compartmentOcid: process.env.OCI_COMPARTMENT_OCID || "ocid1.tenancy.oc1..aaaaaaaazjzelgz2fwfqfjzjxwckslmhtq6yimvcz3oyzhonp2lisa2yfekq",
    region: process.env.OCI_REGION || "uk-london-1",
    sshPublicKeyPath: process.env.SSH_PUBLIC_KEY_PATH || path.join(process.env.HOME!, ".ssh", "ansible.pub"),
    // OCI authentication
    ociProfile: process.env.OCI_CLI_PROFILE || "bunchloch",
    ociConfigFile: process.env.OCI_CLI_CONFIG_FILE || path.join(process.env.HOME!, ".oci", "config"),
    // 1Password Connect
    opConnectHost: process.env.OP_CONNECT_HOST || "http://localhost:8080",
    opConnectToken: process.env.OP_CONNECT_TOKEN || "",
    opVault: process.env.OP_VAULT || "dev-baile",
    // 1Password items
    opServerItem: process.env.OP_SERVER_ITEM || "server-oci",
    opCloudflareItem: process.env.OP_CLOUDFLARE_ITEM || "cloudflare",
    // Cloudflare (can be loaded from 1Password)
    cloudflareZoneId: process.env.CLOUDFLARE_ZONE_ID || "",
    cloudflareApiToken: process.env.CLOUDFLARE_API_TOKEN || "",
    cloudflareDomain: process.env.CLOUDFLARE_DOMAIN || "cianfhoghlaim.ie",
    // Paths for automation
    komodoDir: path.join(__dirname, "..", "..", "komodo"),
    ansibleDir: path.join(__dirname, "..", "..", "ansible"),
};

// =============================================================================
// 1PASSWORD CONNECT HELPERS
// =============================================================================

function getOpToken(): string {
    if (CONFIG.opConnectToken) return CONFIG.opConnectToken;

    const tokenPath = path.join(__dirname, "..", "..", "pangolin", "pangolin-core", "config", "secrets", "op_token");
    if (fs.existsSync(tokenPath)) {
        return fs.readFileSync(tokenPath, "utf-8").trim();
    }
    throw new Error("OP_CONNECT_TOKEN not set and token file not found");
}

function getOpClient(): OPConnect {
    return OnePasswordConnect({
        serverURL: CONFIG.opConnectHost,
        token: getOpToken(),
        keepAlive: false,
    });
}

async function getVaultId(op: OPConnect, vaultName: string): Promise<string> {
    const vaults = await op.listVaults();
    const vault = vaults.find(v => v.name === vaultName);
    if (!vault || !vault.id) {
        throw new Error(`Vault "${vaultName}" not found`);
    }
    return vault.id;
}

/**
 * Load Cloudflare credentials from 1Password
 */
async function loadCloudflareCredentials(): Promise<{ apiToken: string; zoneId: string } | null> {
    if (CONFIG.cloudflareApiToken && CONFIG.cloudflareZoneId) {
        // Already set via environment
        return { apiToken: CONFIG.cloudflareApiToken, zoneId: CONFIG.cloudflareZoneId };
    }

    try {
        const op = getOpClient();
        const vaultId = await getVaultId(op, CONFIG.opVault);
        const item = await op.getItemByTitle(vaultId, CONFIG.opCloudflareItem);

        const apiToken = item.fields?.find(f => f.label === "api_token")?.value;
        const zoneId = item.fields?.find(f => f.label === "zone_id")?.value;

        if (apiToken && zoneId) {
            console.log(`Loaded Cloudflare credentials from 1Password (zone: ${zoneId})`);
            return { apiToken, zoneId };
        }
    } catch (err) {
        console.log("Cloudflare credentials not found in 1Password, DNS records will not be created");
    }

    return null;
}

async function getStack() {
    // Set passphrase for local secrets encryption (can be overridden via env var)
    if (!process.env.PULUMI_CONFIG_PASSPHRASE) {
        process.env.PULUMI_CONFIG_PASSPHRASE = "bunchloch-dev";
    }

    const args: LocalProgramArgs = {
        stackName: CONFIG.stackName,
        workDir: __dirname, // Points to this directory containing index.ts
    };

    const stack = await LocalWorkspace.createOrSelectStack(args);

    // Read SSH public key
    if (!fs.existsSync(CONFIG.sshPublicKeyPath)) {
        throw new Error(`SSH public key not found at: ${CONFIG.sshPublicKeyPath}`);
    }
    const sshPublicKey = fs.readFileSync(CONFIG.sshPublicKeyPath, "utf8").trim();

    // Configure OCI provider authentication
    await stack.setConfig("oci:configFileProfile", { value: CONFIG.ociProfile });
    await stack.setConfig("oci:auth", { value: "SecurityToken" });
    await stack.setConfig("oci:region", { value: CONFIG.region });

    // Configure stack variables (without oci: prefix - these are app config, not provider config)
    await stack.setConfig("compartmentOcid", { value: CONFIG.compartmentOcid });
    await stack.setConfig("sshPublicKey", { value: sshPublicKey });

    // Load Cloudflare credentials from 1Password (if available)
    const cfCreds = await loadCloudflareCredentials();
    if (cfCreds) {
        // Set Cloudflare provider API token
        process.env.CLOUDFLARE_API_TOKEN = cfCreds.apiToken;
        await stack.setConfig("cloudflareZoneId", { value: cfCreds.zoneId });
        await stack.setConfig("cloudflareDomain", { value: CONFIG.cloudflareDomain });
    }

    return stack;
}

async function preview() {
    const stack = await getStack();
    console.log("Previewing stack...");
    const result = await stack.preview({ onOutput: console.info });
    console.log(`Preview complete. Changes: ${JSON.stringify(result.changeSummary)}`);
}

async function saveToOnePassword(outputs: Record<string, { value: unknown }>) {
    try {
        const op = getOpClient();
        const vaultId = await getVaultId(op, CONFIG.opVault);

        const publicIp = outputs.publicIp?.value as string;
        const privateIp = outputs.privateIp?.value as string;
        const instanceOcid = outputs.instanceOcid?.value as string;

        // Field names match servers.ts expectations:
        // - ip: public IP address (servers.ts looks for "ip" or "address")
        // - user: SSH username (servers.ts looks for "user" or "username")
        // - hostname: optional hostname
        const serverUser = "ubuntu"; // OCI Ubuntu images use this user

        // Try to find existing item
        let existingItem;
        try {
            existingItem = await op.getItemByTitle(vaultId, CONFIG.opServerItem);
        } catch {
            // Item doesn't exist, will create new
        }

        if (existingItem) {
            // Update existing item fields
            existingItem.fields = existingItem.fields?.map(field => {
                if (field.label === "ip") return { ...field, value: publicIp };
                if (field.label === "private_ip") return { ...field, value: privateIp };
                if (field.label === "user") return { ...field, value: serverUser };
                if (field.label === "instance_ocid") return { ...field, value: instanceOcid };
                if (field.label === "region") return { ...field, value: CONFIG.region };
                if (field.label === "hostname") return { ...field, value: "arm1.oci" };
                return field;
            }) || [];

            await op.updateItem(vaultId, existingItem);
            console.log(`\n1Password: Updated item "${CONFIG.opServerItem}" in vault "${CONFIG.opVault}"`);
        } else {
            // Create new item with fields matching servers.ts expectations
            const newItem = new ItemBuilder()
                .setCategory("SERVER")
                .setTitle(CONFIG.opServerItem)
                .addField({ label: "ip", value: publicIp, sectionName: "Infrastructure" })
                .addField({ label: "private_ip", value: privateIp, sectionName: "Infrastructure" })
                .addField({ label: "user", value: serverUser, sectionName: "Infrastructure" })
                .addField({ label: "hostname", value: "arm1.oci", sectionName: "Infrastructure" })
                .addField({ label: "instance_ocid", value: instanceOcid, sectionName: "Infrastructure" })
                .addField({ label: "region", value: CONFIG.region, sectionName: "Infrastructure" })
                .build();

            await op.createItem(vaultId, newItem);
            console.log(`\n1Password: Created item "${CONFIG.opServerItem}" in vault "${CONFIG.opVault}"`);
        }
    } catch (err) {
        console.error("\n1Password: Failed to save outputs:", err);
    }
}

// =============================================================================
// POST-DEPLOYMENT AUTOMATION
// =============================================================================

/**
 * Regenerate Ansible inventory from 1Password data using servers.ts
 */
async function regenerateInventory(): Promise<void> {
    console.log("\nRegenerating Ansible inventory from 1Password...");
    try {
        execSync("bun run servers.ts generate-inventory", {
            cwd: CONFIG.komodoDir,
            stdio: "inherit",
        });
        console.log("Inventory regenerated successfully.");
    } catch (err) {
        console.error("Failed to regenerate inventory:", err);
        throw err;
    }
}

/**
 * Run Ansible playbook to deploy infrastructure (1Password Connect, Pangolin, Komodo)
 */
async function runAnsiblePlaybook(): Promise<void> {
    console.log("\nRunning Ansible playbook to deploy infrastructure...");
    try {
        // Start the ansible container and run the playbook
        const cmd = `docker compose run --rm ansible sh -c 'ansible-playbook -i /ansible/inventory/komodo.yml /ansible/playbooks/deploy-infrastructure.yml'`;
        execSync(cmd, {
            cwd: CONFIG.ansibleDir,
            stdio: "inherit",
            env: {
                ...process.env,
                SSH_KEY_PATH: CONFIG.sshPublicKeyPath.replace(".pub", ""),
            },
        });
        console.log("Ansible playbook completed successfully.");
    } catch (err) {
        console.error("Failed to run Ansible playbook:", err);
        throw err;
    }
}

/**
 * Wait for SSH to become available on the new instance
 */
async function waitForSsh(ip: string, timeout: number = 120000): Promise<void> {
    console.log(`\nWaiting for SSH on ${ip}...`);
    const start = Date.now();
    const sshKey = CONFIG.sshPublicKeyPath.replace(".pub", "");

    while (Date.now() - start < timeout) {
        try {
            execSync(
                `ssh -i ${sshKey} -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@${ip} 'echo SSH ready'`,
                { stdio: "pipe" }
            );
            console.log("SSH is available.");
            return;
        } catch {
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
    throw new Error(`SSH not available on ${ip} after ${timeout}ms`);
}

/**
 * Flush iptables on new instance (Oracle Cloud images have restrictive defaults)
 */
async function flushIptables(ip: string): Promise<void> {
    console.log(`\nFlushing iptables on ${ip}...`);
    const sshKey = CONFIG.sshPublicKeyPath.replace(".pub", "");
    const cmd = `ssh -i ${sshKey} -o StrictHostKeyChecking=no ubuntu@${ip} 'sudo iptables -F && sudo iptables -P INPUT ACCEPT && sudo iptables -P FORWARD ACCEPT && sudo iptables -P OUTPUT ACCEPT && sudo netfilter-persistent save'`;

    try {
        execSync(cmd, { stdio: "inherit" });
        console.log("iptables flushed successfully.");
    } catch (err) {
        console.error("Failed to flush iptables:", err);
    }
}

async function up() {
    const stack = await getStack();
    console.log("Deploying stack...");
    const result = await stack.up({ onOutput: console.info });
    console.log(`\nDeployment complete!`);
    console.log(`Outputs:`);
    for (const [key, value] of Object.entries(result.outputs)) {
        console.log(`  ${key}: ${value.value}`);
    }

    // Save outputs to 1Password
    await saveToOnePassword(result.outputs);

    return result.outputs;
}

/**
 * Full deployment with post-provisioning automation
 */
async function deploy() {
    // Step 1: Deploy infrastructure
    console.log("\n" + "=".repeat(60));
    console.log("STEP 1: Deploying OCI Infrastructure");
    console.log("=".repeat(60));
    const outputs = await up();

    const publicIp = outputs.publicIp?.value as string;
    if (!publicIp) {
        throw new Error("No public IP in outputs");
    }

    // Step 2: Wait for instance to be ready
    console.log("\n" + "=".repeat(60));
    console.log("STEP 2: Waiting for Instance");
    console.log("=".repeat(60));
    await waitForSsh(publicIp);

    // Step 3: Flush iptables
    console.log("\n" + "=".repeat(60));
    console.log("STEP 3: Flushing iptables");
    console.log("=".repeat(60));
    await flushIptables(publicIp);

    // Step 4: Regenerate inventory
    console.log("\n" + "=".repeat(60));
    console.log("STEP 4: Regenerating Ansible Inventory");
    console.log("=".repeat(60));
    await regenerateInventory();

    // Step 5: Run Ansible playbook
    console.log("\n" + "=".repeat(60));
    console.log("STEP 5: Running Ansible Playbook");
    console.log("=".repeat(60));
    await runAnsiblePlaybook();

    console.log("\n" + "=".repeat(60));
    console.log("DEPLOYMENT COMPLETE!");
    console.log("=".repeat(60));
    console.log(`\nInstance: ${publicIp}`);
    console.log(`SSH: ssh -i ~/.ssh/ansible ubuntu@${publicIp}`);
    console.log(`Domain: https://*.${CONFIG.cloudflareDomain}`);
    console.log(`\nServices deployed:`);
    console.log(`  - 1Password Connect: http://${publicIp}:8080`);
    console.log(`  - Pangolin: https://pangolin.${CONFIG.cloudflareDomain}`);
    console.log(`  - Komodo: https://komodo.${CONFIG.cloudflareDomain}`);
}

async function destroy() {
    const stack = await getStack();
    console.log("Destroying stack...");
    await stack.destroy({ onOutput: console.info });
    console.log("Destroy complete!");
}

async function refresh() {
    const stack = await getStack();
    console.log("Refreshing stack state...");
    await stack.refresh({ onOutput: console.info });
    console.log("Refresh complete!");
}

async function outputs() {
    const stack = await getStack();
    const outs = await stack.outputs();
    console.log("Stack outputs:");
    for (const [key, value] of Object.entries(outs)) {
        console.log(`  ${key}: ${value.value}`);
    }
    return outs;
}

// CLI handling
const command = process.argv[2];
const commands: Record<string, () => Promise<unknown>> = {
    preview,
    up,
    deploy, // Full automation: deploy + configure + ansible
    destroy,
    refresh,
    outputs,
};

if (!command || !commands[command]) {
    console.log("Usage: bun run deploy.ts <command>");
    console.log("\nCommands:");
    console.log("  preview  - Preview infrastructure changes");
    console.log("  up       - Deploy OCI infrastructure only");
    console.log("  deploy   - Full automation: deploy OCI + flush iptables + regenerate inventory + run Ansible");
    console.log("  destroy  - Destroy all infrastructure");
    console.log("  refresh  - Refresh Pulumi state");
    console.log("  outputs  - Show stack outputs");
    console.log("\nOCI Configuration:");
    console.log("  OCI_COMPARTMENT_OCID - OCI Compartment/Tenancy ID (default: configured tenancy)");
    console.log("  OCI_REGION - OCI Region (default: uk-london-1)");
    console.log("  OCI_CLI_PROFILE - OCI config profile (default: bunchloch)");
    console.log("  PULUMI_STACK - Stack name (default: prod)");
    console.log("  SSH_PUBLIC_KEY_PATH - Path to SSH public key (default: ~/.ssh/ansible.pub)");
    console.log("\nCloudflare Configuration (optional - creates DNS records):");
    console.log("  CLOUDFLARE_API_TOKEN - Cloudflare API token");
    console.log("  CLOUDFLARE_ZONE_ID - Cloudflare zone ID for your domain");
    console.log("  CLOUDFLARE_DOMAIN - Domain name (default: cianfhoghlaim.ie)");
    console.log("\n1Password Connect (optional - saves outputs to 1Password):");
    console.log("  OP_CONNECT_HOST - 1Password Connect server URL");
    console.log("  OP_CONNECT_TOKEN - 1Password Connect token");
    console.log("  OP_VAULT - Vault name (default: dev-baile)");
    console.log("  OP_SERVER_ITEM - Item name for server info (default: server-oci)");
    process.exit(1);
}

commands[command]()
    .then(() => process.exit(0))
    .catch((err) => {
        console.error("Error:", err);
        process.exit(1);
    });
