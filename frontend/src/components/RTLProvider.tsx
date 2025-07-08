import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { i18nService } from '../services/i18n';

interface RTLProviderProps {
  children: React.ReactNode;
}

export const RTLProvider: React.FC<RTLProviderProps> = ({ children }) => {
  const { i18n } = useTranslation();
  const [isRTL, setIsRTL] = useState(false);

  useEffect(() => {
    const updateDirection = () => {
      const currentLang = i18nService.getCurrentLanguage();
      const direction = i18nService.getCurrentDirection();
      setIsRTL(direction === 'rtl');
      
      // Update document attributes
      document.documentElement.dir = direction;
      document.documentElement.lang = currentLang;
      
      // Add/remove RTL class for CSS targeting
      if (direction === 'rtl') {
        document.documentElement.classList.add('rtl');
        document.body.classList.add('rtl');
      } else {
        document.documentElement.classList.remove('rtl');
        document.body.classList.remove('rtl');
      }
    };

    // Initial setup
    updateDirection();

    // Listen for language changes
    const handleLanguageChanged = () => {
      updateDirection();
    };

    i18n.on('languageChanged', handleLanguageChanged);

    return () => {
      i18n.off('languageChanged', handleLanguageChanged);
    };
  }, [i18n]);

  return (
    <div
      dir={isRTL ? 'rtl' : 'ltr'}
      className={`
        min-h-screen transition-all duration-300
        ${isRTL ? 'rtl' : 'ltr'}
      `}
    >
      {children}
    </div>
  );
};

export default RTLProvider; 