/**
 * Leaving Certificate — French resource page.
 * Route: /en/leaving-cert/french
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { FrenchPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/en/lc/french")({
  component: FrenchPage,
});
