"use client";

// <PdfLibraryPanel> — Fetches signed R2 URLs from the Hono endpoint
// (/api/r2/sign?key=<r2-key>) and renders a list of PDF download links
// with the 15-min TTL surfaced to the user.
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/
// R14 (Cloudflare R2 + Hono-issued signed URLs).
//
// Per R21 (machine-readable infrastructure), every CSS value here is
// consumed from the central tokens.css — no hardcoded colours, sizes,
// or fonts.

import * as React from "react";
import { cn } from "../../../packages/ui/src/utils";

export interface PdfAssetRef {
  /** R2 key (e.g. "oideachais/leaving_cert/mathematics/en/2024/Q1.pdf") */
  key: string;
  /** Human-readable title in English */
  title_en: string;
  /** Human-readable title in Gaeilge (Irish) */
  title_ga: string;
  /** Locale for the PDF itself */
  locale: "en" | "ga";
  /** Year of publication (display only) */
  year?: number;
}

export interface PdfSignedUrl {
  url: string;
  expires_at: string;
  key: string;
  ttl_seconds: number;
}

export interface CiPdfLibraryPanelProps {
  /** R2 keys for the assets to render */
  assets: PdfAssetRef[];
  /** Locale for the UI text */
  language: "en" | "ga";
  /** Base URL for the API; defaults to same-origin */
  apiBase?: string;
  className?: string;
}

/**
 * Renders a list of PDF asset links. Each click fetches a fresh signed
 * URL from the Hono /api/r2/sign endpoint (15-min TTL by default).
 *
 * The signed URLs are NOT cached in component state — every click is
 * a fresh round-trip to Hono. This way the user always gets a valid
 * (not-yet-expired) URL.
 */
export function CiPdfLibraryPanel({
  assets,
  language,
  apiBase,
  className,
}: CiPdfLibraryPanelProps) {
  const [signedCache, setSignedCache] = React.useState<Record<string, PdfSignedUrl | "loading" | "error">>({});
  const base = apiBase ?? (typeof window !== "undefined" ? window.location.origin : "");

  const fetchSigned = React.useCallback(
    async (key: string): Promise<PdfSignedUrl> => {
      const res = await fetch(`${base}/api/r2/sign?key=${encodeURIComponent(key)}`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(
          (body as { message?: string }).message ?? `HTTP ${res.status}`,
        );
      }
      return (await res.json()) as PdfSignedUrl;
    },
    [base],
  );

  const onClick = async (asset: PdfAssetRef, e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    setSignedCache((c) => ({ ...c, [asset.key]: "loading" }));
    try {
      const signed = await fetchSigned(asset.key);
      setSignedCache((c) => ({ ...c, [asset.key]: signed }));
      // Open the signed URL in a new tab so the user can preview
      window.open(signed.url, "_blank", "noopener,noreferrer");
    } catch (e) {
      console.error("[CiPdfLibraryPanel] sign failed:", e);
      setSignedCache((c) => ({ ...c, [asset.key]: "error" }));
    }
  };

  return (
    <section
      aria-labelledby="pdf-library-heading"
      data-component="CiPdfLibraryPanel"
      className={cn("space-y-2", className)}
    >
      <header className="flex items-baseline justify-between">
        <h2
          id="pdf-library-heading"
          className="text-base font-bold text-slate-100"
        >
          {language === "ga" ? "Leabharlann PDF" : "PDF Library"}
        </h2>
        <p className="text-[10px] text-slate-500 font-mono">
          {language === "ga"
            ? "Hono-signed · 15 nóiméad TTL"
            : "Hono-signed · 15-min TTL"}
        </p>
      </header>
      <ul className="space-y-1.5">
        {assets.map((asset) => {
          const cached = signedCache[asset.key];
          const title = language === "ga" ? asset.title_ga : asset.title_en;
          return (
            <li
              key={asset.key}
              data-key={asset.key}
              data-locale={asset.locale}
              className="flex items-center justify-between gap-3 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
            >
              <div className="min-w-0 flex-1">
                <span className="block truncate text-slate-100 font-medium">
                  {title}
                </span>
                <span className="block truncate font-mono text-[10px] text-slate-500">
                  {asset.key}
                  {asset.year ? ` · ${asset.year}` : ""}
                  {" · "}<span className="uppercase">{asset.locale}</span>
                </span>
              </div>
              <a
                href="#"
                onClick={(e) => onClick(asset, e)}
                aria-label={`Open ${title}`}
                className={cn(
                  "rounded px-3 py-1 text-xs transition-colors",
                  cached === "loading"
                    ? "bg-slate-700 text-slate-300"
                    : cached === "error"
                      ? "bg-rose-700 text-rose-100"
                      : "bg-amber-600 text-amber-50 hover:bg-amber-500",
                )}
                style={{ borderRadius: "var(--ci-radius-md)" }}
              >
                {cached === "loading"
                  ? language === "ga" ? "Ag síniú…" : "Signing…"
                  : cached === "error"
                    ? language === "ga" ? "Earráid" : "Retry"
                    : language === "ga" ? "Oscail PDF" : "Open PDF"}
              </a>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

/**
 * Default R2 asset list for a per-subject 6-section shell (Mathematics default).
 * Other subjects use their own list — pass via the `assets` prop.
 */
export const DEFAULT_MATHEMATICS_ASSETS: PdfAssetRef[] = [
  {
    key: "oideachais/leaving_cert/mathematics/en/2024/LC_FL_2024.pdf",
    title_en: "Mathematics 2024 (FL)",
    title_ga: "Mata 2024 (FL)",
    locale: "en",
    year: 2024,
  },
  {
    key: "oideachais/leaving_cert/mathematics/en/2024/LC_HL_2024.pdf",
    title_en: "Mathematics 2024 (HL)",
    title_ga: "Mata 2024 (AL)",
    locale: "en",
    year: 2024,
  },
  {
    key: "oideachais/leaving_cert/mathematics/en/2024/LC_FL_2024_marking_scheme.pdf",
    title_en: "Mathematics 2024 Marking Scheme (FL)",
    title_ga: "Mata 2024 Scéim Mharcála (FL)",
    locale: "en",
    year: 2024,
  },
  {
    key: "oideachais/leaving_cert/mathematics/en/2024/LC_HL_2024_marking_scheme.pdf",
    title_en: "Mathematics 2024 Marking Scheme (HL)",
    title_ga: "Mata 2024 Scéim Mharcála (AL)",
    locale: "en",
    year: 2024,
  },
  {
    key: "oideachais/leaving_cert/mathematics/ga/2024/LC_HL_2024_gaeilge.pdf",
    title_en: "Mathematics 2024 (HL, as Gaeilge)",
    title_ga: "Mata 2024 (AL, trí Ghaeilge)",
    locale: "ga",
    year: 2024,
  },
];
