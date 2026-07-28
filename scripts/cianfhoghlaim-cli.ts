#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-cli.ts
 *
 * The canonical Cianfhoghlaim CLI entry point. Replaces bons/kcg task
 * prefixes. Subcommands:
 *
 *   stack lint|plan|deploy|verify|rollback
 *   secrets lint|verify|hydrate|seed
 *   preflight
 *   topology validate
 *   brand lint
 *
 * Design constraints:
 *   - Pure subcommand dispatch. No business logic.
 *   - All commands return JSON when --json is set, text otherwise.
 *   - All commands exit 0 on success, non-zero on failure.
 *   - In CI (CI=true) or --non-interactive, the CLI does not render any
 *     interactive UI and does not prompt.
 */

import { spawn } from "node:child_process";
import { resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");

interface Command {
  name: string;
  description: string;
  run: (args: string[]) => Promise<number>;
}

interface CommandCtx {
  json: boolean;
  nonInteractive: boolean;
  dryRun: boolean;
  yes: boolean;
  verbose: boolean;
}

function parseCtx(argv: string[]): { ctx: CommandCtx; rest: string[] } {
  let json = false;
  let nonInteractive = process.env["CI"] === "true" || process.env["CI"] === "1";
  let dryRun = false;
  let yes = false;
  let verbose = false;
  const rest: string[] = [];
  for (const arg of argv) {
    switch (arg) {
      case "--json":
        json = true;
        break;
      case "--non-interactive":
        nonInteractive = true;
        break;
      case "--dry-run":
        dryRun = true;
        break;
      case "--yes":
        yes = true;
        break;
      case "--verbose":
        verbose = true;
        break;
      default:
        rest.push(arg);
    }
  }
  return {
    ctx: { json, nonInteractive, dryRun, yes, verbose },
    rest,
  };
}

function emit(ctx: CommandCtx, payload: unknown, exitCode = 0): number {
  if (ctx.json) {
    console.log(JSON.stringify(payload, null, 2));
  } else {
    if (payload && typeof payload === "object") {
      const obj = payload as Record<string, unknown>;
      for (const [k, v] of Object.entries(obj)) {
        console.log(`${k}: ${typeof v === "string" ? v : JSON.stringify(v)}`);
      }
    } else {
      console.log(payload);
    }
  }
  return exitCode;
}

function runScript(script: string, args: string[]): Promise<number> {
  return new Promise((resolveRun) => {
    const child = spawn("bun", ["run", script, ...args], {
      cwd: ROOT,
      stdio: "inherit",
      env: process.env,
    });
    child.on("exit", (code) => resolveRun(code ?? 1));
  });
}

const STACK_LINT_SCRIPT = "scripts/cianfhoghlaim-stack-lint.ts";
const STACK_PLAN_SCRIPT = "scripts/cianfhoghlaim-stack-plan.ts";
const SECRETS_LINT_SCRIPT = "scripts/cianfhoghlaim-secrets-lint.ts";
const BRAND_LINT_SCRIPT = "scripts/cianfhoghlaim-brand-lint.ts";
const PREFLIGHT_SCRIPT = "scripts/cianfhoghlaim-preflight.ts";
const TOPOLOGY_SCRIPT = "scripts/cianfhoghlaim-topology.ts";

const COMMANDS: Record<string, Command> = {
  "stack:lint": {
    name: "stack:lint",
    description: "Lint every stack under bonneagar/stacks/ against the canonical 6-file contract",
    run: async (args) => runScript(STACK_LINT_SCRIPT, args),
  },
  "stack:plan": {
    name: "stack:plan",
    description: "Compute the deployment plan for one or all stacks (read-only)",
    run: async (args) => runScript(STACK_PLAN_SCRIPT, args),
  },
  "stack:deploy": {
    name: "stack:deploy",
    description: "Deploy one or all stacks",
    run: async (args) => {
      console.error(
        "cianfhoghlaim stack deploy is not yet wired to Komodo/Pangolin/Infisical apply. Use `iac:deploy` for now.",
      );
      return 1;
    },
  },
  "stack:verify": {
    name: "stack:verify",
    description: "Verify Compose, Locket, service, and route health for a deployed stack",
    run: async (args) => {
      console.error("cianfhoghlaim stack verify is not yet implemented.");
      return 1;
    },
  },
  "stack:rollback": {
    name: "stack:rollback",
    description: "Roll back a stack to a previous known-good revision by receipt",
    run: async (args) => {
      console.error("cianfhoghlaim stack rollback is not yet implemented.");
      return 1;
    },
  },
  "secrets:lint": {
    name: "secrets:lint",
    description: "Lint secrets.env references against the Infisical vault (no reads)",
    run: async (args) => runScript(SECRETS_LINT_SCRIPT, args),
  },
  "secrets:verify": {
    name: "secrets:verify",
    description: "Verify secrets.env references resolve (no values printed)",
    run: async (args) => runScript(SECRETS_LINT_SCRIPT, ["--verify", ...args]),
  },
  "secrets:hydrate": {
    name: "secrets:hydrate",
    description: "Render secrets.env to a tmpfs file (no values persisted to disk)",
    run: async (args) => {
      console.error("cianfhoghlaim secrets hydrate is not yet implemented.");
      return 1;
    },
  },
  "secrets:seed": {
    name: "secrets:seed",
    description: "Seed Infisical vault entries from .env.local (explicit; confirm required)",
    run: async (args) => {
      console.error("cianfhoghlaim secrets seed is not yet implemented.");
      return 1;
    },
  },
  preflight: {
    name: "preflight",
    description: "Run topology + auth + secrets preflight checks before deploy",
    run: async (args) => runScript(PREFLIGHT_SCRIPT, args),
  },
  topology: {
    name: "topology",
    description: "Validate host placement (arm1-oci / bunchloch)",
    run: async (args) => runScript(TOPOLOGY_SCRIPT, args),
  },
  brand: {
    name: "brand",
    description: "Brand and retired-host linter (fails on legacy brand tokens or retired host references)",
    run: async (args) => runScript(BRAND_LINT_SCRIPT, args),
  },
};

function printHelp(): number {
  const lines = [
    "cianfhoghlaim — the Cianfhoghlaim stack deployment CLI",
    "",
    "Usage: cianfhoghlaim <command> [args]",
    "",
    "Commands:",
  ];
  for (const cmd of Object.values(COMMANDS).sort((a, b) => a.name.localeCompare(b.name))) {
    lines.push(`  ${cmd.name.padEnd(20)} ${cmd.description}`);
  }
  lines.push("");
  lines.push("Flags:");
  lines.push("  --json             Emit machine-readable JSON output");
  lines.push("  --non-interactive  Disable interactive prompts (auto in CI=true)");
  lines.push("  --dry-run          Don't mutate anything");
  lines.push("  --yes              Skip confirmations");
  lines.push("  --verbose          Verbose output");
  console.log(lines.join("\n"));
  return 0;
}

async function main(): Promise<number> {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv[0] === "--help" || argv[0] === "-h") {
    return printHelp();
  }
  const { ctx, rest } = parseCtx(argv);
  const commandName = rest[0];
  if (!commandName) return printHelp();
  const cmd = COMMANDS[commandName];
  if (!cmd) {
    return emit(ctx, { error: `unknown command: ${commandName}` }, 1);
  }
  const code = await cmd.run(rest.slice(1));
  return code;
}

process.exit(await main());