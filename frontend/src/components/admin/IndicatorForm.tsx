import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createIndicator, updateIndicator } from "../../api/indicators";
import { useCountryLookup } from "../../hooks/useCountryLookup";
import type { Indicator, IndicatorCategory, IndicatorConfidence } from "../../api/types";
import { ApiError } from "../../api/client";
import { Card } from "../ui";

const CATEGORIES: IndicatorCategory[] = ["ECONOMIC", "MILITARY", "SOCIAL_UNREST"];
const CONFIDENCE_LEVELS: IndicatorConfidence[] = ["EXACT", "CHART_READ", "RANGE"];

// <datalist> suggestions, ΟΧΙ hard enum -- οι 8 τιμές που μπαίνουν στο
// Power Index (βλ. analytics.py NORMALIZATION_RANGES), αλλά το backend
// δέχεται οποιοδήποτε άλλο indicator_type (π.χ. context-only, ή νέο type
// για μελλοντική μελέτη περίπτωσης) και το πεδίο εδώ δεν το περιορίζει.
const KNOWN_INDICATOR_TYPES = [
  "GDP_growth",
  "GDP_absolute_usd",
  "unemployment_rate",
  "trade_share_eu",
  "FDI_net_inflows_pct_gdp",
  "military_expenditure_pct_gdp",
  "military_expenditure_usd",
  "freedom_house_score",
];

interface IndicatorFormProps {
  editing?: Indicator;
  onSuccess: (message: string) => void;
  onCancel: () => void;
}

export function IndicatorForm({ editing, onSuccess, onCancel }: IndicatorFormProps) {
  const queryClient = useQueryClient();
  const { countryMap, isLoading: countriesLoading } = useCountryLookup();
  const countries = [...countryMap.values()].sort((a, b) => a.name.localeCompare(b.name));

  const [countryId, setCountryId] = useState<string>(
    editing ? String(editing.country_id) : countries[0] ? String(countries[0].id) : "",
  );
  const [category, setCategory] = useState<IndicatorCategory>(editing?.category ?? "ECONOMIC");
  const [indicatorType, setIndicatorType] = useState(editing?.indicator_type ?? "");
  const [year, setYear] = useState(editing ? String(editing.year) : "");
  const [value, setValue] = useState(editing ? String(editing.value) : "");
  const [unit, setUnit] = useState(editing?.unit ?? "");
  const [source, setSource] = useState(editing?.source ?? "");
  const [isVerified, setIsVerified] = useState(editing?.is_verified ?? false);
  const [confidence, setConfidence] = useState<IndicatorConfidence | "">(editing?.confidence ?? "");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      const payload = {
        country_id: Number(countryId),
        category,
        indicator_type: indicatorType.trim(),
        year: Number(year),
        value: Number(value),
        unit: unit.trim() === "" ? null : unit.trim(),
        source: source.trim(),
        is_verified: isVerified,
        confidence: confidence === "" ? null : confidence,
      };
      return editing ? updateIndicator(editing.id, payload) : createIndicator(payload);
    },
    onSuccess: () => {
      // Prefix match -- πιάνει και τα ["indicators", "by-country", id] keys
      // που κρατάει το ActorDetailPage/EconomySizeContext.
      queryClient.invalidateQueries({ queryKey: ["indicators"] });
      onSuccess(
        editing
          ? `Indicator "${indicatorType}" (${year}) updated successfully.`
          : `Indicator "${indicatorType}" (${year}) created successfully.`,
      );
    },
    onError: (err) => {
      setError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Save failed.");
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  }

  if (countriesLoading) return <Card>Loading countries…</Card>;

  return (
    <Card>
      <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>
        {editing ? `Edit indicator #${editing.id}` : "New indicator"}
      </h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxWidth: "420px" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Country
          <select value={countryId} onChange={(e) => setCountryId(e.target.value)} required>
            {countries.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Category
          <select value={category} onChange={(e) => setCategory(e.target.value as IndicatorCategory)}>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Indicator type
          <input
            type="text"
            list="known-indicator-types"
            value={indicatorType}
            onChange={(e) => setIndicatorType(e.target.value)}
            required
          />
          <datalist id="known-indicator-types">
            {KNOWN_INDICATOR_TYPES.map((t) => (
              <option key={t} value={t} />
            ))}
          </datalist>
        </label>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem", flex: 1 }}>
            Year
            <input type="number" value={year} onChange={(e) => setYear(e.target.value)} required />
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem", flex: 1 }}>
            Value
            <input type="number" step="any" value={value} onChange={(e) => setValue(e.target.value)} required />
          </label>
        </div>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Unit (optional, e.g. "%", "USD")
          <input type="text" value={unit} onChange={(e) => setUnit(e.target.value)} maxLength={20} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Source
          <input type="text" value={source} onChange={(e) => setSource(e.target.value)} required maxLength={200} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.9rem" }}>
          Confidence (optional)
          <select value={confidence} onChange={(e) => setConfidence(e.target.value as IndicatorConfidence | "")}>
            <option value="">(none)</option>
            {CONFIDENCE_LEVELS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem" }}>
          <input type="checkbox" checked={isVerified} onChange={(e) => setIsVerified(e.target.checked)} />
          Verified -- new indicators default to unverified (see CLAUDE.md gold rule); check this to mark
          it as reviewed and confirmed.
        </label>

        {error && <div className="state-block state-block--error">{error}</div>}

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button type="submit" disabled={mutation.isPending || !indicatorType.trim() || !source.trim() || !year || !value}>
            {mutation.isPending ? "Saving…" : editing ? "Save changes" : "Create indicator"}
          </button>
          <button type="button" onClick={onCancel} disabled={mutation.isPending}>
            Cancel
          </button>
        </div>
      </form>
    </Card>
  );
}
