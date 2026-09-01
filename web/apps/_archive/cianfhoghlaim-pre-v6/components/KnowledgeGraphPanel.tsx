/** KnowledgeGraphPanel - The Cognee 7-cluster knowledge graph panel.
 *
 * Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
 * (Phase 10 - the central Cianfhoghlaim homepage).
 *
 * Surfaces the Cognee 7-cluster knowledge graph (per the
 * centralized-schema-registry spec) as a navigable entity-relationship
 * visualization. The 7 clusters are:
 *   1. Aistear (Early Childhood)
 *   2. Primary
 *   3. Junior Cycle
 *   4. Senior Cycle (LC)
 *   5. University
 *   6. Memory (the cross-subject competency backbone)
 *   7. Activity (the cross-stage usage patterns)
 *
 * Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: the
 * knowledge graph is now rendered via the canonical `GraphSurface`
 * (the A2UI surface generator wrapper from `a2ui/GraphSurface.tsx`).
 */

"use client";

import { type FC, useState } from "react";
import { GraphSurface } from "./a2ui/GraphSurface";

export interface KnowledgeGraphNode {
  /** The cluster ID (aistear | primary | jc | lc | uni | memory | activity) */
  readonly id: string;
  /** The display name */
  readonly name: string;
  /** The human-readable description */
  readonly description: string;
  /** The stage (aistear | primary | jc | sc | uni | cross | cross) */
  readonly stage: string;
  /** The entity count in this cluster */
  readonly entity_count: number;
  /** The relationship count from this cluster */
  readonly relationship_count: number;
  /** The canonical BAAI/bge-m3 1024-d embedding */
  readonly centroid_embedding_id: string;
  /** The per-subject agent that queries this cluster (Phase 8) */
  readonly queryable_by: ReadonlyArray<string>;
}

export interface KnowledgeGraphPanelProps {
  /** The 7 Cognee clusters (consumed from the Phase 4 BAML + Phase 5 DLT) */
  readonly clusters?: ReadonlyArray<KnowledgeGraphNode>;
  /** Whether to show the cluster details (default: true) */
  readonly verbose?: boolean;
}

const DEFAULT_CLUSTERS: ReadonlyArray<KnowledgeGraphNode> = [
  {
    id: "aistear",
    name: "Aistear (Early Childhood)",
    description: "Irish early childhood education framework (ages 0-6)",
    stage: "aistear",
    entity_count: 24,
    relationship_count: 38,
    centroid_embedding_id: "centroid:aistear:v1",
    queryable_by: ["aistear_agent"],
  },
  {
    id: "primary",
    name: "Primary (Bunscoil)",
    description: "Irish primary education framework (ages 4-12)",
    stage: "primary",
    entity_count: 142,
    relationship_count: 256,
    centroid_embedding_id: "centroid:primary:v1",
    queryable_by: ["primary_subject_agents"],
  },
  {
    id: "jc",
    name: "Junior Cycle (Iar-Bhunscoil)",
    description: "NCCA Junior Cycle framework (ages 12-15)",
    stage: "jc",
    entity_count: 512,
    relationship_count: 1248,
    centroid_embedding_id: "centroid:jc:v1",
    queryable_by: ["8_jc_subject_agents"],
  },
  {
    id: "lc",
    name: "Senior Cycle (Leaving Certificate)",
    description: "NCCA Leaving Certificate framework (ages 15-18) - the flagship",
    stage: "sc",
    entity_count: 2048,
    relationship_count: 5680,
    centroid_embedding_id: "centroid:lc:v1",
    queryable_by: ["14_lc_subject_agents"],
  },
  {
    id: "uni",
    name: "University",
    description: "NUI / HEI matriculation framework (post-LC)",
    stage: "uni",
    entity_count: 86,
    relationship_count: 124,
    centroid_embedding_id: "centroid:uni:v1",
    queryable_by: ["uni_subject_agents"],
  },
  {
    id: "memory",
    name: "Memory (Cross-Subject Competency)",
    description: "NCCA 5 Key Competencies + cross-subject topic bridges",
    stage: "cross",
    entity_count: 36,
    relationship_count: 1280,
    centroid_embedding_id: "centroid:memory:v1",
    queryable_by: ["all_60_subject_agents"],
  },
  {
    id: "activity",
    name: "Activity (Cross-Stage Usage)",
    description: "Student learning patterns + cross-stage progression tracking",
    stage: "cross",
    entity_count: 184,
    relationship_count: 512,
    centroid_embedding_id: "centroid:activity:v1",
    queryable_by: ["all_60_subject_agents"],
  },
];

export const KnowledgeGraphPanel: FC<KnowledgeGraphPanelProps> = ({
  clusters = DEFAULT_CLUSTERS,
  verbose = true,
}) => {
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);

  const totalEntities = clusters.reduce((acc, c) => acc + c.entity_count, 0);
  const totalRelationships = clusters.reduce(
    (acc, c) => acc + c.relationship_count,
    0,
  );

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Cognee Knowledge Graph
          </h2>
          <p className="text-sm text-slate-600">
            7-cluster knowledge graph (the cross-stage competency backbone)
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-slate-900">
            {totalEntities.toLocaleString()}
          </p>
          <p className="text-xs text-slate-600">entities</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
        {/* The A2UI graph surface (per the 2026-09-30-mega-3b change) */}
        <GraphSurface
          data={{
            nodes: clusters.map((c) => ({
              id: c.id,
              label: c.name,
              cluster: c.stage,
            })),
            edges: clusters.flatMap((c, i) =>
              i < clusters.length - 1
                ? [
                    {
                      source: c.id,
                      target: clusters[i + 1].id,
                      weight: 0.5,
                    },
                  ]
                : [],
            ),
          }}
        />
        {clusters.map((cluster) => (
          <button
            key={cluster.id}
            type="button"
            onClick={() => setSelectedCluster(cluster.id)}
            className={`text-left p-3 rounded-lg border-2 transition ${
              selectedCluster === cluster.id
                ? "border-blue-500 bg-blue-50"
                : "border-slate-200 hover:border-slate-300 bg-white"
            }`}
          >
            <p className="text-sm font-semibold text-slate-900 truncate">
              {cluster.name}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              {cluster.entity_count} entities
            </p>
            <p className="text-xs text-slate-500">
              {cluster.relationship_count} relations
            </p>
          </button>
        ))}
      </div>

      {selectedCluster && verbose && (
        <ClusterDetail
          cluster={
            clusters.find((c) => c.id === selectedCluster)!
          }
        />
      )}

      <div className="border-t border-slate-200 pt-4">
        <div className="grid grid-cols-3 gap-4 text-center">
          <Stat label="Clusters" value={String(clusters.length)} />
          <Stat
            label="Total entities"
            value={totalEntities.toLocaleString()}
          />
          <Stat
            label="Total relationships"
            value={totalRelationships.toLocaleString()}
          />
        </div>
      </div>
    </div>
  );
};

const ClusterDetail: FC<{ cluster: KnowledgeGraphNode }> = ({ cluster }) => (
  <div className="border border-slate-200 rounded-xl p-4 bg-slate-50">
    <p className="text-sm font-semibold text-slate-900 mb-1">
      {cluster.name}
    </p>
    <p className="text-xs text-slate-600 mb-3">{cluster.description}</p>
    <div className="grid grid-cols-2 gap-3 text-xs">
      <div>
        <p className="text-slate-500">Stage</p>
        <p className="font-mono text-slate-900">{cluster.stage}</p>
      </div>
      <div>
        <p className="text-slate-500">Centroid</p>
        <p className="font-mono text-slate-900 truncate">
          {cluster.centroid_embedding_id}
        </p>
      </div>
    </div>
    <div className="mt-3">
      <p className="text-slate-500 text-xs">Queryable by:</p>
      <div className="flex flex-wrap gap-1 mt-1">
        {cluster.queryable_by.map((q) => (
          <span
            key={q}
            className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded"
          >
            {q}
          </span>
        ))}
      </div>
    </div>
  </div>
);

const Stat: FC<{ label: string; value: string }> = ({ label, value }) => (
  <div>
    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
      {label}
    </p>
    <p className="text-2xl font-bold text-slate-900">{value}</p>
  </div>
);
