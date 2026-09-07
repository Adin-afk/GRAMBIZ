export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  role: string;
  preferred_language: string;
}

export interface Taluka {
  id: string;
  name: string;
  headquarters: string | null;
  total_villages: number | null;
  rural_villages: number | null;
  latitude: number | null;
  longitude: number | null;
}

export interface Village {
  id: string;
  village_name: string;
  taluka_id: string;
  gram_panchayat: string | null;
  area_type: string;
  population: number | null;
  households: number | null;
  latitude: number;
  longitude: number;
  data_status: string;
  verification_status: string;
}

export interface BusinessCategory {
  id: string;
  name: string;
  description: string | null;
  sector: string | null;
  typical_min_investment: number | null;
  typical_max_investment: number | null;
}

export interface ScoreComponents {
  demand: number;
  competition: number;
  accessibility: number;
  cost: number;
  margin: number;
  market_access: number;
  seasonality: number;
}

export interface RecommendationItem {
  category_id: string;
  category_name: string;
  opportunity_score: number;
  components: ScoreComponents;
  competitor_count_5km: number;
  competitor_count_10km: number;
  estimated_investment_low: number | null;
  estimated_investment_high: number | null;
}

export interface RecommendResponse {
  village_id: string;
  available_capital: number;
  recommendations: RecommendationItem[];
  dataset_note: string;
}

export interface MatchedScheme {
  id: string;
  scheme_name: string;
  provider: string;
  interest_rate: number;
  tenure_years: number;
  moratorium_months: number;
  maximum_loan: number;
  loan_percentage: number;
  beneficiary_contribution: number;
  data_status: string;
  source: string | null;
  source_url: string | null;
}

export interface FinancialCalculateResponse {
  available_margin: number;
  project_cost: number;
  loan_amount: number;
  beneficiary_contribution_pct: number;
  matched_schemes: MatchedScheme[];
  selected_scheme: MatchedScheme | null;
}

export interface RepaymentEntry {
  installment_number: number;
  due_date: string;
  principal_component: number;
  interest_component: number;
  remaining_balance: number;
  phase: "MORATORIUM" | "REPAYMENT";
}

export interface RepaymentResponse {
  installment: number;
  total_interest: number;
  total_repayment: number;
  schedule: RepaymentEntry[];
}

export interface NearbyBusiness {
  id: string;
  business_name: string;
  owner_name: string | null;
  category_name: string;
  village_name: string;
  taluka_name: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  data_status: string;
  source: string | null;
  source_date: string | null;
}

export interface NearbyMarket {
  id: string;
  market_name: string;
  market_type: string | null;
  taluka_name: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  data_status: string;
  source: string | null;
  source_date: string | null;
}

export interface AssessmentOut {
  id: string;
  village_id: string;
  category_id: string | null;
  available_capital: number;
  opportunity_score: number | null;
  market_analysis: Record<string, unknown> | null;
  competitor_analysis: {
    competitors_5km: NearbyBusiness[];
    competitors_10km: NearbyBusiness[];
    competitor_count_5km: number;
    competitor_count_10km: number;
    density: { density_5km_per_sqkm: number; density_10km_per_sqkm: number };
  } | null;
  financial_analysis: Record<string, unknown> | null;
  scheme_match: { matched_schemes: string[]; count: number } | null;
  risk_assessment: { risk_level: string; opportunity_score: number } | null;
  swot: Record<string, unknown> | null;
  ai_explanation: string | null;
  confidence_level: string;
  dataset_version: string | null;
  model_version: string | null;
}

export interface ApiError {
  success: false;
  error_code: string;
  message: string;
}
