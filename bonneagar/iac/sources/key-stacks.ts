// bonneagar/iac/sources/key-stacks.ts — The 30 "key" stacks (5-group model filter)
// Returns the names of the stacks the IaC deploys (the curated list).
// v5 cleanup: 11 phantom names removed; all entries point to real directories
// at bonneagar/stacks/<name>/.

export const KEY_STACKS_5_GROUP_MODEL = [
  // ============================ infrastructure (9) ============================
  // All on arm1-oci. The IaC deploys these first (the mesh backbone).
  "pangolin",
  "pocket-id",       // was: "pocketid" (missing hyphen; didn't match dir name)
  "komodo",
  "infisical",
  "backrest",
  "openclaw",
  "openchamber",
  "olake",           // will be deleted in Phase 5; placeholder for now
  "stack-doctor",    // placeholder; the real stack is the IaC `stack-doctor` lint

  // ============================ data-engineering (12) ============================
  // All on bunchloch. The IaC deploys these second (the lakehouse data plane).
  "dagster",
  "lakehouse",
  "marimo",
  "cognee",
  "langfuse",
  "llama-swap",
  "falkordb",
  "graphiti",
  "litellm",
  "logfire",
  "lancedb",
  "qdrant",

  // ============================ agent-platform (7) ============================
  // All on bunchloch. The IaC deploys these third.
  "agent-os",
  "openclaw",        // duplicated from infrastructure; deduplicated at runtime
  "openchamber",     // duplicated from infrastructure; deduplicated at runtime
  "memgraph",
  "mlx-omni",
  "lmnr",
  "hermes",

  // ============================ language-model (6) ============================
  // All on bunchloch. The IaC deploys these fourth.
  "mlflow",
  "motherduck",
  "nimtable",
  "invokeai",
  "r2",              // will be deleted in Phase 5; placeholder for now
  "mlx-omni",        // duplicated from agent-platform; deduplicated at runtime

  // ============================ user-facing-web (6) ============================
  // All on bunchloch. The IaC deploys these fifth.
  "cianfhoghlaim",
  "ci/hf-watchdog",  // path syntax for sub-stack; cf. stacks/ci/hf-watchdog/

  // (cianfhoghlaim_dagster, cianfhoghlaim-api, cianfhoghlaim-frontend,
  // cianfhoghlaim-agent-os, cianfhoghlaim-adk-agents were phantom
  // entries — they're SERVICES within the oideachais stack,
  // not separate top-level stacks. The IaC deploys them via
  // stacks/cianfhoghlaim/pangolin.yaml's 5 service targets.)

  // ============================ ci (1) ============================
  // (ci/hf-watchdog is already counted in user-facing-web)
];

/**
 * Returns the deduplicated + sorted list of key stack names.
 */
export function getKeyStacks(): string[] {
  return [...new Set(KEY_STACKS_5_GROUP_MODEL)].sort();
}

/**
 * Returns the 5-group model (used for the 30-stack IaC plan).
 * The counts reflect the v5 post-cleanup state.
 */
export function getKeyStacksByGroup(): Record<string, string[]> {
  return {
    infrastructure: ["pangolin", "pocket-id", "komodo", "infisical", "backrest", "openclaw", "openchamber", "olake", "stack-doctor"],
    "data-engineering": ["dagster", "lakehouse", "marimo", "cognee", "langfuse", "llama-swap", "falkordb", "graphiti", "litellm", "logfire", "lancedb", "qdrant"],
    "agent-platform": ["agent-os", "openclaw", "openchamber", "memgraph", "mlx-omni", "lmnr", "hermes"],
    "language-model": ["mlflow", "motherduck", "nimtable", "invokeai", "r2", "mlx-omni"],
    "user-facing-web": ["cianfhoghlaim", "ci/hf-watchdog"],
    ci: ["ci/hf-watchdog"],
  };
}
