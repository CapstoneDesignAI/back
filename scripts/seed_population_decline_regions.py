from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import httpx


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings
from app.data.population_decline_regions import (
    POPULATION_DECLINE_REGIONS,
    PopulationDeclineRegion,
)
from app.db.base import get_supabase


class RegionSeedError(Exception):
    """Population decline region seed failed."""


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed population decline regions into Supabase.")
    parser.add_argument(
        "--allow-unresolved",
        action="store_true",
        help="Upsert regions even when TourAPI sigungu_code cannot be resolved.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve and print summary without writing to Supabase.",
    )
    args = parser.parse_args()

    payloads, unresolved = build_region_payloads(allow_unresolved=args.allow_unresolved)

    print(
        "Population decline regions prepared: "
        f"total={len(POPULATION_DECLINE_REGIONS)}, "
        f"resolved={len(payloads) - len(unresolved)}, "
        f"unresolved={len(unresolved)}"
    )
    if unresolved:
        print("Unresolved regions:")
        for region in unresolved:
            print(f"- {region.sido} {region.sigungu} ({region.region_code})")

    if args.dry_run:
        return

    if unresolved and not args.allow_unresolved:
        raise RegionSeedError("Unresolved TourAPI sigungu_code exists. Use --allow-unresolved to seed anyway.")

    get_supabase().table("regions").upsert(payloads, on_conflict="region_code").execute()
    print(f"Supabase regions upsert complete: upserted={len(payloads)}")


def build_region_payloads(
    *,
    allow_unresolved: bool = False,
) -> tuple[list[dict[str, Any]], list[PopulationDeclineRegion]]:
    sigungu_code_cache: dict[str, dict[str, str]] = {}
    payloads: list[dict[str, Any]] = []
    unresolved: list[PopulationDeclineRegion] = []

    for region in POPULATION_DECLINE_REGIONS:
        sigungu_codes = sigungu_code_cache.setdefault(
            region.area_code,
            fetch_tour_api_sigungu_codes(region.area_code),
        )
        sigungu_code = sigungu_codes.get(region.sigungu)
        if not sigungu_code:
            unresolved.append(region)
            if not allow_unresolved:
                continue

        payloads.append(
            {
                "region_code": region.region_code,
                "name": region.sigungu,
                "english_name": region.english_name,
                "description": f"{region.sido} {region.sigungu} 인구감소지역 로컬 여행 권역입니다.",
                "sido": region.sido,
                "sigungu": region.sigungu,
                "area_group": region.area_group,
                "area_code": region.area_code,
                "sigungu_code": sigungu_code,
                "is_population_decline": True,
                "is_active": True,
            }
        )

    return payloads, unresolved


def fetch_tour_api_sigungu_codes(area_code: str) -> dict[str, str]:
    if not settings.tour_api_service_key:
        raise RegionSeedError("TOUR_API_SERVICE_KEY must be configured.")

    response = _get_with_retry(
        f"{settings.tour_api_base_url}/areaCode{settings.tour_api_service_version}",
        params={
            "serviceKey": settings.tour_api_service_key,
            "MobileOS": settings.tour_api_mobile_os,
            "MobileApp": settings.tour_api_mobile_app,
            "_type": "json",
            "numOfRows": 100,
            "pageNo": 1,
            "areaCode": area_code,
        },
    )
    items = _extract_items(response.json())
    return {
        str(item["name"]).strip(): str(item["code"]).strip()
        for item in items
        if item.get("name") and item.get("code")
    }


def _get_with_retry(url: str, *, params: dict[str, Any], retries: int = 3) -> httpx.Response:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(0.8 * attempt)
    raise RegionSeedError(f"TourAPI area code request failed: {last_error}") from last_error


def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", {})
    raw_item = items.get("item", []) if isinstance(items, dict) else []

    if isinstance(raw_item, list):
        return [item for item in raw_item if isinstance(item, dict)]
    if isinstance(raw_item, dict):
        return [raw_item]
    return []


if __name__ == "__main__":
    main()
