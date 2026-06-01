from datetime import date

from app.services.recommendations import get_today_recommendation


def test_today_recommendation_contains_home_card_and_detail_payload() -> None:
    response = get_today_recommendation(reference_date=date(2026, 5, 28))
    data = response.model_dump()

    assert data["today_date"] == "2026-05-28"
    assert data["card"] == {
        "recommendation_id": "sample-danyang-healing-half_day",
        "route_id": "route-danyang-healing-half_day",
        "title": data["recommendation"]["title"],
        "subtitle": data["recommendation"]["subtitle"],
        "summary": "도담삼봉부터 만천하스카이워크까지 이어지는 로컬 동선",
        "sido": "충청북도",
        "sigungu": "단양군",
        "region_label": "충청북도 단양군",
        "theme_label": "힐링",
        "thumbnail_url": None,
        "contribution_score": data["recommendation"]["contribution_score"],
        "estimated_duration_text": data["recommendation"]["summary"]["duration_text"],
        "estimated_cost_text": data["recommendation"]["summary"]["cost_range_text"],
        "local_consumption_text": data["recommendation"]["summary"]["local_consumption_text"],
        "primary_badges": ["힐링", "반나절", "자차"],
        "place_count": 4,
        "place_count_text": "장소 4곳",
        "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
        "place_preview": [
            {
                "order": 1,
                "place_id": "sample-dodamsambong",
                "name": "도담삼봉",
                "category": "자연",
            },
            {
                "order": 2,
                "place_id": "sample-danyang-market",
                "name": "단양구경시장",
                "category": "로컬시장",
            },
            {
                "order": 3,
                "place_id": "sample-cafe-sann",
                "name": "카페산",
                "category": "카페",
            },
        ],
        "route_preview_text": "도담삼봉 → 단양구경시장 → 카페산",
        "ai_reason_summary": data["recommendation"]["ai_reason"][:80],
    }

    assert data["recommendation"]["card"] == data["card"]
    assert data["recommendation"]["legacy_route_payload"]["title"] == data["card"]["title"]
    assert data["recommendation"]["map_markers"][0]["name"] == "도담삼봉"
