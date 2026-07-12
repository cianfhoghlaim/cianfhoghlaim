/**
 * Cloudflare CI Module
 *
 * Provides Cloudflare deployment functions:
 * - Pages deployment
 * - Workers deployment
 * - D1 database operations
 * - R2 storage operations
 */

import {
  dag,
  Container,
  Directory,
  Secret,
  object,
  func,
} from "@dagger.io/dagger";

@object()
export class Cloudflare {
  /**
   * Get a base container with Wrangler
   */
  @func()
  baseContainer(apiToken: Secret): Container {
    return dag
      .container()
      .from("node:22-slim")
      .withExec(["npm", "install", "-g", "wrangler"])
      .withSecretVariable("CLOUDFLARE_API_TOKEN", apiToken);
  }

  /**
   * Deploy to Cloudflare Pages
   */
  @func()
  async deployPages(
    buildDir: Directory,
    projectName: string,
    apiToken: Secret,
    accountId: string
  ): Promise<string> {
    const container = this.baseContainer(apiToken)
      .withEnvVariable("CLOUDFLARE_ACCOUNT_ID", accountId)
      .withDirectory("/build", buildDir)
      .withWorkdir("/build")
      .withExec([
        "wrangler",
        "pages",
        "deploy",
        ".",
        "--project-name",
        projectName,
      ]);

    return container.stdout();
  }

  /**
   * Deploy documentation site to Cloudflare Pages
   */
  @func()
  async deployDocs(
    source: Directory,
    apiToken: Secret,
    accountId: string,
    projectName: string = "cianfhoghlaim-docs"
  ): Promise<string> {
    // First build the docs
    const buildContainer = dag
      .container()
      .from("oven/bun:latest")
      .withDirectory("/src", source)
      .withWorkdir("/src/docs-site")
      .withExec(["bun", "install", "--frozen-lockfile"])
      .withExec(["bun", "run", "build"]);

    const buildDir = buildContainer.directory("build");

    // Then deploy to Pages
    return this.deployPages(buildDir, projectName, apiToken, accountId);
  }

  /**
   * Deploy a Cloudflare Worker
   */
  @func()
  async deployWorker(
    source: Directory,
    workerPath: string,
    apiToken: Secret,
    accountId: string
  ): Promise<string> {
    const container = this.baseContainer(apiToken)
      .withEnvVariable("CLOUDFLARE_ACCOUNT_ID", accountId)
      .withDirectory("/src", source)
      .withWorkdir(`/src/${workerPath}`)
      .withExec(["wrangler", "deploy"]);

    return container.stdout();
  }

  /**
   * List Cloudflare Pages projects
   */
  @func()
  async listProjects(
    apiToken: Secret,
    accountId: string
  ): Promise<string> {
    const container = this.baseContainer(apiToken)
      .withEnvVariable("CLOUDFLARE_ACCOUNT_ID", accountId)
      .withExec(["wrangler", "pages", "project", "list"]);

    return container.stdout();
  }

  /**
   * List Cloudflare Workers
   */
  @func()
  async listWorkers(
    apiToken: Secret,
    accountId: string
  ): Promise<string> {
    const container = this.baseContainer(apiToken)
      .withEnvVariable("CLOUDFLARE_ACCOUNT_ID", accountId)
      .withExec(["wrangler", "deployments", "list"]);

    return container.stdout();
  }

  /**
   * Tail Worker logs
   */
  @func()
  async tailWorker(
    workerName: string,
    apiToken: Secret,
    accountId: string
  ): Promise<string> {
    const container = this.baseContainer(apiToken)
      .withEnvVariable("CLOUDFLARE_ACCOUNT_ID", accountId)
      .withExec(["wrangler", "tail", workerName, "--once"]);

    return container.stdout();
  }
}
