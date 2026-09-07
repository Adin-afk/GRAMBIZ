import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { fetchAssessment, fetchServicesHealth } from "../api/endpoints";
import { extractErrorMessage } from "../api/client";
import type { AssessmentOut } from "../types/api";
import ListenButton from "../components/ListenButton";

function formatInr(n: number): string {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

function riskColor(level: string): string {
  if (level === "LOW") return "text-risk-low";
  if (level === "MEDIUM") return "text-risk-medium";
  return "text-risk-high";
}

export default function ReportPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<AssessmentOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiConfigured, setAiConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchAssessment(id)
      .then(setAssessment)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
    // Best-effort only: if this call fails, we just fall back to the
    // generic "unavailable" message rather than the more precise
    // "not configured for this deployment" one.
    fetchServicesHealth()
      .then((health) => setAiConfigured(health.gemini === "configured"))
      .catch(() => setAiConfigured(null));
  }, [id]);

  if (loading) return <p className="text-sm text-ink-muted">{t("report.loading")}</p>;
  if (error)
    return <div className="border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">{error}</div>;
  if (!assessment) return null;

  const fin = assessment.financial_analysis as {
    project_cost?: number;
    loan_amount?: number;
    beneficiary_contribution_pct?: number;
    error?: string;
  } | null;
  const competitors = assessment.competitor_analysis;
  const risk = assessment.risk_assessment;

  return (
    <div className="max-w-4xl">
      <div className="mb-6 border-b border-border pb-4">
        <p className="text-xs uppercase tracking-wide text-ink-muted">{t("report.advisoryReport")}</p>
        <h1 className="font-display text-2xl font-semibold text-ink">
          {t("report.assessment", { id: assessment.id.slice(0, 8) })}
        </h1>
        <p className="mt-1 text-sm text-ink-muted">
          {t("report.confidenceLevel")} <span className="font-medium">{assessment.confidence_level}</span>
          {assessment.dataset_version && <> &middot; {t("report.dataset")} {assessment.dataset_version}</>}
        </p>
      </div>

      <Section title={t("report.opportunityScore")}>
        <p className="figures text-3xl font-semibold text-primary">
          {assessment.opportunity_score?.toFixed(1) ?? "—"}
          <span className="text-base text-ink-faint">/100</span>
        </p>
      </Section>

      <Section title={t("report.financialFeasibility")}>
        {fin?.error ? (
          <p className="text-sm text-risk-high">{fin.error}</p>
        ) : (
          <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
            <Row label={t("report.availableCapital")} value={formatInr(assessment.available_capital)} />
            {fin?.project_cost !== undefined && <Row label={t("report.projectCost")} value={formatInr(fin.project_cost)} />}
            {fin?.loan_amount !== undefined && <Row label={t("report.loanAmount")} value={formatInr(fin.loan_amount)} />}
          </dl>
        )}
      </Section>

      {competitors && (
        <Section title={t("report.competitorAnalysis")}>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
            <Row label={t("report.competitors5km")} value={String(competitors.competitor_count_5km)} />
            <Row label={t("report.competitors10km")} value={String(competitors.competitor_count_10km)} />
            <Row label={t("report.density5km")} value={competitors.density.density_5km_per_sqkm.toFixed(4)} />
            <Row label={t("report.density10km")} value={competitors.density.density_10km_per_sqkm.toFixed(4)} />
          </dl>
        </Section>
      )}

      {assessment.scheme_match && (
        <Section title={t("report.matchedSchemes")}>
          {assessment.scheme_match.count === 0 ? (
            <p className="text-sm text-ink-muted">{t("report.noSchemesMatched")}</p>
          ) : (
            <ul className="list-inside list-disc text-sm text-ink">
              {assessment.scheme_match.matched_schemes.map((name) => (
                <li key={name}>{name}</li>
              ))}
            </ul>
          )}
        </Section>
      )}

      {risk && (
        <Section title={t("report.riskAssessment")}>
          <p className={`text-lg font-semibold ${riskColor(risk.risk_level)}`}>{risk.risk_level}</p>
        </Section>
      )}

      {assessment.swot && Object.keys(assessment.swot).length > 0 && (
        <Section title={t("report.swotAnalysis")}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <SwotQuadrant title={t("report.swotStrengths")} items={assessment.swot["strengths"]} />
            <SwotQuadrant title={t("report.swotWeaknesses")} items={assessment.swot["weaknesses"]} />
            <SwotQuadrant title={t("report.swotOpportunities")} items={assessment.swot["opportunities"]} />
            <SwotQuadrant title={t("report.swotThreats")} items={assessment.swot["threats"]} />
          </div>
        </Section>
      )}

      <Section
        title={t("report.aiExplanation")}
        action={assessment.ai_explanation ? <ListenButton text={assessment.ai_explanation} /> : undefined}
      >
        {assessment.ai_explanation ? (
          <p className="text-sm text-ink">{assessment.ai_explanation}</p>
        ) : aiConfigured === false ? (
          <p className="text-sm text-ink-faint">{t("report.noLlmConfigured")}</p>
        ) : (
          <p className="text-sm text-ink-faint">{t("report.aiUnavailableForAssessment")}</p>
        )}
      </Section>

      <p className="mt-8 border-t border-border pt-4 text-xs text-ink-faint">
        {t("report.footerNote", {
          dataset: assessment.dataset_version ?? t("report.unspecifiedDataset"),
          model: assessment.model_version ? t("report.andModel", { model: assessment.model_version }) : "",
        })}
      </p>
    </div>
  );
}

function Section({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div className="mb-6 border border-border bg-surface">
      <h2 className="flex items-center justify-between border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
        <span>{title}</span>
        {action && <span className="normal-case tracking-normal">{action}</span>}
      </h2>
      <div className="px-4 py-4">{children}</div>
    </div>
  );
}

function SwotQuadrant({ title, items }: { title: string; items: unknown }) {
  const list = Array.isArray(items) ? items.filter((x): x is string => typeof x === "string" && x.trim().length > 0) : [];
  if (list.length === 0) return null;
  return (
    <div className="border border-border bg-bg p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-ink-muted">{title}</p>
      <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-sm text-ink">
        {list.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
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
