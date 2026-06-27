#!/usr/bin/env bun
// _ccc-deprecation-banner.ts — print a deprecation warning to stderr
// when the legacy `ccc search` CLI is invoked. The v1 replacement is
// `ccc:v1:search` (a v1 CocoIndex App). The legacy CLI is scheduled
// for hard removal on 2026-07-15; see
// `sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md`.
//
// This is intentionally a tiny, dependency-free shim so it can run
// from any context (including a bare `bun run ccc:search` invocation
// with no venv active).
const msg = [
  "",
  "  \x1b[33m⚠  DEPRECATION WARNING\x1b[0m",
  "  \x1b[33m━\x1b[0m━━━━━━━━━━━━━━━━━━━━━",
  "  The \x1b[1mccc search\x1b[0m CLI is deprecated.",
  "  Switch to: \x1b[1mbun run ccc:v1:search <query>\x1b[0m",
  "  Hard removal scheduled: \x1b[1m2026-07-15\x1b[0m",
  "  See: sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md",
  "",
].join("\n");

if (process.env.NO_COLOR) {
  process.stderr.write(msg.replace(/\x1b\[[0-9;]*m/g, ""));
} else {
  process.stderr.write(msg);
}
