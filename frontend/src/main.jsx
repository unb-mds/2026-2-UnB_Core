import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './components/layout/layout.css'
import App from './App.jsx'
import { iniciarTema } from './state/theme'

iniciarTema()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
