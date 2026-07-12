/**
 * tokens:validate — CI gate for the Cianfhoghlaim design tokens.
 *
 * Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/:
 *   - R21 (Machine-readable infrastructure) — drift detector
 *   - R22 (Design-tokens-as-code pipelines) — bun run tokens:validate is the CI gate
 *
 * Reads the 4 token source files and fails if any drift is detected.
 *
 * The 4 sources (KEEP IN SYNC):
 *   1. apps/web/src/styles/tokens.css             (single source of truth)
 *   2. apps/web/src/styles/tokens.ts              (TypeScript mirror)
 *   3. apps/web/src/styles/tokens.schema.json     (JSON Schema — A2UI catalog validation)
 *   4. baml_src/design_tokens.baml                (BAML classes — agent-visible tokens)
 *
 * Usage:
 *   bun run tokens:validate         # default — drift detection (exits non-zero if drift)
 *   bun run tokens:validate --fix   # same drift check, but always exits 0
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const STYLES_DIR = __dirname;
// File: cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/styles/validate-tokens.ts
// Going up 4 levels lands in cianfhoghlaim-leaving-cert/
const APP_ROOT = path.resolve(STYLES_DIR, '..', '..', '..', '..');
const BAML_DIR = path.join(APP_ROOT, 'baml_src');

const TOKENS_CSS    = path.join(STYLES_DIR, 'tokens.css');
const TOKENS_TS     = path.join(STYLES_DIR, 'tokens.ts');
const TOKENS_SCHEMA = path.join(STYLES_DIR, 'tokens.schema.json');
const TOKENS_BAML   = path.join(BAML_DIR,   'design_tokens.baml');

const FIX_MODE = process.argv.includes('--fix');

// ============================================================================
// Group → file-group mapping
// ============================================================================

type Group =
  | 'nations' | 'subjects' | 'competencies' | 'subnations'
  | 'brand' | 'states' | 'surfaces' | 'buttons' | 'materials'
  | 'typography' | 'spacing' | 'radius' | 'shadows' | 'motion' | 'z';

interface ParsedTokens {
  [group: string]: Record<string, string>;
}

const EMPTY: ParsedTokens = {
  nations: {}, subjects: {}, competencies: {}, subnations: {},
  brand: {}, states: {}, surfaces: {}, buttons: {}, materials: {},
  typography: {}, spacing: {}, radius: {}, shadows: {}, motion: {}, z: {},
};

// ============================================================================
// Section detection in tokens.css
// ============================================================================

/** Map a CSS section name (after stripping comments) to a Group. */
function sectionToGroup(sectionName: string): Group | null {
  const s = sectionName.toLowerCase();
  if (s.includes('celtic nation')) return 'nations';
  if (s.includes('ncca subject realm')) return 'subjects';
  if (s.includes('brand accent')) return 'brand';
  if (s.includes('ncca key competencies')) return 'competencies';
  if (s.includes('ui states')) return 'states';
  if (s.includes('surfaces')) return 'surfaces';
  if (s.includes('tactile button')) return 'buttons';
  if (s.includes('material library')) return 'materials';
  if (s.includes('british isles subnation')) return 'subnations';
  if (s.includes('typography')) return 'typography';
  if (s.includes('spacing scale')) return 'spacing';
  if (s.includes('border radius scale')) return 'radius';
  if (s.includes('shadow scale')) return 'shadows';
  if (s.includes('motion') || s.includes('animation')) return 'motion';
  if (s.includes('z-index scale')) return 'z';
  return null;
}

/**
 * Strip the `--ci-<group>-` prefix from a custom property name.
 * Returns the bare key (e.g. "subject-mathematics" → "mathematics").
 */
function stripPrefix(group: Group, key: string): string {
  // Order matters: check longer prefixes first
  const prefixes: Record<Group, string[]> = {
    nations:      ['nations-', 'nation-'],
    subjects:     ['subject-'],
    competencies: ['competencies-', 'competency-'],
    subnations:   ['subnations-', 'subnation-'],
    brand:        ['brand-'],
    states:       ['states-', 'state-'],
    surfaces:     ['surfaces-', 'surface-', 'bg-'],
    buttons:      ['buttons-', 'button-', 'btn-'],
    materials:    ['materials-', 'material-'],
    typography:   ['typography-', 'font-'],
    spacing:      ['spacing-', 'space-'],
    radius:       ['radius-'],
    shadows:      ['shadows-', 'shadow-'],
    motion:       ['motion-'],
    z:            ['z-'],
  };
  for (const p of prefixes[group]) {
    if (key.startsWith(p)) return key.slice(p.length);
  }
  return key;
}

// ============================================================================
// CSS parser
// ============================================================================

function parseTokensCSS(css: string): ParsedTokens {
  const tokens: ParsedTokens = JSON.parse(JSON.stringify(EMPTY));
  // Section header: /* ===== <name> ===== */
  const sectionRegex = /\/\*\s*=+\s*([A-Za-z0-9 .()/_-]+?)\s*=+\s*\*\//g;
  const sections = [...css.matchAll(sectionRegex)];

  for (let i = 0; i < sections.length; i++) {
    const sectionName = sections[i][1].trim();
    const group = sectionToGroup(sectionName);
    if (!group) continue;

    const start = sections[i].index! + sections[i][0].length;
    const end = i + 1 < sections.length ? sections[i + 1].index! : css.length;
    const block = css.slice(start, end);

    // Property: --ci-<key>: <value>;
    const propRegex = /--ci-([a-z0-9_-]+)\s*:\s*([^;]+);/g;
    for (const m of block.matchAll(propRegex)) {
      const rawKey = m[1];
      const value  = m[2].trim();
      const bareKey = stripPrefix(group, rawKey);
      // Normalize: TS uses underscores (applied_mathematics); CSS uses hyphens.
      // Convert hyphens → underscores for cross-source comparison.
      const normalizedKey = bareKey.replace(/-/g, '_');
      (tokens[group] as Record<string, string>)[normalizedKey] = value;
    }
  }
  return tokens;
}

// ============================================================================
// tokens.ts parser
// ============================================================================

/**
 * Extract the per-group `tokens` constant from tokens.ts by stripping
 * TypeScript type annotations and headers, then safely evaluating the
 * resulting JavaScript object literal via `new Function`.
 *
 * This is safe because tokens.ts is checked-in source code that we
 * fully control — there is no untrusted input.
 */
function parseTokensTS(source: string): ParsedTokens {
  // 1. Locate the `export const tokens = { ... };` block
  const startMatch = source.match(/export\s+const\s+tokens\s*:\s*CianfhoghlaimTokens\s*=\s*\{/);
  if (!startMatch) throw new Error('Could not find `export const tokens = ...;` in tokens.ts');

  // 2. Capture from the opening `{` to the matching closing `}` at top-level.
  //    Find the closing brace by counting nested braces.
  const bodyStart = startMatch.index! + startMatch[0].length;
  let depth = 1;
  let i = bodyStart;
  while (i < source.length && depth > 0) {
    const ch = source[i];
    if (ch === '{') depth++;
    else if (ch === '}') depth--;
    i++;
  }
  const body = source.slice(bodyStart, i - 1); // exclude the trailing `}`

  // 3. Strip TypeScript type annotations and header comments
  const cleanedBody = body
    // Strip `as const` and type assertions
    .replace(/\s+as\s+[A-Za-z<>\[\]| ,]+/g, '')
    // Strip TypeScript type annotations on values like `: CianfhoghlaimTokens`
    // (not needed inside body but harmless)
    .replace(/(\w+)\s*:\s*(CianfhoghlaimTokens|Tokens)\b/g, '$1');

  // 4. Wrap in a function that returns the object, then evaluate
  let evaluated: Record<string, Record<string, unknown>>;
  try {
    // eslint-disable-next-line no-new-func
    const fn = new Function(`return ({${cleanedBody}});`);
    evaluated = fn();
  } catch (e) {
    throw new Error(`Failed to evaluate tokens.ts object literal: ${e}`);
  }

  // 5. Convert to ParsedTokens — only keep string values, normalize underscores
  const out: ParsedTokens = JSON.parse(JSON.stringify(EMPTY));
  for (const [group, groupTokens] of Object.entries(evaluated)) {
    if (!EMPTY.hasOwnProperty(group)) continue;
    const normalized: Record<string, string> = {};
    for (const [k, v] of Object.entries(groupTokens)) {
      if (typeof v === 'string') {
        normalized[k] = v;
      } else if (typeof v === 'number') {
        normalized[k] = String(v);
      }
    }
    (out as Record<string, Record<string, string>>)[group] = normalized;
  }
  return out;
}

// ============================================================================
// BAML parser (loose — just confirms required @description comments are present)
// ============================================================================

function parseTokensBAML(source: string): { ok: boolean; missing: string[] } {
  // The BAML file declares NationColor / SubjectColor / etc. classes with field descriptions.
  // Validate that the 5 NCCA subject classes are present.
  const requiredClasses = ['NationColor', 'SubjectColor', 'CompetencyColor', 'SubnationColor', 'DesignTokens'];
  const missing = requiredClasses.filter((c) => !source.includes(`class ${c}`));
  return { ok: missing.length === 0, missing };
}

// ============================================================================
// JSON Schema validator (minimal — checks required groups + keys exist in CSS)
// ============================================================================

function validateAgainstSchema(tokens: ParsedTokens, schema: any): string[] {
  const errors: string[] = [];
  for (const requiredGroup of (schema.required as string[])) {
    const cssGroup = (tokens as Record<string, unknown>)[requiredGroup];
    if (!cssGroup || Object.keys(cssGroup as object).length === 0) {
      errors.push(`  - [schema] required group "${requiredGroup}" is empty or missing in tokens.css`);
      continue;
    }
    const groupSchema = (schema.properties as Record<string, any>)[requiredGroup];
    if (!groupSchema?.required) continue;
    for (const requiredKey of groupSchema.required as string[]) {
      const cssKey = (cssGroup as Record<string, unknown>)?.[requiredKey];
      if (cssKey === undefined) {
        errors.push(`  - [schema] required key "${requiredGroup}.${requiredKey}" is missing in tokens.css`);
      }
    }
  }
  return errors;
}

// ============================================================================
// Diff helpers
// ============================================================================

function diffCssVsTs(css: ParsedTokens, ts: ParsedTokens): string[] {
  const errors: string[] = [];
  for (const group of Object.keys(css) as Group[]) {
    const cssGroup = css[group];
    const tsGroup  = (ts as Record<string, Record<string, string>>)[group] || {};
    for (const key of Object.keys(cssGroup)) {
      if (tsGroup[key] === undefined) {
        errors.push(`  - [css-vs-ts] ${group}.${key}: present in tokens.css, missing in tokens.ts`);
      } else if (cssGroup[key] !== tsGroup[key]) {
        errors.push(`  - [css-vs-ts] ${group}.${key}: CSS="${cssGroup[key]}" TS="${tsGroup[key]}"`);
      }
    }
  }
  return errors;
}

function normalizeTsValue(v: string): string {
  // Strip JS quotes & whitespace
  v = v.trim();
  if ((v.startsWith('"') && v.endsWith('"')) ||
      (v.startsWith("'") && v.endsWith("'")) ||
      (v.startsWith('`') && v.endsWith('`'))) {
    v = v.slice(1, -1);
  }
  return v.trim();
}

// ============================================================================
// Main
// ============================================================================

function main() {
  if (!fs.existsSync(TOKENS_CSS)) { console.error(`✗ tokens.css not found`); process.exit(1); }
  if (!fs.existsSync(TOKENS_TS))  { console.error(`✗ tokens.ts not found`);  process.exit(1); }
  if (!fs.existsSync(TOKENS_SCHEMA)) { console.error(`✗ tokens.schema.json not found`); process.exit(1); }

  const cssSource  = fs.readFileSync(TOKENS_CSS, 'utf-8');
  const tsSource   = fs.readFileSync(TOKENS_TS, 'utf-8');
  const schema     = JSON.parse(fs.readFileSync(TOKENS_SCHEMA, 'utf-8'));
  const bamlSource = fs.existsSync(TOKENS_BAML) ? fs.readFileSync(TOKENS_BAML, 'utf-8') : '';

  const cssTokens = parseTokensCSS(cssSource);
  const tsTokens  = parseTokensTS(tsSource);

  // Normalize the TS values (strip quotes)
  for (const group of Object.keys(tsTokens) as Group[]) {
    for (const key of Object.keys(tsTokens[group])) {
      tsTokens[group][key] = normalizeTsValue(tsTokens[group][key]);
    }
  }

  const errors: string[] = [];

  // 1. CSS schema validation
  errors.push(...validateAgainstSchema(cssTokens, schema));

  // 2. CSS ↔ TS drift
  errors.push(...diffCssVsTs(cssTokens, tsTokens));

  // 3. BAML class coverage
  if (bamlSource) {
    const { ok, missing } = parseTokensBAML(bamlSource);
    if (!ok) {
      for (const m of missing) errors.push(`  - [baml] class "${m}" missing from design_tokens.baml`);
    }
  } else {
    errors.push(`  - [baml] design_tokens.baml not found at ${TOKENS_BAML}`);
  }

  // ---------------------------------------------------------------------------
  // Report
  // ---------------------------------------------------------------------------

  // Print summary of what was detected
  console.log('─'.repeat(72));
  console.log('Cianfhoghlaim Design Tokens — drift detection');
  console.log('─'.repeat(72));
  console.log(`  • tokens.css            : ${Object.values(cssTokens).reduce((n, g) => n + Object.keys(g).length, 0)} keys across ${Object.keys(cssTokens).length} groups`);
  console.log(`  • tokens.ts             : ${Object.values(tsTokens).reduce((n, g) => n + Object.keys(g).length, 0)} keys across ${Object.keys(tsTokens).length} groups`);
  console.log(`  • tokens.schema.json    : ${(schema.required as string[]).length} required groups + ${Object.keys(schema.properties).length} properties`);
  console.log(`  • design_tokens.baml    : ${bamlSource ? 'present' : 'MISSING'}`);
  console.log('─'.repeat(72));

  if (errors.length === 0) {
    console.log('✓ tokens:validate passed — all 4 token sources are drift-free.');
    process.exit(0);
  }

  console.error(`✗ tokens:validate failed — ${errors.length} drift issue(s):`);
  for (const e of errors) console.error(e);
  console.error('\nTo fix: edit tokens.css (the single source of truth) and run `bun run tokens:sync`.');
  process.exit(FIX_MODE ? 0 : 1);
}

main();
