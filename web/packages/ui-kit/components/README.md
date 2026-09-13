# `web/packages/ui-kit/components/` — shadcn-style UI primitives

> **The Cianfhoghlaim shadcn-style UI surface — 46 leaf
> `.tsx` primitives (button, card, dialog, sidebar, etc.) plus
> a barrel `src/index.ts` that re-exports all of them.**
> Created by the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
> change (Phase A) by merging `web/packages/ui/components/`
> + `web/packages/ui/hooks/` into the consolidated
> `@cianfhoghlaim/ui-kit` package.

## Layout

```
web/packages/ui-kit/components/
├── src/
│   └── index.ts          # the barrel: re-exports all 46 primitives + cn
├── accordion.tsx         # leaf: Radix Accordion wrapper
├── alert-dialog.tsx      # leaf: Radix AlertDialog wrapper
├── alert.tsx             # leaf: styled alert
├── aspect-ratio.tsx      # leaf: Radix AspectRatio wrapper
├── avatar.tsx            # leaf: Radix Avatar wrapper
├── badge.tsx             # leaf: styled badge + variants
├── breadcrumb.tsx        # leaf: Radix Breadcrumb wrapper
├── button.tsx            # leaf: styled button + variants
├── calendar.tsx          # leaf: react-day-picker wrapper
├── card.tsx              # leaf: styled card (Header/Content/Footer)
├── carousel.tsx          # leaf: Embla Carousel wrapper
├── checkbox.tsx          # leaf: Radix Checkbox wrapper
├── collapsible.tsx       # leaf: Radix Collapsible wrapper
├── command.tsx           # leaf: cmdk wrapper (Command palette)
├── context-menu.tsx      # leaf: Radix ContextMenu wrapper
├── dialog.tsx            # leaf: Radix Dialog wrapper
├── drawer.tsx            # leaf: Vaul Drawer wrapper
├── dropdown-menu.tsx     # leaf: Radix DropdownMenu wrapper
├── form.tsx              # leaf: react-hook-form + Zod wrapper
├── hover-card.tsx        # leaf: Radix HoverCard wrapper
├── input-otp.tsx         # leaf: input-otp wrapper
├── input.tsx             # leaf: styled input
├── label.tsx             # leaf: Radix Label wrapper
├── menubar.tsx           # leaf: Radix Menubar wrapper
├── navigation-menu.tsx   # leaf: Radix NavigationMenu wrapper
├── pagination.tsx        # leaf: styled pagination
├── popover.tsx           # leaf: Radix Popover wrapper
├── progress.tsx          # leaf: Radix Progress wrapper
├── radio-group.tsx       # leaf: Radix RadioGroup wrapper
├── resizable.tsx         # leaf: react-resizable-panels wrapper
├── scroll-area.tsx       # leaf: Radix ScrollArea wrapper
├── select.tsx            # leaf: Radix Select wrapper
├── separator.tsx         # leaf: Radix Separator wrapper
├── sheet.tsx             # leaf: styled Sheet (Dialog variant)
├── sidebar.tsx           # leaf: shadcn sidebar primitive
├── skeleton.tsx          # leaf: animated skeleton loader
├── slider.tsx            # leaf: Radix Slider wrapper
├── sonner.tsx            # leaf: Sonner toast (Toaster export)
├── switch.tsx            # leaf: Radix Switch wrapper
├── table.tsx             # leaf: styled Table (Header/Body/Row/Cell)
├── tabs.tsx              # leaf: Radix Tabs wrapper
├── textarea.tsx          # leaf: styled textarea
├── toggle-group.tsx      # leaf: Radix ToggleGroup wrapper
├── toggle.tsx            # leaf: Radix Toggle wrapper
├── tooltip.tsx           # leaf: Radix Tooltip wrapper
└── utils.ts              # the `cn()` class-name helper (clsx + tailwind-merge)
```

## Import paths

All primitives are re-exported from the ui-kit root via the barrel
`src/index.ts`. Two import patterns are supported:

```ts
// Canonical (Phase A default)
import { Button, Card, cn } from "@cianfhoghlaim/ui-kit";

// Sub-module (for tree-shaking)
import { Button } from "@cianfhoghlaim/ui-kit/components";
import { Button } from "@cianfhoghlaim/ui-kit/ui";   // alias
```

## Conventions

- Every leaf component is a thin wrapper around Radix UI primitives
  (or `cmdk`, `vaul`, `react-day-picker`, `embla-carousel-react`,
  `react-hook-form`, `sonner` for the non-Radix ones).
- All variants are exposed via `cva` (class-variance-authority) and
  re-exported as `<name>Variants` (e.g. `buttonVariants`,
  `badgeVariants`, `toggleVariants`).
- All primitives accept a `className` prop forwarded to the
  underlying Radix primitive for per-app Tailwind overrides
  (see `apps/<app>/theme-overrides.ts` for the per-app convention).
- The barrel at `src/index.ts` uses **relative parent paths**
  (`../<name>`) to point to the leaf `.tsx` files in this
  directory — DO NOT introduce `./components/ui/<name>` paths here.

## Adjacent specs

- [`web-monorepo-consolidation`](../../../openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/specs/web-monorepo-consolidation/spec.md) — this directory's role in the consolidation
- [`centralized-registry`](../../../.agents/skills/centralized-registry/SKILL.md) — the model + schema registry (where `cn` lives in MODEL_REGISTRY)
- [`schema-codegen`](../../../.agents/skills/schema-codegen/SKILL.md) — the BAML → Zod → Convex → CopilotKit codegen pipeline (consumes the Convex schemas, NOT these primitives)

<!-- created: 2026-09-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase A) -->
