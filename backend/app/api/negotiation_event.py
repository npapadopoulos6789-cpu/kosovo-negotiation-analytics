from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import negotiation_event as event_service
from app.schemas.negotiation_event import (
    NegotiationEventCreate, NegotiationEventUpdate, NegotiationEventRead
)

router = APIRouter(prefix="/negotiation-events", tags=["Negotiation Events"])


@router.get("/", response_model=list[NegotiationEventRead])
def list_events(db: Session = Depends(get_db)):
    return event_service.list_events(db)


@router.get("/{event_id}", response_model=NegotiationEventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return event_service.get_event(db, event_id)


@router.post("/", response_model=NegotiationEventRead, status_code=201)
def create_event(payload: NegotiationEventCreate, db: Session = Depends(get_db)):
    return event_service.create_event(db, payload)


@router.put("/{event_id}", response_model=NegotiationEventRead)
def update_event(event_id: int, payload: NegotiationEventUpdate, db: Session = Depends(get_db)):
    return event_service.update_event(db, event_id, payload)


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event_service.delete_event(db, event_id)