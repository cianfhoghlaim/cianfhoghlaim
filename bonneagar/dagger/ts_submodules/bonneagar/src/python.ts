/**
 * Python CI Module
 *
 * Provides Python testing and validation functions:
 * - pytest testing
 * - pyright type checking
 * - ruff linting
 * - uv dependency management
 * - Dagster asset testing
 */

import {
  dag,
  Container,
  Directory,
  object,
  func,
} from "@dagger.io/dagger";

@object()
export class Python {
  /**
   * Get a base Python container with uv
   */
  @func()
  baseContainer(): Container {
    return dag
      .container()
      .from("ghcr.io/astral-sh/uv:python3.12-bookworm")
      .withEnvVariable("UV_SYSTEM_PYTHON", "1");
  }

  /**
   * Run pytest on a Python project
   */
  @func()
  async test(
    source: Directory,
    project: string = ".",
    extraArgs: string = ""
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["uv", "sync"])
      .withExec(["uv", "run", "pytest", ...extraArgs.split(" ").filter(Boolean)]);

    return container.stdout();
  }

  /**
   * Run pyright type checking
   */
  @func()
  async typecheck(
    source: Directory,
    project: string = "."
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["uv", "sync"])
      .withExec(["uv", "run", "pyright"]);

    return container.stdout();
  }

  /**
   * Run ruff linting
   */
  @func()
  async lint(
    source: Directory,
    project: string = ".",
    fix: boolean = false
  ): Promise<string> {
    const args = fix
      ? ["uv", "run", "ruff", "check", ".", "--fix"]
      : ["uv", "run", "ruff", "check", "."];

    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["uv", "sync"])
      .withExec(args);

    return container.stdout();
  }

  /**
   * Run ruff formatting
   */
  @func()
  async format(
    source: Directory,
    project: string = ".",
    check: boolean = false
  ): Promise<string> {
    const args = check
      ? ["uv", "run", "ruff", "format", ".", "--check"]
      : ["uv", "run", "ruff", "format", "."];

    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["uv", "sync"])
      .withExec(args);

    return container.stdout();
  }

  /**
   * Test Dagster assets and jobs
   */
  @func()
  async testDagster(
    source: Directory,
    project: string = "sruth/oideachas"
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["uv", "sync", "--group", "dagster"])
      .withExec(["uv", "run", "dagster", "asset", "check", "--all"]);

    return container.stdout();
  }

  /**
   * Run all Python checks (lint, typecheck, test)
   */
  @func()
  async check(
    source: Directory,
    project: string = "."
  ): Promise<string> {
    const results: string[] = [];

    results.push("=== Ruff Lint ===");
    try {
      const lintResult = await this.lint(source, project);
      results.push(lintResult);
    } catch (e) {
      results.push(`Lint failed: ${e}`);
    }

    results.push("\n=== Pyright ===");
    try {
      const typecheckResult = await this.typecheck(source, project);
      results.push(typecheckResult);
    } catch (e) {
      results.push(`Typecheck failed: ${e}`);
    }

    results.push("\n=== Pytest ===");
    try {
      const testResult = await this.test(source, project);
      results.push(testResult);
    } catch (e) {
      results.push(`Tests failed: ${e}`);
    }

    return results.join("\n");
  }

  /**
   * Test all Python projects in the workspace
   */
  @func()
  async testAll(source: Directory): Promise<string> {
    const projects = [
      "sruth/oideachas",
      "sruth/teanga",
      "sruth/tuath",
    ];

    const results: string[] = [];

    for (const project of projects) {
      results.push(`\n=== Testing ${project} ===`);
      try {
        const result = await this.test(source, project);
        results.push(result);
      } catch (e) {
        results.push(`Failed: ${e}`);
      }
    }

    return results.join("\n");
  }
}
