import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import commonEn from "./resources/common/en/common.json";
import commonGa from "./resources/common/ga/common.json";
import musicEn from "./resources/streams/music/en/persona.json";
import musicGa from "./resources/streams/music/ga/persona.json";
import teachingEn from "./resources/streams/teaching/en/persona.json";
import teachingGa from "./resources/streams/teaching/ga/persona.json";

const resources = {
  en: {
    common: commonEn,
    music: musicEn,
    teaching: teachingEn,
  },
  ga: {
    common: commonGa,
    music: musicGa,
    teaching: teachingGa,
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
