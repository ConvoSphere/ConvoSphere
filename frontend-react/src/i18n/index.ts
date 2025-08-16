import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";
import de from "./de.json";
import fr from "./fr.json";
import es from "./es.json";
import errorMessages from "./error-messages-multilingual.json";

const resources = {
  en: { translation: { ...en, ...errorMessages.en } },
  de: { translation: { ...de, ...errorMessages.de } },
  fr: { translation: { ...fr, ...errorMessages.fr } },
  es: { translation: { ...es, ...errorMessages.es } },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en", // Default to English
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
