import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Language metadata for UI display
export interface LanguageInfo {
  code: string;
  name: string;
  native_name: string;
  direction: 'ltr' | 'rtl';
}

// Supported languages configuration
export const SUPPORTED_LANGUAGES: LanguageInfo[] = [
  { code: 'en', name: 'English', native_name: 'English', direction: 'ltr' },
  { code: 'de', name: 'German', native_name: 'Deutsch', direction: 'ltr' },
  { code: 'fr', name: 'French', native_name: 'Français', direction: 'ltr' },
  { code: 'es', name: 'Spanish', native_name: 'Español', direction: 'ltr' },
  { code: 'ar', name: 'Arabic', native_name: 'العربية', direction: 'rtl' },
  { code: 'ja', name: 'Japanese', native_name: '日本語', direction: 'ltr' },
];

// Default language
export const DEFAULT_LANGUAGE = 'en';

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Initialize i18n
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    // Default configuration
    fallbackLng: DEFAULT_LANGUAGE,
    debug: import.meta.env.DEV,
    
    // Detection options
    detection: {
      order: ['querystring', 'localStorage', 'navigator', 'htmlTag'],
      lookupQuerystring: 'lang',
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
    
    // Backend configuration for API integration
    backend: {
      loadPath: `${API_BASE_URL}/api/v1/i18n/translations?namespace={{ns}}`,
      addPath: `${API_BASE_URL}/api/v1/i18n/translations`,
      allowMultiLoading: false,
      crossDomain: true,
      withCredentials: true,
      requestOptions: {
        mode: 'cors',
        credentials: 'include',
      },
    },
    
    // Interpolation
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    // Namespaces
    ns: ['common', 'auth', 'user', 'assistant', 'conversation', 'knowledge', 'tools', 'validation', 'errors', 'websocket', 'health'],
    defaultNS: 'common',
    
    // React integration
    react: {
      useSuspense: false, // Disable suspense for better error handling
    },
    
    // Language detection
    supportedLngs: SUPPORTED_LANGUAGES.map(lang => lang.code),
    
    // Load all namespaces by default
    load: 'languageOnly',
    
    // Cache
    cache: {
      enabled: true,
      expirationTime: 24 * 60 * 60 * 1000, // 24 hours
    },
  });

// Language management functions
export const i18nService = {
  // Get current language
  getCurrentLanguage: (): string => {
    return i18n.language || DEFAULT_LANGUAGE;
  },
  
  // Change language
  changeLanguage: async (language: string): Promise<void> => {
    try {
      await i18n.changeLanguage(language);
      
      // Update document direction for RTL languages
      const langInfo = SUPPORTED_LANGUAGES.find(lang => lang.code === language);
      if (langInfo) {
        document.documentElement.dir = langInfo.direction;
        document.documentElement.lang = language;
      }
      
      // Store in localStorage
      localStorage.setItem('i18nextLng', language);
      
      // Update URL query parameter
      const url = new URL(window.location.href);
      url.searchParams.set('lang', language);
      window.history.replaceState({}, '', url.toString());
      
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  },
  
  // Get language info
  getLanguageInfo: (code: string): LanguageInfo | undefined => {
    return SUPPORTED_LANGUAGES.find(lang => lang.code === code);
  },
  
  // Check if language is RTL
  isRTL: (language: string): boolean => {
    const langInfo = SUPPORTED_LANGUAGES.find(lang => lang.code === language);
    return langInfo?.direction === 'rtl';
  },
  
  // Get supported languages
  getSupportedLanguages: (): LanguageInfo[] => {
    return SUPPORTED_LANGUAGES;
  },
  
  // Load translations from API
  loadTranslations: async (language: string, namespace?: string): Promise<void> => {
    try {
      const url = namespace 
        ? `${API_BASE_URL}/api/v1/i18n/translations?namespace=${namespace}`
        : `${API_BASE_URL}/api/v1/i18n/translations`;
      
      const response = await fetch(url, {
        headers: {
          'Accept-Language': language,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        i18n.addResourceBundle(language, namespace || 'common', data.translations, true, true);
      }
    } catch (error) {
      console.error('Failed to load translations:', error);
    }
  },
  
  // Initialize language from URL or localStorage
  initializeLanguage: (): void => {
    // Check URL query parameter first
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');
    
    if (urlLang && SUPPORTED_LANGUAGES.some(lang => lang.code === urlLang)) {
      i18nService.changeLanguage(urlLang);
    } else {
      // Check localStorage
      const storedLang = localStorage.getItem('i18nextLng');
      if (storedLang && SUPPORTED_LANGUAGES.some(lang => lang.code === storedLang)) {
        i18nService.changeLanguage(storedLang);
      } else {
        // Use browser language or default
        const browserLang = navigator.language.split('-')[0];
        const supportedBrowserLang = SUPPORTED_LANGUAGES.some(lang => lang.code === browserLang);
        i18nService.changeLanguage(supportedBrowserLang ? browserLang : DEFAULT_LANGUAGE);
      }
    }
  },
  
  // Get current language direction
  getCurrentDirection: (): 'ltr' | 'rtl' => {
    const currentLang = i18nService.getCurrentLanguage();
    return i18nService.isRTL(currentLang) ? 'rtl' : 'ltr';
  },
  
  // Reload translations
  reloadTranslations: async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/i18n/reload`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        // Reload current language
        const currentLang = i18nService.getCurrentLanguage();
        await i18n.reloadResources(currentLang);
      }
    } catch (error) {
      console.error('Failed to reload translations:', error);
    }
  },
};

// Initialize language on app start
i18nService.initializeLanguage();

export default i18n; 