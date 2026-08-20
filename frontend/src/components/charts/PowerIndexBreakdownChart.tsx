import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import { getPowerIndexBreakdown } from "../../api/analytics";
import { ApiError } from "../../api/client";
import { LoadingState, ErrorState, EmptyState } from "../ui";

// Μόνο αυτά τα 4 από τα 6 KEY_YEARS (backend/app/services/analytics.py)
// έχουν πλήρες Power Index ΚΑΙ για τις δύο χώρες -- 1999/2008 λείπουν
// indicators για το Κόσοβο (βλ. CLAUDE.md business rule 5, seed.py).
const AVAILABLE_YEARS = [2005, 2007, 2013, 2023] as const;

// 404 από το backend σημαίνει "ανεπαρκή δεδομένα" (analytics.py), ΟΧΙ
// σφάλμα -- ο caller το μετατρέπει σε null αντί να το αφήσει να σκάσει
// σε ErrorState. Ίδιο convention με το DashboardPage's KEY_YEARS handling.
async function breakdownOrNull(countryId: number, year: number) {
  try {
    return await getPowerIndexBreakdown(countryId, year);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

interface ChartRow {
  category: string;
  Serbia: number | null;
  Kosovo: number | null;
}

export function PowerIndexBreakdownChart() {
  const [year, setYear] = useState<(typeof AVAILABLE_YEARS)[number]>(2013);
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const serbia = [...countryMap.values()].find((c) => c.name === "Serbia");
  const kosovo = [...countryMap.values()].find((c) => c.name === "Kosovo");

  const breakdown = useQuery({
    queryKey: ["power-index-breakdown", serbia?.id, kosovo?.id, year],
    queryFn: async () => {
      const [serbiaData, kosovoData] = await Promise.all([
        breakdownOrNull(serbia!.id, year),
        breakdownOrNull(kosovo!.id, year),
      ]);
      return { serbiaData, kosovoData };
    },
    enabled: !!serbia && !!kosovo,
  });

  if (countriesLoading) return <LoadingState label="Loading actors…" />;
  if (!serbia || !kosovo) {
    return <ErrorState error={new Error("Serbia/Kosovo not found among seeded actors.")} />;
  }

  const { serbiaData, kosovoData } = breakdown.data ?? {};

  const data: ChartRow[] = serbiaData && kosovoData
    ? [
        { category: "Economic", Serbia: serbiaData.economic, Kosovo: kosovoData.economic },
        { category: "Military", Serbia: serbiaData.military, Kosovo: kosovoData.military },
        { category: "Social", Serbia: serbiaData.social, Kosovo: kosovoData.social },
      ]
    : [];

  return (
    <div>
      <label style={{ fontSize: "0.9rem" }}>
        Year:{" "}
        <select value={year} onChange={(e) => setYear(Number(e.target.value) as typeof year)}>
          {AVAILABLE_YEARS.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </label>

      {breakdown.isLoading && <LoadingState label="Loading Power Index breakdown…" />}
      {breakdown.error && <ErrorState error={breakdown.error} />}
      {breakdown.data && (!serbiaData || !kosovoData) && (
        <EmptyState
          label={`Insufficient indicator data for ${year} (Serbia and/or Kosovo missing an ECONOMIC/MILITARY/SOCIAL_UNREST category that year).`}
        />
      )}
      {data.length > 0 && (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e6" />
            <XAxis dataKey="category" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: "0.85rem" }} />
            <Bar dataKey="Serbia" fill="#22314f" radius={[3, 3, 0, 0]} />
            <Bar dataKey="Kosovo" fill="#9aa5b1" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
