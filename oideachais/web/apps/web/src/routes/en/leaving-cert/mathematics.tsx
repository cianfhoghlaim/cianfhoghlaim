/**
 * Leaving Certificate — Mathematics (Paper 1 + Paper 2) resource page.
 *
 * Route: /leaving-cert/mathematics
 * Exam: Fri 5 Jun (P1) + Mon 8 Jun (P2) 2026
 *
 * The page is built using the shared LeavingCertLayout component
 * and loaded with the Mathematics subject payload from MotherDuck/DuckDB.
 */

"use client";

import { useEffect, useState } from "react";
import { LeavingCertLayout } from "../../../components/leaving-cert/LeavingCertLayout";
import { getSubjectPayload } from "../../../server/leaving-cert";
import type { LeavingCertSubjectPayload, Subject } from "../../../server/leaving-cert";

export default function MathematicsPage() {
  const [payload, setPayload] = useState<LeavingCertSubjectPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const subject: Subject = "mathematics";

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
