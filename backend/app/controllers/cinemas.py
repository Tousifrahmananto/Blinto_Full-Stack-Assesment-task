from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import BookingQuote, CinemaCreate, CinemaDetails
from app.services import cinemas

router = APIRouter(prefix="/cinemas")
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.post("", status_code=201, response_model=CinemaDetails)
def create_cinema(payload: CinemaCreate, session: DatabaseSession):
    return cinemas.create_cinema(session, payload)


@router.get("", response_model=list[CinemaDetails])
def list_cinemas(session: DatabaseSession):
    return cinemas.list_cinemas(session)


@router.get("/{cinema_id}/booking", response_model=BookingQuote)
def booking_quote(
    cinema_id: int, session: DatabaseSession,
    group_size: Annotated[int, Query(alias="groupSize", ge=1, le=10_000)],
):
    return cinemas.booking_quote(session, cinema_id, group_size)
