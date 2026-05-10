
from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_tickets: int
    high_priority_count: int
    negative_sentiment_count: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
    by_sentiment: dict[str, int]
    
    
    
