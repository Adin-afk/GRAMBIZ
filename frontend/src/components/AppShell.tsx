import { NavLink, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { useLocationContext } from "../context/LocationContext";
import LanguageSwitcher from "./LanguageSwitcher";
import PageReadAloud from "./PageReadAloud";

export default function AppShell({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { taluka, village } = useLocationContext();
  const navigate = useNavigate();

  const NAV_ITEMS = [
    { to: "/dashboard", label: t("nav.dashboard") },
    { to: "/location", label: t("nav.location") },
    { to: "/recommend", label: t("nav.recommend") },
    { to: "/financial-calculator", label: t("nav.calculator") },
    { to: "/schemes", label: t("nav.schemes") },
    { to: "/map", label: t("nav.map") },
  ];

  return (
    <div className="min-h-screen bg-bg">
      {/* Masthead */}
      <header className="border-b border-border bg-surface">
        <div className="h-[3px] bg-gradient-to-r from-accent via-border to-primary" />
        <div className="mx-auto flex max-w-[1400px] items-center justify-between px-6 py-3">
          <div>
            <p className="font-display text-lg font-semibold leading-tight text-primary">
              {t("common.appName")}
            </p>
            <p className="text-xs text-ink-muted">{t("common.tagline")}</p>
          </div>
          <div className="flex items-center gap-4 text-sm">
            {village && (
              <span className="hidden text-ink-muted md:inline">
                {taluka?.name} &rsaquo; {village.village_name}
              </span>
            )}
            <LanguageSwitcher />
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-ink-muted">{user.full_name}</span>
                <button
                  onClick={() => {
                    logout();
                    navigate("/login");
                  }}
                  className="border border-border-strong px-3 py-1.5 text-xs font-medium text-ink hover:bg-bg"
                >
                  {t("common.signOut")}
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-[1400px]">
        {/* Sidebar */}
        <nav className="hidden w-56 shrink-0 border-r border-border bg-surface px-3 py-6 md:block">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `block border-l-2 px-3 py-2 text-sm ${
                      isActive
                        ? "border-primary bg-bg font-medium text-primary"
                        : "border-transparent text-ink-muted hover:bg-bg hover:text-ink"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Content */}
        <main id="page-main-content" className="min-w-0 flex-1 px-6 py-6">
          {children}
        </main>
      </div>

      <PageReadAloud />
    </div>
  );
}
