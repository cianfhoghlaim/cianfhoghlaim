# Storybook 8 — Design System Gallery

Per `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md` Requirement **R16**.

## What's here

```
apps/web/.storybook/
├── main.ts             # Storybook 8 + Vite-plugin config + autodocs
├── preview.ts          # Decorators (locale + theme toolbar)
└── theme.css           # ci-dark + ci-light theme variables

20 .stories.tsx files covering:
   - 12 original <Ci*> components (CiButton, CiProgressRing, CiTextbookPanel, …)
   - 2 new central-portal components (CiStageBreadcrumbs, CiLCSubjectGrid)
   - 2 map components (CiRealmMap, CiSubnationFlag)
   - 4 web components (Header, TranslationToggle, MarimoEmbed, CiPdfLibraryPanel)
```

## Activation

Storybook depends on packages that are not in the current `bun.lock`. To activate Storybook, run:

```bash
cd apps/web
bun add -D @storybook/react @storybook/react-vite @storybook/addon-essentials @storybook/addon-a11y
bun run storybook                  # opens http://localhost:6006
bun run build-storybook            # produces .storybook-static/ (static deploy)
```

The activation recipe is documented in `apps/web/package.json` `scripts.storybook` (with a hint when `storybook` is not yet installed).

## Token-driven

Every story consumes `tokens` from the central `apps/web/src/styles/tokens.css`:

| Token | Used for |
|---|---|
| `--ci-brand-primary` | Active subnation highlight |
| `--ci-subject-<slug>` | LC subject card accent |
| `--ci-stage-*` | Stage breadcrumb state (active / deferred) |
| `--ci-bg-primary` | Background |
| `--ci-font-body` | Body text |
| `--ci-font-display` | Display headings |
| `--ci-radius-md` | Card border radius |
| `--ci-spacing-5` | Card padding |

Run `bun run tokens:validate` to confirm drift-free.

## Bilingual EN/GA

The Storybook toolbar exposes `locale` (en / ga) and `theme` (ci-dark / ci-light). Stories that take `language="en" | "ga"` show both variants.

## Adding a new story

1. Write `your-component.stories.tsx` next to the component file:
   ```tsx
   import type { Meta, StoryObj } from "@storybook/react";
   import { YourComponent } from "./your-component";

   const meta: Meta<typeof YourComponent> = {
     title: "UI/YourComponent",
     component: YourComponent,
     tags: ["autodocs"],
   };
   export default meta;

   type Story = StoryObj<typeof YourComponent>;
   export const Default: Story = { args: { /* props */ } };
   ```
2. Restart `bun run storybook`.
3. Visit `http://localhost:6006/?path=/story/ui-yourcomponent--default`.

## See also

- `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md` — R16
- `apps/web/src/styles/tokens.css` — the single source of truth for design tokens
- `apps/web/packages/mcp/design-system-server.py` — the MCP server that publishes these tokens to AI agents (R23)
- `.agents/skills/storybook/SKILL.md` — canonical Storybook patterns
