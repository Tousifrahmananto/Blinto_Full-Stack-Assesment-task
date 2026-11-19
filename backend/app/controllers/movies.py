from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import MovieSummary
from app.services import movies

router = APIRouter(prefix="/movies")


@router.get("", response_model=list[MovieSummary])
def list_movies(session: Annotated[Session, Depends(get_session)]):
    return movies.list_movies(session)
