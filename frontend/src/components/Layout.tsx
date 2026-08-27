import { Suspense, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { LoadingState } from "./ui";
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
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  // Τίτλος + 5 links + auth section δεν χωράνε σε κινητό/tablet πλάτος
  // (βλ. layout.css @media) -- collapse σε hamburger. Κλείσε το menu σε
  // κάθε αλλαγή route (αλλιώς μένει ανοιχτό πάνω από τη νέα σελίδα μετά
  // από κλικ σε link) -- "adjust state during render" pattern (React docs)
  // αντί για useEffect, ώστε να μη γίνεται ένα επιπλέον render pass/flash
  // του παλιού μενού πριν κλείσει.
  const [prevPathname, setPrevPathname] = useState(location.pathname);
  if (location.pathname !== prevPathname) {
    setPrevPathname(location.pathname);
    setMenuOpen(false);
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-title">Kosovo Negotiation Analytics</span>
        <button
          type="button"
          className="app-nav-toggle"
          aria-expanded={menuOpen}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? "✕" : "☰"}
        </button>
        <div
          className={
            menuOpen ? "app-header-collapsible app-header-collapsible--open" : "app-header-collapsible"
          }
        >
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
        </div>
      </header>
      <main className="app-main">
        {/* Κάθε route page είναι πλέον React.lazy (βλ. App.tsx) -- ένα
            Suspense boundary εδώ, όχι ανά route, ώστε το navbar να μένει
            ορατό/λειτουργικό ενώ φορτώνει το chunk της νέας σελίδας. */}
        <Suspense fallback={<LoadingState label="Loading page…" />}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}
