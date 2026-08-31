import { lazy } from "react";
import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { RequireAdmin } from "./auth/RequireAdmin";

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
const MethodologyPage = lazy(() =>
  import("./pages/MethodologyPage").then((m) => ({ default: m.MethodologyPage })),
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

// Admin-only, ΣΚΟΠΙΜΑ δικά τους chunks -- σπάνια επισκέψιμα, δεν αξίζει
// να βαραίνουν το bundle κανενός VIEWER/ανώνυμου επισκέπτη.
const AdminPage = lazy(() => import("./pages/admin/AdminPage").then((m) => ({ default: m.AdminPage })));
const AdminCountriesPage = lazy(() =>
  import("./pages/admin/AdminCountriesPage").then((m) => ({ default: m.AdminCountriesPage })),
);
const AdminIndicatorsPage = lazy(() =>
  import("./pages/admin/AdminIndicatorsPage").then((m) => ({ default: m.AdminIndicatorsPage })),
);
const AdminEventsPage = lazy(() =>
  import("./pages/admin/AdminEventsPage").then((m) => ({ default: m.AdminEventsPage })),
);

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<LandingPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="methodology" element={<MethodologyPage />} />
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
        {/* /admin/* -- layout route, το RequireAdmin ελέγχει role=ADMIN
            μία φορά και ρεντάρει <Outlet/> για όλα τα children. Και τα 4
            entities (Countries/Events/Indicators + hub) καλυμμένα. */}
        <Route path="admin" element={<RequireAdmin />}>
          <Route index element={<AdminPage />} />
          <Route path="countries" element={<AdminCountriesPage />} />
          <Route path="events" element={<AdminEventsPage />} />
          <Route path="indicators" element={<AdminIndicatorsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
