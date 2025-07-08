// ConvoSphere Frontend Entry
import { RouterProvider } from 'react-router-dom';
import { Suspense } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import RTLProvider from './components/RTLProvider';
import router from './router';
import './services/i18n'; // Initialize i18n
import './styles/rtl.css'; // Import RTL styles

const App = () => (
  <ErrorBoundary>
    <Suspense fallback={<div>Loading...</div>}>
      <RTLProvider>
        <RouterProvider router={router} />
      </RTLProvider>
    </Suspense>
  </ErrorBoundary>
);

export default App;