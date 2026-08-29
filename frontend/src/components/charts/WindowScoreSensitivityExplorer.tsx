import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import { getWindowScoreBreakdown } from "../../api/analytics";
import { ApiError } from "../../api/client";
import type { WindowScoreBreakdown } from "../../api/types";
import { LoadingState, ErrorState } from "../ui";

// Ίδιος περιορισμός με τα υπόλοιπα Window Score charts -- μόνο αυτά τα 4
// KEY_YEARS έχουν πλήρες Power Index και για τις δύο χώρες.
const YEARS = [2005, 2007, 2013, 2023] as const;

interface Weights {
  symmetry: number;
  trend: number;
  social: number;
}

// Το επίσημο βάρος του backend (calculate_window_score, analytics.py) --
// σταθερό default, ΟΧΙ κάτι που ο χρήστης βλέπει σαν "σωστή" τιμή, απλά
// το σημείο εκκίνησης πριν πειραματιστεί.
const DEFAULT_WEIGHTS: Weights = { symmetry: 50, trend: 30, social: 20 };

async function breakdownOrNull(
  year: number,
  serbiaId: number,
  kosovoId: number,
): Promise<WindowScoreBreakdown | null> {
  try {
    return await getWindowScoreBreakdown(year, serbiaId, kosovoId);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

// 3-way "άθροισμα=100" slider constraint: όταν ο χρήστης αλλάζει ΕΝΑ
// slider, τα άλλα δύο προσαρμόζονται ΑΝΑΛΟΓΙΚΑ στο προηγούμενο μεταξύ
// τους ποσοστό (όχι ισόποσα πάντα) -- αν π.χ. trend:social ήταν ήδη 3:1,
// μένουν στην ίδια αναλογία 3:1 μετά την προσαρμογή. Το δεύτερο από τα
// δύο "άλλα" υπολογίζεται ως το υπόλοιπο (ΟΧΙ ξεχωριστό rounding), ώστε
// το άθροισμα να είναι ΠΑΝΤΑ ακριβώς 100, χωρίς rounding drift.
function redistribute(changed: keyof Weights, rawNewValue: number, current: Weights): Weights {
  const newValue = Math.max(0, Math.min(100, Math.round(rawNewValue)));
  const otherKeys = (Object.keys(current) as (keyof Weights)[]).filter((k) => k !== changed);
  const [keyA, keyB] = otherKeys;
  const remaining = 100 - newValue;
  const oldOtherSum = current[keyA] + current[keyB];

  let valueA: number;
  if (oldOtherSum === 0) {
    valueA = Math.round(remaining / 2);
  } else {
    valueA = Math.round((remaining * current[keyA]) / oldOtherSum);
  }
  const valueB = remaining - valueA;

  return { ...current, [changed]: newValue, [keyA]: valueA, [keyB]: valueB } as Weights;
}

interface SliderRowProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
}

function SliderRow({ label, value, onChange }: SliderRowProps) {
  return (
    <label style={{ display: "block", marginBottom: "0.75rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", marginBottom: "0.2rem" }}>
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ width: "100%" }}
      />
    </label>
  );
}

// Κλείσιμο του Dashboard, ΜΕΤΑ το "central finding" chart. Ο χρήστης
// ξαναϋπολογίζει το Window Score με ΔΙΚΑ ΤΟΥ weights αντί για το
// επίσημο 50/30/20 -- 1 backend call ανά έτος στο mount (τα raw
// components), μετά όλα client-side, καμία επιπλέον κλήση ανά slider
// drag.
export function WindowScoreSensitivityExplorer() {
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const serbia = [...countryMap.values()].find((c) => c.name === "Serbia");
  const kosovo = [...countryMap.values()].find((c) => c.name === "Kosovo");

  const [weights, setWeights] = useState<Weights>(DEFAULT_WEIGHTS);

  const query = useQuery({
    queryKey: ["window-score-breakdown", "sensitivity-explorer", serbia?.id, kosovo?.id],
    queryFn: async () => {
      const results = await Promise.all(
        YEARS.map((year) => breakdownOrNull(year, serbia!.id, kosovo!.id)),
      );
      return YEARS.map((year, i) => ({ year, breakdown: results[i] }));
    },
    enabled: !!serbia && !!kosovo,
  });

  if (countriesLoading || query.isLoading) {
    return <LoadingState label="Loading sensitivity explorer…" />;
  }
  if (!serbia || !kosovo) {
    return <ErrorState error={new Error("Serbia/Kosovo data not available.")} />;
  }
  if (query.error) return <ErrorState error={query.error} />;

  const rows = (query.data ?? []).filter(
    (r): r is { year: (typeof YEARS)[number]; breakdown: WindowScoreBreakdown } =>
      r.breakdown !== null,
  );

  // Ξαναϋπολογισμός με τα τρέχοντα weights -- ΙΔΙΟΣ τύπος με
  // calculate_window_score (analytics.py), απλά με μεταβλητά αντί για
  // σταθερά 0.5/0.3/0.2.
  const data = rows.map(({ year, breakdown }) => ({
    year,
    score:
      Math.round(
        (breakdown.symmetry_score * weights.symmetry +
          breakdown.trend_score * weights.trend +
          breakdown.social_stability_score * weights.social) /
          100 *
          100,
      ) / 100,
  }));

  const topYear =
    data.length > 0
      ? data.reduce((best, row) => (row.score > best.score ? row : best)).year
      : null;

  const isDefault =
    weights.symmetry === DEFAULT_WEIGHTS.symmetry &&
    weights.trend === DEFAULT_WEIGHTS.trend &&
    weights.social === DEFAULT_WEIGHTS.social;

  return (
    <div>
      <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted)" }}>
        The 50% / 30% / 20% weighting used throughout this platform is my own theoretical
        judgment, not something empirically derived from the data (see Methodology in the
        README). Try the sliders below to see how robust the 2013 finding actually is under
        different assumptions about what matters most for a negotiation window.
      </p>

      <div style={{ maxWidth: "420px", margin: "1rem 0" }}>
        <SliderRow
          label="Power symmetry"
          value={weights.symmetry}
          onChange={(v) => setWeights((prev) => redistribute("symmetry", v, prev))}
        />
        <SliderRow
          label="Mutual declining trend"
          value={weights.trend}
          onChange={(v) => setWeights((prev) => redistribute("trend", v, prev))}
        />
        <SliderRow
          label="Social stability"
          value={weights.social}
          onChange={(v) => setWeights((prev) => redistribute("social", v, prev))}
        />
        <button type="button" onClick={() => setWeights(DEFAULT_WEIGHTS)} disabled={isDefault}>
          Reset to 50/30/20
        </button>
      </div>

      {topYear !== null && (
        <p>
          With your weights, <strong>{topYear}</strong> scores highest.
        </p>
      )}

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e6" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value) => [value, "Window Score (your weights)"]} />
          <Bar dataKey="score" radius={[3, 3, 0, 0]}>
            {data.map((row) => (
              <Cell key={row.year} fill={row.year === topYear ? "#22314f" : "#9aa5b1"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
