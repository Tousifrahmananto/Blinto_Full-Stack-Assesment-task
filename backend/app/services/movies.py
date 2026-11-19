from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Movie


def list_movies(session: Session):
    return session.scalars(select(Movie).order_by(Movie.id)).all()
