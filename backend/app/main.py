from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.controllers.movies import router as movies_router
from app.db import DATABASE_PATH, engine
from app.models import Base


@asynccontextmanager
async def lifespan(_app):
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Doomsday Ready", lifespan=lifespan)
app.include_router(movies_router, prefix="/api")
