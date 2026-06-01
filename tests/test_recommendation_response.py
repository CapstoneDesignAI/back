from app.schemas.recommendations import RecommendationRequest
from app.services.recommendations import DEFAULT_REGION_IMAGE_URLS, create_recommendation


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
    fallback_image_url = DEFAULT_REGION_IMAGE_URLS["region-danyang"]

    assert data["route_id"] == "route-danyang-healing-half_day-walk-friends"
    assert data["title"] == "단양 힐링 로컬 코스"
    assert data["subtitle"] == "충청북도 단양군에서 즐기는 반나절 여행"
    assert data["sido"] == "충청북도"
    assert data["sigungu"] == "단양군"
    assert data["region_story"] == {
        "title": "단양 로컬 여행 이야기",
        "summary": (
            "단양은 남한강을 따라 이어지는 자연 경관과 전통시장, 전망 명소가 "
            "가까이 연결된 충북의 대표 체류형 여행지입니다."
        ),
        "history": (
            "단양은 삼봉 정도전의 이야기가 남아 있는 도담삼봉과 석문, "
            "남한강 물길을 중심으로 형성된 산수 관광 자원이 잘 알려진 지역입니다."
        ),
        "local_story": (
            "힐링 코스에서는 도담삼봉에서 지역의 첫인상을 만들고, 시장과 로컬 카페를 "
            "함께 배치해 방문이 지역 소비로 이어지도록 구성했습니다."
        ),
        "local_tip": (
            "전망 명소 방문 전후로 단양구경시장이나 로컬 카페를 함께 들르면 "
            "짧은 일정에서도 지역 상권 체류 효과를 만들 수 있습니다."
        ),
        "source": "mvp_sample",
    }
    assert data["theme_label"] == "힐링"
    assert data["travel_time_label"] == "반나절"
    assert data["transport_label"] == "뚜벅이"
    assert data["companion_label"] == "친구"
    assert data["source"] == "sample"
    assert data["place_count"] == 4
    assert data["total_stay_minutes"] == 260
    assert data["total_distance_meters"] == sum(
        leg["distance_meters"] for leg in data["route_legs"]
    )
    assert data["total_distance_meters"] > 0
    assert data["total_distance_km"] == round(data["total_distance_meters"] / 1000, 1)
    assert data["total_distance_text"].endswith("km")
    assert data["mobility"] == {
        "level": "high",
        "label": "이동 난이도 높음",
        "summary": "장소 사이 거리가 길어 전체 코스를 도보로만 이동하기에는 부담이 큰 코스입니다.",
        "recommended_transport": "뚜벅이",
    }
    assert data["contribution_info"] == {
        "score": 86,
        "label": "지역 기여도 86점",
        "description": (
            "지역 기여도는 공식 공공 지표가 아니라 Tripick MVP 내부 점수입니다. "
            "코스에 포함된 장소들의 지역 기여도 평균에 로컬 소비 장소 보너스를 더해 계산합니다."
        ),
        "formula": "장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점(최대 10점)",
        "average_place_score": 80,
        "local_consumption_bonus": 6,
        "local_consumption_count": 2,
        "place_count": 4,
        "is_official_metric": False,
    }
    assert data["route_badges"] == ["힐링", "지역 기여도 86점", "로컬 소비 2곳", "반나절 코스"]
    assert data["card"]["route_id"] == data["route_id"]
    assert data["card"]["sido"] == "충청북도"
    assert data["card"]["sigungu"] == "단양군"
    assert data["card"]["region_story"] == data["region_story"]
    assert data["card"]["tags"] == ["힐링", "반나절", "뚜벅이"]
    assert data["card"]["mobility"] == data["mobility"]
    assert data["card"]["contribution_info"] == data["contribution_info"]
    assert data["card"]["local_consumption_points"] == data["local_consumption_points"]
    assert len(data["card"]["tags"]) == 3
    assert data["card"]["metric_badges"] == ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"]
    assert data["card"]["place_count_text"] == "장소 4곳"
    assert data["card"]["place_preview_names"] == ["도담삼봉", "단양구경시장", "카페산"]
    assert data["card"]["route_preview_text"] == "도담삼봉 → 단양구경시장 → 카페산"
    assert data["card"]["place_preview"][0] == {
        "order": 1,
        "place_id": "sample-dodamsambong",
        "name": "도담삼봉",
        "category": "자연",
        "summary": "단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
        "tags": ["힐링", "자연투어"],
        "image_url": fallback_image_url,
        "lat": 36.984539,
        "lng": 128.369267,
        "is_local_consumption": False,
    }
    assert data["card"]["thumbnail_url"] == fallback_image_url
    assert all(place["image_url"] for place in data["card"]["place_preview"])
    assert all(place["image_url"] for place in data["places"])

    assert data["summary"] == {
        "contribution_label": "지역 기여도 86점",
        "duration_text": "5시간 20분",
        "cost_range_text": "35,000원~55,000원",
        "local_consumption_text": "로컬 소비 장소 2곳 포함",
    }
    assert [point["place_id"] for point in data["local_consumption_points"]] == [
        "sample-danyang-market",
        "sample-cafe-sann",
    ]
    assert data["local_consumption_points"][0]["order"] == 2
    assert data["local_consumption_points"][0]["category"] == "로컬시장"
    assert data["local_consumption_points"][0]["estimated_cost_text"] == "15,000원~25,000원"
    assert data["local_consumption_points"][1]["order"] == 3
    assert data["local_consumption_points"][1]["estimated_cost_text"] == "10,000원~15,000원"
    assert set(data["ai_reason_detail"]) == {
        "overview",
        "route_design",
        "local_contribution",
        "traveler_fit",
        "closing_tip",
        "highlights",
        "generation_source",
    }

    assert data["map_markers"][0]["name"] == "도담삼봉"

    first_place = data["places"][0]
    assert first_place["order"] == 1
    assert first_place["visit_order"] == 1
    assert first_place["tags"] == ["힐링", "자연투어", "뚜벅이", "지역활성화 추천"]
    assert first_place["recommendation_score"] == 79
    assert first_place["distance_from_previous_meters"] is None
    assert first_place["place_story"] == (
        "도담삼봉은 단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다."
    )
    assert first_place["local_tip"] == (
        "방문 전후 가까운 전통시장이나 로컬 매장을 함께 둘러보면 더 좋은 동선이 됩니다."
    )

    second_place = data["places"][1]
    first_leg = data["route_legs"][0]
    assert first_leg["order"] == 1
    assert first_leg["from_place_id"] == first_place["place_id"]
    assert first_leg["from_name"] == first_place["name"]
    assert first_leg["to_place_id"] == second_place["place_id"]
    assert first_leg["to_name"] == second_place["name"]
    assert first_leg["distance_meters"] > 0
    assert first_leg["distance_km"] == round(first_leg["distance_meters"] / 1000, 1)
    assert second_place["distance_from_previous_meters"] == first_leg["distance_meters"]
    assert second_place["distance_from_previous_km"] == first_leg["distance_km"]
    assert second_place["distance_from_previous_text"] == first_leg["distance_text"]

    assert data["legacy_route_payload"]["title"] == "단양 힐링 로컬 코스"
    assert data["legacy_route_payload"]["estimated_time"] == "총 예상 소요 시간: 5시간 20분"
    assert data["legacy_route_payload"]["places"][0]["visit_order"] == 1
    assert data["legacy_route_payload"]["places"][0]["description"] == first_place["reason"]
