import { useState } from "react";
import { useTranslation } from "react-i18next";
import { calculateFinancials, calculateRepayment } from "../api/endpoints";
import { extractErrorMessage } from "../api/client";
import DataStatusBadge from "../components/DataStatusBadge";
import type { FinancialCalculateResponse, RepaymentResponse } from "../types/api";

function formatInr(n: number): string {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

export default function FinancialCalculatorPage() {
  const { t } = useTranslation();
  const [margin, setMargin] = useState("100000");
  const [result, setResult] = useState<FinancialCalculateResponse | null>(null);
  const [repayment, setRepayment] = useState<RepaymentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleCalculate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setRepayment(null);
    const value = parseFloat(margin);
    if (Number.isNaN(value)) {
      setError(t("calculator.invalidAmount"));
      return;
    }
    setLoading(true);
    try {
      const res = await calculateFinancials(value);
      setResult(res);
      if (res.selected_scheme) {
        const rep = await calculateRepayment(
          res.loan_amount,
          res.selected_scheme.interest_rate,
          res.selected_scheme.tenure_years,
          res.selected_scheme.moratorium_months
        );
        setRepayment(rep);
      }
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="font-display text-2xl font-semibold text-ink">{t("calculator.title")}</h1>
      <p className="mt-1 text-sm text-ink-muted">{t("calculator.subtitle")}</p>

      <form onSubmit={handleCalculate} className="mt-6 flex items-end gap-3 border border-border bg-surface p-6">
        <label className="flex-1 text-sm">
          <span className="mb-1 block font-medium text-ink">{t("calculator.availableMarginCapital")}</span>
          <input
            type="number"
            value={margin}
            onChange={(e) => setMargin(e.target.value)}
            className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary"
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="bg-accent px-5 py-2.5 text-sm font-medium text-white hover:bg-accent-dark disabled:opacity-60"
        >
          {loading ? t("calculator.calculating") : t("calculator.calculate")}
        </button>
      </form>

      {error && (
        <div className="mt-4 border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">{error}</div>
      )}

      {result && (
        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="border border-border bg-surface">
            <h2 className="border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
              {t("calculator.feasibilitySummary")}
            </h2>
            <dl className="divide-y divide-border text-sm">
              <Row label={t("calculator.availableMargin")} value={formatInr(result.available_margin)} />
              <Row
                label={t("calculator.beneficiaryContribution")}
                value={`${(result.beneficiary_contribution_pct * 100).toFixed(0)}%`}
              />
              <Row label={t("calculator.projectCost")} value={formatInr(result.project_cost)} strong />
              <Row label={t("calculator.loanAmount")} value={formatInr(result.loan_amount)} strong />
            </dl>
          </div>

          <div className="border border-border bg-surface">
            <h2 className="border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
              {t("calculator.matchedSchemes", { count: result.matched_schemes.length })}
            </h2>
            {result.matched_schemes.length === 0 ? (
              <p className="px-4 py-3 text-sm text-ink-muted">{t("calculator.noSchemesMatch")}</p>
            ) : (
              <ul className="divide-y divide-border">
                {result.matched_schemes.map((s) => (
                  <li key={s.id} className="px-4 py-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-ink">{s.scheme_name}</span>
                      <DataStatusBadge status={s.data_status} />
                    </div>
                    <p className="mt-0.5 text-xs text-ink-muted">
                      {s.provider} &middot; {s.interest_rate}% p.a. &middot; {s.tenure_years} yr tenure &middot;{" "}
                      {s.moratorium_months} mo moratorium
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {repayment && (
        <div className="mt-6 border border-border bg-surface">
          <h2 className="border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            {t("calculator.repaymentSchedule")}
          </h2>
          <dl className="grid grid-cols-3 divide-x divide-border border-b border-border text-sm">
            <RowGrid label={t("calculator.installment")} value={formatInr(repayment.installment)} />
            <RowGrid label={t("calculator.totalInterest")} value={formatInr(repayment.total_interest)} />
            <RowGrid label={t("calculator.totalRepayment")} value={formatInr(repayment.total_repayment)} />
          </dl>
          <div className="max-h-72 overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-bg">
                <tr className="text-left text-ink-muted">
                  <th className="px-4 py-2 font-medium">{t("calculator.colNumber")}</th>
                  <th className="px-4 py-2 font-medium">{t("calculator.colDueDate")}</th>
                  <th className="px-4 py-2 font-medium">{t("calculator.colPhase")}</th>
                  <th className="px-4 py-2 font-medium">{t("calculator.colPrincipal")}</th>
                  <th className="px-4 py-2 font-medium">{t("calculator.colInterest")}</th>
                  <th className="px-4 py-2 font-medium">{t("calculator.colBalance")}</th>
                </tr>
              </thead>
              <tbody className="figures divide-y divide-border">
                {repayment.schedule.map((row) => (
                  <tr key={row.installment_number}>
                    <td className="px-4 py-1.5">{row.installment_number}</td>
                    <td className="px-4 py-1.5">{new Date(row.due_date).toLocaleDateString("en-IN")}</td>
                    <td className="px-4 py-1.5">{row.phase}</td>
                    <td className="px-4 py-1.5">{formatInr(row.principal_component)}</td>
                    <td className="px-4 py-1.5">{formatInr(row.interest_component)}</td>
                    <td className="px-4 py-1.5">{formatInr(row.remaining_balance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function Row({ label, value, strong }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="flex items-center justify-between px-4 py-2.5">
      <dt className="text-ink-muted">{label}</dt>
      <dd className={`figures ${strong ? "text-base font-semibold text-primary" : ""}`}>{value}</dd>
    </div>
  );
}

function RowGrid({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-4 py-3 text-center">
      <dt className="text-xs text-ink-muted">{label}</dt>
      <dd className="figures mt-0.5 text-lg font-semibold text-primary">{value}</dd>
    </div>
  );
}
