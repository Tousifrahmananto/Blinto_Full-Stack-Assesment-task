from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers.cinemas import router as cinemas_router
from app.controllers.movies import router as movies_router
from app.db import DATABASE_PATH, engine
from app.models import Base
from app.services.cinemas import CinemaError
from app.services.movies import MovieError


@asynccontextmanager
async def lifespan(_app):
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Doomsday Ready", lifespan=lifespan)
app.include_router(movies_router, prefix="/api")
app.include_router(cinemas_router, prefix="/api")


@app.exception_handler(MovieError)
@app.exception_handler(CinemaError)
async def domain_error(_request: Request, error: MovieError | CinemaError):
    status = {
        "MOVIE_NOT_FOUND": 404,
        "CINEMA_NOT_FOUND": 404,
        "DUPLICATE_CINEMA_NAME": 409,
        "DUPLICATE_TITLE": 409,
        "CIRCULAR_DEPENDENCY": 409,
        "UNKNOWN_PREREQUISITE": 422,
    }[error.code]
    return JSONResponse(status_code=status, content={"code": error.code, "message": str(error)})
