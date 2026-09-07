import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { useLocationContext } from "../context/LocationContext";

export default function DashboardPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { taluka, village, availableCapital } = useLocationContext();

  const QUICK_ACTIONS = [
    { to: "/recommend", label: t("nav.recommend") },
    { to: "/financial-calculator", label: t("nav.calculator") },
    { to: "/schemes", label: t("nav.schemes") },
    { to: "/map", label: t("nav.map") },
  ];

  return (
    <div className="max-w-3xl">
      <h1 className="font-display text-2xl font-semibold text-ink">
        {t("dashboard.welcome", { name: user?.full_name })}
      </h1>
      <p className="mt-1 text-sm text-ink-muted">{t("dashboard.sessionSummary")}</p>

      <div className="mt-6 border border-border bg-surface">
        <h2 className="border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
          {t("dashboard.currentLocation")}
        </h2>
        {village ? (
          <dl className="divide-y divide-border text-sm">
            <Row label={t("dashboard.taluka")} value={taluka?.name ?? "—"} />
            <Row label={t("dashboard.village")} value={village.village_name} />
            <Row
              label={t("dashboard.availableCapital")}
              value={availableCapital ? `₹${availableCapital.toLocaleString("en-IN")}` : "—"}
            />
          </dl>
        ) : (
          <p className="px-4 py-4 text-sm text-ink-muted">
            {t("dashboard.noLocationSelected")}{" "}
            <Link to="/location" className="text-primary underline">
              {t("dashboard.selectYourVillage")}
            </Link>{" "}
            {t("dashboard.toBegin")}
          </p>
        )}
      </div>

      <div className="mt-6">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-muted">
          {t("dashboard.quickActions")}
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {QUICK_ACTIONS.map((action) => (
            <Link
              key={action.to}
              to={action.to}
              className="border border-border bg-surface px-4 py-3 text-sm font-medium text-ink hover:border-primary hover:text-primary"
            >
              {action.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between px-4 py-2.5">
      <dt className="text-ink-muted">{label}</dt>
      <dd className="font-medium text-ink">{value}</dd>
    </div>
  );
}
