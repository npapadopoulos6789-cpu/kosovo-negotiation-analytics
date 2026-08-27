import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import "./layout.css";

// "Actors" (όχι "Countries") στο navbar -- ρητή UI-labeling απόφαση, βλ.
// PROJECT_STATUS.md 2026-08-20: το backend model λέγεται Country αλλά
// καλύπτει και μη-κρατικούς δρώντες (NATO/UN/EU/...).
const NAV_LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/actors", label: "Actors" },
  { to: "/events", label: "Events" },
  { to: "/synthesis", label: "Synthesis" },
  { to: "/compare", label: "Compare" },
];

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-title">Kosovo Negotiation Analytics</span>
        <nav className="app-nav">
          {NAV_LINKS.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                isActive ? "app-nav__link app-nav__link--active" : "app-nav__link"
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        {/* Auth links δεν φράζουν τίποτα -- μόνο δείχνουν login/register
            όταν δεν υπάρχει συνδεδεμένος χρήστης, ή email + logout όταν
            υπάρχει. Καμία από τις παραπάνω σελίδες δεν ελέγχει το user. */}
        <div className="app-auth">
          {user ? (
            <>
              <span className="app-auth__email">{user.email}</span>
              <button type="button" className="app-auth__logout" onClick={handleLogout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  isActive ? "app-nav__link app-nav__link--active" : "app-nav__link"
                }
              >
                Login
              </NavLink>
              <NavLink
                to="/register"
                className={({ isActive }) =>
                  isActive ? "app-nav__link app-nav__link--active" : "app-nav__link"
                }
              >
                Register
              </NavLink>
            </>
          )}
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
