# @cianfhoghlaim/ui-kit — Radix UI + Tailwind 4

Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
openspec change. The canonical UI surface for the Cianfhoghlaim
platform. Consolidates the 3 previous Radix UI installs into one.

## Stack

- **Radix UI** (`@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`,
  `@radix-ui/react-popover`, `@radix-ui/react-tooltip`) — accessible
  primitives
- **Tailwind 4** (`tailwindcss@^4.0.0`, `@tailwindcss/postcss@^4.0.0`)
  — utility CSS
- React 19 + ReactDOM 19

## Setup

```bash
bun add @cianfhoghlaim/ui-kit
```

## Sub-surfaces

The 5 sub-package directories still exist for code organization:

- `analytics/` — analytics + telemetry
- `i18n/` — internationalization
- `components/` — Radix UI components
- `config/` — Tailwind config + theme tokens
- `hooks/` — React hooks (e.g. `useIsMobile`)

## Theme

The single Tailwind config is at
`web/packages/ui-kit/config/src/tailwind.config.ts`. The 5 web apps
extend from this — never create a per-app `tailwind.config.ts`.

## DO NOT

- **Never** create a per-app Radix UI install — extend `@cianfhoghlaim/ui-kit`
- **Never** create a per-app `tailwind.config.ts` — extend from
  `web/packages/ui-kit/config/src/tailwind.config.ts`
- **Never** copy Radix components into a per-app directory — they're
  already exported from `web/packages/ui-kit/components`
