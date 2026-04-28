from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TicketAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=2000)


class TicketListItem(BaseModel):
    id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)