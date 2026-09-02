/**
 * Leaving Certificate — Biology resource page.
 * Route: /ga/leaving-cert/biology
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { BiologyPage } from "../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/lc/biology")({
  component: BiologyPage,
});
