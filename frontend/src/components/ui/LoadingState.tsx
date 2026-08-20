import "./ui.css";

interface LoadingStateProps {
  label?: string;
}

// Χρησιμοποιείται όποτε ένα react-query hook έχει isLoading=true.
export function LoadingState({ label = "Loading…" }: LoadingStateProps) {
  return <div className="state-block">{label}</div>;
}
