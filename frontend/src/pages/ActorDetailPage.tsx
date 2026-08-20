import type { CSSProperties } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useCountryLookup } from "../hooks/useCountryLookup";
import { listIndicatorsByCountry } from "../api/indicators";
import type { Indicator, IndicatorCategory } from "../api/types";
import { Card, Badge, LoadingState, ErrorState, EmptyState } from "../components/ui";

const CATEGORIES: IndicatorCategory[] = ["ECONOMIC", "MILITARY", "SOCIAL_UNREST"];

function groupByCategory(indicators: Indicator[]): Record<IndicatorCategory, Indicator[]> {
  const grouped: Record<IndicatorCategory, Indicator[]> = {
    ECONOMIC: [],
    MILITARY: [],
    SOCIAL_UNREST: [],
  };
  for (const indicator of indicators) {
    grouped[indicator.category].push(indicator);
  }
  for (const category of CATEGORIES) {
    grouped[category].sort((a, b) => a.year - b.year);
  }
  return grouped;
}

export function ActorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const countryId = Number(id);

  const { countryMap, isLoading: actorLoading, error: actorError } = useCountryLookup();
  const actor = countryMap.get(countryId);

  const indicators = useQuery({
    queryKey: ["indicators", "by-country", countryId],
    queryFn: () => listIndicatorsByCountry(countryId),
    enabled: Number.isFinite(countryId),
  });

  if (actorLoading) return <LoadingState label="Loading actor…" />;
  if (actorError) return <ErrorState error={actorError} />;
  if (!actor) return <EmptyState label={`No actor with id ${id}.`} />;

  const grouped = indicators.data ? groupByCategory(indicators.data) : null;

  return (
    <div>
      <Link to="/actors">&larr; Back to Actors</Link>
      <h1>{actor.name}</h1>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", margin: "0.5rem 0 1rem" }}>
        <Badge>{actor.actor_type}</Badge>
        {actor.geopolitical_bloc && <Badge tone="neutral">{actor.geopolitical_bloc}</Badge>}
        {actor.country_code && <Badge tone="neutral">{actor.country_code}</Badge>}
        {actor.recognized_kosovo === true && <Badge tone="positive">recognizes Kosovo</Badge>}
        {actor.recognized_kosovo === false && <Badge tone="negative">does not recognize Kosovo</Badge>}
      </div>

      {actor.role_description && <Card>{actor.role_description}</Card>}

      <h2 style={{ marginTop: "1.5rem" }}>Indicators</h2>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
        Only Serbia and Kosovo carry Power Index indicators (see CLAUDE.md) -- other actors
        typically have none here.
      </p>
      {indicators.isLoading && <LoadingState label="Loading indicators…" />}
      {indicators.error && <ErrorState error={indicators.error} />}
      {grouped &&
        CATEGORIES.every((c) => grouped[c].length === 0) && (
          <EmptyState label="No indicators recorded for this actor." />
        )}
      {grouped &&
        CATEGORIES.map((category) =>
          grouped[category].length === 0 ? null : (
            <div key={category} style={{ marginBottom: "1rem" }}>
              <h3>{category}</h3>
              <div style={{ overflowX: "auto" }}>
                <table style={{ borderCollapse: "collapse", width: "100%" }}>
                  <thead>
                    <tr>
                      <th style={cellStyle}>Year</th>
                      <th style={cellStyle}>Type</th>
                      <th style={cellStyle}>Value</th>
                      <th style={cellStyle}>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grouped[category].map((ind) => (
                      <tr key={ind.id}>
                        <td style={cellStyle}>{ind.year}</td>
                        <td style={cellStyle}>{ind.indicator_type}</td>
                        <td style={cellStyle}>
                          {ind.value}
                          {ind.unit ? ` ${ind.unit}` : ""}
                        </td>
                        <td style={cellStyle}>{ind.source ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ),
        )}
    </div>
  );
}

const cellStyle: CSSProperties = {
  border: "1px solid var(--color-border)",
  padding: "0.4rem 0.6rem",
  textAlign: "left",
  fontSize: "0.9rem",
};
