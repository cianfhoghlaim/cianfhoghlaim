/**
 * Leaving Certificate — History resource page.
 * Route: /ga/leaving-cert/history
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { HistoryPage } from "../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/lc/history")({
  component: HistoryPage,
});
