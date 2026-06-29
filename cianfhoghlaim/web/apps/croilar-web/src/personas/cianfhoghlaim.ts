import type { Persona } from "./_schema";

export const cianfhoghlaim: Persona = {
  id: "cianfhoghlaim",
  slug: "cianfhoghlaim",
  i18n: { en: "Cianfhoghlaim", ga: "Cianfhoghlaim" },
  theme: {
    mode: "light",
    accent: "oklch(0.62 0.16 145)",
    palette: {},
  },
  routes: [
    { path: "/",            label: { en: "Home",           ga: "Baile"           }, icon: "home",        loader: "home"    },
    { path: "/cv",          label: { en: "Curriculum",     ga: "Curaclam"        }, icon: "user",        loader: "cv"      },
    { path: "/research",    label: { en: "Research",       ga: "Taighde"         }, icon: "flask",       loader: "research" },
    { path: "/teaching",    label: { en: "Teaching",       ga: "Teagasc"         }, icon: "book-open",   loader: "teaching" },
    { path: "/publications",label: { en: "Publications",   ga: "Foilseacháin"    }, icon: "file-text",   loader: "publications" },
    { path: "/code",        label: { en: "Code",           ga: "Cód"             }, icon: "code",        loader: "code"    },
    { path: "/data",        label: { en: "Data",           ga: "Sonraí"          }, icon: "bar-chart",   loader: "data"    },
    { path: "/contact",     label: { en: "Contact",        ga: "Teagmháil"       }, icon: "mail",        loader: "contact" },
  ],
  dataSources: ["cv_pdfs", "teaching_pdfs", "ducklake_oideachais", "ducklake_meaisinfhoghlaim", "github"],
  featureFlags: { cv: true, data: true, identity: false, contact: true },
  dagsterAssetGroup: "cianfhoghlaim",
  bamlSchemas: ["cv_extraction", "teaching_extraction"],
};
