import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { recommendBusinesses, createAssessment } from "../api/endpoints";
import { extractErrorMessage } from "../api/client";
import { useLocationContext } from "../context/LocationContext";
import OpportunityScoreBar from "../components/OpportunityScoreBar";
import type { RecommendationItem } from "../types/api";

function formatInr(n: number | null): string {
  if (n === null) return "—";
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

export default function RecommendPage() {
  const { t } = useTranslation();
  const { village, availableCapital } = useLocationContext();
  const navigate = useNavigate();
  const [items, setItems] = useState<RecommendationItem[]>([]);
  const [datasetNote, setDatasetNote] = useState("");
  const [selected, setSelected] = useState<RecommendationItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);

  useEffect(() => {
    if (!village || !availableCapital) return;
    setLoading(true);
    recommendBusinesses(village.id, availableCapital)
      .then((res) => {
        setItems(res.recommendations);
        setDatasetNote(res.dataset_note);
        setSelected(res.recommendations[0] ?? null);
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [village, availableCapital]);

  async function handleFullAnalysis(item: RecommendationItem) {
    if (!village) return;
    setSavingId(item.category_id);
    setError(null);
    try {
      const assessment = await createAssessment(village.id, item.category_id, availableCapital!);
      navigate(`/reports/${assessment.id}`);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSavingId(null);
    }
  }

  if (!village || !availableCapital) {
    return (
      <div className="max-w-xl border border-border bg-surface p-6">
        <p className="text-sm text-ink-muted">
          {t("recommend.selectFirst")}{" "}
          <Link to="/location" className="text-primary underline">
            {t("recommend.goToLocation")}
          </Link>
          .
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink">{t("recommend.title")}</h1>
      <p className="mt-1 text-sm text-ink-muted">
        {village.village_name} &middot; {t("recommend.availableCapital")} {formatInr(availableCapital)}
      </p>
      {datasetNote && (
        <p className="mt-2 max-w-2xl border border-demo/30 bg-demo/5 px-3 py-2 text-xs text-demo">{datasetNote}</p>
      )}

      {error && (
        <div className="mt-4 border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">{error}</div>
      )}

      {loading ? (
        <p className="mt-6 text-sm text-ink-muted">{t("recommend.evaluating")}</p>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_380px]">
          <div className="border border-border bg-surface">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-bg text-left text-xs uppercase tracking-wide text-ink-muted">
                  <th className="px-4 py-2 font-medium">{t("recommend.businessCategory")}</th>
                  <th className="px-4 py-2 font-medium">{t("recommend.score")}</th>
                  <th className="px-4 py-2 font-medium">{t("recommend.competitors5km")}</th>
                  <th className="px-4 py-2 font-medium">{t("recommend.estInvestment")}</th>
                  <th className="px-4 py-2"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {items.map((item) => (
                  <tr
                    key={item.category_id}
                    className={`cursor-pointer ${selected?.category_id === item.category_id ? "bg-primary/5" : "hover:bg-bg"}`}
                    onClick={() => setSelected(item)}
                  >
                    <td className="px-4 py-3 font-medium text-ink">{item.category_name}</td>
                    <td className="figures px-4 py-3 font-semibold text-primary">{item.opportunity_score}/100</td>
                    <td className="figures px-4 py-3 text-ink-muted">{item.competitor_count_5km}</td>
                    <td className="figures px-4 py-3 text-ink-muted">
                      {formatInr(item.estimated_investment_low)}&ndash;{formatInr(item.estimated_investment_high)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFullAnalysis(item);
                        }}
                        disabled={savingId === item.category_id}
                        className="border border-primary px-3 py-1 text-xs font-medium text-primary hover:bg-primary hover:text-white disabled:opacity-50"
                      >
                        {savingId === item.category_id ? t("recommend.analyzing") : t("recommend.fullAnalysis")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div>
            {selected && (
              <>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
                  {selected.category_name} &mdash; {t("recommend.scoreBreakdown")}
                </p>
                <OpportunityScoreBar score={selected.opportunity_score} components={selected.components} />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
