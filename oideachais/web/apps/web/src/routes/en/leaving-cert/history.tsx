/**
 * Leaving Certificate — History resource page.
 * Route: /en/leaving-cert/history
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { LeavingCertLayout } from "../../../components/leaving-cert/LeavingCertLayout";
import { getSubjectPayload } from "../../../server/leaving-cert";
import type { LeavingCertSubjectPayload, Subject } from "../../../server/leaving-cert";

function HistoryPage() {
  const [payload, setPayload] = useState<LeavingCertSubjectPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const subject: Subject = "history";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const data = await getSubjectPayload(subject);
      if (cancelled) return;
      setPayload(data);
      setLoading(false);
    }
    load();
    return () => { cancelled = true; };
  }, [subject]);

  return <LeavingCertLayout subject={subject} payload={payload} isLoading={loading} />;
}

export const Route = createFileRoute("/en/leaving-cert/history")({
  component: HistoryPage,
});
