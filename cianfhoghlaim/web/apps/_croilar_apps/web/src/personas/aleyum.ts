import type { Persona } from "./_schema";

export const aleyum: Persona = {
  id: "aleyum",
  slug: "aleyum",
  i18n: { en: "Aleyum", ga: "Ailéam" },
  theme: {
    mode: "dark",
    accent: "oklch(0.74 0.18 285)",
    palette: {},
  },
  routes: [
    { path: "/",            label: { en: "Home",     ga: "Baile"    }, icon: "home",          loader: "home"    },
    { path: "/cv",          label: { en: "CV",       ga: "CV"       }, icon: "user",          loader: "cv"      },
    { path: "/music",       label: { en: "Music",    ga: "Ceol"     }, icon: "music",         loader: "music"   },
    { path: "/code",        label: { en: "Code",     ga: "Cód"      }, icon: "code",          loader: "code"    },
    { path: "/data",        label: { en: "Data",     ga: "Sonraí"   }, icon: "bar-chart",     loader: "data"    },
    { path: "/contact",     label: { en: "Contact",  ga: "Teagmháil" }, icon: "mail",          loader: "contact" },
  ],
  dataSources: ["spotify", "soundcloud", "youtube", "github", "cv_pdfs", "identity_docs"],
  featureFlags: { cv: true, data: true, identity: true, contact: true },
  dagsterAssetGroup: "aleyum",
  bamlSchemas: ["cv_extraction", "artwork_analysis", "style_transfer"],
};
