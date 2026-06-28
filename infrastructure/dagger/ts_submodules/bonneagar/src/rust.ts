/**
 * Rust CI Module
 *
 * Provides Rust build and test functions:
 * - cargo build
 * - cargo test
 * - cargo clippy
 * - cargo fmt check
 */

import {
  dag,
  Container,
  Directory,
  object,
  func,
} from "@dagger.io/dagger";

@object()
export class Rust {
  /**
   * Get a base Rust container
   */
  @func()
  baseContainer(): Container {
    return dag
      .container()
      .from("rust:1.83-slim")
      .withExec(["apt-get", "update"])
      .withExec(["apt-get", "install", "-y", "pkg-config", "libssl-dev"]);
  }

  /**
   * Build a Rust project
   */
  @func()
  async build(
    source: Directory,
    project: string = "bonneagar/locket",
    release: boolean = false
  ): Promise<string> {
    const args = release
      ? ["cargo", "build", "--release"]
      : ["cargo", "build"];

    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(args);

    return container.stdout();
  }

  /**
   * Run tests
   */
  @func()
  async test(
    source: Directory,
    project: string = "bonneagar/locket"
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["cargo", "test"]);

    return container.stdout();
  }

  /**
   * Run clippy linting
   */
  @func()
  async clippy(
    source: Directory,
    project: string = "bonneagar/locket"
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["rustup", "component", "add", "clippy"])
      .withExec(["cargo", "clippy", "--", "-D", "warnings"]);

    return container.stdout();
  }

  /**
   * Check formatting
   */
  @func()
  async fmtCheck(
    source: Directory,
    project: string = "bonneagar/locket"
  ): Promise<string> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["rustup", "component", "add", "rustfmt"])
      .withExec(["cargo", "fmt", "--", "--check"]);

    return container.stdout();
  }

  /**
   * Run all Rust checks (clippy, fmt, test)
   */
  @func()
  async check(
    source: Directory,
    project: string = "bonneagar/locket"
  ): Promise<string> {
    const results: string[] = [];

    results.push("=== Clippy ===");
    try {
      const clippyResult = await this.clippy(source, project);
      results.push(clippyResult || "No warnings");
    } catch (e) {
      results.push(`Clippy failed: ${e}`);
    }

    results.push("\n=== Format Check ===");
    try {
      const fmtResult = await this.fmtCheck(source, project);
      results.push(fmtResult || "Formatting OK");
    } catch (e) {
      results.push(`Format check failed: ${e}`);
    }

    results.push("\n=== Tests ===");
    try {
      const testResult = await this.test(source, project);
      results.push(testResult);
    } catch (e) {
      results.push(`Tests failed: ${e}`);
    }

    return results.join("\n");
  }

  /**
   * Build release binary
   */
  @func()
  async buildRelease(
    source: Directory,
    project: string = "bonneagar/locket"
  ): Promise<Directory> {
    const container = this.baseContainer()
      .withDirectory("/src", source)
      .withWorkdir(`/src/${project}`)
      .withExec(["cargo", "build", "--release"]);

    return container.directory("target/release");
  }
}
