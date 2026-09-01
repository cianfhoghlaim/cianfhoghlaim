/**
 * useStudyPlan — lifted into the consolidated cianfhoghlaim-nua app
 * per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change.
 *
 * Migrated from web/apps/oideachais/src/hooks/useStudyPlan.ts. The
 * Hono stub moved into src/lib/study_plan_stub.ts.
 */

import * as React from "react";

import type { StudyPlanCardData } from "@cianfhoghlaim/a2ui";

export interface StudyPlanRequestParams {
  lo_codes?: string[];
  target_date?: string;
  duration_weeks?: number;
  dialect?: string;
  language?: string;
  user_id?: string;
  trace_id?: string;
}

export interface UseStudyPlanResult {
  data: StudyPlanCardData | null;
  loading: boolean;
  error: string | null;
  request: (params?: StudyPlanRequestParams) => Promise<void>;
}

export function useStudyPlan(
  subject: string,
  honoApiBase?: string,
): UseStudyPlanResult {
  const [data, setData] = React.useState<StudyPlanCardData | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const baseUrl = React.useMemo(() => {
    if (honoApiBase) return honoApiBase;
    if (typeof window !== "undefined") {
      return `${window.location.protocol}//${window.location.hostname}:8787`;
    }
    return "http://localhost:8787";
  }, [honoApiBase]);

  const request = React.useCallback(
    async (params: StudyPlanRequestParams = {}) => {
      setLoading(true);
      setError(null);
      try {
        const url = `${baseUrl}/api/copilotkit/lc/${subject}/get_study_plan`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(params),
        });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status} ${res.statusText}`);
        }
        const json = (await res.json()) as StudyPlanCardData;
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    },
    [baseUrl, subject],
  );

  return { data, loading, error, request };
}

export default useStudyPlan;