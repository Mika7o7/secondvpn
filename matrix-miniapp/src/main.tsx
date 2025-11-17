import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './pages/App';
import { api } from './api'; // ← ИМПОРТИРУЙ api

// === ДОБАВЬ ЭТО ===
declare global {
  interface Window {
    api?: typeof api;
  }
}
window.api = api; // ← ВОТ ЭТО ВАЖНО!

// === Остальное без изменений ===
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);