import type { ReactNode } from "react";
import "./ui.css";

interface CardProps {
  children: ReactNode;
  className?: string;
}

// Γενικό container -- ομαδοποιεί περιεχόμενο (country/event/analysis) με
// συνεπές padding/border. Δεν κάνει καμία υπόθεση για το τι περιέχει.
export function Card({ children, className }: CardProps) {
  return <div className={className ? `card ${className}` : "card"}>{children}</div>;
}
