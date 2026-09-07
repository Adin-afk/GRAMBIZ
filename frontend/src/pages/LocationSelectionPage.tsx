import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { fetchTalukas, fetchVillages } from "../api/endpoints";
import { extractErrorMessage } from "../api/client";
import { useLocationContext } from "../context/LocationContext";
import DataStatusBadge from "../components/DataStatusBadge";
import type { Taluka, Village } from "../types/api";

export default function LocationSelectionPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { taluka, village, availableCapital, setTaluka, setVillage, setAvailableCapital } = useLocationContext();

  const [talukas, setTalukas] = useState<Taluka[]>([]);
  const [villages, setVillages] = useState<Village[]>([]);
  const [capitalInput, setCapitalInput] = useState(availableCapital?.toString() ?? "");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTalukas()
      .then(setTalukas)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!taluka) {
      setVillages([]);
      return;
    }
    fetchVillages(taluka.id)
      .then(setVillages)
      .catch((err) => setError(extractErrorMessage(err)));
  }, [taluka]);

  function handleTalukaChange(id: string) {
    const t = talukas.find((tk) => tk.id === id) || null;
    setTaluka(t);
    setVillage(null);
  }

  function handleVillageChange(id: string) {
    const v = villages.find((vg) => vg.id === id) || null;
    setVillage(v);
  }

  function handleContinue() {
    const capital = parseFloat(capitalInput);
    if (!village || Number.isNaN(capital) || capital <= 0) return;
    setAvailableCapital(capital);
    navigate("/recommend");
  }

  return (
    <div className="max-w-2xl">
      <h1 className="font-display text-2xl font-semibold text-ink">{t("location.title")}</h1>
      <p className="mt-1 text-sm text-ink-muted">{t("location.subtitle")}</p>

      {error && (
        <div className="mt-4 border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">{error}</div>
      )}

      <div className="mt-6 border border-border bg-surface p-6">
        <ol className="mb-6 flex flex-wrap items-center gap-1 text-xs text-ink-muted">
          <li className="border border-border-strong bg-bg px-2 py-1">{t("location.maharashtra")}</li>
          <li>&rsaquo;</li>
          <li className="border border-border-strong bg-bg px-2 py-1">{t("location.solapurDistrict")}</li>
          <li>&rsaquo;</li>
          <li className="border border-border-strong bg-bg px-2 py-1">{t("location.rural")}</li>
          <li>&rsaquo;</li>
          <li className={`border px-2 py-1 ${taluka ? "border-primary bg-primary/5 text-primary" : "border-border-strong bg-bg"}`}>
            {taluka?.name ?? t("location.talukaPlaceholder")}
          </li>
          <li>&rsaquo;</li>
          <li className={`border px-2 py-1 ${village ? "border-primary bg-primary/5 text-primary" : "border-border-strong bg-bg"}`}>
            {village?.village_name ?? t("location.villagePlaceholder")}
          </li>
        </ol>

        <label className="mb-4 block text-sm">
          <span className="mb-1 block font-medium text-ink">{t("location.talukaLabel")}</span>
          <select
            value={taluka?.id ?? ""}
            onChange={(e) => handleTalukaChange(e.target.value)}
            disabled={loading}
            className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary"
          >
            <option value="">{loading ? t("location.loadingTalukas") : t("location.selectTaluka")}</option>
            {talukas.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
                {t.headquarters ? ` (HQ: ${t.headquarters})` : ""}
              </option>
            ))}
          </select>
        </label>

        <label className="mb-4 block text-sm">
          <span className="mb-1 block font-medium text-ink">{t("location.villageLabel")}</span>
          <select
            value={village?.id ?? ""}
            onChange={(e) => handleVillageChange(e.target.value)}
            disabled={!taluka}
            className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary disabled:bg-bg disabled:text-ink-faint"
          >
            <option value="">{taluka ? t("location.selectVillage") : t("location.selectTalukaFirst")}</option>
            {villages.map((v) => (
              <option key={v.id} value={v.id}>
                {v.village_name}
                {v.population ? ` - pop. ${v.population.toLocaleString("en-IN")}` : ""}
              </option>
            ))}
          </select>
        </label>

        {village && (
          <div className="mb-4 flex items-center justify-between border border-border bg-bg px-3 py-2 text-xs text-ink-muted">
            <span>
              {t("location.gramPanchayat")}: {village.gram_panchayat ?? "—"} &middot; {t("location.households")}:{" "}
              {village.households?.toLocaleString("en-IN") ?? "—"}
            </span>
            <DataStatusBadge status={village.data_status} />
          </div>
        )}

        <label className="mb-6 block text-sm">
          <span className="mb-1 block font-medium text-ink">{t("location.availableCapitalLabel")}</span>
          <input
            type="number"
            min={1}
            value={capitalInput}
            onChange={(e) => setCapitalInput(e.target.value)}
            placeholder={t("location.capitalPlaceholder") ?? undefined}
            className="w-full border border-border-strong bg-surface px-3 py-2 text-sm focus:border-primary"
          />
        </label>

        <button
          onClick={handleContinue}
          disabled={!village || !capitalInput}
          className="bg-accent px-5 py-2.5 text-sm font-medium text-white hover:bg-accent-dark disabled:opacity-40"
        >
          {t("location.continue")}
        </button>
      </div>
    </div>
  );
}
