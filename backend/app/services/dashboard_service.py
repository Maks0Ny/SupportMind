from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.prediction import PredictionBase
from app.models.ticket import TicketBase
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.cache_service import get_dashboard_cache, set_dashboard_cache


def rows_to_dict(rows: list[Any]) -> dict[str, int]:
    result: dict[str, int] = {}

    for row in rows:
        key = row[0]
        value = row[1]

        if key is not None:
            result[str(key)] = int(value)

    return result


def get_dashboard_summary_service(db: Session) -> DashboardSummaryResponse:
    cached_summary = get_dashboard_cache()

    if cached_summary is not None:
        return DashboardSummaryResponse(**cached_summary)

    total_tickets = db.query(func.count(TicketBase.id)).scalar() or 0

    high_priority_count = (
        db.query(func.count(PredictionBase.id))
        .filter(PredictionBase.priority == "high")
        .scalar()
        or 0
    )

    negative_sentiment_count = (
        db.query(func.count(PredictionBase.id))
        .filter(PredictionBase.sentiment == "negative")
        .scalar()
        or 0
    )

    by_category_rows = (
        db.query(PredictionBase.category, func.count(PredictionBase.id))
        .group_by(PredictionBase.category)
        .all()
    )

    by_priority_rows = (
        db.query(PredictionBase.priority, func.count(PredictionBase.id))
        .group_by(PredictionBase.priority)
        .all()
    )

    by_sentiment_rows = (
        db.query(PredictionBase.sentiment, func.count(PredictionBase.id))
        .group_by(PredictionBase.sentiment)
        .all()
    )

    summary = DashboardSummaryResponse(
        total_tickets=total_tickets,
        high_priority_count=high_priority_count,
        negative_sentiment_count=negative_sentiment_count,
        by_category=rows_to_dict(by_category_rows),
        by_priority=rows_to_dict(by_priority_rows),
        by_sentiment=rows_to_dict(by_sentiment_rows),
    )

    set_dashboard_cache(summary.model_dump())

    return summary
