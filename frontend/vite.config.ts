import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // ΣΗΜΕΙΩΣΗ: το production build ΔΕΝ σερβίρεται πια με "vite preview" --
  // το frontend/Dockerfile χρησιμοποιεί nginx (βλ. nginx.conf), που δεν
  // έχει host-allowlist μηχανισμό. Το preview.allowedHosts block που ήταν
  // εδώ (Railway-specific, βλ. git history) είναι πλέον νεκρός κώδικας,
  // αφαιρέθηκε.
  test: {
    environment: 'jsdom',
  },
})
