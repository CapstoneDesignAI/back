import pytest
from fastapi import HTTPException

from app.services import mission_service


class FakeExecuteResult:
    def __init__(self, data):
        self.data = data


class FakeMissionTable:
    def __init__(self, supabase: "FakeSupabase"):
        self.supabase = supabase
        self.filters = {}

    def select(self, fields):
        self.fields = fields
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def single(self):
        return self

    def execute(self):
        self.supabase.filters.append(dict(self.filters))

        if "slug" in self.filters and self.supabase.slug_column_missing:
            raise Exception(
                {
                    "message": 'column missions.slug does not exist',
                    "code": "42703",
                    "hint": None,
                    "details": None,
                }
            )

        if self.filters.get("slug") == "local-market-snack":
            return FakeExecuteResult([{"id": self.supabase.mission_id}][0])

        return FakeExecuteResult(None)


class FakeSupabase:
    def __init__(self):
        self.mission_id = "11111111-1111-1111-1111-111111111111"
        self.slug_column_missing = False
        self.filters = []

    def table(self, name: str):
        assert name == "missions"
        return FakeMissionTable(self)


def test_resolve_mission_id_returns_uuid_without_querying_slug() -> None:
    fake_supabase = FakeSupabase()

    mission_id = mission_service._resolve_mission_id(fake_supabase, fake_supabase.mission_id)

    assert mission_id == fake_supabase.mission_id
    assert fake_supabase.filters == []


def test_resolve_mission_id_supports_slug_when_column_exists() -> None:
    fake_supabase = FakeSupabase()

    mission_id = mission_service._resolve_mission_id(fake_supabase, "local-market-snack")

    assert mission_id == fake_supabase.mission_id
    assert fake_supabase.filters == [{"slug": "local-market-snack"}]


def test_resolve_mission_id_returns_404_when_slug_column_is_missing() -> None:
    fake_supabase = FakeSupabase()
    fake_supabase.slug_column_missing = True

    with pytest.raises(HTTPException) as exc_info:
        mission_service._resolve_mission_id(fake_supabase, "local-market-snack")

    assert exc_info.value.status_code == 404
