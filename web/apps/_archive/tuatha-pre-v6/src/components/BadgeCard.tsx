/**
 * STUB for BadgeCard.
 *
 * Per the 2026-08-26 build subagent report: the BadgeCard component was
 * planned for the tuatha Web-of-Trust / Eiraic Treasures system but never
 * landed. The realm/$subject and student/$id/badges routes import it.
 */
export interface BadgeCardData {
  id?: string;
  student_id?: string;
  subject?: string;
  tier?: number;
  competency?: string;
  date_earned?: string;
}

export interface BadgeCardProps {
  badge: BadgeCardData;
}

export function BadgeCard(_props: BadgeCardProps) {
  return <div>BadgeCard (stub)</div>;
}
