from datetime import date

from app.services.recommendations import DEFAULT_REGION_IMAGE_URLS, get_today_recommendation


def test_today_recommendation_contains_home_card_and_detail_payload() -> None:
    response = get_today_recommendation(reference_date=date(2026, 5, 28))
    data = response.model_dump()
    fallback_image_url = DEFAULT_REGION_IMAGE_URLS["region-danyang"]

    assert data["today_date"] == "2026-05-28"
    assert data["section_title"] == "오늘의 추천 여행"
    assert data["recommendation_id"] == "sample-danyang-healing-half_day"
    assert data["route_id"] == "route-danyang-healing-half_day-car-friends"
    assert (
        data["detail_api_path"]
        == "/api/v1/ai-recommendations/route-danyang-healing-half_day-car-friends"
    )
    assert data["save_api_path"] == "/api/v1/routes/from-recommendation"
    assert data["card"] == {
        "recommendation_id": "sample-danyang-healing-half_day",
        "route_id": "route-danyang-healing-half_day-car-friends",
        "title": data["recommendation"]["title"],
        "subtitle": data["recommendation"]["subtitle"],
        "summary": "도담삼봉부터 만천하스카이워크까지 이어지는 로컬 동선",
        "sido": "충청북도",
        "sigungu": "단양군",
        "region_label": "충청북도 단양군",
        "theme_label": "힐링",
        "region_story": data["recommendation"]["region_story"],
        "thumbnail_url": fallback_image_url,
        "contribution_score": data["recommendation"]["contribution_score"],
        "contribution_info": data["recommendation"]["contribution_info"],
        "estimated_duration_text": data["recommendation"]["summary"]["duration_text"],
        "estimated_cost_text": data["recommendation"]["summary"]["cost_range_text"],
        "local_consumption_text": data["recommendation"]["summary"]["local_consumption_text"],
        "local_consumption_points": data["recommendation"]["local_consumption_points"],
        "mobility": data["recommendation"]["mobility"],
        "tags": ["힐링", "반나절", "자차"],
        "metric_badges": ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"],
        "place_count": 4,
        "place_count_text": "장소 4곳",
        "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
        "place_preview": [
            {
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
            },
            {
                "order": 2,
                "place_id": "sample-danyang-market",
                "name": "단양구경시장",
                "category": "로컬시장",
                "summary": "지역 먹거리와 소상공인 매장을 함께 경험할 수 있는 장소입니다.",
                "tags": ["맛집", "로컬시장"],
                "image_url": fallback_image_url,
                "lat": 36.984784,
                "lng": 128.365889,
                "is_local_consumption": True,
            },
            {
                "order": 3,
                "place_id": "sample-cafe-sann",
                "name": "카페산",
                "category": "카페",
                "summary": "전망과 휴식을 함께 제공해 여행 피로도를 낮추는 중간 지점입니다.",
                "tags": ["힐링", "자연투어"],
                "image_url": fallback_image_url,
                "lat": 37.024255,
                "lng": 128.395729,
                "is_local_consumption": True,
            },
        ],
        "route_preview_text": "도담삼봉 → 단양구경시장 → 카페산",
        "ai_reason_summary": data["recommendation"]["ai_reason"][:80],
    }

    assert "card" not in data["recommendation"]
    assert data["recommendation"]["recommendation_id"] == data["recommendation_id"]
    assert data["recommendation"]["route_id"] == data["route_id"]
    assert data["recommendation"]["title"] == data["card"]["title"]
    assert data["recommendation"]["legacy_route_payload"]["title"] == data["card"]["title"]
    assert "map_markers" not in data["recommendation"]
