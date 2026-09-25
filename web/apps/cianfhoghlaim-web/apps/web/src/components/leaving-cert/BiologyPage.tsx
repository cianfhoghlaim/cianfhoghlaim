import { useEffect, useState } from "react";
import { LeavingCertLayout } from "./LeavingCertLayout";
import { getSubjectPayload } from "../../server/leaving-cert";
import type { LeavingCertSubjectPayload, Subject } from "../../server/leaving-cert";

export function LeavingCertSubjectPage({ subject }: { subject: Subject }) {
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
    return () => {
      cancelled = true;
    };
  }, [subject]);

  return <LeavingCertLayout subject={subject} payload={payload} isLoading={loading} />;
}

export function BiologyPage() {
  return <LeavingCertSubjectPage subject="biology" />;
}

export function BusinessPage() {
  return <LeavingCertSubjectPage subject="business" />;
}

export function ConstructionStudiesPage() {
  return <LeavingCertSubjectPage subject="construction-studies" />;
}

export function FrenchPage() {
  return <LeavingCertSubjectPage subject="french" />;
}

export function HistoryPage() {
  return <LeavingCertSubjectPage subject="history" />;
}

export function IrishPage() {
  return <LeavingCertSubjectPage subject="irish" />;
}

export function MathematicsPage() {
  return <LeavingCertSubjectPage subject="mathematics" />;
}
