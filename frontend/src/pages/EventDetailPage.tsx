import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getNegotiationEvent } from "../api/negotiationEvents";
import { Card, Badge, LoadingState, ErrorState } from "../components/ui";
import { RIPENESS_TONE, ZOPA_TONE } from "./eventBadgeTones";

export function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const eventId = Number(id);

  const { data: event, isLoading, error } = useQuery({
    queryKey: ["negotiation-events", eventId],
    queryFn: () => getNegotiationEvent(eventId),
    enabled: Number.isFinite(eventId),
  });

  if (isLoading) return <LoadingState label="Loading event…" />;
  if (error) return <ErrorState error={error} />;
  if (!event) return null;

  const hasBatna = event.batna_side_a || event.batna_side_b;
  const hasRedLines = event.red_lines_side_a || event.red_lines_side_b;

  return (
    <div>
      <Link to="/events">&larr; Back to Events</Link>
      <h1>{event.title}</h1>
      <p style={{ color: "var(--color-text-muted)" }}>{event.date}</p>

      <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", margin: "0.5rem 0 1rem" }}>
        {event.zopa_size && <Badge tone={ZOPA_TONE[event.zopa_size]}>ZOPA: {event.zopa_size}</Badge>}
        {event.ripeness_status && (
          <Badge tone={RIPENESS_TONE[event.ripeness_status]}>{event.ripeness_status}</Badge>
        )}
        {event.negotiation_type && <Badge tone="neutral">{event.negotiation_type}</Badge>}
      </div>

      {event.description && <Card>{event.description}</Card>}

      {event.zopa_reasoning && (
        <div style={{ marginTop: "1rem" }}>
          <h3>ZOPA reasoning</h3>
          <p>{event.zopa_reasoning}</p>
        </div>
      )}

      {event.ripeness_reasoning && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Ripeness reasoning</h3>
          <p>{event.ripeness_reasoning}</p>
        </div>
      )}

      {hasBatna && (
        <div style={{ marginTop: "1rem" }}>
          <h3>BATNA</h3>
          <div style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
            {event.batna_side_a && (
              <Card>
                <strong>Side A</strong>
                <p>{event.batna_side_a}</p>
              </Card>
            )}
            {event.batna_side_b && (
              <Card>
                <strong>Side B</strong>
                <p>{event.batna_side_b}</p>
              </Card>
            )}
          </div>
        </div>
      )}

      {hasRedLines && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Red lines</h3>
          <div style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
            {event.red_lines_side_a && (
              <Card>
                <strong>Side A</strong>
                <p>{event.red_lines_side_a}</p>
              </Card>
            )}
            {event.red_lines_side_b && (
              <Card>
                <strong>Side B</strong>
                <p>{event.red_lines_side_b}</p>
              </Card>
            )}
          </div>
        </div>
      )}

      <div style={{ marginTop: "1rem" }}>
        <h3>Weights</h3>
        <p>
          Economic {event.economic_weight} · Military {event.military_weight} · Social{" "}
          {event.social_weight} (sum to 10, see CLAUDE.md business rule 1)
        </p>
        {event.implementation_success !== null && (
          <p>Implementation success: {(event.implementation_success * 100).toFixed(0)}%</p>
        )}
      </div>

      {event.participants.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Participants</h3>
          <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
            {event.participants.map((p) => (
              <Badge key={p.id} tone="neutral">
                {p.country_name} ({p.role})
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
