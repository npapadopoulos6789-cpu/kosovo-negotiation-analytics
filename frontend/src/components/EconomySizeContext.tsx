import { useQuery } from "@tanstack/react-query";
import { useCountryLookup } from "../hooks/useCountryLookup";
import { listIndicatorsByCountry } from "../api/indicators";
import { Card, LoadingState, ErrorState, EmptyState } from "./ui";

const GDP_TYPE = "GDP_absolute_usd";

function formatUsd(value: number): string {
  return `$${(value / 1e9).toFixed(1)}B`;
}

// Μικρό, καθαρά πληροφοριακό context box -- δείχνει τη δυσαναλογία μεγέθους
// των δύο οικονομιών (απόλυτο GDP), ΞΕΧΩΡΙΣΤΟ από το Power Index (που
// σκόπιμα ΔΕΝ περιλαμβάνει απόλυτο μέγεθος -- μετράει δυναμική/κατεύθυνση,
// όχι μέγεθος. Βλ. SEED_SOURCE.md). Υπολογίζεται δυναμικά από τα πραγματικά
// δεδομένα (όχι hardcoded λόγος) -- το πιο πρόσφατο έτος όπου ΚΑΙ οι δύο
// χώρες έχουν GDP_absolute_usd.
export function EconomySizeContext() {
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const serbia = [...countryMap.values()].find((c) => c.name === "Serbia");
  const kosovo = [...countryMap.values()].find((c) => c.name === "Kosovo");

  const query = useQuery({
    queryKey: ["gdp-absolute", serbia?.id, kosovo?.id],
    queryFn: async () => {
      const [serbiaIndicators, kosovoIndicators] = await Promise.all([
        listIndicatorsByCountry(serbia!.id),
        listIndicatorsByCountry(kosovo!.id),
      ]);
      const serbiaGdp = new Map(
        serbiaIndicators.filter((i) => i.indicator_type === GDP_TYPE).map((i) => [i.year, i.value]),
      );
      const kosovoGdp = new Map(
        kosovoIndicators.filter((i) => i.indicator_type === GDP_TYPE).map((i) => [i.year, i.value]),
      );
      const sharedYears = [...serbiaGdp.keys()].filter((y) => kosovoGdp.has(y)).sort((a, b) => b - a);
      const latestYear = sharedYears[0];
      if (latestYear === undefined) return null;
      return {
        year: latestYear,
        serbiaGdp: serbiaGdp.get(latestYear)!,
        kosovoGdp: kosovoGdp.get(latestYear)!,
      };
    },
    enabled: !!serbia && !!kosovo,
  });

  if (countriesLoading || query.isLoading) return <LoadingState label="Loading economy size context…" />;
  if (query.error) return <ErrorState error={query.error} />;
  if (!query.data) return <EmptyState label="No absolute GDP data available for both countries in the same year." />;

  const { year, serbiaGdp, kosovoGdp } = query.data;
  const ratio = serbiaGdp / kosovoGdp;

  return (
    <Card>
      <p>
        Serbia's economy is approximately <strong>{ratio.toFixed(1)}x</strong> the size of
        Kosovo's ({year}) -- {formatUsd(serbiaGdp)} vs. {formatUsd(kosovoGdp)} GDP (World Bank,
        current US$).
      </p>
      <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "0.4rem" }}>
        Context only -- absolute economic size is not part of the Power Index above, which
        measures relative trend/direction rather than scale (see SEED_SOURCE.md).
      </p>
    </Card>
  );
}
