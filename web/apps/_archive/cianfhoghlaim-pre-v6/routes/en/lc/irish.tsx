/**
 * Leaving Certificate — Irish resource page.
 * Route: /en/leaving-cert/irish
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { IrishPage } from "../../../components/leaving-cert/BiologyPage";

export const Route = createFileRoute("/en/lc/irish")({
  component: IrishPage,
});
