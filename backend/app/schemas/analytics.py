
from datetime import date
from typing import Optional
from pydantic import BaseModel


class CompetitionOverview(BaseModel):
    event_name: str
    total_revenue: float
    total_orders: int
    total_tickets: int


class WorkshopsOverview(BaseModel):
    event_name: str
    total_revenue: float


class CombinedOverview(BaseModel):
    total_revenue: float


class AnalyticsOverview(BaseModel):
    competition: CompetitionOverview
    workshops: WorkshopsOverview
    combined: CombinedOverview


class EventComparisonItem(BaseModel):
    event_name: str
    total_revenue: float
    revenue_share_percentage: float


class EventComparison(BaseModel):
    total_revenue: float
    highest_revenue_event: str | None
    events: list[EventComparisonItem]


class DailySalesItem(BaseModel):
    sales_date: date
    total_revenue: float
    total_orders: int
    total_tickets: int

class CompetitionSummary(BaseModel):
    total_revenue: float
    total_orders: int
    total_tickets: int
    recorded_days: int
    days_with_sales: int
    zero_sales_days: int


class CompetitionPerformanceMetrics(BaseModel):
    average_daily_revenue: float
    average_revenue_per_order: float
    average_ticket_value: float


class SalesTrends(BaseModel):
    event_name: str
    summary: CompetitionSummary
    performance_metrics: CompetitionPerformanceMetrics
    highest_revenue_day: Optional[DailySalesItem] = None
    lowest_revenue_day: Optional[DailySalesItem] = None
    zero_sales_dates: list[date]
    daily_sales: list[DailySalesItem]

