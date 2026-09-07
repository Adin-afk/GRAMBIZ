import { useTranslation } from "react-i18next";
import type { ScoreComponents } from "../types/api";

interface Props {
  score: number;
  components: ScoreComponents;
}

const KEYS: { key: keyof ScoreComponents; i18nKey: string }[] = [
  { key: "demand", i18nKey: "scoreBar.demand" },
  { key: "competition", i18nKey: "scoreBar.competition" },
  { key: "accessibility", i18nKey: "scoreBar.accessibility" },
  { key: "cost", i18nKey: "scoreBar.affordability" },
  { key: "margin", i18nKey: "scoreBar.margin" },
  { key: "market_access", i18nKey: "scoreBar.marketAccess" },
  { key: "seasonality", i18nKey: "scoreBar.seasonalStability" },
];

function scoreColor(v: number): string {
  if (v >= 0.7) return "bg-verified";
  if (v >= 0.4) return "bg-demo";
  return "bg-risk-high";
}

export default function OpportunityScoreBar({ score, components }: Props) {
  const { t } = useTranslation();
  return (
    <div className="border border-border bg-surface">
      <div className="flex items-baseline justify-between border-b border-border px-4 py-3">
        <span className="font-display text-sm font-semibold uppercase tracking-wide text-ink-muted">
          {t("scoreBar.opportunityScore")}
        </span>
        <span className="figures text-3xl font-semibold text-primary">
          {score.toFixed(1)}
          <span className="text-base text-ink-faint">/100</span>
        </span>
      </div>
      <dl className="divide-y divide-border">
        {KEYS.map(({ key, i18nKey }) => {
          const value = components[key];
          return (
            <div key={key} className="flex items-center gap-3 px-4 py-2">
              <dt className="w-36 shrink-0 text-xs text-ink-muted">{t(i18nKey)}</dt>
              <dd className="flex flex-1 items-center gap-2">
                <div className="h-2 flex-1 bg-bg">
                  <div
                    className={`h-full ${scoreColor(value)}`}
                    style={{ width: `${Math.round(value * 100)}%` }}
                  />
                </div>
                <span className="figures w-10 text-right text-xs text-ink-muted">
                  {Math.round(value * 100)}
                </span>
              </dd>
            </div>
          );
        })}
      </dl>
    </div>
  );
}
