import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import commonEn from "./resources/common/en/common.json";
import commonGa from "./resources/common/ga/common.json";
import aleyumEn from "./resources/aleyum/en/persona.json";
import aleyumGa from "./resources/aleyum/ga/persona.json";
import cianfhoghlaimEn from "./resources/cianfhoghlaim/en/persona.json";
import cianfhoghlaimGa from "./resources/cianfhoghlaim/ga/persona.json";

const resources = {
  en: {
    common: commonEn,
    aleyum: aleyumEn,
    cianfhoghlaim: cianfhoghlaimEn,
  },
  ga: {
    common: commonGa,
    aleyum: aleyumGa,
    cianfhoghlaim: cianfhoghlaimGa,
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en",
  fallbackLng: "en",
  defaultNS: "common",
  interpolation: { escapeValue: false },
});

export default i18n;
