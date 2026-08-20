// Μοιρασμένο ανάμεσα σε EventsListPage/EventDetailPage -- θετικό/αρνητικό
// νόημα ανά enum τιμή. Δεν είναι καθολικό (γι' αυτό δεν είναι μέσα στο
// ίδιο το Badge component, βλ. Badge.tsx), αλλά ΕΙΝΑΙ κοινό ανάμεσα στις
// δύο events σελίδες -- εδώ, όχι διπλογραμμένο.
import type { RipenessStatus, ZopaSize } from "../api/types";
import type { BadgeTone } from "../components/ui";

export const RIPENESS_TONE: Record<RipenessStatus, BadgeTone> = {
  RIPE: "positive",
  EMERGING: "warning",
  NOT_RIPE: "negative",
};

export const ZOPA_TONE: Record<ZopaSize, BadgeTone> = {
  WIDE: "positive",
  MODERATE: "warning",
  NARROW: "negative",
};
