import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

// Ένα QueryClient για όλη την εφαρμογή -- κρατάει το cache των react-query
// hooks (π.χ. useCountryLookup). Χωρίς Provider, κάθε useQuery/useMutation
// hook σκάει με "No QueryClient set" στο runtime.
const queryClient = new QueryClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
