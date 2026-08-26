import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Vite preview server (χρησιμοποιείται στο Dockerfile/Railway, βλ. CMD
  // "vite preview --host 0.0.0.0") μπλοκάρει από προεπιλογή requests με
  // Host header που δεν αναγνωρίζει -- ασφαλές default, αλλά χρειάζεται
  // ρητή λίστα για domains πέρα από localhost. Wildcard suffix (τελεία
  // μπροστά) αντί για το ακριβές σημερινό domain -- επιτρέπει οποιοδήποτε
  // μελλοντικό Railway-generated *.up.railway.app subdomain, ώστε ένα
  // rename/redeploy να μην ξαναφέρει το ίδιο block error. host: true ώστε
  // ο server να ακούει σε 0.0.0.0 αντί μόνο localhost (απαραίτητο μέσα σε
  // Docker container).
  preview: {
    allowedHosts: ['.up.railway.app'],
    host: true,
  },
  test: {
    environment: 'jsdom',
  },
})
