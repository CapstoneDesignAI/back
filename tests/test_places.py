from fastapi.testclient import TestClient

from app.main import app
from app.schemas.places import PlaceCreateRequest
from app.services import place_service

client = TestClient(app)

class FakeExecuteResult:
    def __init__(self, data):
        self.data = data

class FakeTable:
    def __init__(self, name: str, supabase: "FakeSupabase"):
        self.name = name
        self.supabase = supabase
        self.filters: dict[str, object] = {}
        self.insert_payload = None

    def select(self, columns: str):
        self.supabase.calls.append((self.name, "select", columns))
        return self

    def eq(self, column: str, value):
        self.filters[column] = value
        self.supabase.calls.append((self.name, "eq", {column: value}))
        return self

    def insert(self, payload):
        self.insert_payload = payload
        self.supabase.inserted_payloads.append(payload)
        self.supabase.calls.append((self.name, "insert", payload))
        return self

    def execute(self):
        if self.insert_payload is not None:
            return FakeExecuteResult(self.supabase.insert_result)

        kakao_place_id = self.filters.get("kakao_place_id")
        return FakeExecuteResult(self.supabase.existing_places.get(kakao_place_id, []))

class FakeSupabase:
    def __init__(self):
        self.calls: list[tuple[str, str, object]] = []
        self.existing_places: dict[str, list[dict[str, str]]] = {}
        self.inserted_payloads: list[dict[str, object]] = []
        self.insert_result = [{"id": "new-place-id"}]

    def table(self, name: str):
        return FakeTable(name, self)


def test_create_or_get_place_returns_existing_place(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    fake_supabase.existing_places["123456789"] = [{"id": "existing-place-id"}]
    monkeypatch.setattr(place_service, "get_supabase", lambda: fake_supabase)

    place_id, is_newly_created = place_service.create_or_get_place(_place_request())

    assert place_id == "existing-place-id"
    assert is_newly_created is False
    assert fake_supabase.inserted_payloads == []


def test_create_or_get_place_inserts_new_place(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(place_service, "get_supabase", lambda: fake_supabase)

    place_id, is_newly_created = place_service.create_or_get_place(_place_request())

    assert place_id == "new-place-id"
    assert is_newly_created is True
    assert fake_supabase.inserted_payloads == [
        {
            "kakao_place_id": "123456789",
            "name": "스타벅스 강남역점",
            "lat": 37.498,
            "lng": 127.0276,
            "address": "서울 강남구 강남대로 390",
            "category": "카페",
        }
    ]


def test_create_place_api_returns_place_id(monkeypatch) -> None:
    def fake_create_or_get_place(request_data: PlaceCreateRequest) -> tuple[str, bool]:
        assert request_data.kakao_place_id == "123456789"
        return "f47ac10b-58cc-4372-a567-0e02b2c3d479", True

    monkeypatch.setattr(place_service, "create_or_get_place", fake_create_or_get_place)

    response = client.post(
        "/api/v1/places",
        json={
            "kakao_place_id": "123456789",
            "name": "스타벅스 강남역점",
            "latitude": 37.4980,
            "longitude": 127.0276,
            "address": "서울 강남구 강남대로 390",
            "category": "카페",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "message": "장소가 성공적으로 등록/조회되었습니다.",
        "place_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "is_newly_created": True,
    }


def _place_request() -> PlaceCreateRequest:
    return PlaceCreateRequest(
        kakao_place_id="123456789",
        name="스타벅스 강남역점",
        latitude=37.4980,
        longitude=127.0276,
        address="서울 강남구 강남대로 390",
        category="카페",
    )
