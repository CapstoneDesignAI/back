from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.db.base import get_supabase
from app.schemas.recommendations import RegionItem
from app.services.tour_api import (
    fetch_tour_api_place_items,
    map_tour_api_item_to_place_candidate,
)


TAG_LABELS = {
    "healing": "힐링",
    "food": "맛집",
    "walk": "뚜벅이",
    "nature": "자연투어",
    "local_market": "로컬시장",
    "revitalization": "지역활성화 추천",
}

INDOOR_CATEGORIES = {"맛집", "로컬시장", "카페", "문화", "숙박"}


@dataclass(frozen=True)
class TourPlaceSyncResult:
    region_code: str
    fetched_count: int
    upserted_count: int
    place_ids: tuple[str, ...]


@dataclass(frozen=True)
class TourPlaceSyncFailure:
    region_code: str
    error: str


@dataclass(frozen=True)
class TourPlaceBatchSyncResult:
    total_regions: int
    success_count: int
    failure_count: int
    fetched_count: int
    upserted_count: int
    results: tuple[TourPlaceSyncResult, ...]
    failures: tuple[TourPlaceSyncFailure, ...]


class TourPlaceSyncError(Exception):
    """TourAPI place synchronization failed."""


def list_sync_target_regions(
    *,
    area_group: str | None = None,
    region_codes: list[str] | None = None,
    offset_regions: int = 0,
    limit_regions: int | None = None,
) -> list[dict[str, Any]]:
    supabase = get_supabase()
    query = (
        supabase.table("regions")
        .select(
            "id, region_code, name, sido, sigungu, area_group, area_code, "
            "sigungu_code, is_population_decline, is_active"
        )
        .eq("is_population_decline", True)
        .eq("is_active", True)
    )
    if area_group:
        query = query.eq("area_group", area_group)

    rows = query.execute().data or []
    if region_codes:
        requested_codes = set(region_codes)
        rows = [row for row in rows if row.get("region_code") in requested_codes]
    rows = sorted(rows, key=lambda row: str(row.get("region_code") or ""))
    if offset_regions:
        rows = rows[offset_regions:]
    if limit_regions is not None:
        rows = rows[:limit_regions]
    return rows


def sync_tour_api_places_for_regions(
    *,
    region_codes: list[str] | None = None,
    area_group: str | None = None,
    theme: str | None = None,
    limit: int = 50,
    offset_regions: int = 0,
    limit_regions: int | None = None,
) -> TourPlaceBatchSyncResult:
    target_regions = list_sync_target_regions(
        area_group=area_group,
        region_codes=region_codes,
        offset_regions=offset_regions,
        limit_regions=limit_regions,
    )
    results: list[TourPlaceSyncResult] = []
    failures: list[TourPlaceSyncFailure] = []

    for region in target_regions:
        region_code = str(region.get("region_code") or "")
        try:
            results.append(
                _sync_tour_api_places_for_region(
                    region=region,
                    theme=theme,
                    limit=limit,
                )
            )
        except Exception as exc:
            failures.append(TourPlaceSyncFailure(region_code=region_code, error=str(exc)))

    return TourPlaceBatchSyncResult(
        total_regions=len(target_regions),
        success_count=len(results),
        failure_count=len(failures),
        fetched_count=sum(result.fetched_count for result in results),
        upserted_count=sum(result.upserted_count for result in results),
        results=tuple(results),
        failures=tuple(failures),
    )


def sync_tour_api_places(
    *,
    region_code: str,
    theme: str | None = None,
    limit: int = 50,
) -> TourPlaceSyncResult:
    supabase = get_supabase()
    region = _fetch_region(supabase=supabase, region_code=region_code)
    return _sync_tour_api_places_for_region(region=region, theme=theme, limit=limit)


def _sync_tour_api_places_for_region(
    *,
    region: dict[str, Any],
    theme: str | None,
    limit: int,
) -> TourPlaceSyncResult:
    supabase = get_supabase()
    region_code = str(region.get("region_code") or "")
    area_code = str(region.get("area_code") or "")
    sigungu_code = str(region.get("sigungu_code") or "")

    if not area_code or not sigungu_code:
        raise TourPlaceSyncError(
            f"regions.{region_code} must have area_code and sigungu_code before TourAPI sync."
        )

    items = fetch_tour_api_place_items(
        area_code=area_code,
        sigungu_code=sigungu_code,
        theme=theme,
        num_of_rows=limit,
    )
    payloads = [
        _to_place_upsert_payload(item=item, region=region)
        for item in items
        if item.get("contentid") and item.get("title") and item.get("mapx") and item.get("mapy")
    ]

    if payloads:
        supabase.table("places").upsert(payloads, on_conflict="place_id").execute()

    return TourPlaceSyncResult(
        region_code=region_code,
        fetched_count=len(items),
        upserted_count=len(payloads),
        place_ids=tuple(payload["place_id"] for payload in payloads),
    )


def _fetch_region(*, supabase: Any, region_code: str) -> dict[str, Any]:
    result = (
        supabase.table("regions")
        .select(
            "id, region_code, name, sido, sigungu, area_group, area_code, "
            "sigungu_code, is_population_decline"
        )
        .eq("region_code", region_code)
        .single()
        .execute()
    )
    if not result.data:
        raise TourPlaceSyncError(f"Region not found: {region_code}")
    return result.data


def _to_place_upsert_payload(*, item: dict[str, Any], region: dict[str, Any]) -> dict[str, Any]:
    region_code = str(region["region_code"])
    candidate = map_tour_api_item_to_place_candidate(
        item=item,
        region=RegionItem(
            id=region_code,
            area_group=str(region.get("area_group") or ""),
            sido=str(region.get("sido") or ""),
            sigungu=str(region.get("sigungu") or region.get("name") or ""),
            is_population_decline=bool(region.get("is_population_decline")),
        ),
    )
    source_content_id = str(item["contentid"])
    now = datetime.now(timezone.utc).isoformat()

    return {
        "place_id": candidate.place_id,
        "name": candidate.name,
        "category": candidate.category,
        "description": candidate.reason,
        "is_indoor": candidate.category in INDOOR_CATEGORIES,
        "lat": candidate.lat,
        "lng": candidate.lng,
        "address": candidate.address,
        "image_url": candidate.image_url,
        "thumbnail_url": candidate.image_url,
        "region_id": region["id"],
        "source": "tour_api",
        "source_content_id": source_content_id,
        "tags": _to_korean_tags(candidate.theme_tags),
        "theme_tags": list(candidate.theme_tags),
        "transport_tags": list(candidate.transport_tags),
        "companion_tags": list(candidate.companion_tags),
        "stay_minutes": candidate.stay_minutes,
        "estimated_cost_min": candidate.estimated_cost_min,
        "estimated_cost_max": candidate.estimated_cost_max,
        "local_contribution_score": candidate.local_contribution_score,
        "is_local_consumption": candidate.is_local_consumption,
        "reason": candidate.reason,
        "contribution_reason": candidate.contribution_reason,
        "raw_payload": item,
        "last_synced_at": now,
    }


def _to_korean_tags(tag_codes: tuple[str, ...]) -> list[str]:
    return [TAG_LABELS.get(tag, tag) for tag in tag_codes]
