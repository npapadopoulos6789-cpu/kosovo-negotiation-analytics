import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listNegotiationEvents } from "../../api/negotiationEvents";
import { listIndicators } from "../../api/indicators";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import { Card } from "../../components/ui";
import { AdminNav } from "../../components/admin/AdminNav";

// Hub -- 3 κάρτες, μία ανά entity, με σύντομο πλήθος εγγραφών. Το ίδιο το
// route ("admin") είναι ήδη πίσω από RequireAdmin (βλ. App.tsx) -- καμία
// επιπλέον auth logic εδώ.
export function AdminPage() {
  const { countryMap } = useCountryLookup();
  const events = useQuery({ queryKey: ["negotiation-events"], queryFn: listNegotiationEvents });
  const indicators = useQuery({ queryKey: ["indicators"], queryFn: listIndicators });

  return (
    <div>
      <h1>Admin</h1>
      <AdminNav />
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Create, edit, and delete the underlying data -- same backend endpoints as everywhere
        else on this platform, just with a form instead of Swagger.
      </p>

      <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginTop: "1rem" }}>
        <Link to="/admin/countries" style={{ textDecoration: "none", color: "inherit" }}>
          <Card>
            <strong>Countries</strong>
            <p style={{ marginTop: "0.5rem", color: "var(--color-text-muted)" }}>
              {countryMap.size} {countryMap.size === 1 ? "actor" : "actors"}
            </p>
          </Card>
        </Link>
        <Link to="/admin/events" style={{ textDecoration: "none", color: "inherit" }}>
          <Card>
            <strong>Negotiation Events</strong>
            <p style={{ marginTop: "0.5rem", color: "var(--color-text-muted)" }}>
              {events.data ? `${events.data.length} events` : "…"}
            </p>
          </Card>
        </Link>
        <Link to="/admin/indicators" style={{ textDecoration: "none", color: "inherit" }}>
          <Card>
            <strong>Indicators</strong>
            <p style={{ marginTop: "0.5rem", color: "var(--color-text-muted)" }}>
              {indicators.data ? `${indicators.data.length} indicators` : "…"}
            </p>
          </Card>
        </Link>
      </div>
    </div>
  );
}
