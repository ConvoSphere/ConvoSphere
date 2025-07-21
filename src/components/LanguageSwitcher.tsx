import React from 'react';
import { Select } from 'antd';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation();
  return (
    <Select
      value={i18n.language}
      onChange={lng => i18n.changeLanguage(lng)}
      style={{ width: 120 }}
      aria-label="Language Switcher"
      options={[
        { value: 'en', label: t('language.en') },
        { value: 'de', label: t('language.de') },
      ]}
    />
  );
};

export default LanguageSwitcher; 