/**
 * TypeScript CI Module
 *
 * Provides TypeScript/JavaScript build and test functions:
 * - Bun build
 * - TypeScript type checking
 * - ESLint linting
 * - TanStack Start builds
 * - Docusaurus builds
 */

import {
  dag,
  Container,
  Directory,
  object,
  func,
} from "@dagger.io/dagger";

@object()
export class TypeScript {
  /**
   * Get a base container with Bun
   */
  @func()
  baseContainer(): Container {
    return dag
      .container()
      .from("oven/bun:latest");
  }

  /**
   * Install dependencies
   */
  @func()
  async install(source: Directory): Promise<Container> {
    return this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir("/src")
      .withExec(["bun", "install", "--frozen-lockfile"]);
  }

  /**
   * Run TypeScript type checking
   */
  @func()
  async typecheck(source: Directory): Promise<string> {
    const container = await this.install(source);
    return container
      .withExec(["bunx", "tsc", "--noEmit"])
      .stdout();
  }

  /**
   * Run ESLint
   */
  @func()
  async lint(
    source: Directory,
    fix: boolean = false
  ): Promise<string> {
    const container = await this.install(source);
    const args = fix
      ? ["bunx", "eslint", ".", "--fix"]
      : ["bunx", "eslint", "."];

    return container
      .withExec(args)
      .stdout();
  }

  /**
   * Build all TypeScript packages
   */
  @func()
  async build(source: Directory): Promise<string> {
    const container = await this.install(source);
    return container
      .withExec(["bun", "run", "build"])
      .stdout();
  }

  /**
   * Build a specific TanStack Start app
   */
  @func()
  async buildApp(
    source: Directory,
    appPath: string
  ): Promise<Directory> {
    const container = await this.install(source);
    return container
      .withWorkdir(`/src/${appPath}`)
      .withExec(["bun", "run", "build"])
      .directory("dist");
  }

  /**
   * Build Docusaurus site
   */
  @func()
  async buildDocs(source: Directory): Promise<Directory> {
    const container = await this.install(source);
    return container
      .withWorkdir("/src/docs-site")
      .withExec(["bun", "run", "build"])
      .directory("build");
  }

  /**
   * Run all checks (typecheck, lint)
   */
  @func()
  async check(source: Directory): Promise<string> {
    const results: string[] = [];

    results.push("=== TypeScript Check ===");
    try {
      const typecheckResult = await this.typecheck(source);
      results.push(typecheckResult || "No errors");
    } catch (e) {
      results.push(`Typecheck failed: ${e}`);
    }

    results.push("\n=== ESLint ===");
    try {
      const lintResult = await this.lint(source);
      results.push(lintResult || "No errors");
    } catch (e) {
      results.push(`Lint failed: ${e}`);
    }

    return results.join("\n");
  }

  /**
   * Build and export Docusaurus as static files
   */
  @func()
  async exportDocs(source: Directory): Promise<Directory> {
    return this.buildDocs(source);
  }
}
