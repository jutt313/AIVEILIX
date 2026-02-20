import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Silence all console output in production
if (import.meta.env.PROD) {
  console.log = () => {}
  console.warn = () => {}
  console.error = () => {}
  console.info = () => {}
  console.debug = () => {}
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
