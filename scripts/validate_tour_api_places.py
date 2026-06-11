from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.base import get_supabase


SERVICE_AREA_GROUPS = (
    "chungcheong",
    "gangwon",
    "near_capital",
    "jeolla",
    "gyeongsang",
)


def main() -> None:
    supabase = get_supabase()
    regions = _fetch_regions(supabase)
    places = _fetch_places(supabase)

    region_by_id = {row["id"]: row for row in regions}
    active_regions = [
        row
        for row in regions
        if row.get("is_population_decline")
        and row.get("is_active")
        and row.get("area_group") in SERVICE_AREA_GROUPS
    ]

    places_by_region_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unknown_places: list[dict[str, Any]] = []
    for place in places:
        region = region_by_id.get(place.get("region_id"))
        if not region or region.get("area_group") not in SERVICE_AREA_GROUPS:
            unknown_places.append(place)
            continue
        places_by_region_id[str(region["id"])].append(place)

    zero_place_regions = [
        region for region in active_regions if not places_by_region_id.get(str(region["id"]))
    ]
    target_places = [
        place for region in active_regions for place in places_by_region_id.get(str(region["id"]), [])
    ]
    missing_coordinates = [
        place for place in target_places if place.get("lat") is None or place.get("lng") is None
    ]
    missing_images = [
        place
        for place in target_places
        if not place.get("image_url") and not place.get("thumbnail_url")
    ]

    print("Tripick TourAPI place validation")
    print("--------------------------------")
    print(f"regions_total={len(regions)}")
    print(f"active_population_decline_regions={len(active_regions)}")
    print(f"places_total={len(places)}")
    print(f"service_target_places={len(target_places)}")
    print(f"unknown_places={len(unknown_places)}")
    print(f"zero_place_regions={len(zero_place_regions)}")
    print(f"missing_coordinates={len(missing_coordinates)}")
    print(f"missing_images={len(missing_images)}")
    print()

    _print_area_summary(active_regions=active_regions, places_by_region_id=places_by_region_id)
    _print_place_summary(target_places)

    if unknown_places:
        print()
        print("Unknown places")
        for place in unknown_places[:20]:
            print(
                "- "
                f"place_id={place.get('place_id')}, "
                f"name={place.get('name')}, "
                f"source={place.get('source')}, "
                f"region_id={place.get('region_id')}"
            )

    if zero_place_regions:
        print()
        print("Regions with zero places")
        for region in zero_place_regions:
            print(f"- {region.get('region_code')} {region.get('name')}")

    if missing_coordinates:
        print()
        print("Places missing coordinates")
        for place in missing_coordinates[:20]:
            print(f"- {place.get('place_id')} {place.get('name')}")

    if zero_place_regions or missing_coordinates:
        raise SystemExit(1)


def _fetch_regions(supabase: Any) -> list[dict[str, Any]]:
    return (
        supabase.table("regions")
        .select("id, region_code, name, area_group, is_population_decline, is_active")
        .execute()
        .data
        or []
    )


def _fetch_places(supabase: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    page_size = 1000
    while True:
        page = (
            supabase.table("places")
            .select(
                "place_id, name, category, source, region_id, lat, lng, "
                "image_url, thumbnail_url, is_local_consumption"
            )
            .range(start, start + page_size - 1)
            .execute()
            .data
            or []
        )
        rows.extend(page)
        if len(page) < page_size:
            break
        start += page_size
    return rows


def _print_area_summary(
    *,
    active_regions: list[dict[str, Any]],
    places_by_region_id: dict[str, list[dict[str, Any]]],
) -> None:
    regions_by_area = Counter(region.get("area_group") for region in active_regions)
    places_by_area = Counter()
    for region in active_regions:
        area_group = region.get("area_group")
        places_by_area[area_group] += len(places_by_region_id.get(str(region["id"]), []))

    print("Area summary")
    for area_group in SERVICE_AREA_GROUPS:
        print(
            "- "
            f"area_group={area_group}, "
            f"regions={regions_by_area[area_group]}, "
            f"places={places_by_area[area_group]}"
        )


def _print_place_summary(places: list[dict[str, Any]]) -> None:
    category = Counter(place.get("category") or "unknown" for place in places)
    source = Counter(place.get("source") or "unknown" for place in places)
    image_present = sum(1 for place in places if place.get("image_url") or place.get("thumbnail_url"))
    local_consumption = sum(1 for place in places if place.get("is_local_consumption"))

    print()
    print("Place summary")
    print(f"category={dict(category.most_common())}")
    print(f"source={dict(source.most_common())}")
    print(f"image_present={image_present}")
    print(f"image_missing={len(places) - image_present}")
    print(f"local_consumption={local_consumption}")
    print(f"general={len(places) - local_consumption}")


if __name__ == "__main__":
    main()
