/**
 * Leaving Certificate — Mathematics resource page.
 * Route: /ga/leaving-cert/mathematics
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { MathematicsPage } from "../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/lc/mathematics")({
  component: MathematicsPage,
});
