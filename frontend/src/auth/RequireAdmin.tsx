import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { ErrorState } from "../components/ui";

// Layout-route guard (React Router nested-route pattern) -- ένα route
// ελέγχει role=ADMIN για όλα τα /admin/* children μέσω <Outlet/>, το
// μοναδικό protected route του site (βλ. AuthContext).
export function RequireAdmin() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== "ADMIN") {
    return <ErrorState error={new Error("Admin access required.")} />;
  }

  return <Outlet />;
}
