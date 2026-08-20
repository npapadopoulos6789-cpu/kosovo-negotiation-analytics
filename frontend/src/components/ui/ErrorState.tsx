import { ApiError } from "../../api/client";
import "./ui.css";

interface ErrorStateProps {
  error: unknown;
}

// react-query τυπώνει το error ως `unknown` -- εδώ το κάνουμε ανθρώπινο.
// Ειδική περίπτωση για ApiError (client.ts) ώστε να δείχνουμε το detail
// που έστειλε το FastAPI, όχι ένα γενικό "[object Object]".
export function ErrorState({ error }: ErrorStateProps) {
  let message: string;
  if (error instanceof ApiError) {
    message = `${error.status}: ${typeof error.detail === "string" ? error.detail : error.message}`;
  } else if (error instanceof Error) {
    message = error.message;
  } else {
    message = "Something went wrong.";
  }

  return <div className="state-block state-block--error">{message}</div>;
}
