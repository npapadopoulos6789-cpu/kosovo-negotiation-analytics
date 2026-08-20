import "./ui.css";

interface EmptyStateProps {
  label?: string;
}

// Χρησιμοποιείται όποτε ένα request πέτυχε αλλά επέστρεψε άδεια λίστα --
// ξεχωριστό από το LoadingState (ακόμα φορτώνει) και το ErrorState (απέτυχε).
export function EmptyState({ label = "No data yet." }: EmptyStateProps) {
  return <div className="state-block">{label}</div>;
}
