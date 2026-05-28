from typing import Any

import httpx

from app.core.config import settings
from app.data.danyang_places import PlaceCandidate
from app.schemas.recommendations import RegionItem


TOUR_API_AREA_CODES = {
    "region-danyang": {"area_code": "33", "sigungu_code": "2"},
}

TOUR_API_CONTENT_TYPES = {
    "tourist_attraction": "12",
    "culture": "14",
    "festival": "15",
    "travel_course": "25",
    "leisure": "28",
    "lodging": "32",
    "shopping": "38",
    "restaurant": "39",
}

THEME_CONTENT_TYPES = {
    "food": ("39", "38"),
    "local_market": ("38", "39"),
    "nature": ("12", "28"),
    "healing": ("12", "14", "28", "39"),
    "walk": ("12", "14", "25"),
    "revitalization": ("12", "14", "28", "38", "39"),
}


def fetch_tour_api_places(
    region: RegionItem,
    theme: str | None = None,
    num_of_rows: int = 20,
) -> tuple[PlaceCandidate, ...]:
    if not settings.tour_api_service_key:
        return ()

    region_code = TOUR_API_AREA_CODES.get(region.id)
    if not region_code:
        return ()

    items = _fetch_area_based_items(
        area_code=region_code["area_code"],
        sigungu_code=region_code["sigungu_code"],
        content_type_ids=THEME_CONTENT_TYPES.get(theme or "", ("12", "14", "28", "38", "39")),
        num_of_rows=num_of_rows,
    )

    return tuple(
        _to_place_candidate(item=item, region=region)
        for item in items
        if _has_required_location(item)
    )


def _fetch_area_based_items(
    area_code: str,
    sigungu_code: str,
    content_type_ids: tuple[str, ...],
    num_of_rows: int,
) -> list[dict[str, Any]]:
    collected_items: list[dict[str, Any]] = []
    seen_content_ids: set[str] = set()

    for content_type_id in content_type_ids:
        params = {
            "serviceKey": settings.tour_api_service_key,
            "MobileOS": settings.tour_api_mobile_os,
            "MobileApp": settings.tour_api_mobile_app,
            "_type": "json",
            "numOfRows": num_of_rows,
            "pageNo": 1,
            "arrange": "O",
            "areaCode": area_code,
            "sigunguCode": sigungu_code,
            "contentTypeId": content_type_id,
        }
        response = httpx.get(
            f"{settings.tour_api_base_url}/areaBasedList{settings.tour_api_service_version}",
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()

        for item in _extract_items(response.json()):
            content_id = str(item.get("contentid") or "")
            if content_id and content_id not in seen_content_ids:
                collected_items.append(item)
                seen_content_ids.add(content_id)

    return collected_items


def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", {})
    raw_item = items.get("item", []) if isinstance(items, dict) else []

    if isinstance(raw_item, list):
        return [item for item in raw_item if isinstance(item, dict)]
    if isinstance(raw_item, dict):
        return [raw_item]
    return []


def _has_required_location(item: dict[str, Any]) -> bool:
    return bool(item.get("contentid") and item.get("title") and item.get("mapx") and item.get("mapy"))


def _to_place_candidate(item: dict[str, Any], region: RegionItem) -> PlaceCandidate:
    content_type_id = str(item.get("contenttypeid") or "")
    title = str(item.get("title") or "").strip()
    category = _category_from_content_type(content_type_id, title)
    is_local_consumption = _is_local_consumption(content_type_id, title)
    theme_tags = _theme_tags_from_item(content_type_id, title, is_local_consumption)

    return PlaceCandidate(
        place_id=f"tour-{item['contentid']}",
        region_id=region.id,
        name=title,
        category=category,
        address=_join_address(item),
        lat=float(item["mapy"]),
        lng=float(item["mapx"]),
        stay_minutes=_stay_minutes(content_type_id, title),
        estimated_cost_min=12000 if is_local_consumption else 0,
        estimated_cost_max=30000 if is_local_consumption else 10000,
        local_contribution_score=88 if is_local_consumption else 72,
        theme_tags=theme_tags,
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=is_local_consumption,
        reason=f"{region.sigungu}에서 {category} 경험을 할 수 있는 한국관광공사 제공 장소입니다.",
        contribution_reason=(
            "식사, 쇼핑, 체류 소비로 지역 상권에 직접 기여할 수 있습니다."
            if is_local_consumption
            else "지역 대표 자원 방문을 통해 주변 상권 방문 가능성을 높입니다."
        ),
        image_url=item.get("firstimage") or item.get("firstimage2") or None,
        source="tour_api",
    )


def _join_address(item: dict[str, Any]) -> str:
    return " ".join(
        part.strip()
        for part in (str(item.get("addr1") or ""), str(item.get("addr2") or ""))
        if part.strip()
    )


def _category_from_content_type(content_type_id: str, title: str) -> str:
    if content_type_id == "39":
        return "맛집"
    if content_type_id == "38" or "시장" in title:
        return "로컬시장"
    if content_type_id == "28":
        return "액티비티"
    if content_type_id == "14":
        return "문화"
    if content_type_id == "25":
        return "여행코스"
    if content_type_id == "32":
        return "숙박"
    return "관광지"


def _is_local_consumption(content_type_id: str, title: str) -> bool:
    consumption_keywords = ("시장", "카페", "커피", "식당", "맛집", "상가", "거리", "먹거리")
    return content_type_id in {"38", "39", "32"} or any(keyword in title for keyword in consumption_keywords)


def _theme_tags_from_item(
    content_type_id: str,
    title: str,
    is_local_consumption: bool,
) -> tuple[str, ...]:
    tags = {"revitalization"}
    if content_type_id in {"12", "14", "25", "28"}:
        tags.add("healing")
    if content_type_id in {"12", "28"} or any(keyword in title for keyword in ("산", "숲", "계곡", "강", "호수", "공원")):
        tags.add("nature")
    if is_local_consumption:
        tags.add("food")
    if content_type_id == "38" or "시장" in title:
        tags.add("local_market")
    tags.add("walk")
    return tuple(sorted(tags))


def _stay_minutes(content_type_id: str, title: str) -> int:
    if content_type_id == "39" or any(keyword in title for keyword in ("식당", "맛집")):
        return 60
    if content_type_id == "38" or "시장" in title:
        return 70
    if content_type_id == "28":
        return 80
    if content_type_id == "25":
        return 120
    return 50
