// Connacht province rendering — the home base
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md
// T12.8 + T12.14.
//
// The Connacht province (Galway + Mayo + Roscommon + Sligo) is the
// home base with the Cian lineage highlights (Delbhna Tír Dhá Locha +
// Lough Corrib + Galway Bay + Moycullen). The 4 NCCA provinces are
// Connacht + Leinster + Munster + Ulster, rendered inside the Éire
// subnation.

import { CiSubnationRegion } from "@cianfhoghlaim/ui/map/subnation-region";
import { CiLandmark, type KeyCompetencySlug } from "@cianfhoghlaim/ui/map/landmark";

export interface ConnachtProvinceProps {
  language: "en" | "ga";
  onLandmarkClick?: (competency: KeyCompetencySlug) => void;
  className?: string;
}

// The 4 counties of Connacht with the Cian lineage highlights
const CONNACHT_COUNTIES = [
  {
    name_en: "Galway",
    name_ga: "Gaillimh",
    coords: { x: 130, y: 210 },
    highlight: "Moycullen — the Delbhna Tír Dhá Locha tuath (the Sea-Kings of Connacht)",
    color: "#f59e0b",
  },
  {
    name_en: "Mayo",
    name_ga: "Maigh Eo",
    coords: { x: 100, y: 195 },
    highlight: "Lough Corrib — the western lake of the two-lake tuath",
    color: "#10b981",
  },
  {
    name_en: "Roscommon",
    name_ga: "Ros Comáin",
    coords: { x: 140, y: 200 },
    highlight: "",
    color: "#94a3b8",
  },
  {
    name_en: "Sligo",
    name_ga: "Sligeach",
    coords: { x: 110, y: 180 },
    highlight: "",
    color: "#94a3b8",
  },
];

const CONNACHT_LANDMARKS: Array<{
  competency: KeyCompetencySlug;
  city: { name: string; coords: { x: number; y: number } };
  subnation: string;
}> = [
  { competency: "communicating", city: { name: "Galway (Moycullen)", coords: { x: 115, y: 215 } }, subnation: "eire" },
  { competency: "personal-effectiveness", city: { name: "Lough Corrib", coords: { x: 105, y: 205 } }, subnation: "eire" },
  { competency: "working-with-others", city: { name: "Galway Bay", coords: { x: 120, y: 225 } }, subnation: "eire" },
];

export function ConnachtProvince({ language, onLandmarkClick, className }: ConnachtProvinceProps) {
  return (
    <div className={className}>
      <svg viewBox="0 0 200 250" className="w-full" xmlns="http://www.w3.org/2000/svg">
        {/* Lough Corrib (the great lake) */}
        <ellipse cx="115" cy="210" rx="20" ry="15" fill="#1e3a8a" opacity="0.4" stroke="#0ea5e9" strokeWidth="1" />
        <text x="115" y="212" fill="#0ea5e9" fontSize="6" textAnchor="middle">Loch Corrib</text>

        {/* Galway Bay */}
        <ellipse cx="100" cy="240" rx="15" ry="8" fill="#0e7490" opacity="0.5" />
        <text x="100" y="242" fill="#06b6d4" fontSize="5" textAnchor="middle">Galway Bay</text>

        {/* County outlines (simplified) */}
        {CONNACHT_COUNTIES.map((county) => (
          <g key={county.name_en}>
            <circle cx={county.coords.x} cy={county.coords.y} r="6" fill={county.color} stroke="#92400e" strokeWidth="1" />
            <text x={county.coords.x} y={county.coords.y + 12} fill="#f8fafc" fontSize="5" textAnchor="middle">
              {language === "ga" ? county.name_ga : county.name_en}
            </text>
            {county.highlight && (
              <text x={county.coords.x} y={county.coords.y - 8} fill="#f59e0b" fontSize="3" textAnchor="middle">
                ★
              </text>
            )}
          </g>
        ))}

        {/* Connacht landmarks */}
        {CONNACHT_LANDMARKS.map((lm) => (
          <CiLandmark
            key={lm.competency}
            competency={lm.competency}
            city={lm.city}
            subnation={lm.subnation}
            onClick={() => onLandmarkClick?.(lm.competency)}
          />
        ))}
      </svg>

      {/* The Cian lineage highlights panel */}
      <div className="mt-4 p-4 bg-slate-800 rounded-lg border border-amber-700">
        <h4 className="font-cinzel text-sm font-bold text-amber-400 mb-2">
          The Cian Lineage in Connacht
        </h4>
        <ul className="text-xs text-slate-300 space-y-1">
          <li>• <strong>Delbhna Tír Dhá Locha</strong> — the two-lake tuath (Lough Corrib + Galway Bay)</li>
          <li>• <strong>Moycullen</strong> — the Barony of Moycullen where the Mac Con Raoi kings ruled</li>
          <li>• <strong>Sea-Kings of Connacht</strong> — the Meic Con Raoi alongside the O'Malleys, O'Dowds, O'Flahertys</li>
          <li>• <strong>Claddagh District</strong> — the historic Gaeltacht district in Galway city</li>
        </ul>
        <p className="text-xs text-slate-500 mt-2 italic">
          See <code>docs/CIANFHLOGHLAIM_LORE.md</code> for the full lineage (operator-only).
        </p>
      </div>
    </div>
  );
}