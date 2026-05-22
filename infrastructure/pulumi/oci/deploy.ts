import { LocalWorkspace, LocalProgramArgs } from "@pulumi/pulumi/automation";
import { InfisicalClient } from "@infisical/sdk";
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
    // Infisical
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
    infisicalEnvironment: process.env.INFISICAL_ENVIRONMENT || "prod",
    // Cloudflare (can be loaded from Infisical)
    cloudflareZoneId: process.env.CLOUDFLARE_ZONE_ID || "",
    cloudflareApiToken: process.env.CLOUDFLARE_API_TOKEN || "",
    cloudflareDomain: process.env.CLOUDFLARE_DOMAIN || "cianfhoghlaim.ie",
    // Paths for automation
    komodoDir: path.join(__dirname, "..", "..", "komodo"),
    ansibleDir: path.join(__dirname, "..", "..", "ansible"),
};

// =============================================================================
// INFISICAL HELPERS
// =============================================================================

function getInfisicalSecret(): string {
    if (CONFIG.infisicalClientSecret) return CONFIG.infisicalClientSecret;

    const tokenPath = path.join(__dirname, "..", "..", "pangolin", "pangolin-core", "config", "secrets", "infisical_secret");
    if (fs.existsSync(tokenPath)) {
        return fs.readFileSync(tokenPath, "utf-8").trim();
    }
    throw new Error("INFISICAL_CLIENT_SECRET not set and secret file not found");
}

let _client: InfisicalClient | null = null;
function getInfisicalClient(): InfisicalClient {
    if (_client) return _client;
    const clientSecret = getInfisicalSecret();
    _client = new InfisicalClient({
        clientId: CONFIG.infisicalClientId,
        clientSecret,
    });
    return _client;
}

/**
 * Load Cloudflare credentials from Infisical
 */
async function loadCloudflareCredentials(): Promise<{ apiToken: string; zoneId: string } | null> {
    if (CONFIG.cloudflareApiToken && CONFIG.cloudflareZoneId) {
        // Already set via environment
        return { apiToken: CONFIG.cloudflareApiToken, zoneId: CONFIG.cloudflareZoneId };
    }

    try {
        const client = getInfisicalClient();
        const apiTokenSecret = await client.getSecret({ secretName: "CLOUDFLARE_API_TOKEN", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, path: "/" });
        const zoneIdSecret = await client.getSecret({ secretName: "CLOUDFLARE_ZONE_ID", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, path: "/" });

        const apiToken = apiTokenSecret.secretValue;
        const zoneId = zoneIdSecret.secretValue;

        if (apiToken && zoneId) {
            console.log(`Loaded Cloudflare credentials from Infisical (zone: ${zoneId})`);
            return { apiToken, zoneId };
        }
    } catch (err) {
        console.log("Cloudflare credentials not found in Infisical, DNS records will not be created");
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

    // Load Cloudflare credentials from Infisical (if available)
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

async function saveToInfisical(outputs: Record<string, { value: unknown }>) {
    try {
        const client = getInfisicalClient();

        const publicIp = outputs.publicIp?.value as string;
        const privateIp = outputs.privateIp?.value as string;
        const instanceOcid = outputs.instanceOcid?.value as string;
        const serverUser = "ubuntu";

        const secretsToSave = [
            { name: "SERVER_PUBLIC_IP", value: publicIp },
            { name: "SERVER_PRIVATE_IP", value: privateIp },
            { name: "SERVER_USER", value: serverUser },
            { name: "SERVER_INSTANCE_OCID", value: instanceOcid },
            { name: "SERVER_REGION", value: CONFIG.region },
            { name: "SERVER_HOSTNAME", value: "arm1.oci" }
        ];

        for (const secret of secretsToSave) {
            if (!secret.value) continue;
            try {
                await client.createSecret({
                    secretName: secret.name,
                    secretValue: secret.value,
                    projectId: CONFIG.infisicalProjectId,
                    environment: CONFIG.infisicalEnvironment,
                    path: "/"
                });
            } catch {
                await client.updateSecret({
                    secretName: secret.name,
                    secretValue: secret.value,
                    projectId: CONFIG.infisicalProjectId,
                    environment: CONFIG.infisicalEnvironment,
                    path: "/"
                });
            }
        }
        console.log("\nInfisical: Saved outputs successfully");
    } catch (err) {
        console.error("\nInfisical: Failed to save outputs:", err);
    }
}

// =============================================================================
// POST-DEPLOYMENT AUTOMATION
// =============================================================================

/**
 * Regenerate Ansible inventory from Infisical data using servers.ts
 */
async function regenerateInventory(): Promise<void> {
    console.log("\nRegenerating Ansible inventory from Infisical...");
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
 * Run Ansible playbook to deploy infrastructure (Infisical, Pangolin, Komodo)
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

    // Save outputs to Infisical
    await saveToInfisical(result.outputs);

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
    console.log(`  - Infisical: http://${publicIp}:8080`);
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
    console.log("\nInfisical (optional - saves outputs to Infisical):");
    console.log("  INFISICAL_CLIENT_ID - Infisical Client ID");
    console.log("  INFISICAL_CLIENT_SECRET - Infisical Client Secret");
    console.log("  INFISICAL_PROJECT_ID - Infisical Project ID");
    console.log("  INFISICAL_ENVIRONMENT - Environment (default: prod)");
    process.exit(1);
}

commands[command]()
    .then(() => process.exit(0))
    .catch((err) => {
        console.error("Error:", err);
        process.exit(1);
    });
