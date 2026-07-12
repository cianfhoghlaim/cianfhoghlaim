/**
 * Bonneagar Infrastructure Dagger Module
 *
 * Provides infrastructure automation functions for:
 * - 1Password secret retrieval
 * - Ansible playbook execution
 * - Docker Compose stack management
 * - Full deployment orchestration
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

@object()
export class Bonneagar {
  @field()
  ansibleDir: Directory;

  @field()
  secretsDir?: Directory;

  constructor(ansibleDir: Directory, secretsDir?: Directory) {
    this.ansibleDir = ansibleDir;
    this.secretsDir = secretsDir;
  }

  /**
   * Get a base container with Ansible installed
   */
  @func()
  async ansibleContainer(): Promise<Container> {
    return dag
      .container()
      .from("python:3.12-slim")
      .withExec(["pip", "install", "ansible", "docker", "community.docker"])
      .withMountedDirectory("/ansible", this.ansibleDir)
      .withWorkdir("/ansible");
  }

  /**
   * Run an Ansible playbook
   */
  @func()
  async runPlaybook(
    playbook: string,
    inventory: string = "inventory/hosts.yml",
    extraVars?: string,
    tags?: string,
    limit?: string
  ): Promise<string> {
    let container = await this.ansibleContainer();

    const args = [
      "ansible-playbook",
      `-i ${inventory}`,
      playbook,
    ];

    if (extraVars) {
      args.push(`-e '${extraVars}'`);
    }

    if (tags) {
      args.push(`--tags ${tags}`);
    }

    if (limit) {
      args.push(`-l ${limit}`);
    }

    container = container.withExec(["sh", "-c", args.join(" ")]);

    return container.stdout();
  }

  /**
   * Deploy infrastructure to a specific host
   */
  @func()
  async deployInfrastructure(
    host: string,
    sshKey: Secret,
    opCredentials?: Secret,
    opToken?: Secret
  ): Promise<string> {
    let container = await this.ansibleContainer();

    // Mount SSH key
    container = container
      .withMountedSecret("/root/.ssh/id_ed25519", sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"]);

    // Mount 1Password credentials if provided
    if (opCredentials && this.secretsDir) {
      container = container.withMountedDirectory("/ansible/secrets", this.secretsDir);
    }

    // Run deployment playbook
    container = container.withExec([
      "ansible-playbook",
      "-i", "inventory/hosts.yml",
      "playbooks/deploy-infrastructure.yml",
      "-l", host,
      "-v",
    ]);

    return container.stdout();
  }

  /**
   * Deploy only Pangolin stack
   */
  @func()
  async deployPangolin(
    host: string,
    sshKey: Secret,
    domain: string
  ): Promise<string> {
    let container = await this.ansibleContainer();

    container = container
      .withMountedSecret("/root/.ssh/id_ed25519", sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
      .withExec([
        "ansible-playbook",
        "-i", "inventory/hosts.yml",
        "playbooks/deploy-infrastructure.yml",
        "-l", host,
        "--tags", "pangolin",
        "-e", `pangolin_domain=${domain}`,
      ]);

    return container.stdout();
  }

  /**
   * Deploy only Komodo stack
   */
  @func()
  async deployKomodo(
    host: string,
    sshKey: Secret
  ): Promise<string> {
    let container = await this.ansibleContainer();

    container = container
      .withMountedSecret("/root/.ssh/id_ed25519", sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
      .withExec([
        "ansible-playbook",
        "-i", "inventory/hosts.yml",
        "playbooks/komodo.yml",
        "-l", host,
      ]);

    return container.stdout();
  }

  /**
   * Deploy Komodo periphery agents
   */
  @func()
  async deployPeriphery(
    hosts: string,
    sshKey: Secret
  ): Promise<string> {
    let container = await this.ansibleContainer();

    container = container
      .withMountedSecret("/root/.ssh/id_ed25519", sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
      .withExec([
        "ansible-playbook",
        "-i", "inventory/hosts.yml",
        "playbooks/periphery.yml",
        "-l", hosts,
      ]);

    return container.stdout();
  }

  /**
   * Check infrastructure health
   */
  @func()
  async healthCheck(
    hosts: string,
    sshKey: Secret
  ): Promise<string> {
    let container = await this.ansibleContainer();

    container = container
      .withMountedSecret("/root/.ssh/id_ed25519", sshKey)
      .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
      .withExec([
        "ansible",
        "-i", "inventory/hosts.yml",
        hosts,
        "-m", "ping",
      ]);

    return container.stdout();
  }

  /**
   * Run linter on Ansible code
   */
  @func()
  async lint(): Promise<string> {
    let container = await this.ansibleContainer();

    container = container
      .withExec(["pip", "install", "ansible-lint"])
      .withExec(["ansible-lint", "playbooks/", "roles/"]);

    return container.stdout();
  }
}

@object()
export class DockerCompose {
  @field()
  composeDir: Directory;

  constructor(composeDir: Directory) {
    this.composeDir = composeDir;
  }

  /**
   * Get a container with Docker Compose
   */
  @func()
  async composeContainer(): Promise<Container> {
    return dag
      .container()
      .from("docker:27-cli")
      .withMountedDirectory("/compose", this.composeDir)
      .withWorkdir("/compose");
  }

  /**
   * Validate compose files
   */
  @func()
  async validate(composeFile: string = "docker-compose.yml"): Promise<string> {
    const container = await this.composeContainer();
    return container
      .withExec(["docker", "compose", "-f", composeFile, "config"])
      .stdout();
  }

  /**
   * Generate compose config with secrets resolved
   */
  @func()
  async generateConfig(
    composeFile: string = "docker-compose.yml"
  ): Promise<string> {
    const container = await this.composeContainer();
    return container
      .withExec(["docker", "compose", "-f", composeFile, "config", "--no-interpolate"])
      .stdout();
  }
}

@object()
export class OnePassword {
  /**
   * Get a secret from 1Password using op CLI
   */
  @func()
  async getSecret(
    reference: string,
    connectHost: string,
    connectToken: Secret
  ): Promise<Secret> {
    const container = dag
      .container()
      .from("1password/op:2")
      .withSecretVariable("OP_CONNECT_TOKEN", connectToken)
      .withEnvVariable("OP_CONNECT_HOST", connectHost);

    const output = await container
      .withExec(["op", "read", reference])
      .stdout();

    return dag.setSecret("op-secret", output.trim());
  }

  /**
   * Inject secrets into a file using op inject
   */
  @func()
  async injectSecrets(
    templateFile: Directory,
    templatePath: string,
    connectHost: string,
    connectToken: Secret
  ): Promise<string> {
    const container = dag
      .container()
      .from("1password/op:2")
      .withSecretVariable("OP_CONNECT_TOKEN", connectToken)
      .withEnvVariable("OP_CONNECT_HOST", connectHost)
      .withMountedDirectory("/templates", templateFile)
      .withWorkdir("/templates");

    return container
      .withExec(["op", "inject", "-i", templatePath])
      .stdout();
  }
}

// =============================================================================
// Re-export modules for Dagger
// =============================================================================
export { Forgejo } from "./forgejo.js";
export { Komodo } from "./komodo.js";
export { GitOpsSetup } from "./gitops.js";
export { Periphery } from "./periphery.js";
export { PangolinLabels } from "./pangolin-labels.js";
export { Infrastructure } from "./infrastructure.js";
export { DevEnvironment } from "./dev-environment.js";
export { AuthStack } from "./auth-stack.js";
export { GitHubSync } from "./github-sync.js";
export { PangolinApi } from "./pangolin-api.js";
export { PangolinDeployment } from "./pangolin.js";

// =============================================================================
// Sruth Monorepo Dev Environment Modules
// =============================================================================
export { AppRegistry } from "./apps.js";
export { SecretsManager } from "./secrets.js";
export { ServiceOrchestrator } from "./services.js";
export { Workspace } from "./workspace.js";
export { Microfrontends } from "./microfrontends.js";
export { AuthAutomation } from "./auth.js";

// =============================================================================
// ML Infrastructure Modules
// =============================================================================
export { MLGateway } from "./ml.js";
export { Observability } from "./observability.js";
export { VectorDB } from "./vectordb.js";
export { AIMemory } from "./memory.js";
export { Orchestration } from "./orchestration.js";
export { ServiceClients } from "./service-clients.js";
