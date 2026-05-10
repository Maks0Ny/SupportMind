from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.prediction import PredictionBase
from app.models.ticket import TicketBase
from app.ml.category_predictor import predictor
from app.schemas.prediction import TicketAnalyzeResponse
from app.schemas.ticket import TicketAnalyzeRequest
from app.services.cache_service import clear_dashboard_cache


def analyze_ticket_service(
    payload: TicketAnalyzeRequest,
    db: Session,
) -> TicketAnalyzeResponse:
    ticket = TicketBase(text=payload.text)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    prediction_result = predictor.predict(payload.text)

    prediction = PredictionBase(
        ticket_id=ticket.id,
        category=prediction_result.category,
        priority=prediction_result.priority,
        sentiment=prediction_result.sentiment,
        confidence=prediction_result.confidence,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    clear_dashboard_cache()

    return TicketAnalyzeResponse(
        ticket_id=ticket.id,
        category=prediction.category,
        priority=prediction.priority,
        sentiment=prediction.sentiment,
        confidence=prediction.confidence,
    )


def list_tickets_service(
    db: Session,
    priority: str | None = None,
    category: str | None = None,
    sentiment: str | None = None,
) -> list[TicketBase]:
    tickets = db.query(TicketBase).join(PredictionBase)

    if priority:
        tickets = tickets.filter(PredictionBase.priority == priority)

    if category:
        tickets = tickets.filter(PredictionBase.category == category)

    if sentiment:
        tickets = tickets.filter(PredictionBase.sentiment == sentiment)

    return tickets.order_by(TicketBase.id.desc()).all()


def get_ticket_service(ticket_id: int, db: Session) -> TicketBase:
    ticket = (
        db.query(TicketBase)
        .options(joinedload(TicketBase.prediction))
        .filter(TicketBase.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


def delete_ticket_service(ticket_id: int, db: Session) -> dict[str, str]:
    ticket = (
        db.query(TicketBase)
        .options(joinedload(TicketBase.prediction))
        .filter(TicketBase.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()

    clear_dashboard_cache()

    return {"message": "Ticket deleted successfully"}


def update_prediction_service(
    ticket_id: int,
    db: Session,
    category: str | None = None,
    priority: str | None = None,
    sentiment: str | None = None,
    confidence: float | None = None,
) -> TicketAnalyzeResponse:
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

    clear_dashboard_cache()

    return TicketAnalyzeResponse(
        ticket_id=ticket.id,
        category=prediction.category,
        priority=prediction.priority,
        sentiment=prediction.sentiment,
        confidence=prediction.confidence,
    )
