import pytest


def test_cinema_create_list_and_quote(api):
    client, _ = api
    assert client.get("/api/cinemas").json() == []
    response = client.post("/api/cinemas", json={"name": "  Star Cinema  ", "bundle_sizes": [4, 3, 1]})
    assert response.status_code == 201
    cinema = response.json()
    assert cinema == {"id": 1, "name": "Star Cinema", "bundle_sizes": [1, 3, 4]}
    assert client.get("/api/cinemas").json() == [cinema]
    quote = client.get("/api/cinemas/1/booking", params={"groupSize": 6})
    assert quote.status_code == 200
    assert quote.json() == {"possible": True, "bundle_count": 2, "bundles": [{"size": 3, "quantity": 2}]}

    duplicate = client.post("/api/cinemas", json={"name": "Star Cinema", "bundle_sizes": [2]})
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "DUPLICATE_CINEMA_NAME"
    assert client.get("/api/cinemas").json() == [cinema]


def test_quote_impossible_unknown_cinema_and_bounds(api):
    client, _ = api
    assert client.post("/api/cinemas", json={"name": "Even Cinema", "bundle_sizes": [4, 6]}).status_code == 201
    response = client.get("/api/cinemas/1/booking?groupSize=7")
    assert response.status_code == 200
    assert response.json() == {"possible": False, "bundle_count": None, "bundles": []}
    assert client.get("/api/cinemas/1/booking?groupSize=10000").json()["bundle_count"] == 1667
    assert client.get("/api/cinemas/1/booking").status_code == 422
    for group_size in (0, 10_001, 1.5):
        assert client.get("/api/cinemas/1/booking", params={"groupSize": group_size}).status_code == 422
    missing = client.get("/api/cinemas/99/booking?groupSize=6")
    assert missing.status_code == 404
    assert missing.json()["code"] == "CINEMA_NOT_FOUND"


@pytest.mark.parametrize("sizes", [[], [1, 1], [0], [501], [True], ["2"], list(range(1, 12))])
def test_invalid_bundle_sizes(api, sizes):
    client, _ = api
    response = client.post("/api/cinemas", json={"name": "Cinema", "bundle_sizes": sizes})
    assert response.status_code == 422
    assert client.get("/api/cinemas").json() == []
