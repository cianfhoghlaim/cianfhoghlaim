import { useTranslation } from "react-i18next";
import { Shield, Calendar, Building } from "lucide-react";

interface VerificationDoc {
  type: string;
  authority: string;
  expiry: string;
}

export function VerificationCard({ type, authority, expiry }: VerificationDoc) {
  const { t } = useTranslation();

  const isExpired = new Date(expiry) < new Date();

  return (
    <div className={`rounded-xl border p-5 ${isExpired ? "border-red-800/50 bg-red-900/5" : "border-border bg-card"}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-full ${isExpired ? "bg-red-600/10" : "bg-emerald-600/10"}`}>
            <Shield className={`h-5 w-5 ${isExpired ? "text-red-400" : "text-emerald-400"}`} />
          </div>
          <div>
            <p className="font-semibold text-sm">{type}</p>
            <p className="text-xs text-muted-foreground">{t("identity.documentType")}</p>
          </div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full ${isExpired ? "bg-red-600/10 text-red-400" : "bg-emerald-600/10 text-emerald-400"}`}>
          {isExpired ? t("identity.pending") : t("identity.verified")}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="flex items-center gap-2">
          <Building className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-muted-foreground">{authority}</span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-muted-foreground">{new Date(expiry).toLocaleDateString("en-IE")}</span>
        </div>
      </div>
    </div>
  );
}
