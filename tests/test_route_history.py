from fastapi.testclient import TestClient

from app.core.jwt import get_current_user
from app.main import app
from app.schemas.recommendations import RecommendationRequest
from app.services import route_service
from app.services.recommendations import create_recommendation

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


def test_create_recommended_route_returns_route_id_and_saves_places(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    recommendation = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="healing",
            travel_time="half_day",
            transport="walk",
            companion="friends",
        )
    )

    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)

    route_id = route_service.create_recommended_route(
        user_id="user-test-id",
        route_data=recommendation.legacy_route_payload,
    )

    assert route_id == "route-test-id"
    assert fake_supabase.calls[0] == (
        "routes",
        {
            "user_id": "user-test-id",
            "title": recommendation.legacy_route_payload.title,
        },
    )
    assert fake_supabase.calls[1][0] == "route_places"
    assert fake_supabase.calls[1][1][0] == {
        "route_id": "route-test-id",
        "place_id": "sample-dodamsambong",
        "visit_order": 1,
        "description": recommendation.legacy_route_payload.places[0].description,
        "tags": ["힐링", "자연투어", "뚜벅이", "지역활성화 추천"],
    }


def test_create_recommended_route_from_route_id_reuses_existing_save_flow(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)

    route_id = route_service.create_recommended_route_from_route_id(
        user_id="user-test-id",
        route_id="route-danyang-healing-half_day-walk-friends",
    )

    assert route_id == "route-test-id"
    assert fake_supabase.calls[0] == (
        "routes",
        {
            "user_id": "user-test-id",
            "title": "단양 힐링 로컬 코스",
        },
    )
    assert fake_supabase.calls[1][0] == "route_places"
    assert [place["place_id"] for place in fake_supabase.calls[1][1]] == [
        "sample-dodamsambong",
        "sample-danyang-market",
        "sample-cafe-sann",
        "sample-mancheonha",
    ]


def test_create_recommended_route_from_route_id_returns_none_for_unknown_route_id(
    monkeypatch,
) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)

    route_id = route_service.create_recommended_route_from_route_id(
        user_id="user-test-id",
        route_id="route-unknown-healing-half_day",
    )

    assert route_id is None
    assert fake_supabase.calls == []


def test_save_route_from_recommendation_endpoint_accepts_route_id(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)
    app.dependency_overrides[get_current_user] = lambda: "user-test-id"

    try:
        response = client.post(
            "/api/v1/routes/from-recommendation",
            json={"route_id": "route-danyang-healing-half_day-walk-friends"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "message": "동선이 성공적으로 저장되었습니다.",
        "route_id": "route-test-id",
        "saved_route_id": "route-test-id",
        "source_route_id": "route-danyang-healing-half_day-walk-friends",
        "is_saved": True,
    }
    assert fake_supabase.calls[0][0] == "routes"
    assert fake_supabase.calls[1][0] == "route_places"
