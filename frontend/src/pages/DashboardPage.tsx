import { useQuery } from "@tanstack/react-query";
import { listNegotiationEvents } from "../api/negotiationEvents";
import { ZopaImplementationChart } from "../components/charts/ZopaImplementationChart";
import { PowerIndexBreakdownChart } from "../components/charts/PowerIndexBreakdownChart";
import { LoadingState, ErrorState, EmptyState } from "../components/ui";

export function DashboardPage() {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ["negotiation-events"],
    queryFn: listNegotiationEvents,
  });

  return (
    <div>
      <h1>Dashboard</h1>

      <h2>ZOPA size vs. implementation success</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Does a wider Zone of Possible Agreement predict a better-implemented outcome? Only events
        that reached an agreement (implementation_success recorded) are shown.
      </p>
      {isLoading && <LoadingState label="Loading events…" />}
      {error && <ErrorState error={error} />}
      {events && events.every((e) => e.implementation_success === null) && (
        <EmptyState label="No events with recorded implementation_success yet." />
      )}
      {events && <ZopaImplementationChart events={events} />}

      <h2 style={{ marginTop: "2rem" }}>Power Index breakdown</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Economic (40%) / Military (40%) / Social (20%) components of the Power Index, Serbia vs.
        Kosovo. Only years with indicator data for both countries are selectable.
      </p>
      <PowerIndexBreakdownChart />
    </div>
  );
}
