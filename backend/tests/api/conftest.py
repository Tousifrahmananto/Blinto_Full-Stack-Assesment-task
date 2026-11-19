import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import get_session, make_engine
from app.main import app
from app.models import Base


@pytest.fixture
def api(tmp_path):
    engine = make_engine(tmp_path / "test.sqlite3")
    Base.metadata.create_all(engine)

    def test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = test_session
    try:
        yield TestClient(app), engine
    finally:
        app.dependency_overrides.pop(get_session)
        engine.dispose()
