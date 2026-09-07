import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";
import { extractErrorMessage } from "../api/client";
import DataStatusBadge from "../components/DataStatusBadge";

interface SchemeRow {
  id: string;
  scheme_name: string;
  provider: string;
  minimum_project_cost: number;
  maximum_project_cost: number;
  interest_rate: number;
  tenure_years: number;
  moratorium_months: number;
  maximum_loan: number;
  eligibility: string | null;
  source: string | null;
  last_verified_date: string | null;
  data_status: string;
}

function formatInr(n: number): string {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

export default function SchemesPage() {
  const { t } = useTranslation();
  const [schemes, setSchemes] = useState<SchemeRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<SchemeRow[]>("/api/schemes")
      .then((res) => setSchemes(res.data))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink">{t("schemes.title")}</h1>
      <p className="mt-1 max-w-2xl text-sm text-ink-muted">{t("schemes.subtitle")}</p>

      {error && (
        <div className="mt-4 border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">{error}</div>
      )}
      {loading && <p className="mt-6 text-sm text-ink-muted">{t("schemes.loading")}</p>}

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        {schemes.map((s) => (
          <div key={s.id} className="border border-border bg-surface p-4">
            <div className="flex items-start justify-between gap-2">
              <h2 className="font-display text-base font-semibold text-ink">{s.scheme_name}</h2>
              <DataStatusBadge status={s.data_status} />
            </div>
            <p className="mt-0.5 text-xs text-ink-muted">{s.provider}</p>

            <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
              <Row label={t("schemes.projectCostBand")} value={`${formatInr(s.minimum_project_cost)} – ${formatInr(s.maximum_project_cost)}`} />
              <Row label={t("schemes.interestRate")} value={`${s.interest_rate}% p.a.`} />
              <Row label={t("schemes.tenure")} value={t("schemes.tenureYears", { count: s.tenure_years })} />
              <Row label={t("schemes.moratorium")} value={t("schemes.moratoriumMonths", { count: s.moratorium_months })} />
              <Row label={t("schemes.maximumLoan")} value={formatInr(s.maximum_loan)} />
              <Row label={t("schemes.lastVerified")} value={s.last_verified_date ? new Date(s.last_verified_date).toLocaleDateString("en-IN") : t("schemes.notYetVerified")} />
            </dl>

            {s.eligibility && <p className="mt-3 border-t border-border pt-2 text-xs text-ink-muted">{s.eligibility}</p>}
            {s.source && <p className="mt-1 text-[11px] text-ink-faint">{t("schemes.source")}: {s.source}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-faint">{label}</dt>
      <dd className="figures text-ink">{value}</dd>
    </div>
  );
}
