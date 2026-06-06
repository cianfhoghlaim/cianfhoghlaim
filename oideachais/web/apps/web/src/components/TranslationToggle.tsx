// components/TranslationToggle.tsx — EN/GA language switcher chip
// Cianfhoghlaim Oideachais: bilingual EN/GA per URL pattern
//   /en/stages/$stage vs /ga/céimeanna/$céim
import { useRouter, useRouterState } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";

interface StageSlug {
  en: string;
  ga: string;
}

const STAGE_MAP: Record<string, StageSlug> = {
  aistear: { en: "aistear", ga: "aistear" },
  primary: { en: "primary", ga: "bunscoil" },
  "junior-cycle": { en: "junior-cycle", ga: "iar-bhunscoil" },
  "senior-cycle": { en: "senior-cycle", ga: "scoil-daraigh" },
  tertiary: { en: "tertiary", ga: "ardteistiméireacht" },
};

function detectCurrentLocale(): "en" | "ga" {
  if (typeof window === "undefined") return "en";
  return window.location.pathname.startsWith("/ga/") ? "ga" : "en";
}

function detectCurrentStage(): string | null {
  if (typeof window === "undefined") return null;
  const p = window.location.pathname;
  const m = p.match(/^\/(en|ga)\/stages\/([^/]+)/);
  if (m) return m[2];
  const m2 = p.match(/^\/ga\/c\u00e9imeanna\/([^/]+)/);
  if (m2) return m2[1];
  return null;
}

function gaSlugFor(enSlug: string): string {
  for (const [en, val] of Object.entries(STAGE_MAP)) {
    if (val.en === enSlug) return val.ga;
  }
  return enSlug;
}

function enSlugFor(gaSlug: string): string {
  for (const [_, val] of Object.entries(STAGE_MAP)) {
    if (val.ga === gaSlug) return val.en;
  }
  return gaSlug;
}

export function TranslationToggle() {
  const locale = detectCurrentLocale();
  const stage = detectCurrentStage();

  const en = locale === "en" ? "/en" : stage ? `/en/stages/${enSlugFor(stage)}` : "/";
  const ga = locale === "ga" ? "/ga" : stage ? `/ga/céimeanna/${gaSlugFor(stage)}` : "/";

  return (
    <div className="flex items-center gap-1 bg-slate-800 px-3 py-1 rounded-full border border-slate-700 text-xs font-mono">
      <Link
        to={en}
        className={
          locale === "en"
            ? "text-emerald-400 hover:text-emerald-300"
            : "text-slate-400 hover:text-slate-200"
        }
        title="English"
      >
        EN
      </Link>
      <span className="text-slate-600">/</span>
      <Link
        to={ga}
        className={
          locale === "ga"
            ? "text-emerald-400 hover:text-emerald-300"
            : "text-slate-400 hover:text-slate-200"
        }
        title="Gaeilge"
      >
        GA
      </Link>
    </div>
  );
}
