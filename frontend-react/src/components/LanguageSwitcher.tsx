import React from "react";
import { Select } from "antd";
import { useTranslation } from "react-i18next";
import { saveLanguagePreference } from "../utils/languageDetection";

const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation();

  const handleLanguageChange = (lng: string) => {
    i18n.changeLanguage(lng);
    saveLanguagePreference(lng);
  };

  return (
    <Select
      value={i18n.language}
      onChange={handleLanguageChange}
      style={{ width: 120 }}
      aria-label="Language Switcher"
      options={[
        { value: "en", label: t("language.en") },
        { value: "de", label: t("language.de") },
        { value: "fr", label: t("language.fr") },
        { value: "es", label: t("language.es") },
      ]}
    />
  );
};

export default LanguageSwitcher;
