/**
 * Genie UI tile module — `personal_archive_browser`.
 *
 * Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
 * (WS10 — Convex + CopilotKit + Genie + ADK). Wires the module
 * browser to the 5 Convex actions / queries defined in
 * `web/apps/cianfhoghlaim/convex/personalArchive.ts`:
 *
 *   1. `getModuleDossier`        — drives the per-module dossier view
 *   2. `getQuestionsForTopic`    — drives the cross-module topic view
 *   3. `getMyAnswerForQuestion`  — drives the per-question answer view
 *   4. `searchSimilarQuestions`  — drives the F-granularity search view
 *   5. `chatOverMyArchive`       — drives the chat-with-archive view
 *
 * This module is the canonical home for the personal-archive Genie
 * tile; mount it from the central Cianfhoghlaim homepage's
 * `/personal-archive` route.
 *
 * The module exports a small `tile` factory so the Genie runtime can
 * render the module in either server-side or client-side mode
 * without a hard React import (mirrors the per-subject tile pattern
 * from `web/apps/oideachais-dashboard/convex/lc/gaeilge.ts`).
 */

import { type FC } from "react";

export type PersonalArchiveTileProps = {
  readonly module_code?: string;
  readonly topic_name?: string;
  readonly question_id?: string;
};

// ---------------------------------------------------------------------------
// 1. getModuleDossier — the per-module dossier view
// ---------------------------------------------------------------------------

export async function getModuleDossierTile(module_code: string): Promise<{
  module_code: string;
  artefact_count: number;
  question_count: number;
  topic_count: number;
  reading_list_count: number;
  code_cell_count: number;
  transcript_row_count: number;
}> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { default: client } = require("../convex/browser") as {
    default: {
      query: <T>(name: string, args: unknown) => Promise<T>;
    };
  };
  const dossier = (await client.query("personalArchive:getModuleDossier", {
    module_code,
  })) as {
    artefact_count: number;
    question_count: number;
    topic_count: number;
    reading_list_count: number;
    code_cell_count: number;
    transcript_row_count: number;
  };
  return { module_code, ...dossier };
}

// ---------------------------------------------------------------------------
// 2. getQuestionsForTopic — the cross-module question view
// ---------------------------------------------------------------------------

export async function getQuestionsForTopicTile(
  topic_name: string
): Promise<Array<Record<string, unknown>>> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { default: client } = require("../convex/browser") as {
    default: {
      query: <T>(name: string, args: unknown) => Promise<T>;
    };
  };
  return await client.query<Array<Record<string, unknown>>>(
    "personalArchive:getQuestionsForTopic",
    { topic_name }
  );
}

// ---------------------------------------------------------------------------
// 3. getMyAnswerForQuestion — the per-question answer view
// ---------------------------------------------------------------------------

export async function getMyAnswerForQuestionTile(
  question_id: string
): Promise<Record<string, unknown> | null> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { default: client } = require("../convex/browser") as {
    default: {
      query: <T>(name: string, args: unknown) => Promise<T>;
    };
  };
  return await client.query<Record<string, unknown> | null>(
    "personalArchive:getMyAnswerForQuestion",
    { question_id }
  );
}

// ---------------------------------------------------------------------------
// 4. searchSimilarQuestions — the F-granularity semantic search view
// ---------------------------------------------------------------------------

export async function searchSimilarQuestionsTile(
  question_text: string,
  limit?: number
): Promise<{ hits: Array<Record<string, unknown>>; error?: string }> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { default: client } = require("../convex/browser") as {
    default: {
      action: <T>(name: string, args: unknown) => Promise<T>;
    };
  };
  return await client.action<{
    hits: Array<Record<string, unknown>>;
    error?: string;
  }>("personalArchive:searchSimilarQuestions", {
    question_text,
    limit: limit ?? 5,
  });
}

// ---------------------------------------------------------------------------
// 5. chatOverMyArchive — the chat-with-archive view
// ---------------------------------------------------------------------------

export async function chatOverMyArchiveTile(args: {
  thread_id: string;
  user_message: string;
  module_code?: string;
}): Promise<{
  thread_id: string;
  assistant_message: string;
  hits: Array<Record<string, unknown>>;
  module_code: string | null;
}> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { default: client } = require("../convex/browser") as {
    default: {
      action: <T>(name: string, args: unknown) => Promise<T>;
    };
  };
  return await client.action("personalArchive:chatOverMyArchive", args);
}

// ---------------------------------------------------------------------------
// React tile component (server-renderable).
// ---------------------------------------------------------------------------

export const PersonalArchiveBrowserTile: FC<PersonalArchiveTileProps> = ({
  module_code,
  topic_name,
  question_id,
}) => {
  return (
    <div
      data-genie-tile="personal_archive_browser"
      className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6"
    >
      <h2 className="text-xl font-bold text-slate-900 mb-2">
        Personal Archive Browser
      </h2>
      <p className="text-sm text-slate-600 mb-4">
        Genie UI tile for the UoG personal-archive Convex actions.
      </p>
      <dl className="text-sm text-slate-700 space-y-1">
        {module_code ? (
          <div>
            <dt className="inline font-semibold">Module:</dt>{" "}
            <dd className="inline">{module_code}</dd>
          </div>
        ) : null}
        {topic_name ? (
          <div>
            <dt className="inline font-semibold">Topic:</dt>{" "}
            <dd className="inline">{topic_name}</dd>
          </div>
        ) : null}
        {question_id ? (
          <div>
            <dt className="inline font-semibold">Question:</dt>{" "}
            <dd className="inline">{question_id}</dd>
          </div>
        ) : null}
        {!module_code && !topic_name && !question_id ? (
          <p className="text-xs text-slate-500">
            Provide <code>module_code</code>, <code>topic_name</code>, or{" "}
            <code>question_id</code> as the tile prop.
          </p>
        ) : null}
      </dl>
    </div>
  );
};

export default PersonalArchiveBrowserTile;
