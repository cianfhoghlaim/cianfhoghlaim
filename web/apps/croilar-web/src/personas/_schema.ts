import { z } from "zod";

export const THEME_MODES = ["dark", "light"] as const;
export type ThemeMode = (typeof THEME_MODES)[number];

const RouteItem = z.object({
  path: z.string(),
  label: z.object({ en: z.string(), ga: z.string() }),
  icon: z.string(),
  loader: z.string(),
});

export const DataSource = z.enum([
  "spotify", "soundcloud", "youtube", "github",
  "cv_pdfs", "teaching_pdfs", "identity_docs",
  "ducklake_oideachais", "ducklake_meaisinfhoghlaim",
]);

export const Persona = z.object({
  id: z.string(),
  slug: z.string(),
  i18n: z.object({ en: z.string(), ga: z.string() }),
  theme: z.object({
    mode: z.enum(THEME_MODES),
    accent: z.string(),
    palette: z.record(z.string(), z.string()),
  }),
  routes: z.array(RouteItem).min(1),
  dataSources: z.array(DataSource).min(1),
  featureFlags: z.object({
    cv: z.boolean(),
    data: z.boolean(),
    identity: z.boolean(),
    contact: z.boolean(),
  }),
  dagsterAssetGroup: z.string(),
  bamlSchemas: z.array(z.string()),
});

export type Persona = z.infer<typeof Persona>;
export type RouteItem = z.infer<typeof RouteItem>;
export type DataSource = z.infer<typeof DataSource>;

export const THEME_CSS = {
  aleyum: `
    color-scheme: dark;
    --color-accent: oklch(0.74 0.18 285);
    --color-primary: oklch(0.65 0.18 285);
    --color-background: oklch(0.13 0.02 285);
    --color-foreground: oklch(0.92 0.01 285);
    --color-muted: oklch(0.25 0.02 285);
    --color-border: oklch(0.28 0.02 285);
    --color-card: oklch(0.16 0.02 285);
  `,
  cianfhoghlaim: `
    color-scheme: light;
    --color-accent: oklch(0.62 0.16 145);
    --color-primary: oklch(0.55 0.16 145);
    --color-background: oklch(0.97 0.01 145);
    --color-foreground: oklch(0.15 0.02 145);
    --color-muted: oklch(0.88 0.02 145);
    --color-border: oklch(0.83 0.02 145);
    --color-card: oklch(0.94 0.01 145);
  `,
} as const;

export function getThemeCss(slug: string): string {
  return THEME_CSS[slug as keyof typeof THEME_CSS] ?? THEME_CSS.aleyum;
}
