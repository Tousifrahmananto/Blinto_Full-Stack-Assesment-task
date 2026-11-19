from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.algorithms.dependency_graph import prerequisite_order
from app.models import Movie, MoviePrerequisite
from app.schemas import MovieDetails, MovieSummary, RewatchPlan


class MovieError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _catalog(session: Session):
    movies = {movie.id: movie for movie in session.scalars(select(Movie).order_by(Movie.id))}
    graph: dict[int, list[int]] = {}
    edges = select(MoviePrerequisite).order_by(
        MoviePrerequisite.movie_id, MoviePrerequisite.prerequisite_id
    )
    for edge in session.scalars(edges):
        graph.setdefault(edge.movie_id, []).append(edge.prerequisite_id)
    return movies, graph


def _details(movie: Movie, prerequisites: list[int]) -> MovieDetails:
    return MovieDetails(**MovieSummary.model_validate(movie).model_dump(),
                        prerequisite_ids=prerequisites)


def list_movies(session: Session):
    session.execute(text("BEGIN"))
    movies, graph = _catalog(session)
    return [_details(movie, graph.get(movie.id, [])) for movie in movies.values()]


def save_movie(session: Session, fields: dict, movie_id: int | None = None):
    with session.begin():
        # Reserve the write lock before reading so overlapping edits cannot form a cycle together.
        session.execute(text("BEGIN IMMEDIATE"))
        prerequisites = fields.pop("prerequisite_ids", None)
        movie = Movie() if movie_id is None else session.get(Movie, movie_id)
        if movie is None:
            raise MovieError("MOVIE_NOT_FOUND", "Movie not found.")
        if "title" in fields:
            owner = session.scalar(select(Movie.id).where(Movie.title == fields["title"]))
            if owner is not None and owner != movie_id:
                raise MovieError("DUPLICATE_TITLE", "A movie already has this title.")
        for key, value in fields.items():
            setattr(movie, key, value)
        if movie_id is None:
            session.add(movie)
        session.flush()
        saved_movies, graph = _catalog(session)
        if prerequisites is not None:
            prerequisites = sorted(set(prerequisites))
            graph[movie.id] = prerequisites
            try:
                prerequisite_order(graph, movie.id)
            except ValueError as error:
                raise MovieError("CIRCULAR_DEPENDENCY", str(error)) from error
            if any(item not in saved_movies for item in prerequisites):
                raise MovieError("UNKNOWN_PREREQUISITE", "A prerequisite movie does not exist.")
            session.execute(delete(MoviePrerequisite).where(MoviePrerequisite.movie_id == movie.id))
            session.add_all([
                MoviePrerequisite(movie_id=movie.id, prerequisite_id=item)
                for item in prerequisites
            ])
        return _details(movie, graph.get(movie.id, []))


def rewatch_plan(session: Session, movie_id: int):
    session.execute(text("BEGIN"))
    movies, graph = _catalog(session)
    if movie_id not in movies:
        raise MovieError("MOVIE_NOT_FOUND", "Movie not found.")
    ordered = [movies[item] for item in prerequisite_order(graph, movie_id)]
    return RewatchPlan(
        movies=[MovieSummary.model_validate(movie) for movie in ordered],
        watched_count=sum(movie.watched for movie in ordered),
        remaining_runtime_minutes=sum(movie.runtime_minutes for movie in ordered if not movie.watched),
    )
