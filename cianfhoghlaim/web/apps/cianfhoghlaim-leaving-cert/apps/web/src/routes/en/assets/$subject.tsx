// /en/assets/$subject — 3D + 2D asset gallery (Hades dual-mode)
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R4.

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { CiSemanticPill } from "@cianfhoghlaim/ui";
import { CiSkillTree } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/assets/$subject")({
  component: AssetsPage,
});

// Sample assets (the real ones are uploaded to s3://cianfhoghlaim-asset-v2/)
const SAMPLE_ASSETS = [
  { id: "math-comp-num", name: "Complex Numbers symbol", format: "glb", size: 2.4, eraic: 3 },
  { id: "math-comp-num-sprite", name: "Complex Numbers sprite atlas", format: "png", size: 0.8, eraic: 3 },
  { id: "math-algebra", name: "Algebra icon", format: "glb", size: 1.9, eraic: 3 },
  { id: "math-algebra-sprite", name: "Algebra sprite", format: "png", size: 0.5, eraic: 3 },
  { id: "math-calc", name: "Calculus glyph", format: "glb", size: 3.1, eraic: 3 },
  { id: "math-calc-sprite", name: "Calculus sprite", format: "png", size: 1.0, eraic: 3 },
];

function AssetsPage() {
  const { subject } = Route.useParams();

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {subject.replace("_", " ")} — 3D + 2D Asset Gallery
        </h1>
        <p className="text-slate-400 text-lg">
          Hades dual-mode: 3D meshes via TRELLIS.2 + SAM-3D-Objects + 2D sprite atlases
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Generated from s3://cianfhoghlaim-asset-v2/{3d,2d}/{subject}/
        </p>
      </div>

      {/* Skill tree */}
      <CiTextbookPanel title="The 13 Éraic Treasures — Skill Tree" material="gold-leaf">
        <CiSkillTree
          root={{
            id: "math-mastery",
            label: "Mathematics Mastery",
            tier: 1,
            unlocked: true,
            children: SAMPLE_ASSETS.slice(0, 3).map((asset) => ({
              id: asset.id,
              label: asset.name,
              tier: asset.eraic,
              unlocked: asset.id === "math-comp-num",
            })),
          }}
        />
      </CiTextbookPanel>

      {/* Asset grid */}
      <CiTextbookPanel title="Available Assets" material="parchment">
        <div className="grid grid-cols-3 gap-4">
          {SAMPLE_ASSETS.map((asset) => (
            <div
              key={asset.id}
              className="bg-slate-800 border border-slate-700 rounded-xl p-4 hover:border-emerald-700 transition-colors"
            >
              <div
                className="aspect-square rounded-lg mb-3 flex items-center justify-center text-6xl bg-gradient-to-br from-slate-700 to-slate-900"
                style={{
                  backgroundImage: `linear-gradient(135deg, ${asset.format === "glb" ? "var(--ci-subject-mathematics)" : "var(--ci-material-gold-leaf)"}40, transparent)`,
                }}
              >
                {asset.format === "glb" ? "🧊" : "🖼️"}
              </div>
              <div className="text-sm font-medium text-slate-100 truncate">{asset.name}</div>
              <div className="flex items-center justify-between mt-2">
                <CiSemanticPill
                  kind={asset.format === "glb" ? "eiraic" : "available"}
                  label={asset.format.toUpperCase()}
                />
                <span className="text-xs text-slate-500">{asset.size} MB</span>
              </div>
              <div className="text-xs text-slate-400 mt-2 italic">
                Éraic tier {asset.eraic}/13
              </div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      {/* 3D viewer placeholder */}
      <CiTextbookPanel title="3D Viewer (Babylon.js + model-viewer)" material="knotwork">
        <div className="aspect-video bg-slate-950 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-2">🧊</div>
            <p className="text-slate-400 text-sm">
              Babylon.js scene with model-viewer fallback
            </p>
            <p className="text-slate-500 text-xs mt-1">
              Hard cap: 5 models per scene, 4 MB GLB per asset
            </p>
          </div>
        </div>
      </CiTextbookPanel>
    </div>
  );
}