// bonneagar/iac/sources/discover-secrets.ts — Walks bonneagar/stacks/*/secrets.env
// Produces typed InfisicalSecret[] (one per infisical://dev-baile/<stack>/<key> ref).

import { join } from "node:path";
import type { InfisicalSecret } from "../models/infisical.ts";
import { discoverStacks } from "./discover-stacks.ts";

export function discoverSecrets(
  projectId: string = "dev-baile",
  environment: string = "dev-baile",
  rootDir?: string,
): InfisicalSecret[] {
  const stacks = discoverStacks(rootDir);
  const secrets: InfisicalSecret[] = [];

  for (const stack of stacks) {
    if (!stack.hasSecrets) continue;
    const secretsPath = join(stack.path, "secrets.env");
    const fs = require("node:fs");
    const text = fs.readFileSync(secretsPath, "utf8");
    const parsed = parseSecretsEnv(text, projectId, environment, stack.name);
    secrets.push(...parsed);
  }

  return secrets;
}

function parseSecretsEnv(
  text: string,
  projectId: string,
  environment: string,
  stackName: string,
): InfisicalSecret[] {
  const secrets: InfisicalSecret[] = [];

  for (const rawLine of text.split("\n")) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;

    // Match: KEY=infisical://dev-baile/<stack>/<key>
    const m = line.match(/^([A-Z_][A-Z0-9_]*)=infisical:\/\/dev-baile\/([^/]+)\/([^/]+)\/([^/]+)\/?$/);
    if (!m) continue;

    const [, envVar, pathPrefix, secretKey] = m;
    // The path inside Infisical uses "/" as the separator; e.g. "ci/hf-watchdog"
    // The env var maps to the key. The path is the parent dir.
    const path = `/${pathPrefix}`;
    secrets.push({
      key: secretKey,
      // Value is REDACTED in the output (sync-secrets reads the actual value
      // from the env var or Locket-injected file)
      value: "", // Will be populated at sync time from the source env var
      path,
      environment,
      projectId,
      comment: `env_var=${envVar}, stack=${stackName}`,
    });
  }

  return secrets;
}
