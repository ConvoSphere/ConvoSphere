import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";
import de from "./de.json";
import fr from "./fr.json";
import es from "./es.json";

const resources = {
  en: { translation: en },
  de: { translation: de },
  fr: { translation: fr },
  es: { translation: es },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en", // Default to English
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
