import { lazy } from "react";
import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";

// React.lazy -- κάθε route page γίνεται δικό της JS chunk (code-splitting),
// ο browser κατεβάζει μόνο τον κώδικα της σελίδας που επισκέπτεται ο
// χρήστης, όχι όλη την εφαρμογή μονομιάς (βλ. build warning για
// >500KB single bundle). .then(m => ({ default: m.X })) χρειάζεται γιατί
// τα page components κάνουν named export (`export function X()`), όχι
// default export -- το lazy() θέλει module με .default. Το Suspense
// boundary που δείχνει το loading fallback ζει στο Layout.tsx (γύρω από
// το <Outlet/>), μία φορά για όλα τα routes.
const LandingPage = lazy(() => import("./pages/LandingPage").then((m) => ({ default: m.LandingPage })));
const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((m) => ({ default: m.DashboardPage })),
);
const ActorsPage = lazy(() => import("./pages/ActorsPage").then((m) => ({ default: m.ActorsPage })));
const ActorDetailPage = lazy(() =>
  import("./pages/ActorDetailPage").then((m) => ({ default: m.ActorDetailPage })),
);
const EventsListPage = lazy(() =>
  import("./pages/EventsListPage").then((m) => ({ default: m.EventsListPage })),
);
const EventDetailPage = lazy(() =>
  import("./pages/EventDetailPage").then((m) => ({ default: m.EventDetailPage })),
);
const SynthesisPage = lazy(() =>
  import("./pages/SynthesisPage").then((m) => ({ default: m.SynthesisPage })),
);
const ComparePage = lazy(() => import("./pages/ComparePage").then((m) => ({ default: m.ComparePage })));
const LoginPage = lazy(() => import("./pages/LoginPage").then((m) => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import("./pages/RegisterPage").then((m) => ({ default: m.RegisterPage })));

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LandingPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="actors" element={<ActorsPage />} />
        <Route path="actors/:id" element={<ActorDetailPage />} />
        <Route path="events" element={<EventsListPage />} />
        <Route path="events/:id" element={<EventDetailPage />} />
        <Route path="synthesis" element={<SynthesisPage />} />
        <Route path="compare" element={<ComparePage />} />
        {/* Public routes, ΟΧΙ protected -- βλ. σχόλιο στο AuthProvider.
            Ίδιο Layout (navbar) με όλα τα άλλα, κανένα guard γύρω τους. */}
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
      </Route>
    </Routes>
  );
}

export default App;
