from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import MovieCreate, MovieDetails, MoviePatch, RewatchPlan
from app.services import movies

router = APIRouter(prefix="/movies")
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[MovieDetails])
def list_movies(session: DatabaseSession):
    return movies.list_movies(session)


@router.post("", status_code=201, response_model=MovieDetails)
def create_movie(payload: MovieCreate, session: DatabaseSession):
    return movies.save_movie(session, payload.model_dump())


@router.patch("/{movie_id}", response_model=MovieDetails)
def update_movie(movie_id: int, payload: MoviePatch, session: DatabaseSession):
    return movies.save_movie(session, payload.model_dump(exclude_unset=True), movie_id)


@router.get("/{movie_id}/rewatch-order", response_model=RewatchPlan)
def get_rewatch_order(movie_id: int, session: DatabaseSession):
    return movies.rewatch_plan(session, movie_id)
