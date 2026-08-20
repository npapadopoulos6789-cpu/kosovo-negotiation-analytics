import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { ActorsPage } from "./pages/ActorsPage";
import { ActorDetailPage } from "./pages/ActorDetailPage";
import { EventsPage } from "./pages/EventsPage";
import { SynthesisPage } from "./pages/SynthesisPage";
import { ComparePage } from "./pages/ComparePage";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="actors" element={<ActorsPage />} />
        <Route path="actors/:id" element={<ActorDetailPage />} />
        <Route path="events" element={<EventsPage />} />
        <Route path="synthesis" element={<SynthesisPage />} />
        <Route path="compare" element={<ComparePage />} />
      </Route>
    </Routes>
  );
}

export default App;
