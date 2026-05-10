from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.prediction import TicketAnalyzeResponse, TicketDetailResponse
from app.schemas.ticket import TicketAnalyzeRequest, TicketListItem
from app.services.ticket_service import (
    analyze_ticket_service,
    delete_ticket_service,
    get_ticket_service,
    list_tickets_service,
    update_prediction_service,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/ping")
def return_ping():
    return {"message": "tickets router works"}


@router.get("/example")
def get_example():
    return {
        "id": 1,
        "text": "После обновления приложение вылетает при оплате",
        "category": "payment_bug",
        "priority": "high",
        "sentiment": "negative",
    }


@router.post("/analyze", response_model=TicketAnalyzeResponse)
def analyze_ticket(payload: TicketAnalyzeRequest, db: Session = Depends(get_db)):
    return analyze_ticket_service(payload=payload, db=db)


@router.get("", response_model=list[TicketListItem])
def list_tickets(
    priority: str | None = None,
    category: str | None = None,
    sentiment: str | None = None,
    db: Session = Depends(get_db),
):
    return list_tickets_service(
        db=db,
        priority=priority,
        category=category,
        sentiment=sentiment,
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return get_ticket_service(ticket_id=ticket_id, db=db)


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return delete_ticket_service(ticket_id=ticket_id, db=db)


@router.put("/{ticket_id}/prediction", response_model=TicketAnalyzeResponse)
def update_prediction(
    ticket_id: int,
    db: Session = Depends(get_db),
    category: str | None = None,
    priority: str | None = None,
    sentiment: str | None = None,
    confidence: float | None = None,
):
    return update_prediction_service(
        ticket_id=ticket_id,
        db=db,
        category=category,
        priority=priority,
        sentiment=sentiment,
        confidence=confidence,
    )
