from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.tour_place_sync import sync_tour_api_places
from app.services.tour_place_sync import sync_tour_api_places_for_regions


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync TourAPI places into Supabase places.")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--region-code", action="append", help="regions.region_code value")
    target_group.add_argument("--area-group", help="regions.area_group value")
    target_group.add_argument(
        "--all-active-regions",
        action="store_true",
        help="Sync all active population decline regions.",
    )
    parser.add_argument("--theme", default=None, help="Optional Tripick theme code")
    parser.add_argument("--limit", type=int, default=50, help="TourAPI rows per content type")
    parser.add_argument(
        "--offset-regions",
        type=int,
        default=0,
        help="Number of matched regions to skip before syncing. Useful for batch runs.",
    )
    parser.add_argument(
        "--limit-regions",
        type=int,
        default=None,
        help="Maximum regions to sync in this run. Useful for smoke tests.",
    )
    args = parser.parse_args()

    if (
        args.region_code
        and len(args.region_code) == 1
        and args.offset_regions == 0
        and args.limit_regions is None
    ):
        _sync_single_region(args)
        return

    result = sync_tour_api_places_for_regions(
        region_codes=args.region_code,
        area_group=args.area_group,
        theme=args.theme,
        limit=args.limit,
        offset_regions=args.offset_regions,
        limit_regions=args.limit_regions,
    )
    print(
        "TourAPI batch sync complete: "
        f"total_regions={result.total_regions}, "
        f"success={result.success_count}, "
        f"failed={result.failure_count}, "
        f"fetched={result.fetched_count}, "
        f"upserted={result.upserted_count}"
    )
    for item in result.results:
        print(
            "SUCCESS "
            f"region_code={item.region_code}, "
            f"fetched={item.fetched_count}, "
            f"upserted={item.upserted_count}"
        )
    for failure in result.failures:
        print(f"FAILED region_code={failure.region_code}, error={failure.error}")


def _sync_single_region(args: argparse.Namespace) -> None:
    result = sync_tour_api_places(
        region_code=args.region_code[0],
        theme=args.theme,
        limit=args.limit,
    )
    print(
        "TourAPI sync complete: "
        f"region_code={result.region_code}, "
        f"fetched={result.fetched_count}, "
        f"upserted={result.upserted_count}"
    )
    if result.place_ids:
        print("place_ids=" + ", ".join(result.place_ids))


if __name__ == "__main__":
    main()
