from app.schemas.recommendations import RecommendationRequest
from app.services.recommendations import create_recommendation


def test_ai_reason_detail_mentions_route_and_local_contribution() -> None:
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

    assert "단양군" in data["ai_reason"]
    assert "도담삼봉" in data["ai_reason"]
    assert "단양구경시장" in data["ai_reason_detail"]["local_contribution"]
    assert data["ai_reason_detail"]["generation_source"] == "rule_based_ai_ready"
    assert data["ai_reason_detail"]["highlights"] == [
        "힐링 테마 적합",
        "지역 기여도 86점",
        "로컬 소비 장소 2곳 포함",
    ]

