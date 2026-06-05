from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_recommendations_uses_scored_recommendation_response() -> None:
    response = client.post(
        "/api/v1/ai-recommendations",
        json={
            "duration": "반나절",
            "transportation": "도보",
            "travel_purpose": "힐링",
            "companion": "친구",
            "atmosphere": "감성적인",
            "activity_style": "정적/잔잔함",
            "region": "단양군",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["recommendation_id"] == "sample-danyang-healing-half_day"
    assert data["route_id"] == "route-danyang-healing-half_day-walk-friends"
    assert data["title"] == "단양 힐링 로컬 코스"
    assert data["sido"] == "충청북도"
    assert data["sigungu"] == "단양군"
    assert data["region_story"]["title"] == "단양 로컬 여행 이야기"
    assert data["region_story"]["source"] == "mvp_sample"
    assert data["tags"] == ["힐링", "반나절", "뚜벅이"]
    assert data["mobility"]["level"] == "high"
    assert data["mobility"]["recommended_transport"] == "뚜벅이"
    assert data["contribution_info"]["score"] == 86
    assert data["contribution_info"]["average_place_score"] == 80
    assert data["contribution_info"]["local_consumption_bonus"] == 6
    assert data["contribution_info"]["is_official_metric"] is False
    assert [point["place_id"] for point in data["local_consumption_points"]] == [
        "sample-danyang-market",
        "sample-cafe-sann",
    ]
    assert len(data["tags"]) == 3
    assert data["metric_badges"] == ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"]
    assert data["place_preview_names"] == ["도담삼봉", "단양구경시장", "카페산"]
    assert data["place_preview"][1]["name"] == "단양구경시장"
    assert data["place_preview"][1]["tags"] == ["맛집", "로컬시장"]
    assert data["place_preview"][1]["is_local_consumption"] is True
    assert data["place_count"] == 4
    assert "places" not in data
    assert "map_markers" not in data
    assert "legacy_route_payload" not in data


def test_ai_recommendations_accepts_english_alias_values() -> None:
    response = client.post(
        "/api/v1/ai-recommendations",
        json={
            "duration": "half_day",
            "transportation": "walk",
            "travel_purpose": "healing",
            "companion": "friends",
            "region": "region-danyang",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["recommendation_id"] == "sample-danyang-healing-half_day"
    assert data["route_id"] == "route-danyang-healing-half_day-walk-friends"
    assert len(data["tags"]) == 3
    assert len(data["metric_badges"]) == 3
    assert data["place_count"] == len(data["place_preview_names"]) + 1
    assert data["place_preview"][0]["order"] == 1
    assert "places" not in data
    assert "route_legs" not in data


def test_ai_recommendations_defaults_to_ai_region_when_region_is_missing() -> None:
    response = client.post(
        "/api/v1/ai-recommendations",
        json={
            "duration": "하루",
            "transportation": "자차",
            "travel_purpose": "자연/풍경",
            "companion": "가족",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["route_id"] == "route-danyang-nature-full_day-car-family"
    assert data["sido"] == "충청북도"
    assert data["sigungu"] == "단양군"
    assert data["tags"] == ["자연투어", "하루", "자차"]


def test_ai_recommendations_accepts_mvp_korean_option_labels() -> None:
    response = client.post(
        "/api/v1/ai-recommendations",
        json={
            "duration": "3시간",
            "transportation": "뚜벅이",
            "travel_purpose": "지역활성화 추천",
            "companion": "연인",
            "region": "충청북도 단양군",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["route_id"] == "route-danyang-revitalization-3hours-walk-couple"
    assert data["sido"] == "충청북도"
    assert data["sigungu"] == "단양군"
    assert data["tags"] == ["지역활성화 추천", "3시간", "뚜벅이"]


def test_recommendations_endpoint_accepts_korean_labels() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "region_id": "단양군",
            "theme": "맛집",
            "travel_time": "반나절",
            "transport": "대중교통",
            "companion": "가족",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["region"]["id"] == "region-danyang"
    assert data["theme"] == "food"
    assert data["theme_label"] == "맛집"
    assert data["travel_time"] == "half_day"
    assert data["transport"] == "public_transport"
    assert data["companion"] == "family"


def test_ai_recommendation_detail_returns_route_by_route_id() -> None:
    response = client.get(
        "/api/v1/ai-recommendations/route-danyang-healing-half_day-walk-friends"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["route_id"] == "route-danyang-healing-half_day-walk-friends"
    assert data["title"] == "단양 힐링 로컬 코스"
    assert data["sido"] == "충청북도"
    assert data["sigungu"] == "단양군"
    assert "card" not in data
    assert data["mobility"]["label"] == "이동 난이도 높음"
    assert data["local_consumption_points"][0]["name"] == "단양구경시장"
    assert data["region_story"]["local_tip"].startswith("전망 명소 방문 전후")
    assert data["contribution_info"]["formula"] == (
        "장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점(최대 10점)"
    )
    assert data["places"][0]["distance_from_previous_meters"] is None
    assert (
        data["places"][1]["distance_from_previous_meters"]
        == data["route_legs"][0]["distance_meters"]
    )
    assert data["total_distance_meters"] == sum(
        leg["distance_meters"] for leg in data["route_legs"]
    )
    assert data["places"][0]["name"] == "도담삼봉"
    assert data["places"][1]["place_story"].startswith("단양구경시장은")
    assert data["places"][1]["local_tip"] == (
        "이 장소에서는 식사, 카페, 간식 등 실제 지역 상권 소비로 이어질 수 있습니다."
    )
    assert "map_markers" not in data
    assert data["legacy_route_payload"]["title"] == data["title"]


def test_ai_recommendation_detail_accepts_legacy_route_id() -> None:
    response = client.get("/api/v1/ai-recommendations/route-danyang-healing-half_day")

    assert response.status_code == 200
    data = response.json()

    assert data["route_id"] == "route-danyang-healing-half_day-walk-friends"
    assert data["transport"] == "walk"
    assert data["companion"] == "friends"


def test_ai_recommendation_detail_returns_404_for_unknown_route_id() -> None:
    response = client.get("/api/v1/ai-recommendations/route-unknown-healing-half_day")

    assert response.status_code == 404
