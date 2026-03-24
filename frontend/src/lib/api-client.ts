import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_BASE });

export interface Region {
  id: number;
  name: string;
  code: string;
  level: string;
  parent_id: number | null;
  latitude: number | null;
  longitude: number | null;
  population: number | null;
}

export interface PeriodMetrics {
  disease: string;
  region: string;
  period_start: string;
  period_end: string;
  total_new_cases: number;
  total_new_deaths: number;
  cases_at_start: number;
  cases_at_end: number;
  deaths_at_start: number;
  deaths_at_end: number;
  avg_daily_cases: number;
  avg_daily_deaths: number;
  num_days: number;
  trend: string;
  incidence_rate: number;
  mortality_rate: number;
}

export interface Anomaly {
  date: string;
  value: number;
  type: string;
  severity: string;
  z_score: number;
  deviation_pct: number;
}

export interface TimeSeriesData {
  date: string;
  new_cases: number;
  new_deaths: number;
  total_cases: number;
  total_deaths: number;
}

export interface InsightRequest {
  question: string;
  disease?: string;
  region?: string;
  regions?: string[];
  start_date?: string;
  end_date?: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface InsightResponse {
  query: string;
  narrative: string;
  correlations: Array<{
    factor1: string;
    factor2: string;
    correlation_coefficient: number;
    p_value: number;
    interpretation: string;
  }>;
  supporting_data: Record<string, any>;
  visualization_data?: {
    time_series: TimeSeriesData[];
    chart_type: string;
  };
  anomalies: Anomaly[];
  trend_data?: {
    growth_rate_pct: number;
    current_7day_avg: number;
    previous_7day_avg: number;
    trend: string;
  };
}

export const apiClient = {
  async getRegions(): Promise<Region[]> {
    const { data } = await api.get('/api/regions/');
    return data;
  },

  async getPeriodMetrics(disease: string, regionCode: string, startDate: string, endDate: string): Promise<PeriodMetrics> {
    const { data } = await api.get(`/api/diseases/${encodeURIComponent(disease)}/period-metrics`, {
      params: { region_code: regionCode, start_date: startDate, end_date: endDate }
    });
    return data;
  },

  async generateInsight(request: InsightRequest): Promise<InsightResponse> {
    const { data } = await api.post('/api/insights/', request);
    return data;
  },

  async getTimeSeries(disease: string, regionCode: string, startDate: string, endDate: string): Promise<TimeSeriesData[]> {
    const { data } = await api.get(`/api/diseases/${encodeURIComponent(disease)}/time-series`, {
      params: { region_code: regionCode, start_date: startDate, end_date: endDate }
    });
    return data;
  },
};
