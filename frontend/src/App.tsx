import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { ActorsPage } from "./pages/ActorsPage";
import { ActorDetailPage } from "./pages/ActorDetailPage";
import { EventsListPage } from "./pages/EventsListPage";
import { EventDetailPage } from "./pages/EventDetailPage";
import { SynthesisPage } from "./pages/SynthesisPage";
import { ComparePage } from "./pages/ComparePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
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
