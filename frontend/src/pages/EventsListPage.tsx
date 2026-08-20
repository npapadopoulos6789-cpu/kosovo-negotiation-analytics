import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listNegotiationEvents } from "../api/negotiationEvents";
import { Card, Badge, LoadingState, ErrorState, EmptyState } from "../components/ui";
import { RIPENESS_TONE, ZOPA_TONE } from "./eventBadgeTones";

export function EventsListPage() {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ["negotiation-events"],
    queryFn: listNegotiationEvents,
  });

  if (isLoading) return <LoadingState label="Loading events…" />;
  if (error) return <ErrorState error={error} />;
  if (!events || events.length === 0) return <EmptyState label="No negotiation events seeded yet." />;

  const sorted = [...events].sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div>
      <h1>Negotiation Events</h1>
      <p>Chronological record of the negotiation events analyzed in this dataset.</p>
      <div style={{ display: "grid", gap: "0.75rem" }}>
        {sorted.map((event) => (
          <Link key={event.id} to={`/events/${event.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <Card>
              <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "0.5rem" }}>
                <strong>{event.title}</strong>
                <span style={{ color: "var(--color-text-muted)" }}>{event.date}</span>
              </div>
              <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                {event.zopa_size && <Badge tone={ZOPA_TONE[event.zopa_size]}>ZOPA: {event.zopa_size}</Badge>}
                {event.ripeness_status && (
                  <Badge tone={RIPENESS_TONE[event.ripeness_status]}>{event.ripeness_status}</Badge>
                )}
                {event.negotiation_type && <Badge tone="neutral">{event.negotiation_type}</Badge>}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
