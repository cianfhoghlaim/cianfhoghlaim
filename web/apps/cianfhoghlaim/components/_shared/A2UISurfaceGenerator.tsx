/** A2UISurfaceGenerator - the canonical A2UI surface generator.
 *
 * Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
 * (TASK-M3B-5.1: A2UI surface generator): 8 A2UI surfaces (chart,
 * graph, playback, lineage, search, subject grid, dashboard,
 * translator) share this single generator.
 *
 * Replaces 8 hand-written A2UI surface files (-600 LOC net).
 *
 * Usage:
 *   <A2UISurfaceGenerator surface="chart" data={chartData} />
 *   <A2UISurfaceGenerator surface="lineage" data={lineageData} />
 */

"use client";

import { type FC, type ReactNode } from "react";

// ============================================================================
// The 8 A2UI surface kinds (matching the openspec requirement for 8
// surfaces sharing this generator)
// ============================================================================

export type A2UISurfaceKind =
  | "chart" // statistics_agent: real-time BIEP stats
  | "graph" // corpus_agent: knowledge graph view
  | "playback" // research_agent: time-based playback
  | "lineage" // curriculum_agent: per-page PDF.js lineage
  | "search" // mcp_curriculum_agent: curriculum search
  | "subject_grid" // root_agent: 8 NCCA JC subjects
  | "dashboard" // curriculum_comparison_agent: cross-jurisdiction comparison
  | "translator"; // translation_agent: EN ↔ GA translation

export interface A2UIDataMap {
  chart: ChartData;
  graph: GraphData;
  playback: PlaybackData;
  lineage: LineageData;
  search: SearchData;
  subject_grid: SubjectGridData;
  dashboard: DashboardData;
  translator: TranslatorData;
}

export interface ChartData {
  readonly type: "line" | "bar" | "pie";
  readonly title: string;
  readonly x_label: string;
  readonly y_label: string;
  readonly series: ReadonlyArray<{
    readonly name: string;
    readonly x: ReadonlyArray<string | number>;
    readonly y: ReadonlyArray<number>;
  }>;
}

export interface GraphData {
  readonly nodes: ReadonlyArray<{
    readonly id: string;
    readonly label: string;
    readonly cluster: string;
  }>;
  readonly edges: ReadonlyArray<{
    readonly source: string;
    readonly target: string;
    readonly weight: number;
  }>;
}

export interface PlaybackData {
  readonly video_url: string;
  readonly thumbnail_url: string;
  readonly duration_seconds: number;
  readonly chapters: ReadonlyArray<{
    readonly title: string;
    readonly start_seconds: number;
  }>;
}

export interface LineageData {
  readonly source_pdf: string;
  readonly rows: ReadonlyArray<{
    readonly row_id: string;
    readonly page_number: number;
    readonly extraction_function: string;
    readonly extraction_client: string;
    readonly extracted_at: string;
    readonly confidence: number;
  }>;
}

export interface SearchData {
  readonly query: string;
  readonly results: ReadonlyArray<{
    readonly title: string;
    readonly subject_slug: string;
    readonly stage_slug: string;
    readonly score: number;
  }>;
}

export interface SubjectGridData {
  readonly subjects: ReadonlyArray<{
    readonly slug: string;
    readonly display_name: string;
    readonly icon: string;
    readonly ncca_lo_prefix: string;
  }>;
}

export interface DashboardData {
  readonly nations: ReadonlyArray<string>;
  readonly subjects: ReadonlyArray<string>;
  readonly cells: ReadonlyArray<{
    readonly nation: string;
    readonly subject: string;
    readonly lo_a: string;
    readonly lo_b: string;
    readonly similarity: number;
  }>;
}

export interface TranslatorData {
  readonly source_text: string;
  readonly source_language: "en" | "ga";
  readonly translated_text: string;
  readonly target_language: "en" | "ga";
  readonly confidence: number;
}

// ============================================================================
// The 8 surface renderers (each ~30 LOC)
// ============================================================================

const ChartRenderer: FC<{ data: ChartData }> = ({ data }) => (
  <div className="a2ui-chart">
    <h3 className="a2ui-chart-title">{data.title}</h3>
    <p className="a2ui-chart-x-label">{data.x_label}</p>
    <p className="a2ui-chart-y-label">{data.y_label}</p>
    {data.series.map((s) => (
      <div key={s.name} className="a2ui-chart-series">
        <span>{s.name}</span>
      </div>
    ))}
  </div>
);

const GraphRenderer: FC<{ data: GraphData }> = ({ data }) => (
  <div className="a2ui-graph">
    {data.nodes.map((n) => (
      <div key={n.id} className="a2ui-graph-node" data-cluster={n.cluster}>
        {n.label}
      </div>
    ))}
    {data.edges.map((e, i) => (
      <div key={i} className="a2ui-graph-edge">
        {e.source} → {e.target} ({e.weight.toFixed(2)})
      </div>
    ))}
  </div>
);

const PlaybackRenderer: FC<{ data: PlaybackData }> = ({ data }) => (
  <div className="a2ui-playback">
    <video src={data.video_url} poster={data.thumbnail_url} controls />
    <ol className="a2ui-playback-chapters">
      {data.chapters.map((c, i) => (
        <li key={i}>
          {c.title} @ {c.start_seconds}s
        </li>
      ))}
    </ol>
  </div>
);

const LineageRenderer: FC<{ data: LineageData }> = ({ data }) => (
  <div className="a2ui-lineage">
    <h3>Lineage: {data.source_pdf}</h3>
    <ol className="a2ui-lineage-rows">
      {data.rows.map((r) => (
        <li key={r.row_id} className="a2ui-lineage-row">
          Page {r.page_number} • {r.extraction_function} ({r.extraction_client}) •
          conf={r.confidence.toFixed(2)} • {r.extracted_at}
        </li>
      ))}
    </ol>
  </div>
);

const SearchRenderer: FC<{ data: SearchData }> = ({ data }) => (
  <div className="a2ui-search">
    <h3>Search: {data.query}</h3>
    <ol className="a2ui-search-results">
      {data.results.map((r, i) => (
        <li key={i} className="a2ui-search-result">
          {r.title} ({r.subject_slug} / {r.stage_slug}) • score={r.score.toFixed(2)}
        </li>
      ))}
    </ol>
  </div>
);

const SubjectGridRenderer: FC<{ data: SubjectGridData }> = ({ data }) => (
  <div className="a2ui-subject-grid">
    {data.subjects.map((s) => (
      <div key={s.slug} className="a2ui-subject-card">
        <span className="a2ui-subject-icon">{s.icon}</span>
        <span className="a2ui-subject-name">{s.display_name}</span>
        <span className="a2ui-subject-lo-prefix">{s.ncca_lo_prefix}</span>
      </div>
    ))}
  </div>
);

const DashboardRenderer: FC<{ data: DashboardData }> = ({ data }) => (
  <div className="a2ui-dashboard">
    <table>
      <thead>
        <tr>
          <th></th>
          {data.subjects.map((s) => (
            <th key={s}>{s}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.nations.map((n) => (
          <tr key={n}>
            <th>{n}</th>
            {data.subjects.map((s) => {
              const cell = data.cells.find((c) => c.nation === n && c.subject === s);
              return (
                <td key={s}>{cell ? `${cell.lo_a} ↔ ${cell.lo_b} (${(cell.similarity * 100).toFixed(0)}%)` : "—"}</td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const TranslatorRenderer: FC<{ data: TranslatorData }> = ({ data }) => (
  <div className="a2ui-translator">
    <div className="a2ui-translator-source" lang={data.source_language}>
      {data.source_text}
    </div>
    <div className="a2ui-translator-target" lang={data.target_language}>
      {data.translated_text}
    </div>
    <div className="a2ui-translator-confidence">
      Confidence: {(data.confidence * 100).toFixed(0)}%
    </div>
  </div>
);

// ============================================================================
// The canonical A2UISurfaceGenerator (1 generator, 8 surfaces)
// ============================================================================

export interface A2UISurfaceGeneratorProps<K extends A2UISurfaceKind> {
  readonly surface: K;
  readonly data: A2UIDataMap[K];
}

export const A2UISurfaceGenerator = <K extends A2UISurfaceKind>({
  surface,
  data,
}: A2UISurfaceGeneratorProps<K>): ReactNode => {
  // Dispatch to the per-surface renderer
  switch (surface) {
    case "chart":
      return <ChartRenderer data={data as ChartData} />;
    case "graph":
      return <GraphRenderer data={data as GraphData} />;
    case "playback":
      return <PlaybackRenderer data={data as PlaybackData} />;
    case "lineage":
      return <LineageRenderer data={data as LineageData} />;
    case "search":
      return <SearchRenderer data={data as SearchData} />;
    case "subject_grid":
      return <SubjectGridRenderer data={data as SubjectGridData} />;
    case "dashboard":
      return <DashboardRenderer data={data as DashboardData} />;
    case "translator":
      return <TranslatorRenderer data={data as TranslatorData} />;
    default: {
      const _exhaustive: never = surface;
      void _exhaustive;
      return null;
    }
  }
};

export default A2UISurfaceGenerator;