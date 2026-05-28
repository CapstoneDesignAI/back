from datetime import date

from app.services.recommendations import get_today_recommendation


def test_today_recommendation_contains_home_card_and_detail_payload() -> None:
    response = get_today_recommendation(reference_date=date(2026, 5, 28))
    data = response.model_dump()

    assert data["today_date"] == "2026-05-28"
    assert data["card"] == {
        "recommendation_id": "sample-danyang-healing-half_day",
        "title": data["recommendation"]["title"],
        "subtitle": data["recommendation"]["subtitle"],
        "region_label": "충청북도 단양군",
        "theme_label": "힐링",
        "contribution_score": data["recommendation"]["contribution_score"],
        "estimated_duration_text": data["recommendation"]["summary"]["duration_text"],
        "estimated_cost_text": data["recommendation"]["summary"]["cost_range_text"],
        "local_consumption_text": data["recommendation"]["summary"]["local_consumption_text"],
        "primary_badges": ["힐링", "지역 기여도 86점", "로컬 소비 2곳"],
        "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
    }

    assert data["recommendation"]["legacy_route_payload"]["title"] == data["card"]["title"]
    assert data["recommendation"]["map_markers"][0]["name"] == "도담삼봉"
