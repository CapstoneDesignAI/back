from typing import Any

from app.data.danyang_places import PlaceCandidate
from app.db.base import get_supabase
from app.schemas.recommendations import RegionItem


DEFAULT_TRANSPORT_TAGS = ("walk", "car", "public_transport")
DEFAULT_COMPANION_TAGS = ("solo", "friends", "family", "couple")


def fetch_place_candidates_from_supabase(
    *,
    region: RegionItem,
    theme: str | None = None,
    limit: int = 100,
) -> tuple[PlaceCandidate, ...]:
    supabase = get_supabase()
    region_row = _fetch_region_row(supabase=supabase, region_code=region.id)
    if not region_row:
        return ()

    result = (
        supabase.table("places")
        .select(
            "place_id, region_id, name, category, description, lat, lng, address, "
            "image_url, thumbnail_url, tags, theme_tags, transport_tags, companion_tags, "
            "stay_minutes, estimated_cost_min, estimated_cost_max, local_contribution_score, "
            "is_local_consumption, reason, contribution_reason, source"
        )
        .eq("region_id", region_row["id"])
        .limit(limit)
        .execute()
    )

    candidates = tuple(
        _to_place_candidate(row=row, region_code=region.id)
        for row in result.data or []
        if _has_required_place_fields(row)
    )
    if theme:
        themed_candidates = tuple(
            candidate for candidate in candidates if theme in candidate.theme_tags
        )
        if themed_candidates:
            return themed_candidates
    return candidates


def _fetch_region_row(*, supabase: Any, region_code: str) -> dict[str, Any] | None:
    result = (
        supabase.table("regions")
        .select("id, region_code")
        .eq("region_code", region_code)
        .execute()
    )
    rows = result.data or []
    return rows[0] if rows else None


def _has_required_place_fields(row: dict[str, Any]) -> bool:
    return bool(
        row.get("place_id")
        and row.get("name")
        and row.get("category")
        and row.get("lat") is not None
        and row.get("lng") is not None
    )


def _to_place_candidate(*, row: dict[str, Any], region_code: str) -> PlaceCandidate:
    theme_tags = _to_tuple(row.get("theme_tags")) or _infer_theme_tags(row)
    transport_tags = _to_tuple(row.get("transport_tags")) or DEFAULT_TRANSPORT_TAGS
    companion_tags = _to_tuple(row.get("companion_tags")) or DEFAULT_COMPANION_TAGS
    image_url = row.get("image_url") or row.get("thumbnail_url")

    return PlaceCandidate(
        place_id=str(row["place_id"]),
        region_id=region_code,
        name=str(row["name"]),
        category=str(row["category"]),
        address=str(row.get("address") or ""),
        lat=float(row["lat"]),
        lng=float(row["lng"]),
        stay_minutes=int(row.get("stay_minutes") or 60),
        estimated_cost_min=int(row.get("estimated_cost_min") or 0),
        estimated_cost_max=int(row.get("estimated_cost_max") or 0),
        local_contribution_score=int(row.get("local_contribution_score") or 50),
        theme_tags=theme_tags,
        transport_tags=transport_tags,
        companion_tags=companion_tags,
        is_local_consumption=bool(row.get("is_local_consumption")),
        reason=str(row.get("reason") or row.get("description") or "지역 여행지 후보 장소입니다."),
        contribution_reason=str(
            row.get("contribution_reason")
            or "방문과 체류를 통해 지역 상권과 관광 흐름에 기여할 수 있습니다."
        ),
        image_url=image_url,
        source=str(row.get("source") or "supabase"),
    )


def _to_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, tuple):
        return tuple(str(item) for item in value if item)
    if isinstance(value, list):
        return tuple(str(item) for item in value if item)
    return ()


def _infer_theme_tags(row: dict[str, Any]) -> tuple[str, ...]:
    category = str(row.get("category") or "")
    tags = {"revitalization", "walk"}
    if category in {"맛집", "카페"}:
        tags.add("food")
    if category == "로컬시장":
        tags.update({"food", "local_market"})
    if category in {"자연", "관광지", "액티비티"}:
        tags.update({"healing", "nature"})
    return tuple(sorted(tags))
