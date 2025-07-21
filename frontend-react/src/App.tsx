import React from 'react';
import { ConfigProvider, theme as antdTheme } from 'antd';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import { I18nextProvider } from 'react-i18next';
// import i18n from './i18n';
import ThemeSwitcher from './components/ThemeSwitcher';

const App: React.FC = () => {
  return (
    // <I18nextProvider i18n={i18n}>
    <ConfigProvider
      theme={{
        algorithm: antdTheme.defaultAlgorithm,
        // Später: Custom Tokens für Farben, siehe Design-System
      }}
    >
      {/* <Router>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          ...
        </Routes>
      </Router> */}
      <div style={{ padding: 24 }}>
        <ThemeSwitcher />
        <div>ConvoSphere React Frontend – Grundgerüst</div>
      </div>
    </ConfigProvider>
    // </I18nextProvider>
  );
};

export default App;
