from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import get_session, make_engine
from app.main import app
from app.models import Base, Movie


def test_movies_list_reads_database(tmp_path):
    engine = make_engine(tmp_path / "test.sqlite3")
    Base.metadata.create_all(engine)

    def test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = test_session
    try:
        client = TestClient(app)
        response = client.get("/api/movies")
        assert response.status_code == 200
        assert response.json() == []

        with Session(engine) as session:
            session.add(Movie(title="Iron Man", release_year=2008, runtime_minutes=126))
            session.commit()

        response = client.get("/api/movies")
        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "title": "Iron Man", "release_year": 2008,
             "runtime_minutes": 126, "watched": False}
        ]
    finally:
        app.dependency_overrides.pop(get_session)
        engine.dispose()
