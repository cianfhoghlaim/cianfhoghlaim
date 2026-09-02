// /ga/leaving-cert/{gaSlug}/lineage — GA mirror of the CocoInsight-style document-lineage viewer.
//
// The `$subject` param accepts the GA slugs (mata / ceimic / tireolaiocht /
// gaeilge / bearla / riomheolaiocht). For invalid subjects, the route renders
// the canonical 404 UI.
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R26 + R29 + R30 + R31 + R32 + R33.

import * as React from "react";
import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { BIEPNavigationRail } from "../../../src/components/BIEPNavigationRail";
import {
  resolveLineageSubject,
  getLineageLabels,
} from "../../../src/lib/lineage-routes";
import { LineageViewer } from "../../../../../packages/ui-kit/components/lineage/LineageViewer";
import type { LineageRow } from "../../../../../packages/ui-kit/components/lineage/types";

export const Route = createFileRoute("/lc/gaeilge/ga-$subject-lineage")({
  component: LineagePageGA,
  loader: async ({ params }) => {
    const resolved = resolveLineageSubject(params.subject, "ga");
    if (!resolved || !resolved.subject) {
      throw notFound();
    }
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
      // best-effort
    }
    return { resolved, rows };
  },
});

function LineagePageGA() {
  const { resolved, rows } = Route.useLoaderData();
  if (!resolved.subject) return null;
  const labels = getLineageLabels("ga");

  return (
    <div className="flex flex-col gap-4 max-w-7xl mx-auto p-6" lang="ga">
      <header className="flex flex-col gap-2 border-b border-slate-800 pb-4">
        <div className="text-sm text-slate-500 font-mono">
          BIEP v1 · {resolved.subject.code} · NCCA LC {resolved.subject.level.toUpperCase()}
        </div>
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          {resolved.subject.name_ga} · {labels.page_heading}
        </h1>
        <p className="text-slate-400 text-sm">{labels.blurb}</p>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-500">
          <Link
            to={`/ga/subjects/${resolved.ga_slug}` as never}
            className="underline hover:opacity-80"
            style={{ color: resolved.subject.color }}
          >
            ← Leathanach an ábhair
          </Link>
          <Link
            to={`/en/leaving-cert/${resolved.en_slug}/lineage` as never}
            className="underline hover:opacity-80 text-slate-400"
          >
            View in English →
          </Link>
        </div>
      </header>

      <BIEPNavigationRail
        subject={resolved.en_slug}
        active="lineage"
        language="ga"
      />

      <LineageViewer
        subject={resolved.subject}
        language="ga"
        rows={rows}
        labels={labels}
      />
    </div>
  );
}
