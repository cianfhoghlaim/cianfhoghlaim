/**
 * Leaving Certificate — Business resource page.
 * Route: /en/leaving-cert/business
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { BusinessPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/en/lc/business")({
  component: BusinessPage,
});
