// vite.config.ts — ФИНАЛЬНАЯ ВЕРСИЯ (2025)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    host: true,           // чтобы запускался на 0.0.0.0 (важно для ngrok/tunnel)
    port: 3000,
    strictPort: true,

    // РАЗРЕШАЕМ ВСЕ *.lhr.life и любые ngrok/tunnel навсегда
    allowedHosts: [
      'localhost',
      '.lhr.life',                    // ЭТО ГЛАВНОЕ — больше никогда не будет ошибки "add ... to allowedHosts"
      '127.0.0.1',
    ],

    // ПРОКСИ — теперь работает и с localhost:8000, и с любым https туннелем
    proxy: {
      '/api': {
        // МЕНЯЙ ТОЛЬКО ЭТУ СТРОЧКУ, КОГДА МЕНЯЕШЬ ТУННЕЛЬ
        target: 'http://localhost:8000',   // ← твой текущий туннель
        // target: 'http://localhost:8000',          // ← раскомментируй, когда тестируешь локально

        changeOrigin: true,
        secure: false,        // ngrok даёт самоподписанный SSL — отключаем проверку
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },

  // Для продакшена (vite build + preview)
  preview: {
    host: true,
    port: 3000,
    allowedHosts: ['.lhr.life'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // сюда тоже вставь свой продакшен-домен потом
        changeOrigin: true,
        secure: false,
      },
    },
  },
});