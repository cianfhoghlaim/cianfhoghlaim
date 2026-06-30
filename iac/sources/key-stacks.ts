// bonneagar/iac/sources/key-stacks.ts — The 30 "key" stacks (5-group model filter)
// Returns the names of the stacks the IaC deploys (the curated list).

export const KEY_STACKS_5_GROUP_MODEL = [
  // ============================ infrastructure (9) ============================
  // All on arm1-oci. The IaC deploys these first (the mesh backbone).
  "pangolin",
  "pocketid",
  "tinyauth",
  "traefik",
  "infisical",
  "locket",
  "komodo",
  "backrest",
  "gerbil",

  // ============================ data-engineering (12) ============================
  // All on bunchloch. The IaC deploys these second (the lakehouse data plane).
  "dagster",
  "lakehouse",
  "marimo",
  "cognee",
  "langfuse",
  "llama-swap",
  "duckdb",
  "ducklake",
  "falkordb",
  "graphiti",
  "litellm",
  "logfire",

  // ============================ agent-platform (7) ============================
  // All on bunchloch. The IaC deploys these third.
  "agent-os",
  "openclaw",
  "openchamber",
  "letta",
  "memgraph",
  "mlx-omni",
  "lmnr",

  // ============================ language-model (6) ============================
  // All on bunchloch. The IaC deploys these fourth.
  "mlflow",
  "motherduck",
  "nimtable",
  "invokeai",
  "r2",
  "mlx-omni", // Already counted above; deduped at runtime

  // ============================ user-facing-web (6) ============================
  // All on bunchloch. The IaC deploys these fifth.
  "oideachais",
  "oideachais_dagster",
  "oideachais-api",
  "oideachais-frontend",
  "oideachais-agent-os",
  "oideachais-adk-agents",

  // ============================ ci (1) ============================
  "ci/hf-watchdog",
];

export function getKeyStacks(): string[] {
  // Dedupe + sort
  return [...new Set(KEY_STACKS_5_GROUP_MODEL)].sort();
}

export function getKeyStacksByGroup(): Record<string, string[]> {
  return {
    infrastructure: ["pangolin", "pocketid", "tinyauth", "traefik", "infisical", "locket", "komodo", "backrest", "gerbil"],
    "data-engineering": ["dagster", "lakehouse", "marimo", "cognee", "langfuse", "llama-swap", "duckdb", "ducklake", "falkordb", "graphiti", "litellm", "logfire"],
    "agent-platform": ["agent-os", "openclaw", "openchamber", "letta", "memgraph", "mlx-omni", "lmnr"],
    "language-model": ["mlflow", "motherduck", "nimtable", "invokeai", "r2"],
    "user-facing-web": ["oideachais", "oideachais_dagster", "oideachais-api", "oideachais-frontend", "oideachais-agent-os", "oideachais-adk-agents"],
    "ci": ["ci/hf-watchdog"],
  };
}
