// /en/leaving-cert/{subject}/lineage — CocoInsight-style document-lineage viewer.
//
// Mounts the `<LineageViewer>` shell for the 6 BIEP v1 LC subjects.
// The `$subject` param accepts the EN slugs (mathematics / chemistry /
// geography / gaeilge / english / computer_science). For invalid subjects,
// the route renders the canonical 404 UI.
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R26 + R29 + R30 + R31 + R32 + R33.

import * as React from "react";
import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { BIEPNavigationRail } from "../../../../../components/BIEPNavigationRail";
import {
  resolveLineageSubject,
  getLineageLabels,
} from "../../../../../lib/lineage-routes";
import { LineageViewer } from "../../../../../packages/lineage/LineageViewer";
import type { LineageRow } from "../../../../../packages/lineage/types";

export const Route = createFileRoute("/en/leaving-cert/$subject/lineage")({
  component: LineagePageEN,
  loader: async ({ params }) => {
    const resolved = resolveLineageSubject(params.subject, "en");
    if (!resolved || !resolved.subject) {
      throw notFound();
    }
    // Fetch lineage rows from the Hono oRPC endpoint (R30 + R31).
    // In dev mode the Hono API runs on port 8787; in production it is
    // reached via the `/api` reverse proxy. The endpoint is best-effort
    // — failure returns an empty array + a non-fatal warning.
    const apiBase =
      typeof window === "undefined"
        ? (process.env.HONO_API_BASE ?? "http://localhost:8787")
        : "/api";
    let rows: LineageRow[] = [];
    try {
      const res = await fetch(`${apiBase}/lineage/${resolved.en_slug}`);
      if (res.ok) {
        const json = (await res.json()) as { rows: LineageRow[] };
        rows = json.rows ?? [];
      }
    } catch {
      // best-effort; render with empty rows so the UI still mounts
    }
    return { resolved, rows };
  },
});

function LineagePageEN() {
  const { resolved, rows } = Route.useLoaderData();
  if (!resolved.subject) return null;
  const labels = getLineageLabels("en");

  return (
    <div className="flex flex-col gap-4 max-w-7xl mx-auto p-6">
      <header className="flex flex-col gap-2 border-b border-slate-800 pb-4">
        <div className="text-sm text-slate-500 font-mono">
          BIEP v1 · {resolved.subject.code} · NCCA LC {resolved.subject.level.toUpperCase()}
        </div>
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          {resolved.subject.name} · {labels.page_heading}
        </h1>
        <p className="text-slate-400 text-sm">{labels.blurb}</p>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-500">
          <Link
            to={`/en/subjects/${resolved.en_slug}` as never}
            className="underline hover:opacity-80"
            style={{ color: resolved.subject.color }}
          >
            ← Per-subject landing
          </Link>
          <Link
            to={`/ga/leaving-cert/${resolved.ga_slug}/lineage` as never}
            className="underline hover:opacity-80 text-slate-400"
          >
            Léigh i nGaeilge →
          </Link>
        </div>
      </header>

      <BIEPNavigationRail
        subject={resolved.en_slug}
        active="lineage"
        language="en"
      />

      <LineageViewer
        subject={resolved.subject}
        language="en"
        rows={rows}
        labels={labels}
      />
    </div>
  );
}
