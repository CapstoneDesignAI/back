from app.schemas.recommendations import RecommendationRequest
from app.services import route_service
from app.services.recommendations import create_recommendation


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
        "tags": ["healing", "nature", "walk", "revitalization"],
    }
