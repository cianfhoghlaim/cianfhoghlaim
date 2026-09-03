#!/usr/bin/env bun
/**
 * scripts/lakehouse-memory-doctor.ts
 *
 * Probe the 5 memory backends of the Cianfhoghlaim agent-platform cluster
 * + emit a JSON health report at `stedding/memory-health/<utc-ts>.json`.
 *
 * Implements the R "Memory-stack health is exposed via the marimo doctor"
 * of the `2026-08-15-lakehouse-memory-stack-deep-integration-v1` openspec
 * change, plus the R "Phase 7 of deploy-full.sh runs the memory-stack
 * doctor" of the `agent-platform-cluster` spec delta.
 *
 * The 5 backends probed:
 *   - cognee      → GET http://cognee:8000/health
 *   - graphiti    → GET http://graphiti:8000/healthcheck
 *   - lancedb     → GET http://lakehouse-lance-namespace:8182/v1/info
 *   - falkordb    → TCP connect to falkordb:6379
 *   - memgraph    → TCP connect to memgraph:7687 (Bolt endpoint)
 *
 * Usage:
 *   bun run scripts/lakehouse-memory-doctor.ts          # human-readable summary
 *   bun run scripts/lakehouse-memory-doctor.ts --json   # JSON to stdout
 *   bun run scripts/lakehouse-memory-doctor.ts --strict # exit 1 if any backend unhealthy
 *
 * Environment overrides:
 *   COGNEE_URL, GRAPHITI_URL, LANCEDB_URL, FALKORDB_HOST, MEMGRAPH_HOST
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { networkInterfaces } from "node:os";

interface ProbeResult {
  status: "healthy" | "not_healthy" | "not_reachable";
  latency_ms: number;
  error: string | null;
  endpoint: string;
  purpose: string;
  spec: string;
}

interface DoctorReport {
  timestamp: string;
  summary: {
    healthy: number;
    failed: number;
    total: number;
  };
  backends: Record<string, ProbeResult>;
}

const ENDPOINTS: Record<string, { url: string; kind: "http" | "tcp"; purpose: string; spec: string }> = {
  cognee: {
    url: process.env.COGNEE_URL || "http://cognee:8000/health",
    kind: "http",
    purpose: "Structured knowledge graph (entities + relationships)",
    spec: "cognee SKILL.md (1.2.2)",
  },
  graphiti: {
    url: process.env.GRAPHITI_URL || "http://graphiti:8000/healthcheck",
    kind: "http",
    purpose: "Temporal knowledge graph (bi-temporal episodes)",
    spec: "graphiti SKILL.md (0.29.2)",
  },
  lancedb: {
    url: process.env.LANCEDB_URL || "http://lakehouse-lance-namespace:8182/v1/info",
    kind: "http",
    purpose: "Vector RAG (HNSW, Lance Format v2.2, Namespace 0.9)",
    spec: "lancedb SKILL.md",
  },
  falkordb: {
    url: process.env.FALKORDB_URL || "falkordb:6379",
    kind: "tcp",
    purpose: "Vector + graph hybrid (vector.so loadmodule)",
    spec: "falkordb SKILL.md (v4.18.11)",
  },
  memgraph: {
    url: process.env.MEMGRAPH_HOST || "memgraph:7687",
    kind: "tcp",
    purpose: "Production graph (Cypher + MAGE algorithms)",
    spec: "memgraph SKILL.md (3.6.0)",
  },
};

async function probeHttp(url: string, timeoutMs = 3000): Promise<{ status: ProbeResult["status"]; latency_ms: number; error: string | null }> {
  const started = Date.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      method: "GET",
      signal: controller.signal,
    });
    clearTimeout(timer);
    const latency = Date.now() - started;
    if (response.ok || response.status < 500) {
      return { status: "healthy", latency_ms: latency, error: null };
    }
    return {
      status: "not_healthy",
      latency_ms: latency,
      error: `HTTP ${response.status}`,
    };
  } catch (e) {
    clearTimeout(timer);
    const latency = Date.now() - started;
    const err = e instanceof Error ? e : new Error(String(e));
    return {
      status: "not_reachable",
      latency_ms: latency,
      error: err.name === "AbortError" ? "timeout" : err.message,
    };
  }
}

async function probeTcp(hostport: string, timeoutMs = 3000): Promise<{ status: ProbeResult["status"]; latency_ms: number; error: string | null }> {
  const started = Date.now();
  try {
    const [host, portStr] = hostport.split(":");
    const port = parseInt(portStr, 10);
    if (!host || !port) {
      return {
        status: "not_reachable",
        latency_ms: 0,
        error: `invalid hostport: ${hostport}`,
      };
    }
    // Bun supports Bun.connect; for portability we just await a TCP probe via net
    // We use the Node net module which Bun provides
    const net = await import("node:net");
    await new Promise<void>((resolve, reject) => {
      const socket = new net.Socket();
      const timer = setTimeout(() => {
        socket.destroy();
        reject(new Error("timeout"));
      }, timeoutMs);
      socket.once("connect", () => {
        clearTimeout(timer);
        socket.end();
        resolve();
      });
      socket.once("error", (err) => {
        clearTimeout(timer);
        reject(err);
      });
      socket.connect(port, host);
    });
    const latency = Date.now() - started;
    return { status: "healthy", latency_ms: latency, error: null };
  } catch (e) {
    const latency = Date.now() - started;
    const err = e instanceof Error ? e : new Error(String(e));
    return {
      status: "not_reachable",
      latency_ms: latency,
      error: err.message,
    };
  }
}

async function probe(name: string): Promise<ProbeResult> {
  const cfg = ENDPOINTS[name];
  let probeResult;
  if (cfg.kind === "http") {
    probeResult = await probeHttp(cfg.url);
  } else {
    probeResult = await probeTcp(cfg.url);
  }
  return {
    status: probeResult.status,
    latency_ms: probeResult.latency_ms,
    error: probeResult.error,
    endpoint: cfg.url,
    purpose: cfg.purpose,
    spec: cfg.spec,
  };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const jsonOnly = args.includes("--json");
  const strict = args.includes("--strict");
  const writeReport = !args.includes("--no-write");

  const results: Record<string, ProbeResult> = {};
  for (const name of Object.keys(ENDPOINTS)) {
    results[name] = await probe(name);
  }

  const healthy = Object.values(results).filter((r) => r.status === "healthy").length;
  const failed = Object.values(results).filter((r) => r.status !== "healthy");

  const report: DoctorReport = {
    timestamp: new Date().toISOString(),
    summary: {
      healthy,
      failed: failed.length,
      total: Object.keys(results).length,
    },
    backends: results,
  };

  if (writeReport) {
    const ts = new Date()
      .toISOString()
      .replace(/[:.]/g, "-")
      .replace(/T/, "_")
      .replace(/Z$/, "Z");
    const dir = "stedding/memory-health";
    mkdirSync(dir, { recursive: true });
    const path = join(dir, `${ts}.json`);
    writeFileSync(path, JSON.stringify(report, null, 2));
  }

  if (jsonOnly) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(`=== Lakehouse memory doctor (${healthy}/5 healthy) ===`);
    for (const [name, data] of Object.entries(results)) {
      const emoji = data.status === "healthy" ? "✅" : "❌";
      const errSuffix = data.error ? ` — ${data.error}` : "";
      console.log(`  ${emoji} ${name.padEnd(12)} ${data.status.padEnd(15)} ${data.latency_ms}ms${errSuffix}`);
    }
    if (failed.length > 0) {
      console.log(
        `\n❌ ${failed.length} backend(s) unhealthy. Run \`mise run deploy:full --phase=7\` after remediation.`,
      );
    }
  }

  if (strict && healthy < Object.keys(results).length) {
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(`lakehouse-memory-doctor failed: ${e instanceof Error ? e.message : String(e)}`);
  process.exit(2);
});