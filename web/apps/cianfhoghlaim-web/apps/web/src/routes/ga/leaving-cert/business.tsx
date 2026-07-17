/**
 * Leaving Certificate — Business resource page.
 * Route: /ga/leaving-cert/business
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { BusinessPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/ga/leaving-cert/business")({
  component: BusinessPage,
});
