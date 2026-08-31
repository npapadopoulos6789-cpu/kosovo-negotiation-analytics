import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createNegotiationEvent, updateNegotiationEvent } from "../../api/negotiationEvents";
import type {
  NegotiationEvent,
  ZopaSize,
  RipenessStatus,
  NegotiationType,
} from "../../api/types";
import { ApiError } from "../../api/client";
import { Card } from "../ui";

const ZOPA_SIZES: ZopaSize[] = ["NARROW", "MODERATE", "WIDE"];
const RIPENESS_STATUSES: RipenessStatus[] = ["NOT_RIPE", "EMERGING", "RIPE"];
const NEGOTIATION_TYPES: NegotiationType[] = ["DISTRIBUTIVE", "INTEGRATIVE_WIN_WIN"];

const labelStyle = { display: "flex", flexDirection: "column" as const, gap: "0.25rem", fontSize: "0.9rem" };

interface EventFormProps {
  editing?: NegotiationEvent;
  // savedEvent -- η σελίδα-γονέας περνάει σε edit mode αμέσως μετά το
  // create, χωρίς να περιμένει refetch. Participants ΔΕΝ αγγίζονται εδώ --
  // ξεχωριστό component (ParticipantsManager), ξεχωριστά PUT calls.
  onSuccess: (message: string, savedEvent: NegotiationEvent) => void;
  onCancel: () => void;
}

export function EventForm({ editing, onSuccess, onCancel }: EventFormProps) {
  const queryClient = useQueryClient();

  const [title, setTitle] = useState(editing?.title ?? "");
  const [date, setDate] = useState(editing?.date ?? "");
  const [description, setDescription] = useState(editing?.description ?? "");
  const [zopaSize, setZopaSize] = useState<ZopaSize | "">(editing?.zopa_size ?? "");
  const [zopaReasoning, setZopaReasoning] = useState(editing?.zopa_reasoning ?? "");
  const [ripenessStatus, setRipenessStatus] = useState<RipenessStatus | "">(editing?.ripeness_status ?? "");
  const [ripenessReasoning, setRipenessReasoning] = useState(editing?.ripeness_reasoning ?? "");
  const [batnaA, setBatnaA] = useState(editing?.batna_side_a ?? "");
  const [batnaB, setBatnaB] = useState(editing?.batna_side_b ?? "");
  const [redLinesA, setRedLinesA] = useState(editing?.red_lines_side_a ?? "");
  const [redLinesB, setRedLinesB] = useState(editing?.red_lines_side_b ?? "");
  const [negotiationType, setNegotiationType] = useState<NegotiationType | "">(editing?.negotiation_type ?? "");
  const [economicWeight, setEconomicWeight] = useState(String(editing?.economic_weight ?? 4));
  const [militaryWeight, setMilitaryWeight] = useState(String(editing?.military_weight ?? 4));
  const [socialWeight, setSocialWeight] = useState(String(editing?.social_weight ?? 2));
  const [implementationSuccess, setImplementationSuccess] = useState(
    editing?.implementation_success != null ? String(editing.implementation_success) : "",
  );
  const [error, setError] = useState<string | null>(null);

  // Ίδιο business rule με το backend (_validate_weights) -- ελέγχεται και
  // client-side ώστε το λάθος να φανεί πριν το submit, όχι μόνο μετά από
  // 422. Το backend παραμένει η τελική αυθεντία.
  const weightsTotal = Number(economicWeight || 0) + Number(militaryWeight || 0) + Number(socialWeight || 0);
  const weightsValid = weightsTotal === 10;

  const mutation = useMutation({
    mutationFn: () => {
      const payload = {
        title: title.trim(),
        date,
        description: description.trim() === "" ? null : description.trim(),
        zopa_size: zopaSize === "" ? null : zopaSize,
        zopa_reasoning: zopaReasoning.trim() === "" ? null : zopaReasoning.trim(),
        ripeness_status: ripenessStatus === "" ? null : ripenessStatus,
        ripeness_reasoning: ripenessReasoning.trim() === "" ? null : ripenessReasoning.trim(),
        batna_side_a: batnaA.trim() === "" ? null : batnaA.trim(),
        batna_side_b: batnaB.trim() === "" ? null : batnaB.trim(),
        red_lines_side_a: redLinesA.trim() === "" ? null : redLinesA.trim(),
        red_lines_side_b: redLinesB.trim() === "" ? null : redLinesB.trim(),
        negotiation_type: negotiationType === "" ? null : negotiationType,
        economic_weight: Number(economicWeight),
        military_weight: Number(militaryWeight),
        social_weight: Number(socialWeight),
        implementation_success: implementationSuccess.trim() === "" ? null : Number(implementationSuccess),
      };
      // Χωρίς "participants" key: σε update, το backend αφήνει τους
      // υπάρχοντες participants ανέγγιχτους όταν το πεδίο λείπει
      // (NegotiationEventUpdate.participants, exclude_unset=True).
      return editing ? updateNegotiationEvent(editing.id, payload) : createNegotiationEvent(payload);
    },
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: ["negotiation-events"] });
      onSuccess(
        editing ? `Event "${saved.title}" updated successfully.` : `Event "${saved.title}" created successfully.`,
        saved,
      );
    },
    onError: (err) => {
      setError(err instanceof ApiError ? (typeof err.detail === "string" ? err.detail : err.message) : "Save failed.");
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!weightsValid) return;
    mutation.mutate();
  }

  return (
    <Card>
      <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>
        {editing ? `Edit event #${editing.id}` : "New event"}
      </h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxWidth: "560px" }}>
        <label style={labelStyle}>
          Title
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required maxLength={200} />
        </label>
        <label style={labelStyle}>
          Date
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
        </label>
        <label style={labelStyle}>
          Description (optional)
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} />
        </label>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <label style={{ ...labelStyle, flex: 1 }}>
            ZOPA size
            <select value={zopaSize} onChange={(e) => setZopaSize(e.target.value as ZopaSize | "")}>
              <option value="">(none)</option>
              {ZOPA_SIZES.map((z) => <option key={z} value={z}>{z}</option>)}
            </select>
          </label>
          <label style={{ ...labelStyle, flex: 1 }}>
            Ripeness status
            <select value={ripenessStatus} onChange={(e) => setRipenessStatus(e.target.value as RipenessStatus | "")}>
              <option value="">(none)</option>
              {RIPENESS_STATUSES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </label>
        </div>
        <label style={labelStyle}>
          ZOPA reasoning (optional)
          <textarea value={zopaReasoning} onChange={(e) => setZopaReasoning(e.target.value)} rows={2} />
        </label>
        <label style={labelStyle}>
          Ripeness reasoning (optional)
          <textarea value={ripenessReasoning} onChange={(e) => setRipenessReasoning(e.target.value)} rows={2} />
        </label>

        <label style={labelStyle}>
          Negotiation type
          <select value={negotiationType} onChange={(e) => setNegotiationType(e.target.value as NegotiationType | "")}>
            <option value="">(none)</option>
            {NEGOTIATION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <label style={{ ...labelStyle, flex: 1 }}>
            BATNA -- side A (optional)
            <textarea value={batnaA} onChange={(e) => setBatnaA(e.target.value)} rows={2} />
          </label>
          <label style={{ ...labelStyle, flex: 1 }}>
            BATNA -- side B (optional)
            <textarea value={batnaB} onChange={(e) => setBatnaB(e.target.value)} rows={2} />
          </label>
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <label style={{ ...labelStyle, flex: 1 }}>
            Red lines -- side A (optional)
            <textarea value={redLinesA} onChange={(e) => setRedLinesA(e.target.value)} rows={2} />
          </label>
          <label style={{ ...labelStyle, flex: 1 }}>
            Red lines -- side B (optional)
            <textarea value={redLinesB} onChange={(e) => setRedLinesB(e.target.value)} rows={2} />
          </label>
        </div>

        <div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <label style={{ ...labelStyle, flex: 1 }}>
              Economic weight
              <input type="number" value={economicWeight} onChange={(e) => setEconomicWeight(e.target.value)} required />
            </label>
            <label style={{ ...labelStyle, flex: 1 }}>
              Military weight
              <input type="number" value={militaryWeight} onChange={(e) => setMilitaryWeight(e.target.value)} required />
            </label>
            <label style={{ ...labelStyle, flex: 1 }}>
              Social weight
              <input type="number" value={socialWeight} onChange={(e) => setSocialWeight(e.target.value)} required />
            </label>
          </div>
          <p style={{ fontSize: "0.8rem", margin: "0.35rem 0 0", color: weightsValid ? "var(--color-text-muted)" : "var(--color-danger, #b91c1c)" }}>
            Weights must sum to 10 -- currently {weightsTotal}.
          </p>
        </div>

        <label style={labelStyle}>
          Implementation success (optional, 0.0-1.0)
          <input
            type="number"
            step="0.01"
            min={0}
            max={1}
            value={implementationSuccess}
            onChange={(e) => setImplementationSuccess(e.target.value)}
          />
        </label>

        {error && <div className="state-block state-block--error">{error}</div>}

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button type="submit" disabled={mutation.isPending || !title.trim() || !date || !weightsValid}>
            {mutation.isPending ? "Saving…" : editing ? "Save changes" : "Create event"}
          </button>
          <button type="button" onClick={onCancel} disabled={mutation.isPending}>
            Cancel
          </button>
        </div>
      </form>
    </Card>
  );
}
