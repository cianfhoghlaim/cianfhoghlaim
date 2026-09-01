/**
 * OralStudyPlayer — the canonical A2UI v0.9 oral study plan
 * audio player.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
 * (Phase 6 oral study plans). Renders the per-week spoken audio
 * segments from the Convex `audio_segments` table + the oral
 * study plan metadata.
 */

import * as React from "react";

export interface OralStudySegmentData {
  week_number: number;
  text_en: string;
  text_ga?: string | null;
  estimated_duration_sec: number;
  tts_provider: string;
  voice_id: string;
  audio_b64?: string | null;
}

export interface OralStudyPlayerData {
  subject: string;
  dialect: string;
  total_duration_min: number;
  segments: OralStudySegmentData[];
  phase?: "phase1_stub" | "phase6_wired";
}

export interface OralStudyPlayerProps {
  data: OralStudyPlayerData | null;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

export function OralStudyPlayer({
  data,
  loading,
  error,
  className,
}: OralStudyPlayerProps): React.ReactElement {
  if (loading) {
    return (
      <div
        className={
          className ??
          "rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500"
        }
        aria-label="Oral study plan loading"
      >
        Synthesizing oral study plan audio…
      </div>
    );
  }
  if (error) {
    return (
      <div
        className={
          className ??
          "rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        }
        aria-label="Oral study plan error"
      >
        Oral plan error: {error}
      </div>
    );
  }
  if (!data) {
    return (
      <div
        className={
          className ??
          "rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500"
        }
        aria-label="No oral study plan"
      >
        No oral study plan generated yet.
      </div>
    );
  }

  const segments = data.segments ?? [];
  const isStub = data.phase === "phase1_stub";

  return (
    <section
      className={
        className ??
        "rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      }
      aria-label={`${data.subject} oral study plan`}
    >
      <header className="flex items-baseline justify-between gap-3 border-b border-slate-200 pb-3">
        <h3 className="text-lg font-bold text-slate-900">
          Oral study plan — {data.subject} ({data.dialect})
        </h3>
        <span className="text-xs text-slate-500">
          {(data.total_duration_min ?? 0).toFixed(1)} min ·{" "}
          {segments.length} segments ·{" "}
          {isStub ? "phase1_stub (silent WAV)" : "phase6_wired (TTS)"}
        </span>
      </header>

      <ul className="mt-4 space-y-2">
        {segments.map((seg, i) => (
          <li
            key={`week-${seg.week_number}-${i}`}
            className="rounded-lg border border-slate-100 bg-slate-50 p-3"
          >
            <div className="flex items-baseline justify-between gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Week {seg.week_number}
              </span>
              <span className="text-xs text-slate-400">
                {seg.estimated_duration_sec.toFixed(0)}s · {seg.tts_provider}
              </span>
            </div>
            <div className="mt-1 text-sm text-slate-700">{seg.text_en}</div>
            {seg.text_ga ? (
              <div className="mt-1 text-sm text-slate-600">
                {seg.text_ga}
              </div>
            ) : null}
            {seg.audio_b64 ? (
              <audio
                controls
                className="mt-2 w-full"
                src={`data:audio/wav;base64,${seg.audio_b64}`}
              >
                <track kind="captions" />
              </audio>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default OralStudyPlayer;