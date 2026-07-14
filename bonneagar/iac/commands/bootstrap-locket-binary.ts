// bonneagar/iac/commands/bootstrap-locket-binary.ts — Downloads the locket Rust binary
//
// Locket (https://github.com/bpbradley/locket) is a secrets management
// agent that materializes secrets from a provider (Infisical, 1Password, etc.)
// into tmpfs files at container startup. It's the canonical pattern the
// bons IaC uses for the bundled `stacks/control-plane/` stack.
//
// The IaC itself needs the locket binary locally too (for health checks,
// secret materialization in dev, etc.) — this command installs it.
//
// Usage:
//   bun run iac:bootstrap-locket-binary
//   bun run iac:bootstrap-locket-binary --force  # re-download even if installed
//
// Idempotent: skips the download if locket is already at ~/.local/bin/locket.

import { existsSync, mkdirSync, chmodSync } from "node:fs";
import { join } from "node:path";
import { execSync } from "node:child_process";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";

const LOCKET_VERSION = "0.17.3";
const LOCKET_REPO = "bpbradley/locket";
const LOCKET_BIN = join(process.env.HOME ?? "/root", ".local", "bin", "locket");

interface InstallResult {
  action: "skipped" | "downloaded" | "verified";
  version?: string;
  path: string;
}

export async function bootstrapLocketBinary(opts?: { force?: boolean }): Promise<InstallResult> {
  logStep("iac:bootstrap-locket-binary — installs the locket Rust binary for IaC use");

  // 1. Check if already installed
  if (!opts?.force && existsSync(LOCKET_BIN)) {
    try {
      const version = execSync(`${LOCKET_BIN} --version`, { encoding: "utf-8" }).trim();
      logOk(`locket already installed at ${LOCKET_BIN} (${version})`);
      return { action: "skipped", version, path: LOCKET_BIN };
    } catch (e) {
      logWarn(`locket at ${LOCKET_BIN} is broken: ${(e as Error).message} — re-installing`);
    }
  }

  // 2. Download from GitHub releases
  // Asset naming: locket-{arch}-{platform}.tar.xz (e.g. locket-aarch64-apple-darwin.tar.xz)
  const arch = process.arch === "arm64" ? "aarch64" : "x86_64";
  const platform = process.platform === "darwin" ? "apple-darwin" : "unknown-linux-gnu";
  const assetName = `locket-${arch}-${platform}.tar.xz`;
  const downloadUrl = `https://github.com/${LOCKET_REPO}/releases/download/v${LOCKET_VERSION}/${assetName}`;

  log(`  downloading ${assetName}...`);
  mkdirSync(join(process.env.HOME ?? "/root", ".local", "bin"), { recursive: true });

  try {
    const tmpTar = `/tmp/locket-${LOCKET_VERSION}.tar.xz`;
    const tmpExtract = `/tmp/locket-${LOCKET_VERSION}-extract`;
    execSync(`curl -fsSL -o ${tmpTar} ${downloadUrl}`, { stdio: "inherit" });
    // The tar contains a single subdirectory like `locket-aarch64-apple-darwin/locket`.
    // Extract and find the binary inside.
    execSync(`rm -rf ${tmpExtract} && mkdir -p ${tmpExtract}`, { stdio: "pipe" });
    execSync(`tar -xJf ${tmpTar} -C ${tmpExtract}`, { stdio: "inherit" });
    // Find the locket binary (typically in a single subdirectory)
    // Use -perm +111 (cross-platform; macOS find doesn't support -executable)
    const findResult = execSync(`find ${tmpExtract} -type f -name 'locket' -perm +111 | head -1`, { encoding: "utf-8" }).trim();
    if (!findResult) {
      throw new Error(`Could not find 'locket' binary inside the tar archive`);
    }
    execSync(`mv ${findResult} ${LOCKET_BIN}`, { stdio: "inherit" });
    execSync(`rm -rf ${tmpTar} ${tmpExtract}`, { stdio: "pipe" });
    chmodSync(LOCKET_BIN, 0o755);
  } catch (e) {
    logError(`Failed to download locket from ${downloadUrl}: ${(e as Error).message}`);
    log("  Manual install: see https://github.com/bpbradley/locket/releases");
    throw e;
  }

  // 3. Verify
  try {
    const version = execSync(`${LOCKET_BIN} --version`, { encoding: "utf-8" }).trim();
    logOk(`locket installed at ${LOCKET_BIN} (${version})`);
    return { action: "downloaded", version, path: LOCKET_BIN };
  } catch (e) {
    logError(`locket install verification failed: ${(e as Error).message}`);
    throw e;
  }
}
