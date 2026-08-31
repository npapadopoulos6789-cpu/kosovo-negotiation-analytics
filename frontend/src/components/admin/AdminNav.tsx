import { NavLink } from "react-router-dom";

const ADMIN_LINKS = [
  { to: "/admin", label: "Overview", end: true },
  { to: "/admin/countries", label: "Countries" },
  { to: "/admin/events", label: "Events" },
  { to: "/admin/indicators", label: "Indicators" },
];

// Μικρό sub-nav, πάνω σε κάθε /admin/* σελίδα -- ίδιο μοτίβο styling με
// το κύριο navbar (app-nav__link classes, βλ. layout.css), όχι νέο στυλ.
export function AdminNav() {
  return (
    <nav style={{ display: "flex", gap: "1.25rem", margin: "0.5rem 0 1.5rem", flexWrap: "wrap" }}>
      {ADMIN_LINKS.map(({ to, label, end }) => (
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
  );
}
