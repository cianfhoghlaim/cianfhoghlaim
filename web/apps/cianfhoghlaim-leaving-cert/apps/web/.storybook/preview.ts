// apps/web/.storybook/preview.ts — storybook preview config
//
// Wraps every story in a TanStack-Router context + a Cianfhoghlaim theme
// provider (dark by default; can be flipped to light via the toolbar).
// Bilingual EN/GA labels are surfaced via the `locale` global decorator.

import type { Preview } from "@storybook/react";
import { initialize } from "@storybook/react-vite";
import React from "react";
import { CiTranslationToggle } from "../src/components/TranslationToggle";
import "./theme.css";

initialize();

const preview: Preview = {
  // Default to dark mode (per the Cianfhoghlaim professional + minimal
  // theming from UI_INSPIRATION_GUIDE.md). Light mode is selectable
  // via the Storybook toolbar addon.
  parameters: {
    backgrounds: {
      default: "ci-dark",
      values: [
        { name: "ci-dark", value: "var(--ci-bg-primary)" },
        { name: "ci-light", value: "#f8fafc" },
      ],
    },
    layout: "centered",
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  globalTypes: {
    locale: {
      name: "Locale",
      description: "Bilingual locale for EN/GA label sets",
      defaultValue: "en",
      toolbar: {
        icon: "globe",
        items: [
          { value: "en", title: "English (EN)" },
          { value: "ga", title: "Gaeilge (GA)" },
        ],
        dynamicTitle: true,
      },
    },
    theme: {
      name: "Theme",
      description: "Cianfhoghlaim dark/light theme",
      defaultValue: "ci-dark",
      toolbar: {
        icon: "circlehollow",
        items: [
          { value: "ci-dark", title: "Dark (default)" },
          { value: "ci-light", title: "Light" },
        ],
        dynamicTitle: true,
      },
    },
  },
  decorators: [
    (Story, context) => {
      const locale = (context.globals.locale as "en" | "ga") ?? "en";
      const theme = (context.globals.theme as "ci-dark" | "ci-light") ?? "ci-dark";
      return (
        <div
          data-locale={locale}
          data-theme={theme}
          className={theme === "ci-dark" ? "dark" : "light"}
          style={{
            padding: "2rem",
            minHeight: "100vh",
            background: theme === "ci-dark" ? "var(--ci-bg-primary)" : "#f8fafc",
            color: theme === "ci-dark" ? "#f1f5f9" : "#0f172a",
            fontFamily: "var(--ci-font-body)",
          }}
        >
          <div className="mb-4 flex items-center gap-3">
            <CiTranslationToggle currentLocale={locale} />
            <span className="font-mono text-[10px] uppercase tracking-wide opacity-70">
              locale={locale} · theme={theme}
            </span>
          </div>
          <Story />
        </div>
      );
    },
  ],
};

export default preview;
