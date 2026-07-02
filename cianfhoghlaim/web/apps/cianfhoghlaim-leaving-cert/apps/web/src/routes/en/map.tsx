// /en/map — The accurate British Isles map with the 6 subnations
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// agentic-frontend-frameworks/spec.md R7.

import { createFileRoute } from "@tanstack/react-router";
import { CiRealmMap } from "@cianfhoghlaim/ui/map/realm-map";
import { CiSubnationFlag } from "@cianfhoghlaim/ui/map/subnation-flag";
import { CiLandmark, type KeyCompetencySlug } from "@cianfhoghlaim/ui/map/landmark";
import { CiDragonBanner } from "@cianfhoghlaim/ui/lore/dragon-banner";

export const Route = createFileRoute("/en/map")({
  component: MapPage,
});

// The 5 NCCA Key Competencies → 5 land-marks on the map
// (Dublin + Edinburgh + Cardiff + London + Douglas + Belfast)
const LANDMARKS: Array<{
  competency: KeyCompetencySlug;
  city: { name: string; coords: { x: number; y: number } };
  subnation: string;
}> = [
  { competency: "communicating", city: { name: "Dublin", coords: { x: 130, y: 200 } }, subnation: "eire" },        // The Book of Kells, Trinity College Library
  { competency: "information-processing", city: { name: "Edinburgh", coords: { x: 125, y: 95 } }, subnation: "scotland" },     // The Library of the University of Edinburgh
  { competency: "critical-creative-thinking", city: { name: "Cardiff", coords: { x: 197, y: 202 } }, subnation: "wales" },    // The Welsh Dragon
  { competency: "personal-effectiveness", city: { name: "London", coords: { x: 245, y: 175 } }, subnation: "england" },    // The Royal College of Physicians
  { competency: "working-with-others", city: { name: "Douglas", coords: { x: 159, y: 164 } }, subnation: "isle-of-man" },    // The Tynwald
];

function MapPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The Accurate British Isles Map
        </h1>
        <p className="text-slate-400 text-lg">
          6 subnations · 5 NCCA Key Competencies as 5 land-marks · Wales flies the Dragon Banner
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          The Esker Riada (Dublin Bay ↔ Galway Bay) is the EN ↔ GA divider
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* The map */}
        <div className="flex-1 bg-slate-800 border border-slate-700 rounded-2xl p-6">
          <svg viewBox="0 0 360 280" className="w-full" xmlns="http://www.w3.org/2000/svg">
            {/* Sea texture (background) */}
            <rect width="360" height="280" fill="#0e7490" />
            <pattern id="sea" patternUnits="userSpaceOnUse" width="20" height="20">
              <path d="M 0 10 Q 10 8 20 10" stroke="#06b6d4" strokeWidth="0.3" fill="none" opacity="0.5" />
            </pattern>
            <rect width="360" height="280" fill="url(#sea)" />

            {/* Subnation regions (drawn manually since CiRealmMap uses its own SVG) */}
            {/* Ireland */}
            <path
              d="M 80 180 L 180 175 L 175 230 L 100 240 L 75 200 Z"
              fill="#059669"
              opacity="0.9"
              stroke="#fbbf24"
              strokeWidth="1.5"
            />
            {/* Northern Ireland */}
            <path
              d="M 110 140 L 175 130 L 180 175 L 80 180 L 75 155 Z"
              fill="#2563eb"
              opacity="0.4"
            />
            {/* Scotland */}
            <path
              d="M 110 60 L 175 50 L 180 100 L 175 130 L 110 140 L 75 110 L 75 70 Z"
              fill="#0ea5e9"
              opacity="0.4"
            />
            {/* England */}
            <path
              d="M 180 130 L 280 130 L 295 175 L 250 200 L 180 175 L 175 130 Z"
              fill="#dc2626"
              opacity="0.4"
            />
            {/* Wales */}
            <path
              d="M 175 175 L 220 180 L 215 220 L 175 230 L 180 175 Z"
              fill="#b91c1c"
              opacity="0.4"
            />
            {/* Isle of Man */}
            <path
              d="M 150 160 L 165 158 L 168 168 L 155 170 L 150 165 Z"
              fill="#475569"
              opacity="0.4"
            />

            {/* 5 land-marks (one per NCCA Key Competency) */}
            {LANDMARKS.map((lm) => (
              <CiLandmark
                key={lm.competency}
                competency={lm.competency}
                city={lm.city}
                subnation={lm.subnation}
              />
            ))}

            {/* Belfast (the 6th Cross-Border Studies node) */}
            <circle cx="120" cy="160" r="3" fill="#fbbf24" stroke="#92400e" strokeWidth="0.5" />
            <text x="125" y="163" fill="#fbbf24" fontSize="3">Belfast (Cross-Border Studies)</text>

            {/* The Esker Riada divider */}
            <line
              x1="175" y1="180" x2="100" y2="230"
              stroke="#fbbf24"
              strokeWidth="0.5"
              strokeDasharray="3 2"
              opacity="0.5"
            />
            <text x="120" y="210" fill="#fbbf24" fontSize="3" opacity="0.7">
              Esker Riada (Dublin ↔ Galway Bay)
            </text>

            {/* The Dragon Banner (Wales subnation) */}
            <g transform="translate(195, 220)">
              <CiDragonBanner size={16} />
            </g>
          </svg>
        </div>

        {/* The legend */}
        <div className="lg:w-80 space-y-3">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <h3 className="font-cinzel text-lg font-bold text-slate-100 mb-3">
              The 6 Subnations
            </h3>
            <div className="space-y-2">
              {[
                { slug: "eire" as const, name_en: "Éire", active: true },
                { slug: "northern-ireland" as const, name_en: "Northern Ireland", active: false },
                { slug: "scotland" as const, name_en: "Scotland", active: false },
                { slug: "england" as const, name_en: "England", active: false },
                { slug: "wales" as const, name_en: "Wales", active: false },
                { slug: "isle-of-man" as const, name_en: "Isle of Man", active: false },
              ].map((sub) => (
                <div key={sub.slug} className="flex items-center gap-2">
                  <CiSubnationFlag subnation={sub.slug} size={20} />
                  <span className={`text-sm ${sub.active ? "text-emerald-400 font-medium" : "text-slate-400"}`}>
                    {sub.name_en}
                  </span>
                  {sub.active && (
                    <span className="ml-auto text-xs text-amber-400">v1 active</span>
                  )}
                  {!sub.active && (
                    <span className="ml-auto text-xs text-slate-500">Coming soon</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <h3 className="font-cinzel text-lg font-bold text-slate-100 mb-3">
              The 5 Key Competencies
            </h3>
            <div className="space-y-2 text-sm">
              <div><strong className="text-emerald-400">Communicating</strong> · Dublin · Brigid</div>
              <div><strong className="text-blue-400">Information Processing</strong> · Edinburgh · Ogma</div>
              <div><strong className="text-amber-400">Critical & Creative</strong> · Cardiff · Lugh</div>
              <div><strong className="text-amber-700">Personal Effectiveness</strong> · London · Dian Cecht</div>
              <div><strong className="text-red-400">Working with Others</strong> · Douglas · Trí Dé Dána</div>
              <div><strong className="text-yellow-400">Belfast</strong> · Cross-Border Studies · 6th</div>
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
            <h3 className="font-cinzel text-lg font-bold text-slate-100 mb-3">
              Wales — Dragon Banner
            </h3>
            <p className="text-xs text-slate-400 italic mb-2">
              Per Cadwaladr ap Cadwallon (7th c.) + Owain Glyndwr (1400)
            </p>
            <CiDragonBanner size={48} />
          </div>
        </div>
      </div>
    </div>
  );
}