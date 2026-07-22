// apps/web/.storybook/main.ts
//
// Storybook 8 + Vite-plugin config for the Cianfhoghlaim Leaving Cert app.
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/ R16.
//
// To activate:
//   cd apps/web
//   bun add -D @storybook/react @storybook/react-vite @storybook/addon-essentials
//   bun run storybook    # opens http://localhost:6006
//
// Stories are loaded from:
//   - apps/web/src/**/*.stories.{ts,tsx}
//   - apps/web/src/components/**/*.stories.{ts,tsx}
//   - packages/ui/src/**/*.stories.{ts,tsx}

import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: [
    "../src/**/*.stories.@(ts|tsx)",
    "../src/components/**/*.stories.@(ts|tsx)",
    "../../packages/ui/src/**/*.stories.@(ts|tsx)",
    "../../packages/lineage/**/*.stories.@(ts|tsx)",
  ],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-a11y",
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  docs: {
    autodocs: "tag",
  },
  viteFinal: (config) => {
    // Inherit the app's Vite config (Tailwind 4 + tsconfig-paths)
    return config;
  },
  core: {
    disableTelemetry: true,
  },
};

export default config;
