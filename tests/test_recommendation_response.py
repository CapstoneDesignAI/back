from app.schemas.recommendations import RecommendationRequest
from app.services.recommendations import create_recommendation


def test_recommendation_response_contract_for_frontend() -> None:
    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="healing",
            travel_time="half_day",
            transport="walk",
            companion="friends",
        )
    )
    data = response.model_dump()

    assert data["title"] == "단양 힐링 로컬 코스"
    assert data["subtitle"] == "충청북도 단양군에서 즐기는 반나절 여행"
    assert data["theme_label"] == "힐링"
    assert data["travel_time_label"] == "반나절"
    assert data["transport_label"] == "뚜벅이"
    assert data["companion_label"] == "친구"
    assert data["source"] == "sample"
    assert data["place_count"] == 4
    assert data["total_stay_minutes"] == 260
    assert data["route_badges"] == ["힐링", "지역 기여도 86점", "로컬 소비 2곳", "반나절 코스"]

    assert data["summary"] == {
        "contribution_label": "지역 기여도 86점",
        "duration_text": "5시간 20분",
        "cost_range_text": "35,000원~55,000원",
        "local_consumption_text": "로컬 소비 장소 2곳 포함",
    }
    assert set(data["ai_reason_detail"]) == {
        "overview",
        "route_design",
        "local_contribution",
        "traveler_fit",
        "closing_tip",
        "highlights",
        "generation_source",
    }

    assert data["map_markers"][0] == {
        "order": 1,
        "place_id": "sample-dodamsambong",
        "name": "도담삼봉",
        "category": "자연",
        "lat": 36.984539,
        "lng": 128.369267,
    }

    first_place = data["places"][0]
    assert first_place["order"] == 1
    assert first_place["visit_order"] == 1
    assert first_place["tags"] == ["healing", "nature", "walk", "revitalization"]
    assert first_place["recommendation_score"] == 79

    assert data["legacy_route_payload"]["title"] == "단양 힐링 로컬 코스"
    assert data["legacy_route_payload"]["estimated_time"] == "총 예상 소요 시간: 5시간 20분"
    assert data["legacy_route_payload"]["places"][0]["visit_order"] == 1
    assert data["legacy_route_payload"]["places"][0]["description"] == first_place["reason"]
