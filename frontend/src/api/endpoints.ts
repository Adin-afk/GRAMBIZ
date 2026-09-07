import { api } from "./client";
import type {
  AssessmentOut,
  BusinessCategory,
  FinancialCalculateResponse,
  NearbyBusiness,
  NearbyMarket,
  RecommendResponse,
  RepaymentResponse,
  Taluka,
  User,
  Village,
} from "../types/api";

export async function registerUser(payload: {
  full_name: string;
  email: string;
  password: string;
  phone?: string;
}): Promise<User> {
  const { data } = await api.post<User>("/api/auth/register", payload);
  return data;
}

export async function loginUser(email: string, password: string): Promise<string> {
  const { data } = await api.post<{ access_token: string }>("/api/auth/login", { email, password });
  return data.access_token;
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/api/users/me");
  return data;
}

export async function fetchTalukas(): Promise<Taluka[]> {
  const { data } = await api.get<Taluka[]>("/api/locations/talukas");
  return data;
}

export async function fetchVillages(talukaId: string, areaType = "RURAL"): Promise<Village[]> {
  const { data } = await api.get<Village[]>("/api/locations/villages", {
    params: { taluka_id: talukaId, area_type: areaType },
  });
  return data;
}

export async function fetchVillage(villageId: string): Promise<Village> {
  const { data } = await api.get<Village>(`/api/locations/villages/${villageId}`);
  return data;
}

export async function fetchBusinessCategories(): Promise<BusinessCategory[]> {
  const { data } = await api.get<BusinessCategory[]>("/api/business-categories");
  return data;
}

export async function fetchNearbyBusinesses(
  villageId: string,
  radiusKm: number,
  categoryId?: string
): Promise<NearbyBusiness[]> {
  const { data } = await api.get<NearbyBusiness[]>("/api/businesses/nearby", {
    params: { village_id: villageId, radius_km: radiusKm, category_id: categoryId },
  });
  return data;
}

export async function fetchNearbyMarkets(villageId: string, radiusKm: number): Promise<NearbyMarket[]> {
  const { data } = await api.get<NearbyMarket[]>("/api/market/nearby", {
    params: { village_id: villageId, radius_km: radiusKm },
  });
  return data;
}

export async function recommendBusinesses(villageId: string, availableCapital: number): Promise<RecommendResponse> {
  const { data } = await api.post<RecommendResponse>("/api/business/recommend", {
    village_id: villageId,
    available_capital: availableCapital,
  });
  return data;
}

export async function calculateFinancials(
  availableMargin: number,
  beneficiaryContributionPct?: number
): Promise<FinancialCalculateResponse> {
  const { data } = await api.post<FinancialCalculateResponse>("/api/financial/calculate", {
    available_margin: availableMargin,
    beneficiary_contribution_pct: beneficiaryContributionPct,
  });
  return data;
}

export async function calculateRepayment(
  principal: number,
  annualInterestRatePct: number,
  tenureYears: number,
  moratoriumMonths: number
): Promise<RepaymentResponse> {
  const { data } = await api.post<RepaymentResponse>("/api/financial/repayment", {
    principal,
    annual_interest_rate_pct: annualInterestRatePct,
    tenure_years: tenureYears,
    moratorium_months: moratoriumMonths,
  });
  return data;
}

export async function createAssessment(
  villageId: string,
  categoryId: string,
  availableCapital: number
): Promise<AssessmentOut> {
  const { data } = await api.post<AssessmentOut>("/api/assessment/create", {
    village_id: villageId,
    category_id: categoryId,
    available_capital: availableCapital,
  });
  return data;
}

export async function fetchAssessment(id: string): Promise<AssessmentOut> {
  const { data } = await api.get<AssessmentOut>(`/api/assessment/${id}`);
  return data;
}

export async function synthesizeSpeech(text: string): Promise<Blob> {
  const { data } = await api.post<Blob>(
    "/api/voice/speak",
    { text },
    { responseType: "blob" }
  );
  return data;
}

export async function fetchVoiceStatus(): Promise<{ configured: boolean }> {
  const { data } = await api.get<{ configured: boolean }>("/api/voice/status");
  return data;
}

export async function fetchServicesHealth(): Promise<{
  gemini: "configured" | "not_configured";
  gemini_last_error: string | null;
  elevenlabs_voice: "configured" | "not_configured";
}> {
  const { data } = await api.get("/api/health/services");
  return data;
}
