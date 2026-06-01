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
    assert data["primary_badges"] == ["힐링", "반나절", "뚜벅이"]
    assert len(data["primary_badges"]) == 3
    assert data["metric_badges"] == ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"]
    assert data["place_preview_names"] == ["도담삼봉", "단양구경시장", "카페산"]
    assert data["place_preview"][1]["name"] == "단양구경시장"
    assert data["place_preview"][1]["tags"] == ["food", "local_market"]
    assert data["place_preview"][1]["is_local_consumption"] is True
    assert data["place_count"] == 4
    assert "places" not in data
    assert "map_markers" not in data
    assert "legacy_route_payload" not in data


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
    assert data["primary_badges"] == ["자연투어", "하루", "자차"]


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
    assert data["primary_badges"] == ["지역활성화 추천", "3시간", "뚜벅이"]


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
    assert data["places"][0]["name"] == "도담삼봉"
    assert data["map_markers"][0]["name"] == "도담삼봉"
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
