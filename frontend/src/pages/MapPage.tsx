import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import L from "leaflet";
import { fetchNearbyBusinesses, fetchNearbyMarkets } from "../api/endpoints";
import { extractErrorMessage } from "../api/client";
import { useLocationContext } from "../context/LocationContext";
import DataStatusBadge from "../components/DataStatusBadge";
import type { NearbyBusiness, NearbyMarket } from "../types/api";

// Default Leaflet marker icons don't resolve correctly under bundlers;
// point them at the unpkg CDN assets instead.
const villageIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapPage() {
  const { t } = useTranslation();
  const { village } = useLocationContext();
  const [businesses, setBusinesses] = useState<NearbyBusiness[]>([]);
  const [markets, setMarkets] = useState<NearbyMarket[]>([]);
  const [radius, setRadius] = useState<5 | 10>(5);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!village) return;
    setLoading(true);
    setError(null);
    Promise.all([fetchNearbyBusinesses(village.id, radius), fetchNearbyMarkets(village.id, radius)])
      .then(([b, m]) => {
        setBusinesses(b);
        setMarkets(m);
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [village, radius]);

  if (!village) {
    return (
      <div className="max-w-xl border border-border bg-surface p-6">
        <p className="text-sm text-ink-muted">
          {t("map.selectVillageFirst")}{" "}
          <Link to="/location" className="text-primary underline">
            {t("map.goToLocation")}
          </Link>
          .
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">{village.village_name}</h1>
          <p className="text-sm text-ink-muted">
            {businesses.length} {t("map.businessesCount")} &middot; {markets.length} {t("map.marketsWithin")} {radius}{" "}
            {t("map.km")}
          </p>
        </div>
        <div className="flex border border-border-strong text-sm">
          <button
            onClick={() => setRadius(5)}
            className={`px-3 py-1.5 ${radius === 5 ? "bg-primary text-white" : "bg-surface text-ink-muted"}`}
          >
            5 {t("map.km")}
          </button>
          <button
            onClick={() => setRadius(10)}
            className={`px-3 py-1.5 ${radius === 10 ? "bg-primary text-white" : "bg-surface text-ink-muted"}`}
          >
            10 {t("map.km")}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 border border-risk-high/30 bg-risk-high/5 px-3 py-2 text-sm text-risk-high">{error}</div>
      )}
      {loading && <p className="mb-2 text-xs text-ink-muted">{t("map.loadingSpatial")}</p>}

      <div className="h-[520px] border border-border">
        <MapContainer center={[village.latitude, village.longitude]} zoom={12} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={[village.latitude, village.longitude]} icon={villageIcon}>
            <Popup>
              <strong>{village.village_name}</strong>
              <br />
              {t("map.selectedVillage")}
            </Popup>
          </Marker>
          <Circle
            center={[village.latitude, village.longitude]}
            radius={radius * 1000}
            pathOptions={{ color: "#1b3a5c", fillOpacity: 0.03, weight: 1 }}
          />
          {businesses.map((b) => (
            <Marker key={b.id} position={[b.latitude, b.longitude]}>
              <Popup>
                <strong>{b.business_name}</strong>
                <br />
                {b.category_name} &middot; {b.distance_km} km away
                <br />
                <span style={{ fontSize: 11, color: "#a66a00" }}>{b.data_status}</span>
              </Popup>
            </Marker>
          ))}
          {markets.map((m) => (
            <Marker key={m.id} position={[m.latitude, m.longitude]}>
              <Popup>
                <strong>{m.market_name}</strong>
                <br />
                {m.market_type} &middot; {m.distance_km} km away
                <br />
                <span style={{ fontSize: 11, color: "#a66a00" }}>{m.data_status}</span>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="border border-border bg-surface">
          <h2 className="border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            {t("map.nearbyBusinesses")}
          </h2>
          <ul className="max-h-64 divide-y divide-border overflow-y-auto">
            {businesses.map((b) => (
              <li key={b.id} className="flex items-center justify-between px-4 py-2 text-sm">
                <div>
                  <p className="font-medium text-ink">{b.business_name}</p>
                  <p className="text-xs text-ink-muted">
                    {b.category_name} &middot; {b.distance_km} km
                  </p>
                </div>
                <DataStatusBadge status={b.data_status} />
              </li>
            ))}
            {businesses.length === 0 && !loading && (
              <li className="px-4 py-3 text-sm text-ink-muted">{t("map.noBusinessesFound", { radius })}</li>
            )}
          </ul>
        </div>

        <div className="border border-border bg-surface">
          <h2 className="border-b border-border bg-bg px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            {t("map.nearbyMarkets")}
          </h2>
          <ul className="max-h-64 divide-y divide-border overflow-y-auto">
            {markets.map((m) => (
              <li key={m.id} className="flex items-center justify-between px-4 py-2 text-sm">
                <div>
                  <p className="font-medium text-ink">{m.market_name}</p>
                  <p className="text-xs text-ink-muted">
                    {m.market_type} &middot; {m.distance_km} km
                  </p>
                </div>
                <DataStatusBadge status={m.data_status} />
              </li>
            ))}
            {markets.length === 0 && !loading && (
              <li className="px-4 py-3 text-sm text-ink-muted">{t("map.noMarketsFound", { radius })}</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
