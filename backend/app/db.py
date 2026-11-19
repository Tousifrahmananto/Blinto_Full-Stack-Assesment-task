from pathlib import Path

from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import Session

DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "doomsday.sqlite3"


def make_engine(path):
    engine = create_engine(URL.create("sqlite", database=str(path)))

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys = ON")

    return engine


engine = make_engine(DATABASE_PATH)


def get_session():
    with Session(engine) as session:
        yield session
