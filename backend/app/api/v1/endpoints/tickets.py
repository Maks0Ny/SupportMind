from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.ticket import TicketBase
from app.models.prediction import PredictionBase
from app.schemas.ticket import TicketAnalyzeRequest, TicketListItem
from app.schemas.prediction import TicketAnalyzeResponse, TicketDetailResponse

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
        "sentiment": "negative"
    }


@router.post("/analyze", response_model=TicketAnalyzeResponse)
def analyze_ticket(payload: TicketAnalyzeRequest, db: Session = Depends(get_db)):
    ticket = TicketBase(text=payload.text)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    prediction = PredictionBase(
        ticket_id=ticket.id,
        category="payment_bug",
        priority="high",
        sentiment="negative",
        confidence=0.91
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return TicketAnalyzeResponse(
        ticket_id=ticket.id,
        category=prediction.category,
        priority=prediction.priority,
        sentiment=prediction.sentiment,
        confidence=prediction.confidence
    )


@router.get("", response_model=list[TicketListItem])
def list_tickets(priority: str | None = None,
                 category: str | None = None,
                 sentiment: str | None = None,
                 db: Session = Depends(get_db)
):
    tickets = db.query(TicketBase).join(PredictionBase)

    if priority:
        tickets = tickets.filter(PredictionBase.priority == priority)

    if category:
        tickets = tickets.filter(PredictionBase.category == category)

    if sentiment:
        tickets = tickets.filter(PredictionBase.sentiment == sentiment)

    tickets = tickets.order_by(TicketBase.id.desc()).all()

    return tickets
    

@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = (
        db.query(TicketBase)
        .options(joinedload(TicketBase.prediction))
        .filter(TicketBase.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = (
        db.query(TicketBase)
        .options(joinedload(TicketBase.prediction))
        .filter(TicketBase.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    else:
        db.delete(ticket)
        db.commit()

    return {"message": "Ticket deleted successfully"}


@router.put("/{ticket_id}/prediction", response_model=TicketAnalyzeResponse)
def update_prediction(ticket_id: int, 
                      db: Session = Depends(get_db),
                      category: str | None = None,
                      priority: str | None = None,
                      sentiment: str | None = None,
                      confidence: float | None = None
):
    ticket = (
        db.query(TicketBase)
        .options(joinedload(TicketBase.prediction))
        .filter(TicketBase.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    prediction = ticket.prediction

    if category is not None:
        prediction.category = category

    if priority is not None:
        prediction.priority = priority

    if sentiment is not None:
        prediction.sentiment = sentiment

    if confidence is not None:
        prediction.confidence = confidence

    db.commit()
    db.refresh(prediction)

    return TicketAnalyzeResponse(
        ticket_id=ticket.id,
        category=prediction.category,
        priority=prediction.priority,
        sentiment=prediction.sentiment,
        confidence=prediction.confidence,
    )