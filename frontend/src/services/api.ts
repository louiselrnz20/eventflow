
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// ==========================================
// OVERVIEW
// ==========================================

export interface EventOverview {
  event_name: string;
  total_revenue: number;
  total_orders?: number;
  total_tickets?: number;
}

export interface AnalyticsOverview {
  competition: EventOverview;
  workshops: {
    event_name: string;
    total_revenue: number;
  };
  combined: {
    total_revenue: number;
  };
}

// ==========================================
// EVENT COMPARISON
// ==========================================

export interface EventComparisonItem {
  event_name: string;
  total_revenue: number;
  revenue_share_percentage: number;
}

export interface EventComparison {
  total_revenue: number;
  highest_revenue_event: string | null;
  events: EventComparisonItem[];
}

// ==========================================
// DAILY SALES
// ==========================================

export interface DailySalesItem {
  sales_date: string;
  total_revenue: number;
  total_orders: number;
  total_tickets: number;
}

export interface CompetitionSummary {
  total_revenue: number;
  total_orders: number;
  total_tickets: number;
  recorded_days: number;
  days_with_sales: number;
  zero_sales_days: number;
}

export interface CompetitionPerformanceMetrics {
  average_daily_revenue: number;
  average_revenue_per_order: number;
  average_ticket_value: number;
}

export interface SalesTrends {
  event_name: string;
  summary: CompetitionSummary;
  performance_metrics: CompetitionPerformanceMetrics;
  highest_revenue_day: DailySalesItem | null;
  lowest_revenue_day: DailySalesItem | null;
  zero_sales_dates: string[];
  daily_sales: DailySalesItem[];
}

// ==========================================
// WORKSHOP ANALYTICS
// ==========================================

export interface WorkshopRevenueSummary {
  early_bird: number;
  regular: number;
  walk_ins: number;
  total_revenue: number;
}

export interface WorkshopInstructor {
  instructor_name: string;
  schedule: string;
  early_bird_revenue: number;
  regular_revenue: number;
  walk_in_revenue: number;
  source_reported_total: number;
}

export interface WorkshopInstructors {
  local: WorkshopInstructor[];
  international: WorkshopInstructor[];
  note: string;
}

export interface WorkshopPricing {
  package_name: string;
  early_bird_price: number | null;
  regular_price: number | null;
  walk_in_price: number | null;
  discounted_price?: number | null;
}

export interface WorkshopPackageRevenue {
  category: string;
  category_type: string;
  revenue_amount: number;
}

export interface WorkshopWithMerch {
  item_or_instructor: string;
  revenue_amount: number;
}

export interface WorkshopDiscount {
  package_name: string;
  recorded_amount: number;
}

export interface NickJosephSales {
  description: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
}

export interface WorkshopAnalytics {
  event_name: string;
  revenue_summary: WorkshopRevenueSummary;
  instructors: WorkshopInstructors;
  single_class_pricing: WorkshopPricing[];
  bundle_pricing: WorkshopPricing[];
  package_revenue_breakdown: WorkshopPackageRevenue[];
  with_merch: WorkshopWithMerch[];
  discount_records: WorkshopDiscount[];
  nick_joseph_sales_breakdown: NickJosephSales[];
  data_notes: string[];
}

// ==========================================
// API FUNCTIONS
// ==========================================

export const getOverview = async () => {
  const response = await api.get<AnalyticsOverview>(
    "/api/analytics/overview"
  );
  return response.data;
};

export const getEventComparison = async () => {
  const response = await api.get<EventComparison>(
    "/api/analytics/events"
  );
  return response.data;
};

export const getSalesTrends = async () => {
  const response = await api.get<SalesTrends>(
    "/api/analytics/sales-trends"
  );
  return response.data;
};

export const getWorkshopAnalytics = async () => {
  const response = await api.get<WorkshopAnalytics>(
    "/api/analytics/workshops"
  );
  return response.data;
};

export default api;
