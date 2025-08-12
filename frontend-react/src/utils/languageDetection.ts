/**
 * Language detection utility for the ConvoSphere application.
 * Detects the user's preferred language based on browser settings and saved preferences.
 */

// Supported languages in the application
export const SUPPORTED_LANGUAGES = ["en", "de", "fr", "es"] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

/**
 * Validates if a language code is supported
 */
export const isSupportedLanguage = (
  language: string,
): language is SupportedLanguage => {
  return SUPPORTED_LANGUAGES.includes(language as SupportedLanguage);
};

/**
 * Safely converts a string to a supported language, with fallback
 */
export const toSupportedLanguage = (language: string): SupportedLanguage => {
  return isSupportedLanguage(language) ? language : "en";
};

/**
 * Detects the user's preferred language based on:
 * 1. Saved language preference in localStorage
 * 2. Browser language settings
 * 3. Fallback to English (default language)
 */
export const detectLanguage = (): SupportedLanguage => {
  // 1. Check localStorage for saved language preference
  const savedLanguage = localStorage.getItem("i18n_language");
  if (savedLanguage && isSupportedLanguage(savedLanguage)) {
    return savedLanguage;
  }

  // 2. Check browser language
  const browserLanguage = navigator.language || navigator.languages?.[0];
  if (browserLanguage) {
    // Extract language code (e.g., "de-DE" -> "de")
    const langCode = browserLanguage.split("-")[0].toLowerCase();
    if (isSupportedLanguage(langCode)) {
      return langCode;
    }
  }

  // 3. Check browser languages array
  if (navigator.languages) {
    for (const lang of navigator.languages) {
      const langCode = lang.split("-")[0].toLowerCase();
      if (isSupportedLanguage(langCode)) {
        return langCode;
      }
    }
  }

  // 4. Fallback to English (default language)
  return "en";
};

/**
 * Saves the language preference to localStorage
 */
export const saveLanguagePreference = (language: string): void => {
  const supportedLanguage = toSupportedLanguage(language);
  localStorage.setItem("i18n_language", supportedLanguage);
};

/**
 * Gets the current language from localStorage
 */
export const getSavedLanguage = (): SupportedLanguage | null => {
  const saved = localStorage.getItem("i18n_language");
  return saved && isSupportedLanguage(saved) ? saved : null;
};
