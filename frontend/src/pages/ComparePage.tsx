import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { listNegotiationEvents } from "../api/negotiationEvents";
import { createComparison } from "../api/negotiationAnalyses";
import { LLMAnswerCard } from "../components/LLMAnswerCard";
import { LoadingState, ErrorState } from "../components/ui";

// POST /compare: LLM ερμηνεία της διαφοράς ανάμεσα σε ΑΚΡΙΒΩΣ δύο events
// (καμία free-text ερώτηση, βλ. backend/app/schemas/negotiation_analysis.py
// CompareCreate). Το backend αρνείται event_a_id == event_b_id με 422
// (IdenticalComparisonEventsError) -- εδώ κάνουμε το ίδιο check client-side
// ώστε να μη χρειάζεται καν το round-trip.
export function ComparePage() {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ["negotiation-events"],
    queryFn: listNegotiationEvents,
  });

  const [eventAId, setEventAId] = useState<string>("");
  const [eventBId, setEventBId] = useState<string>("");

  const mutation = useMutation({ mutationFn: createComparison });

  const sameEvent = eventAId !== "" && eventAId === eventBId;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (eventAId && eventBId && !sameEvent) {
      mutation.mutate({ event_a_id: Number(eventAId), event_b_id: Number(eventBId) });
    }
  }

  if (isLoading) return <LoadingState label="Loading events…" />;
  if (error) return <ErrorState error={error} />;

  const sorted = [...(events ?? [])].sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div>
      <h1>Compare Events</h1>
      <p>Pick two negotiation events for an LLM-generated comparison of ZOPA, power, and ripeness.</p>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", gap: "0.75rem", alignItems: "flex-end", flexWrap: "wrap" }}
      >
        {/* minWidth: 0 -- χωρίς αυτό, ένα <select> με μακριούς τίτλους events
            σαν options αρνείται να συρρικνωθεί κάτω από το intrinsic content
            width του μέσα σε flex container (browser default min-width:auto
            σε flex items), προκαλώντας οριζόντιο overflow σε στενές οθόνες
            παρόλο που flexWrap είναι ήδη ενεργό. */}
        <label style={{ flex: "1 1 200px", minWidth: 0 }}>
          Event A
          <br />
          <select
            value={eventAId}
            onChange={(e) => setEventAId(e.target.value)}
            style={{ width: "100%" }}
          >
            <option value="">Select…</option>
            {sorted.map((ev) => (
              <option key={ev.id} value={ev.id}>
                {ev.title} ({ev.date})
              </option>
            ))}
          </select>
        </label>
        <label style={{ flex: "1 1 200px", minWidth: 0 }}>
          Event B
          <br />
          <select
            value={eventBId}
            onChange={(e) => setEventBId(e.target.value)}
            style={{ width: "100%" }}
          >
            <option value="">Select…</option>
            {sorted.map((ev) => (
              <option key={ev.id} value={ev.id}>
                {ev.title} ({ev.date})
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={!eventAId || !eventBId || sameEvent || mutation.isPending}>
          {mutation.isPending ? "Comparing…" : "Compare"}
        </button>
      </form>
      {sameEvent && <p style={{ color: "var(--color-text-muted)" }}>Pick two different events.</p>}

      {mutation.isError && <ErrorState error={mutation.error} />}
      {mutation.isSuccess && (
        <div style={{ marginTop: "1rem" }}>
          <LLMAnswerCard analysis={mutation.data} variant="compare" />
        </div>
      )}
    </div>
  );
}
