/**
 * Leaving Certificate — Mathematics resource page.
 * Route: /en/leaving-cert/mathematics
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { MathematicsPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/en/leaving-cert/mathematics")({
  component: MathematicsPage,
});
