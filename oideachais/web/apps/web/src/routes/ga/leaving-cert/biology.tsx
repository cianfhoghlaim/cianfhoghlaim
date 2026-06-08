/**
 * Leaving Certificate — Biology resource page.
 * Route: /ga/leaving-cert/biology
 */
"use client";

import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { LeavingCertLayout } from "../../../components/leaving-cert/LeavingCertLayout";
import { getSubjectPayload } from "../../../server/leaving-cert";
import type { LeavingCertSubjectPayload, Subject } from "../../../server/leaving-cert";

function BiologyPage() {
  const [payload, setPayload] = useState<LeavingCertSubjectPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const subject: Subject = "biology";

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

export const Route = createFileRoute("/ga/leaving-cert/biology")({
  component: BiologyPage,
});
