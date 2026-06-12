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
    def __init__(self, name: str, supabase: "FakeSupabase"):
        self.name = name
        self.supabase = supabase
        self.calls = supabase.calls
        self.select_query = None

    def insert(self, payload):
        self.calls.append((self.name, payload))
        return self

    def select(self, query):
        self.select_query = query
        if self.name == "routes":
            self.supabase.route_selects.append(query)
        return self

    def upsert(self, payload, **kwargs):
        self.calls.append((self.name, payload, kwargs))
        return self

    def update(self, payload):
        self.calls.append((self.name, payload))
        return self
        
    def eq(self, key, value):
        return self

    def single(self):
        return self

    def execute(self):
        if self.select_query and self.name == "routes":
            top_level_select = self.select_query.split("route_places", 1)[0]
            for column in self.supabase.fail_route_detail_columns:
                if f", {column}," in f", {top_level_select},":
                    raise Exception(
                        {
                            "message": f"column routes.{column} does not exist",
                            "code": "42703",
                            "hint": None,
                            "details": None,
                        }
                    )
            return FakeExecuteResult(
                {
                    "id": "route-test-id",
                    "title": "테스트 동선",
                    "created_at": "2026-06-12T00:00:00",
                    "image_url": None,
                    "route_places": [],
                }
            )

        if (
            self.name == "routes"
            and self.supabase.fail_route_description_insert
            and self.calls
            and self.calls[-1][0] == "routes"
            and isinstance(self.calls[-1][1], dict)
            and "description" in self.calls[-1][1]
        ):
            raise Exception(
                {
                    "message": "Could not find the 'description' column of 'routes' in the schema cache",
                    "code": "PGRST204",
                    "hint": None,
                    "details": None,
                }
            )
        if self.name == "routes":
            return FakeExecuteResult([{"id": "route-test-id"}])
        if self.name == "regions":
            return FakeExecuteResult([{"id": "region-danyang-db-id"}])
        return FakeExecuteResult([])


class FakeSupabase:
    def __init__(self):
        self.calls: list[tuple[str, object]] = []
        self.fail_route_description_insert = False
        self.fail_route_detail_columns: list[str] = []
        self.route_selects: list[str] = []

    def table(self, name: str):
        return FakeTable(name, self)


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
        "places",
        [
            {
                "place_id": "sample-dodamsambong",
                "name": "도담삼봉",
                "address": "충청북도 단양군 매포읍 삼봉로 644",
                "lat": 36.984539,
                "lng": 128.369267,
                "category": "자연",
                "description": recommendation.legacy_route_payload.places[0].description,
                "image_url": recommendation.legacy_route_payload.places[0].image_url,
                "is_indoor": False,
            },
            {
                "place_id": "sample-danyang-market",
                "name": "단양구경시장",
                "address": "충청북도 단양군 단양읍 도전5길 31",
                "lat": 36.984784,
                "lng": 128.365889,
                "category": "로컬시장",
                "description": recommendation.legacy_route_payload.places[1].description,
                "image_url": recommendation.legacy_route_payload.places[1].image_url,
                "is_indoor": True,
            },
            {
                "place_id": "sample-cafe-sann",
                "name": "카페산",
                "address": "충청북도 단양군 가곡면 두산길 196-86",
                "lat": 37.024255,
                "lng": 128.395729,
                "category": "카페",
                "description": recommendation.legacy_route_payload.places[2].description,
                "image_url": recommendation.legacy_route_payload.places[2].image_url,
                "is_indoor": True,
            },
            {
                "place_id": "sample-mancheonha",
                "name": "만천하스카이워크",
                "address": "충청북도 단양군 적성면 옷바위길 10",
                "lat": 36.966326,
                "lng": 128.343638,
                "category": "액티비티",
                "description": recommendation.legacy_route_payload.places[3].description,
                "image_url": recommendation.legacy_route_payload.places[3].image_url,
                "is_indoor": False,
            },
        ],
        {"on_conflict": "place_id"},
    )
    assert fake_supabase.calls[1] == (
        "routes",
        {
            "user_id": "user-test-id",
            "title": recommendation.legacy_route_payload.title,
            "description": recommendation.legacy_route_payload.description,
            "image_url": recommendation.legacy_route_payload.image_url,
        },
    )
    
    # route_places insert would be the last call after places updates
    route_places_call = next(call for call in reversed(fake_supabase.calls) if call[0] == "route_places")
    
    assert route_places_call[1][0] == {
        "route_id": "route-test-id",
        "place_id": "sample-dodamsambong",
        "visit_order": 1,
        "description": recommendation.legacy_route_payload.places[0].description,
        "tags": ["힐링", "자연투어", "뚜벅이", "지역활성화 추천"],
    }
    assert fake_supabase.calls[-1] == (
        "user_region_stamps",
        {
            "user_id": "user-test-id",
            "region_id": "region-danyang-db-id",
            "collected_stamps": 0,
        },
    )


def test_create_recommended_route_from_route_id_reuses_existing_save_flow(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)

    route_id = route_service.create_recommended_route_from_route_id(
        user_id="user-test-id",
        route_id="route-danyang-healing-half_day-walk-friends",
    )

    assert route_id == "route-test-id"
    assert fake_supabase.calls[1] == (
        "routes",
        {
            "user_id": "user-test-id",
            "title": "단양 힐링 로컬 코스",
            "description": route_service.get_recommendation_detail(
                "route-danyang-healing-half_day-walk-friends"
            ).legacy_route_payload.description,
            "image_url": route_service.get_recommendation_detail(
                "route-danyang-healing-half_day-walk-friends"
            ).legacy_route_payload.image_url,
        },
    )
    
    route_places_call = next(call for call in reversed(fake_supabase.calls) if call[0] == "route_places")
    assert [place["place_id"] for place in route_places_call[1]] == [
        "sample-dodamsambong",
        "sample-danyang-market",
        "sample-cafe-sann",
        "sample-mancheonha",
    ]


def test_create_recommended_route_retries_without_route_description_when_column_is_missing(
    monkeypatch,
) -> None:
    fake_supabase = FakeSupabase()
    fake_supabase.fail_route_description_insert = True
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
    route_insert_calls = [call for call in fake_supabase.calls if call[0] == "routes"]
    assert route_insert_calls == [
        (
            "routes",
            {
                "user_id": "user-test-id",
                "title": recommendation.legacy_route_payload.title,
                "description": recommendation.legacy_route_payload.description,
                "image_url": recommendation.legacy_route_payload.image_url,
            },
        ),
        (
            "routes",
            {
                "user_id": "user-test-id",
                "title": recommendation.legacy_route_payload.title,
                "image_url": recommendation.legacy_route_payload.image_url,
            },
        ),
    ]
    assert any(call[0] == "route_places" for call in fake_supabase.calls)


def test_missing_route_description_column_detection_accepts_postgres_undefined_column() -> None:
    error = Exception(
        {
            "message": 'column routes.description does not exist',
            "code": "42703",
            "hint": None,
            "details": None,
        }
    )

    assert route_service._is_missing_column_error(error, "description", "routes")


def test_get_route_detail_retries_without_missing_route_optional_columns(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    fake_supabase.fail_route_detail_columns = ["description", "tags"]
    monkeypatch.setattr(route_service, "get_supabase", lambda: fake_supabase)

    route = route_service.get_route_detail("route-test-id")

    assert route["route_id"] == "route-test-id"
    assert route["description"] is None
    assert route["tags"] == ["추천", "힐링"]
    assert len(fake_supabase.route_selects) == 3
    top_level_selects = [
        select_query.split("route_places", 1)[0] for select_query in fake_supabase.route_selects
    ]
    assert "description" in top_level_selects[0]
    assert "tags" in top_level_selects[1]
    assert "description" not in top_level_selects[2]
    assert "tags" not in top_level_selects[2]


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
        "source_detail_api_path": (
            "/api/v1/ai-recommendations/route-danyang-healing-half_day-walk-friends"
        ),
        "saved_detail_api_path": "/api/v1/routes/route-test-id",
        "is_saved": True,
    }
    assert fake_supabase.calls[0][0] == "places"
    assert fake_supabase.calls[1][0] == "routes"
