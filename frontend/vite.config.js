import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy /api to the Django dev server so the frontend can call it without CORS worries.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
