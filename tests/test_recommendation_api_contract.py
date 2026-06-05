from fastapi.testclient import TestClient

from app.core.jwt import get_current_user
from app.main import app
from app.services import route_service


client = TestClient(app)


class FakeExecuteResult:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, name: str, calls: list[tuple[str, object]]):
        self.name = name
        self.calls = calls

    def insert(self, payload):
        self.calls.append((self.name, payload))
        return self

    def execute(self):
        if self.name == "routes":
            return FakeExecuteResult([{"id": "route-test-id"}])
        return FakeExecuteResult([])


class FakeSupabase:
    def __init__(self):
        self.calls: list[tuple[str, object]] = []

    def table(self, name: str):
        return FakeTable(name, self.calls)


def test_today_recommendation_endpoint_matches_card_detail_contract() -> None:
    response = client.get("/api/v1/recommendations/today")

    assert response.status_code == 200
    data = response.json()

    assert data["recommendation_id"] == data["card"]["recommendation_id"]
    assert data["route_id"] == data["card"]["route_id"]
    assert data["route_id"] == data["recommendation"]["route_id"]
    assert data["detail_api_path"] == f"/api/v1/ai-recommendations/{data['route_id']}"
    assert "card" not in data["recommendation"]
    assert "map_markers" not in data["recommendation"]
    assert "places" not in data["card"]
    assert len(data["card"]["tags"]) == 3
    assert len(data["card"]["metric_badges"]) == 3
    assert len(data["card"]["place_preview"]) <= 3
    assert len(data["recommendation"]["places"]) >= len(data["card"]["place_preview"])
    assert data["recommendation"]["total_distance_meters"] == sum(
        leg["distance_meters"] for leg in data["recommendation"]["route_legs"]
    )


def test_save_route_from_recommendation_endpoint_returns_404_for_unknown_route_id(
    monkeypatch,
) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)
    app.dependency_overrides[get_current_user] = lambda: "user-test-id"

    try:
        response = client.post(
            "/api/v1/routes/from-recommendation",
            json={"route_id": "route-unknown-healing-half_day-walk-friends"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert fake_supabase.calls == []
