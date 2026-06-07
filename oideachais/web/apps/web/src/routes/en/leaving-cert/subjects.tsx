// Route stub — Irish, Biology, French, History, Business, Construction Studies
// share the same pattern as the Mathematics page.

"use client";

import { useEffect, useState } from "react";
import { LeavingCertLayout } from "../../../components/leaving-cert/LeavingCertLayout";
import { getSubjectPayload } from "../../../server/leaving-cert";
import type { LeavingCertSubjectPayload, Subject } from "../../../server/leaving-cert";

const SUBJECTS: Subject[] = ["irish", "biology", "french", "history", "business", "construction-studies"];

function SubjectPage({ subject }: { subject: Subject }) {
  const [payload, setPayload] = useState<LeavingCertSubjectPayload | null>(null);
  const [loading, setLoading] = useState(true);

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

export function IrishPage() { return <SubjectPage subject="irish" />; }
export function BiologyPage() { return <SubjectPage subject="biology" />; }
export function FrenchPage() { return <SubjectPage subject="french" />; }
export function HistoryPage() { return <SubjectPage subject="history" />; }
export function BusinessPage() { return <SubjectPage subject="business" />; }
export function ConstructionStudiesPage() { return <SubjectPage subject="construction-studies" />; }
