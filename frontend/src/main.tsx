import { StrictMode } from 'react'
import { Provider } from 'react-redux'
import { store } from './app/store'
import { authService } from './services/authService'
import { createRoot } from 'react-dom/client'
import './styles/global.css'
import App from './App.tsx'

// Initialize authentication state
authService.initializeAuth()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>,
)
