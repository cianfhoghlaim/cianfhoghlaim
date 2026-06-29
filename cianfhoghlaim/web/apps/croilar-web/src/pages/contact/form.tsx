import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Send, Lock, Check } from "lucide-react";

export function ContactForm() {
  const { t } = useTranslation();
  const [sent, setSent] = useState(false);

  if (sent) {
    return (
      <div className="rounded-xl bg-card border border-border p-8 text-center">
        <div className="inline-flex items-center justify-center p-3 rounded-full bg-emerald-600/10 mb-4">
          <Check className="h-6 w-6 text-emerald-400" />
        </div>
        <p className="font-semibold text-lg">{t("contact.sent")}</p>
      </div>
    );
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        setSent(true);
      }}
      className="rounded-xl bg-card border border-border p-6 space-y-4"
    >
      <div>
        <label className="block text-sm font-medium mb-1">{t("contact.name")}</label>
        <input
          type="text"
          required
          className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">{t("contact.email")}</label>
        <input
          type="email"
          required
          className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">{t("contact.message")}</label>
        <textarea
          required
          rows={5}
          className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm resize-none"
        />
      </div>
      <button
        type="submit"
        className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
      >
        <Send className="h-4 w-4" />
        {t("contact.send")}
      </button>
      <p className="text-xs text-muted-foreground text-center flex items-center justify-center gap-1">
        <Lock className="h-3 w-3" />
        {t("contact.encrypted")}
      </p>
    </form>
  );
}
