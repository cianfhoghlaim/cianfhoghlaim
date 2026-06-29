import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { ContactForm } from "@/pages/contact/form";

export const Route = createFileRoute("/contact")({
  component: ContactPage,
});

function ContactPage() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-lg mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">{t("contact.title")}</h1>
          <p className="text-muted-foreground text-lg">{t("contact.subtitle")}</p>
        </header>

        <ContactForm />
      </div>
    </div>
  );
}
