from sqlalchemy.orm import Session

from app.models import Movie


def test_movies_list_reads_database(api):
    client, engine = api
    assert client.get("/api/movies").json() == []
    with Session(engine) as session:
        session.add(Movie(title="Iron Man", release_year=2008, runtime_minutes=126))
        session.commit()
    response = client.get("/api/movies")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "Iron Man", "release_year": 2008, "runtime_minutes": 126,
         "watched": False, "prerequisite_ids": []}
    ]


def create(client, title, prerequisites=(), **fields):
    body = {"title": title, "release_year": 2020, "runtime_minutes": 100,
            "prerequisite_ids": list(prerequisites), **fields}
    response = client.post("/api/movies", json=body)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_rewatch_plan_and_cycle_rollback(api):
    client, _ = api
    iron_man = create(client, "Iron Man", watched=True)
    first_avenger = create(client, "First Avenger")
    avengers = create(client, "Avengers", (iron_man, first_avenger))
    civil_war = create(client, "Civil War", (avengers, iron_man))
    ragnarok = create(client, "Ragnarok")
    infinity_war = create(client, "Infinity War", (civil_war, ragnarok))
    endgame = create(client, "Endgame", (infinity_war,))
    doomsday = create(client, "Doomsday", (endgame,))

    def plan(target):
        response = client.get(f"/api/movies/{target}/rewatch-order")
        assert response.status_code == 200
        return response.json()

    before = plan(doomsday)
    assert [movie["id"] for movie in before["movies"]] == [
        iron_man, first_avenger, avengers, civil_war, ragnarok, infinity_war, endgame
    ]
    assert before["watched_count"] == 1
    assert before["remaining_runtime_minutes"] == 600
    assert plan(ragnarok) == {"movies": [], "watched_count": 0, "remaining_runtime_minutes": 0}

    failed = client.patch(f"/api/movies/{iron_man}", json={
        "prerequisite_ids": [endgame], "watched": False, "title": "Changed"
    })
    assert failed.status_code == 409
    assert failed.json()["code"] == "CIRCULAR_DEPENDENCY"
    assert plan(doomsday) == before

    assert client.patch(f"/api/movies/{first_avenger}", json={"watched": True}).status_code == 200
    assert plan(doomsday)["remaining_runtime_minutes"] == 500
    assert plan(doomsday)["watched_count"] == 2
    assert client.patch(f"/api/movies/{avengers}", json={"prerequisite_ids": []}).json()["prerequisite_ids"] == []
    assert first_avenger not in [movie["id"] for movie in plan(doomsday)["movies"]]


def test_movie_errors_do_not_persist_changes(api):
    client, _ = api
    body = {"title": "One", "release_year": 2026, "runtime_minutes": 60}
    self_reference = client.post("/api/movies", json={**body, "prerequisite_ids": [1]})
    assert (self_reference.status_code, self_reference.json()["code"]) == (409, "CIRCULAR_DEPENDENCY")
    assert client.post("/api/movies", json={**body, "prerequisite_ids": [99]}).status_code == 422
    assert client.post("/api/movies", json={**body, "runtime_minutes": 301}).status_code == 422
    assert client.get("/api/movies").json() == []
    movie_id = create(client, "One")
    assert client.post("/api/movies", json={**body, "title": " One "}).status_code == 409
    assert client.patch(f"/api/movies/{movie_id}", json={"watched": None}).status_code == 422
    assert client.get("/api/movies/99/rewatch-order").status_code == 404


def test_competing_edits_cannot_create_cycle(api):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    client, _ = api
    first = create(client, "First")
    second = create(client, "Second")
    start = Barrier(2)

    def edit(movie_id, prerequisite):
        start.wait(timeout=5)
        return client.patch(f"/api/movies/{movie_id}", json={
            "prerequisite_ids": [prerequisite]
        })

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = [
            pool.submit(edit, first, second),
            pool.submit(edit, second, first),
        ]
        results = [response.result(timeout=10) for response in responses]
    assert sorted(response.status_code for response in results) == [200, 409]
    assert next(response for response in results if response.status_code == 409).json()[
        "code"
    ] == "CIRCULAR_DEPENDENCY"
