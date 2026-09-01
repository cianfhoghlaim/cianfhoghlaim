/**
 * Leaving Certificate — Irish resource page.
 * Route: /ga/leaving-cert/irish
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { IrishPage } from "../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/lc/irish")({
  component: IrishPage,
});
