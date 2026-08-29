import { Link } from "react-router-dom";
import { useCountryLookup } from "../hooks/useCountryLookup";
import { Card, Badge, LoadingState, ErrorState, EmptyState } from "../components/ui";

// "Actors" -- UI-facing label, βλ. Layout.tsx/PROJECT_STATUS.md για την
// εξήγηση. Το underlying resource/model παραμένει Country/countries.
export function ActorsPage() {
  const { countryMap, isLoading, error } = useCountryLookup();
  const actors = [...countryMap.values()];

  if (isLoading) return <LoadingState label="Loading actors…" />;
  if (error) return <ErrorState error={error} />;
  if (actors.length === 0) return <EmptyState label="No actors available yet." />;

  return (
    <div>
      <h1>Actors</h1>
      <p>States and international actors with a role in the negotiations.</p>
      <div style={{ display: "grid", gap: "0.75rem" }}>
        {actors.map((actor) => (
          <Link key={actor.id} to={`/actors/${actor.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <Card>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", flexWrap: "wrap" }}>
                <strong>{actor.name}</strong>
                <Badge>{actor.actor_type}</Badge>
                {actor.geopolitical_bloc && <Badge tone="neutral">{actor.geopolitical_bloc}</Badge>}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
