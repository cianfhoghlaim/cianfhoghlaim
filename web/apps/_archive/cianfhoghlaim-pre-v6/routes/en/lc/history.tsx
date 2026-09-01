/**
 * Leaving Certificate — History resource page.
 * Route: /en/leaving-cert/history
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { HistoryPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/en/lc/history")({
  component: HistoryPage,
});
