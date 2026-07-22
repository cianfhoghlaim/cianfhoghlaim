/**
 * Leaving Certificate — Biology resource page.
 * Route: /en/leaving-cert/biology
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { BiologyPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/en/leaving-cert/biology")({
  component: BiologyPage,
});
