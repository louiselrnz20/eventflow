
from fastapi import APIRouter

from app.schemas.analytics import (
    AnalyticsOverview,
    EventComparison,
    SalesTrends,
)

from app.services.analytics_service import (
    get_overview,
    get_event_comparison,
    get_sales_trends,
    get_workshop_analytics,
)

router = APIRouter()


@router.get(
    "/overview",
    response_model=AnalyticsOverview
)
def analytics_overview():
    return get_overview()


@router.get(
    "/events",
    response_model=EventComparison
)
def event_comparison():
    return get_event_comparison()


@router.get(
    "/sales-trends",
    response_model=SalesTrends
)
def sales_trends():
    return get_sales_trends()

@router.get("/workshops")
def workshop_analytics():
    return get_workshop_analytics()