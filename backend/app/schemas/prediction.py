from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TicketAnalyzeResponse(BaseModel):
    ticket_id: int
    category: str
    priority: str
    sentiment: str
    confidence: float

class TicketExampleResponse(BaseModel):
    id: int
    text: str
    category: str
    priority: str
    sentiment: str

class PredictionData(BaseModel):
    category: str
    priority: str
    sentiment: str
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    prediction: PredictionData | None = None

    model_config = ConfigDict(from_attributes=True)