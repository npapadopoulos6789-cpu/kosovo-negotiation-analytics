import { Link } from "react-router-dom";
import { Card } from "./ui";

interface LoginRequiredNoticeProps {
  toolName: string;
}

// Ίδιο μήνυμα, ξαναχρησιμοποιείται από SynthesisPage/ComparePage -- και
// τα δύο πλέον απαιτούν login (βλ. backend Depends(get_current_user) στα
// /synthesis, /compare). ΟΧΙ το per-event Q&A (EventDetailPage) -- αυτό
// μένει δημόσιο, δεν χρησιμοποιεί αυτό το component.
export function LoginRequiredNotice({ toolName }: LoginRequiredNoticeProps) {
  return (
    <Card>
      <p>{toolName} requires a free account -- it runs a real AI analysis call per question.</p>
      <p style={{ marginTop: "0.5rem" }}>
        <Link to="/register">Create a free account</Link> to use this tool, or{" "}
        <Link to="/login">log in</Link> if you already have one.
      </p>
    </Card>
  );
}
