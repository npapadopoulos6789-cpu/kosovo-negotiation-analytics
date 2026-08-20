import { NavLink, Outlet } from "react-router-dom";
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
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
