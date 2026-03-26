// =============================================================================
// RUN ANSIBLE PLAYBOOK ACTION
// =============================================================================
// Executes Ansible playbooks using the existing uirlisí/ansible infrastructure.
// The Ansible execution environment is deployed to arm1-oci at:
//   /etc/komodo/uirlisi/ansible/
//
// Usage:
//   km run action run-ansible-playbook --playbook=periphery.yml
//   km run action run-ansible-playbook --playbook=periphery.yml --limit=cax41-hetzner
//   km run action run-ansible-playbook --playbook=periphery.yml --dryRun=true
//
// Available playbooks:
//   - periphery.yml: Deploy Periphery + Locket to servers
//   - deploy-infrastructure.yml: Full infrastructure deployment
//   - site.yml: Site-wide deployment
// =============================================================================

const dryRun = ARGS.dryRun || false;
const playbook = ARGS.playbook || "periphery.yml";
const limit = ARGS.limit || "";
const tags = ARGS.tags || "";
const extraVars = ARGS.extraVars || "";
const verbose = ARGS.verbose || false;

// Ansible EE runs on arm1-oci
const ansibleServer = "arm1-oci";
const ansibleRoot = "/etc/komodo/uirlisi/ansible";

console.log("=".repeat(60));
console.log("RUN ANSIBLE PLAYBOOK");
console.log("=".repeat(60));
console.log(`Playbook: ${playbook}`);
console.log(`Server: ${ansibleServer}`);
console.log(`Limit: ${limit || "(all hosts)"}`);
console.log(`Tags: ${tags || "(none)"}`);
console.log(`Dry run: ${dryRun}`);
console.log(`Verbose: ${verbose}`);
console.log("=".repeat(60));

// Build ansible-playbook command
let cmd = `cd ${ansibleRoot} && docker compose exec -T ansible ansible-playbook`;
cmd += ` -i /ansible/inventory/komodo.yml`;
cmd += ` /ansible/playbooks/${playbook}`;

if (limit) cmd += ` --limit=${limit}`;
if (tags) cmd += ` --tags=${tags}`;
if (extraVars) cmd += ` -e '${extraVars}'`;
if (dryRun) cmd += ` --check --diff`;
if (verbose) cmd += ` -vv`;

console.log(`\nCommand: ${cmd}\n`);
console.log("-".repeat(60));

// Execute the playbook
const result = await komodo.execute("RunCommand", {
  server: ansibleServer,
  command: cmd,
});

// Output results
if (result.stdout) {
  console.log(result.stdout);
}
if (result.stderr) {
  console.error("\nSTDERR:");
  console.error(result.stderr);
}

console.log("-".repeat(60));
console.log(`\nResult: ${result.success ? "SUCCESS" : "FAILED"}`);

return {
  success: result.success,
  playbook,
  limit: limit || "all",
  dryRun,
  tags: tags || "none",
};
