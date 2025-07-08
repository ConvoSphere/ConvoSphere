import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, Globe, Check } from 'lucide-react';
import { i18nService, SUPPORTED_LANGUAGES } from '../services/i18n';
import type { LanguageInfo } from '../services/i18n';

interface LanguageSelectorProps {
  className?: string;
  variant?: 'dropdown' | 'list';
  showNativeNames?: boolean;
  showFlags?: boolean;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  className = '',
  variant = 'dropdown',
  showNativeNames = true,
  showFlags = false,
}) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const currentLanguage = i18nService.getCurrentLanguage();
  const currentLangInfo = i18nService.getLanguageInfo(currentLanguage);

  const handleLanguageChange = async (language: LanguageInfo) => {
    await i18nService.changeLanguage(language.code);
    setIsOpen(false);
  };

  const getFlagEmoji = (languageCode: string): string => {
    const flagMap: Record<string, string> = {
      en: '🇺🇸',
      de: '🇩🇪',
      fr: '🇫🇷',
      es: '🇪🇸',
      ar: '🇸🇦',
      ja: '🇯🇵',
    };
    return flagMap[languageCode] || '🌐';
  };

  const LanguageOption: React.FC<{ language: LanguageInfo }> = ({ language }) => {
    const isSelected = language.code === currentLanguage;
    
    return (
      <button
        onClick={() => handleLanguageChange(language)}
        className={`
          flex items-center justify-between w-full px-4 py-2 text-left
          hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
          ${isSelected ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : ''}
          ${language.direction === 'rtl' ? 'text-right' : 'text-left'}
        `}
      >
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          {showFlags && (
            <span className="text-lg">{getFlagEmoji(language.code)}</span>
          )}
          <div className="flex flex-col">
            <span className="font-medium">{language.name}</span>
            {showNativeNames && language.native_name !== language.name && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {language.native_name}
              </span>
            )}
          </div>
        </div>
        {isSelected && (
          <Check className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        )}
      </button>
    );
  };

  if (variant === 'list') {
    return (
      <div className={`space-y-1 ${className}`}>
        {SUPPORTED_LANGUAGES.map((language) => (
          <LanguageOption key={language.code} language={language} />
        ))}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center space-x-2 px-3 py-2 rounded-lg border
          bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600
          hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          ${currentLangInfo?.direction === 'rtl' ? 'space-x-reverse' : ''}
        `}
        aria-label={t('common.select_language')}
      >
        <Globe className="w-4 h-4" />
        {showFlags && (
          <span className="text-sm">{getFlagEmoji(currentLanguage)}</span>
        )}
        <span className="font-medium">
          {showNativeNames ? currentLangInfo?.native_name : currentLangInfo?.name}
        </span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className={`
            absolute top-full mt-1 w-64 bg-white dark:bg-gray-800 border
            border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-20
            ${currentLangInfo?.direction === 'rtl' ? 'right-0' : 'left-0'}
          `}>
            <div className="py-1">
              {SUPPORTED_LANGUAGES.map((language) => (
                <LanguageOption key={language.code} language={language} />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSelector; 