from app.schemas.recommendations import RecommendationRequest
from app.services.recommendations import create_recommendation, list_places
from app.services import place_repository


class FakeExecuteResult:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, name: str, supabase: "FakeSupabase"):
        self.name = name
        self.supabase = supabase
        self.filters = {}

    def select(self, columns: str):
        self.supabase.calls.append((self.name, "select", columns))
        return self

    def eq(self, column: str, value):
        self.filters[column] = value
        self.supabase.calls.append((self.name, "eq", {column: value}))
        return self

    def limit(self, value: int):
        self.supabase.calls.append((self.name, "limit", value))
        return self

    def execute(self):
        if self.name == "regions":
            return FakeExecuteResult(self.supabase.regions)
        if self.name == "places":
            return FakeExecuteResult(self.supabase.places)
        return FakeExecuteResult([])


class FakeSupabase:
    def __init__(self):
        self.calls = []
        self.regions = [{"id": "region-uuid", "region_code": "region-danyang"}]
        self.places = [
            {
                "place_id": "tour-999001",
                "region_id": "region-uuid",
                "name": "단양 로컬 맛집",
                "category": "맛집",
                "description": "지역 식당입니다.",
                "lat": 36.984784,
                "lng": 128.365889,
                "address": "충청북도 단양군 단양읍 시장길 1",
                "image_url": "https://example.com/food.jpg",
                "thumbnail_url": None,
                "tags": ["맛집", "지역활성화 추천"],
                "theme_tags": ["food", "revitalization", "walk"],
                "transport_tags": ["walk", "car"],
                "companion_tags": ["solo", "friends"],
                "stay_minutes": 60,
                "estimated_cost_min": 12000,
                "estimated_cost_max": 30000,
                "local_contribution_score": 88,
                "is_local_consumption": True,
                "reason": "지역 상권 소비로 이어지는 장소입니다.",
                "contribution_reason": "식사 소비가 지역 매출로 연결됩니다.",
                "source": "tour_api",
            }
        ]

    def table(self, name: str):
        return FakeTable(name, self)


def test_list_places_can_use_supabase_candidates(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(place_repository, "get_supabase", lambda: fake_supabase)

    response = list_places(region_id="region-danyang", source="supabase", theme="food")

    assert response.places[0].place_id == "tour-999001"
    assert response.places[0].name == "단양 로컬 맛집"
    assert response.places[0].source == "tour_api"
    assert response.places[0].tags == ["맛집", "지역활성화 추천", "뚜벅이"]
    assert ("places", "eq", {"region_id": "region-uuid"}) in fake_supabase.calls


def test_create_recommendation_can_use_supabase_candidates(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(place_repository, "get_supabase", lambda: fake_supabase)

    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="food",
            travel_time="3hours",
            transport="walk",
            companion="friends",
            data_source="supabase",
        )
    )

    assert response.places[0].place_id == "tour-999001"
    assert response.places[0].name == "단양 로컬 맛집"
    assert response.places[0].image_url == "https://example.com/food.jpg"
    assert response.card.thumbnail_url == "https://example.com/food.jpg"
    assert response.card.place_preview[0].image_url == "https://example.com/food.jpg"
    assert response.legacy_route_payload.places[0].place_id == "tour-999001"
    assert response.legacy_route_payload.places[0].image_url == "https://example.com/food.jpg"
    assert response.local_consumption_count == 1
    assert response.source == "tour_api"
    assert ("places", "eq", {"region_id": "region-uuid"}) in fake_supabase.calls
