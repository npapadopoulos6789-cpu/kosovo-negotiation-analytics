import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listNegotiationEvents, deleteNegotiationEvent } from "../../api/negotiationEvents";
import type { NegotiationEvent } from "../../api/types";
import { ApiError } from "../../api/client";
import { Card, Badge, LoadingState, ErrorState, EmptyState } from "../../components/ui";
import { AdminNav } from "../../components/admin/AdminNav";
import { EventForm } from "../../components/admin/EventForm";
import { ParticipantsManager } from "../../components/admin/ParticipantsManager";

// "create" δεν έχει ακόμα id -- ParticipantsManager χρειάζεται event.id,
// άρα μετά από επιτυχές create περνάμε στο edit mode (NegotiationEvent
// object) αντί να κλείσουμε τη φόρμα, ώστε να προστεθούν participants
// αμέσως.
type FormState = "closed" | "create" | NegotiationEvent;

export function AdminEventsPage() {
  const events = useQuery({ queryKey: ["negotiation-events"], queryFn: listNegotiationEvents });
  const queryClient = useQueryClient();

  const [formState, setFormState] = useState<FormState>("closed");
  const [message, setMessage] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const deleteMutation = useMutation({
    mutationFn: deleteNegotiationEvent,
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["negotiation-events"] });
      setDeleteError(null);
      setMessage(`Event #${id} deleted.`);
      if (typeof formState === "object" && formState.id === id) setFormState("closed");
    },
    onError: (err) => {
      setDeleteError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Delete failed.");
    },
  });

  if (events.isLoading) return <LoadingState label="Loading events…" />;
  if (events.error) return <ErrorState error={events.error} />;

  const sorted = [...(events.data ?? [])].sort((a, b) => a.date.localeCompare(b.date));

  // formState κρατάει ένα στιγμιότυπο του event -- ξαναβρίσκουμε το
  // φρέσκο αντικείμενο από το query cache σε κάθε render, ώστε ένα
  // participant add/remove να φαίνεται αμέσως χωρίς stale props.
  const editingEvent = typeof formState === "object"
    ? sorted.find((e) => e.id === formState.id) ?? formState
    : undefined;

  function handleFormSuccess(successMessage: string, savedEvent: NegotiationEvent) {
    setMessage(successMessage);
    setFormState(savedEvent);
  }

  function handleDelete(event: NegotiationEvent) {
    if (
      window.confirm(
        `Delete "${event.title}"? This cannot be undone. Blocked if any Q&A analyses reference this event -- delete those first.`,
      )
    ) {
      setMessage(null);
      deleteMutation.mutate(event.id);
    }
  }

  return (
    <div>
      <h1>Admin -- Events</h1>
      <AdminNav />

      {message && <div className="state-block" style={{ textAlign: "left" }}>{message}</div>}
      {deleteError && <ErrorState error={new Error(deleteError)} />}

      {formState !== "closed" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <EventForm
            editing={formState === "create" ? undefined : editingEvent}
            onSuccess={handleFormSuccess}
            onCancel={() => setFormState("closed")}
          />
          {editingEvent && <ParticipantsManager event={editingEvent} />}
          {editingEvent && (
            <button type="button" onClick={() => setFormState("closed")} style={{ alignSelf: "flex-start" }}>
              Done
            </button>
          )}
        </div>
      ) : (
        <button type="button" onClick={() => setFormState("create")}>
          + New event
        </button>
      )}

      <div style={{ display: "grid", gap: "0.5rem", marginTop: "1.5rem" }}>
        {sorted.length === 0 ? (
          <EmptyState label="No events yet." />
        ) : (
          sorted.map((event) => (
            <Card key={event.id}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", flexWrap: "wrap" }}>
                  <strong>{event.title}</strong>
                  <span style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>{event.date}</span>
                  {event.zopa_size && <Badge tone="neutral">{event.zopa_size}</Badge>}
                  {event.ripeness_status && <Badge tone="neutral">{event.ripeness_status}</Badge>}
                  <span style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
                    {event.participants.length} participant{event.participants.length === 1 ? "" : "s"}
                  </span>
                </div>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button type="button" onClick={() => setFormState(event)}>
                    Edit
                  </button>
                  <button type="button" onClick={() => handleDelete(event)} disabled={deleteMutation.isPending}>
                    Delete
                  </button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
