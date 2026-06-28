import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { Shield, FileCheck, Lock } from "lucide-react";
import { VerificationCard } from "@/pages/identity/verification-card";

export const Route = createFileRoute("/identity")({
  component: IdentityPage,
});

const VERIFICATION_DOCS = [
  { type: "Passport", authority: "Department of Foreign Affairs, Ireland", expiry: "2030-06-15" },
  { type: "Garda Vetting", authority: "National Vetting Bureau, Ireland", expiry: "2027-01-10" },
  { type: "Teaching Council Registration", authority: "The Teaching Council, Ireland", expiry: "2026-12-31" },
];

function IdentityPage() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <header className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-3 rounded-full bg-amber-600/10 mb-4">
            <Shield className="h-8 w-8 text-amber-400" />
          </div>
          <h1 className="text-4xl font-bold mb-4">{t("identity.title")}</h1>
          <p className="text-muted-foreground text-lg">{t("identity.subtitle")}</p>
        </header>

        <div className="rounded-xl bg-card border border-border p-4 mb-8 flex items-center gap-3">
          <Lock className="h-5 w-5 text-amber-400 shrink-0" />
          <p className="text-sm text-muted-foreground">
            PII documents are GPG-encrypted with the croilar-encryption key from Infisical.
            Runtime decryption requires Pocket ID OIDC authentication via the Pangolin private resource.
            Only verification metadata (document type, issuing authority, expiry) is shown below.
          </p>
        </div>

        <div className="space-y-4">
          {VERIFICATION_DOCS.map((doc) => (
            <VerificationCard key={doc.type} {...doc} />
          ))}
        </div>

        <div className="mt-8 text-center">
          <button
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-border bg-card hover:border-primary/50 transition-colors text-sm"
            disabled
          >
            <FileCheck className="h-4 w-4" />
            {t("identity.signIn")}
          </button>
          <p className="text-xs text-muted-foreground mt-2">{t("identity.authRequired")}</p>
        </div>
      </div>
    </div>
  );
}
