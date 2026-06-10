from app.services import tour_place_sync


class FakeExecuteResult:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, name: str, supabase: "FakeSupabase"):
        self.name = name
        self.supabase = supabase
        self.filters = {}
        self.upsert_payload = None

    def select(self, columns: str):
        self.supabase.calls.append((self.name, "select", columns))
        return self

    def eq(self, column: str, value):
        self.filters[column] = value
        self.supabase.calls.append((self.name, "eq", {column: value}))
        return self

    def single(self):
        self.supabase.calls.append((self.name, "single", None))
        return self

    def upsert(self, payload, on_conflict=None):
        self.upsert_payload = payload
        self.supabase.upserted_payloads.append(payload)
        self.supabase.calls.append((self.name, "upsert", {"payload": payload, "on_conflict": on_conflict}))
        return self

    def execute(self):
        if self.name == "regions":
            return FakeExecuteResult(self.supabase.region)
        return FakeExecuteResult(self.upsert_payload or [])


class FakeSupabase:
    def __init__(self):
        self.calls = []
        self.upserted_payloads = []
        self.region = {
            "id": "ee1b8221-5e3f-42db-8ff2-45de00000000",
            "region_code": "region-danyang",
            "name": "단양군",
            "sido": "충청북도",
            "sigungu": "단양군",
            "area_group": "chungcheong",
            "area_code": "33",
            "sigungu_code": "2",
            "is_population_decline": True,
        }

    def table(self, name: str):
        return FakeTable(name, self)


def test_sync_tour_api_places_upserts_places(monkeypatch) -> None:
    fake_supabase = FakeSupabase()
    monkeypatch.setattr(tour_place_sync, "get_supabase", lambda: fake_supabase)
    monkeypatch.setattr(
        tour_place_sync,
        "fetch_tour_api_place_items",
        lambda **kwargs: [
            {
                "contentid": "999001",
                "contenttypeid": "39",
                "title": "단양 로컬 맛집",
                "addr1": "충청북도 단양군 단양읍",
                "addr2": "시장길 1",
                "mapx": "128.365889",
                "mapy": "36.984784",
                "firstimage": "https://example.com/food.jpg",
            }
        ],
    )

    result = tour_place_sync.sync_tour_api_places(
        region_code="region-danyang",
        theme="food",
        limit=10,
    )

    assert result.fetched_count == 1
    assert result.upserted_count == 1
    assert result.place_ids == ("tour-999001",)
    payload = fake_supabase.upserted_payloads[0][0]
    assert payload["place_id"] == "tour-999001"
    assert payload["source"] == "tour_api"
    assert payload["source_content_id"] == "999001"
    assert payload["region_id"] == fake_supabase.region["id"]
    assert payload["image_url"] == "https://example.com/food.jpg"
    assert payload["theme_tags"]
    assert payload["tags"]
    assert fake_supabase.calls[-1] == (
        "places",
        "upsert",
        {"payload": fake_supabase.upserted_payloads[0], "on_conflict": "place_id"},
    )
