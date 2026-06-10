from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.tour_place_sync import sync_tour_api_places


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync TourAPI places into Supabase places.")
    parser.add_argument("--region-code", required=True, help="regions.region_code value")
    parser.add_argument("--theme", default=None, help="Optional Tripick theme code")
    parser.add_argument("--limit", type=int, default=50, help="TourAPI rows per content type")
    args = parser.parse_args()

    result = sync_tour_api_places(
        region_code=args.region_code,
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
