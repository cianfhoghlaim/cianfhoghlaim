import { Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { usePersona } from "@/routes/__root";
import { Button } from "@cianfhoghlaim/ui-kit";
import { Home } from "lucide-react";

export function NotFound() {
  const { t } = useTranslation();
  const persona = usePersona();
  const homePath = persona ? `/?persona=${persona.slug}` : "/";

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <h1 className="text-7xl font-bold text-primary mb-4">404</h1>
        <h2 className="text-2xl font-semibold mb-2">
          {t("notFound.title", "404 — Not Found")}
        </h2>
        <p className="text-muted-foreground mb-6">
          {t("notFound.subtitle", "The page you are looking for does not exist or has been moved.")}
        </p>
        <Link to={homePath}>
          <Button>
            <Home className="h-4 w-4 mr-2" />
            {t("notFound.backHome", "Back to Home")}
          </Button>
        </Link>
      </div>
    </div>
  );
}
