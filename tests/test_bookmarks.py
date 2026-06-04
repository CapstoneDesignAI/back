from app.schemas.bookmarks import BookmarkAddRequest
from app.schemas.places import PlaceCreateRequest
from app.services import bookmark_service, place_service

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
        return self

    def eq(self, column: str, value):
        self.filters[column] = value
        return self

    def insert(self, payload):
        self.insert_payload = payload
        self.supabase.inserted_payloads.append((self.name, payload))
        return self

    def execute(self):
        if self.insert_payload is not None:
            return FakeExecuteResult([{"id": "bookmark-id"}])

        if self.name == "folders":
            return FakeExecuteResult([{"id": "default-folder-id"}])

        return FakeExecuteResult([])


class FakeSupabase:
    def __init__(self):
        self.inserted_payloads: list[tuple[str, dict[str, object]]] = []

    def table(self, name: str):
        return FakeTable(name, self)


def test_add_bookmark_creates_place_when_place_payload_is_given(monkeypatch) -> None:
    fake_supabase = FakeSupabase()

    def fake_create_or_get_place(payload: PlaceCreateRequest) -> tuple[str, bool]:
        assert payload.kakao_place_id == "123456789"
        return "created-place-id", True

    monkeypatch.setattr(bookmark_service, "get_supabase", lambda: fake_supabase)
    monkeypatch.setattr(place_service, "create_or_get_place", fake_create_or_get_place)

    result = bookmark_service.add_bookmark(
        "user-id",
        BookmarkAddRequest(
            place=_place_request(),
        ),
    )

    assert result is not None
    assert result.place_id == "created-place-id"
    assert result.is_newly_created_place is True
    assert fake_supabase.inserted_payloads == [
        (
            "bookmarks",
            {
                "user_id": "user-id",
                "folder_id": "default-folder-id",
                "place_id": "created-place-id",
            },
        )
    ]


def test_add_bookmark_keeps_existing_place_id_flow(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(bookmark_service, "get_supabase", lambda: fake_supabase)

    result = bookmark_service.add_bookmark(
        "user-id",
        BookmarkAddRequest(
            place_id="existing-place-id",
            folder_id="custom-folder-id",
        ),
    )

    assert result is not None
    assert result.place_id == "existing-place-id"
    assert result.is_newly_created_place is False
    assert fake_supabase.inserted_payloads == [
        (
            "bookmarks",
            {
                "user_id": "user-id",
                "folder_id": "custom-folder-id",
                "place_id": "existing-place-id",
            },
        )
    ]


def _place_request() -> PlaceCreateRequest:
    return PlaceCreateRequest(
        kakao_place_id="123456789",
        name="스타벅스 강남역점",
        latitude=37.4980,
        longitude=127.0276,
        address="서울 강남구 강남대로 390",
        category="카페",
    )
