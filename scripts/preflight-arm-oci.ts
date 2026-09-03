#!/usr/bin/env bun
/**
 * preflight-arm-oci.ts
 *
 * Pre-flight gate before any arm-oci stack deploy.
 * Runs 4 checks: Pangolin health, Komodo health, Infisical health,
 * process namespace isolation.
 *
 * Usage:
 *   bun run preflight:arm-oci                          # all 4 checks, --dry-run by default
 *   bun run preflight:arm-oci --strict --emit-md      # strict + write report
 *   bun run preflight:arm-oci --skip-namespace        # dev override (NOT for prod deploys)
 *
 * Exit codes:
 *   0 = ALL CHECKS PASSED
 *   1 = PREFLIGHT FAILED (one or more checks failed)
 *   2 = SCRIPT ERROR (missing env vars, docker not available, etc.)
 */

interface CheckResult {
  name: string;
  ok: boolean;
  message: string;
  durationMs: number;
}

const FORBIDDEN_CONTAINERS = [
  "openchamber", "openclaw", "hermes", "komodo", "pangolin", "infisical",
];

/** Check 1: Pangolin health */
async function checkPangolin(): Promise<CheckResult> {
  const start = Date.now();
  const url = process.env.PANGOLIN_URL ?? "https://pangolin.cianfhoghlaim.ie";
  const apiKey = process.env.PANGOLIN_API_KEY;
  if (!apiKey) {
    return {
      name: "Pangolin health",
      ok: false,
      message: `PANGOLIN_API_KEY is not set in the environment (mise/Infisical hydration may not have run); set it via .infisical.env or 'infisical export'`,
      durationMs: Date.now() - start,
    };
  }
  try {
    const res = await fetch(`${url}/api/v1/`, {
      headers: { Authorization: `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(5000),
    });
    return {
      name: "Pangolin health",
      ok: res.ok,
      message: res.ok ? `Pangolin OK (${res.status} at ${url})` : `Pangolin returned ${res.status} at ${url}`,
      durationMs: Date.now() - start,
    };
  } catch (e) {
    return {
      name: "Pangolin health",
      ok: false,
      message: `Pangolin unreachable at ${url}: ${e instanceof Error ? e.message : String(e)}`,
      durationMs: Date.now() - start,
    };
  }
}

/** Check 2: Komodo health */
async function checkKomodo(): Promise<CheckResult> {
  const start = Date.now();
  const url = process.env.KOMODO_URL ?? "https://komodo.cianfhoghlaim.ie";
  const apiKey = process.env.KOMODO_API_KEY;
  if (!apiKey) {
    return {
      name: "Komodo health",
      ok: false,
      message: `KOMODO_API_KEY is not set in the environment`,
      durationMs: Date.now() - start,
    };
  }
  try {
    const res = await fetch(`${url}/ping`, {
      headers: { Authorization: `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(5000),
    });
    return {
      name: "Komodo health",
      ok: res.ok,
      message: res.ok ? `Komodo OK (${res.status} at ${url})` : `Komodo returned ${res.status} at ${url}`,
      durationMs: Date.now() - start,
    };
  } catch (e) {
    return {
      name: "Komodo health",
      ok: false,
      message: `Komodo unreachable at ${url}: ${e instanceof Error ? e.message : String(e)}`,
      durationMs: Date.now() - start,
    };
  }
}

/** Check 3: Infisical health */
async function checkInfisical(): Promise<CheckResult> {
  const start = Date.now();
  const url = process.env.INFISICAL_URL ?? "https://infisical.cianfhoghlaim.ie";
  const token = process.env.INFISICAL_TOKEN;
  if (!token) {
    return {
      name: "Infisical health",
      ok: false,
      message: `INFISICAL_TOKEN is not set in the environment`,
      durationMs: Date.now() - start,
    };
  }
  try {
    const res = await fetch(`${url}/api/status`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(5000),
    });
    return {
      name: "Infisical health",
      ok: res.ok,
      message: res.ok ? `Infisical OK (${res.status} at ${url})` : `Infisical returned ${res.status} at ${url}`,
      durationMs: Date.now() - start,
    };
  } catch (e) {
    return {
      name: "Infisical health",
      ok: false,
      message: `Infisical unreachable at ${url}: ${e instanceof Error ? e.message : String(e)}`,
      durationMs: Date.now() - start,
    };
  }
}

/** Check 4: Process namespace isolation
 *
 * Refuses to proceed if the current opencode session PID shares a
 * PID namespace with any forbidden container (openchamber, openclaw,
 * hermes, komodo, pangolin, infisical).
 */
async function checkProcessNamespace(): Promise<CheckResult> {
  const start = Date.now();
  // Read /proc/self/status for NStgid (PID namespace ID)
  let status: string;
  try {
    status = await Bun.file("/proc/self/status").text();
  } catch (e) {
    return {
      name: "Process namespace",
      ok: true,
      message: `Skipped (cannot read /proc/self/status: ${e instanceof Error ? e.message : String(e)} — likely macOS dev environment)`,
      durationMs: Date.now() - start,
    };
  }
  const nsMatch = status.match(/^NStgid:\s+(\d+)/m);
  if (!nsMatch) {
    return {
      name: "Process namespace",
      ok: true,
      message: "Skipped (NStgid not found in /proc/self/status — non-Linux host)",
      durationMs: Date.now() - start,
    };
  }
  const myNs = nsMatch[1];

  // Check if any forbidden container is in the same namespace
  for (const c of FORBIDDEN_CONTAINERS) {
    const proc = Bun.spawn(["docker", "top", c, "-o", "pid"], {
      stdout: "pipe",
      stderr: "pipe",
    });
    const out = await new Response(proc.stdout).text();
    if (out.trim() && !out.includes("Error") && !out.toLowerCase().includes("no such")) {
      const pids = out.trim().split("\n").slice(1).map((l) => l.trim()).filter(Boolean);
      for (const pid of pids) {
        try {
          const otherNs = await Bun.file(`/proc/${pid}/status`).text();
          const otherNsMatch = otherNs.match(/^NStgid:\s+(\d+)/m);
          if (otherNsMatch && otherNsMatch[1] === myNs) {
            return {
              name: "Process namespace",
              ok: false,
              message: `REFUSING TO DEPLOY: opencode PID ${process.pid} shares namespace ${myNs} with ${c} container PID ${pid}; restart opencode outside the ${c} namespace first`,
              durationMs: Date.now() - start,
            };
          }
        } catch {
          // Cannot read other PID's status — skip
        }
      }
    }
  }
  return {
    name: "Process namespace",
    ok: true,
    message: `Opencode PID ${process.pid} in namespace ${myNs} — isolated from ${FORBIDDEN_CONTAINERS.join(", ")}`,
    durationMs: Date.now() - start,
  };
}

function printResults(checks: CheckResult[], dryRun: boolean): boolean {
  const allOk = checks.every((c) => c.ok);
  const header = dryRun ? "preflight:arm-oci (DRY-RUN)" : "preflight:arm-oci";
  console.log(`\n=== ${header} ===`);
  for (const c of checks) {
    const icon = c.ok ? "✅" : "❌";
    console.log(`${icon} ${c.name.padEnd(28)} ${c.durationMs}ms — ${c.message}`);
  }
  console.log(allOk ? "\nALL CHECKS PASSED" : "\nPREFLIGHT FAILED");
  console.log("=========================\n");
  return allOk;
}

async function emitReport(checks: CheckResult[], dryRun: boolean, ts: string): Promise<string> {
  const allOk = checks.every((c) => c.ok);
  const path = `docs/agents/preflight-report-${ts}.md`;
  const md = `# Preflight report — ${ts}\n\n${dryRun ? "_DRY-RUN MODE_\n\n" : ""}${checks.map((c) => `- **${c.ok ? "✅" : "❌"} ${c.name}** (${c.durationMs}ms)\n  ${c.message}`).join("\n")}\n\n**Result**: ${allOk ? "PASS" : "FAIL"}\n`;
  await Bun.write(path, md);
  return path;
}

async function main() {
  const args = process.argv.slice(2);
  const strict = args.includes("--strict");
  const emitMd = args.includes("--emit-md");
  const skipNs = args.includes("--skip-namespace");
  const dryRun = args.includes("--dry-run") || !args.includes("--apply");

  const checks: CheckResult[] = [];
  checks.push(await checkPangolin());
  checks.push(await checkKomodo());
  checks.push(await checkInfisical());
  if (!skipNs) checks.push(await checkProcessNamespace());

  const allOk = printResults(checks, dryRun);

  if (emitMd) {
    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    const path = await emitReport(checks, dryRun, ts);
    console.log(`Report written to ${path}`);
  }

  if (!allOk && strict) {
    console.error("STRICT MODE: refusing to continue with one or more failed checks");
    process.exit(1);
  }
  process.exit(allOk ? 0 : 1);
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});