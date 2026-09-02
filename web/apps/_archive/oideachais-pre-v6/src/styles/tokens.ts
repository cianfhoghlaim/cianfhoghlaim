/**
 * Cianfhoghlaim Design Tokens — TypeScript types.
 *
 * Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/:
 *   - R21 (Machine-readable infrastructure) — TypeScript mirror of tokens.css
 *   - R22 (Design-tokens-as-code pipelines) — companion to tokens.css
 *
 * The CI gate `bun run tokens:validate` confirms this file stays in sync
 * with the corresponding CSS custom properties, the BAML classes, and
 * the JSON Schema.
 *
 * DO NOT edit values here — edit tokens.css and run `bun run tokens:sync`.
 */

export type HexColor = `#${string}`;
export type RgbaColor = `rgba(${string})`;

/** Celtic nation colours (4 ancient nations) */
export interface NationTokens {
  irish: HexColor;
  scottish: HexColor;
  welsh: HexColor;
  breton: HexColor;
}

/** 8 NCCA subject realm colours */
export interface SubjectTokens {
  mathematics: HexColor;
  applied_mathematics: HexColor;
  chemistry: HexColor;
  geography: HexColor;
  history: HexColor;
  english: HexColor;
  gaeilge: HexColor;
  computer_science: HexColor;
}

/** 5 NCCA Key Competencies (the 5 land-marks) */
export interface CompetencyTokens {
  communicating: HexColor;
  information: HexColor;
  creative_thinking: HexColor;
  personal_effective: HexColor;
  working_with_others: HexColor;
}

/** 6 British Isles subnation colours (accurate map) */
export interface SubnationTokens {
  eire: HexColor;
  northern_ireland: HexColor;
  scotland: HexColor;
  england: HexColor;
  wales: HexColor;
  isle_of_man: HexColor;
}

/** UI states */
export interface StateTokens {
  success: HexColor;
  warning: HexColor;
  error: HexColor;
  info: HexColor;
}

/** Surfaces */
export interface SurfaceTokens {
  primary: HexColor;
  secondary: HexColor;
  tertiary: HexColor;
  glass: RgbaColor;
}

/** Brand */
export interface BrandTokens {
  primary: HexColor;
  secondary: HexColor;
}

/** Tactile button depth */
export interface ButtonTokens {
  border_bottom: string;
  border_bottom_active: string;
  shadow: string;
  shadow_active: string;
}

/** Material library (URL references) */
export interface MaterialTokens {
  parchment: string;
  slate: string;
  ink_wash: string;
  gold_leaf: string;
  knotwork: string;
}

/** Typography */
export interface TypographyTokens {
  display: string;
  body: string;
  mono: string;
}

/** Spacing scale (4px base) */
export interface SpacingTokens {
  '1': string;
  '2': string;
  '3': string;
  '4': string;
  '5': string;
  '6': string;
  '7': string;
  '8': string;
}

/** Border radius scale */
export interface RadiusTokens {
  sm: string;
  md: string;
  lg: string;
  xl: string;
  full: string;
}

/** Shadow scale */
export interface ShadowTokens {
  sm: string;
  md: string;
  lg: string;
  xl: string;
}

/** Motion / animation */
export interface MotionTokens {
  fast: string;
  base: string;
  slow: string;
  standard_ease: string;
  emphasized_ease: string;
}

/** Z-index scale */
export interface ZIndexTokens {
  base: number;
  dropdown: number;
  sticky: number;
  overlay: number;
  modal: number;
  popover: number;
  toast: number;
}

/** Lineage viewer (CocoInsight click-to-highlight)
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1 R32.
 * The `dim` value is an opacity (0..1), not a color. */
export interface LineageTokens {
  /** Purple — the clicked element. */
  selected: HexColor;
  /** Blue — direct upstream dependencies of the clicked element. */
  upstream: HexColor;
  /** Green — direct downstream consumers of the clicked element. */
  downstream: HexColor;
  /** Opacity 0..1 — unrelated fields/nodes render at this opacity. */
  dim: number;
}

/**
 * The complete Cianfhoghlaim design token set.
 *
 * Every <Ci*> component + A2UI catalog entry + Storybook story + marimo
 * notebook cell MUST consume tokens via these typed accessors (never
 * hardcode a hex / px value).
 */
export interface CianfhoghlaimTokens {
  nations: NationTokens;
  subjects: SubjectTokens;
  competencies: CompetencyTokens;
  subnations: SubnationTokens;
  brand: BrandTokens;
  states: StateTokens;
  surfaces: SurfaceTokens;
  buttons: ButtonTokens;
  materials: MaterialTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  radius: RadiusTokens;
  shadows: ShadowTokens;
  motion: MotionTokens;
  z: ZIndexTokens;
  /** R32 — CocoInsight click-to-highlight state colors. */
  lineage: LineageTokens;
}

/**
 * The reference token set — extracted from tokens.css.
 *
 * This object is the single source of truth at the TypeScript layer.
 * Run `bun run tokens:sync` to regenerate it from tokens.css.
 */
export const tokens: CianfhoghlaimTokens = {
  nations: {
    irish: '#059669',
    scottish: '#2563eb',
    welsh: '#dc2626',
    breton: '#9333ea',
  },
  subjects: {
    mathematics: '#2563eb',
    applied_mathematics: '#7c3aed',
    chemistry: '#16a34a',
    geography: '#ca8a04',
    history: '#b91c1c',
    english: '#ea580c',
    gaeilge: '#059669',
    computer_science: '#475569',
  },
  competencies: {
    communicating: '#059669',
    information: '#2563eb',
    creative_thinking: '#ca8a04',
    personal_effective: '#92400e',
    working_with_others: '#b91c1c',
  },
  subnations: {
    eire: '#059669',
    northern_ireland: '#2563eb',
    scotland: '#0ea5e9',
    england: '#dc2626',
    wales: '#b91c1c',
    isle_of_man: '#475569',
  },
  brand: {
    primary: '#059669',
    secondary: '#2563eb',
  },
  states: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#f43f5e',
    info: '#0ea5e9',
  },
  surfaces: {
    primary: '#0f172a',
    secondary: '#1e293b',
    tertiary: '#334155',
    glass: 'rgba(30, 41, 59, 0.9)',
  },
  buttons: {
    border_bottom: '4px',
    border_bottom_active: '2px',
    shadow: '0 4px 0 0 rgba(0, 0, 0, 0.3)',
    shadow_active: '0 2px 0 0 rgba(0, 0, 0, 0.3)',
  },
  materials: {
    parchment: "url('/cdn/materials/parchment.webp')",
    slate: "url('/cdn/materials/slate.webp')",
    ink_wash: "url('/cdn/materials/ink-wash.webp')",
    gold_leaf: "url('/cdn/materials/gold-leaf.webp')",
    knotwork: "url('/cdn/materials/insular-knotwork.svg')",
  },
  typography: {
    display: '"Cinzel", serif',
    body: '"Inter", sans-serif',
    mono: '"JetBrains Mono", monospace',
  },
  spacing: {
    '1': '4px',
    '2': '8px',
    '3': '12px',
    '4': '16px',
    '5': '24px',
    '6': '32px',
    '7': '48px',
    '8': '64px',
  },
  radius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
  },
  motion: {
    fast: '150ms',
    base: '300ms',
    slow: '600ms',
    standard_ease: 'cubic-bezier(0.2, 0, 0.2, 1)',
    emphasized_ease: 'cubic-bezier(0.3, 0, 0, 1)',
  },
  z: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    overlay: 1200,
    modal: 1300,
    popover: 1400,
    toast: 1500,
  },
  lineage: {
    selected: '#7c3aed',
    upstream: '#2563eb',
    downstream: '#16a34a',
    dim: 0.4,
  },
};

/**
 * Token accessor helpers — preferred over hardcoded values.
 *
 *   const accentColor = tokenColor('subjects', 'gaeilge');    // → '#059669'
 *   const cardPadding = tokenValue('spacing', '5');            // → '24px'
 */
export function tokenColor<K extends keyof Pick<CianfhoghlaimTokens, 'nations' | 'subjects' | 'competencies' | 'subnations' | 'brand' | 'states' | 'surfaces'>>(
  group: K,
  key: keyof CianfhoghlaimTokens[K],
): string {
  const groupTokens = tokens[group] as Record<string, string>;
  return groupTokens[key as string];
}

export function tokenValue<K extends keyof Pick<CianfhoghlaimTokens, 'spacing' | 'radius' | 'motion'>>(
  group: K,
  key: keyof CianfhoghlaimTokens[K],
): string {
  const groupTokens = tokens[group] as Record<string, string>;
  return groupTokens[key as string];
}
