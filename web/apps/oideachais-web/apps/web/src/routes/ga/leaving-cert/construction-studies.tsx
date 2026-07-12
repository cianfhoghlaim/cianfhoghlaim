/**
 * Leaving Certificate — Construction Studies resource page.
 * Route: /ga/leaving-cert/construction-studies
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { ConstructionStudiesPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/ga/leaving-cert/construction-studies")({
  component: ConstructionStudiesPage,
});
