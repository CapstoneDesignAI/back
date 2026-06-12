from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.schemas.recommendations import RecommendationCard
from app.api.v1.endpoints import recommendations as recommendations_endpoint
from app.services import recommendations as recommendation_service


client = TestClient(app)


@pytest.fixture(autouse=True)
def _disable_supabase_candidates(monkeypatch) -> None:
    monkeypatch.setattr(
        recommendation_service,
        "fetch_place_candidates_from_supabase",
        lambda **kwargs: (),
    )
    monkeypatch.setattr(
        recommendation_service,
        "fetch_tour_api_places",
        lambda **kwargs: (),
    )


def test_ai_recommendations_uses_auto_data_source(monkeypatch) -> None:
    captured_request = None

    def fake_create_recommendation(request):
        nonlocal captured_request
        captured_request = request
        return type(
            "FakeRecommendation",
            (),
            {
                "card": RecommendationCard(
                    recommendation_id="sample-danyang-healing-half_day",
                    route_id="route-danyang-healing-half_day-walk-friends",
                    title="단양 힐링 로컬 코스",
                    subtitle="충청북도 단양군에서 즐기는 반나절 여행",
                    summary="DB 후보 기반 추천 카드",
                    sido="충청북도",
                    sigungu="단양군",
                    region_label="충청북도 단양군",
                    theme_label="힐링",
                    region_story={
                        "title": "단양 로컬 여행 이야기",
                        "summary": "요약",
                        "history": "역사",
                        "local_story": "스토리",
                        "local_tip": "팁",
                        "source": "mvp_sample",
                    },
                    thumbnail_url=None,
                    contribution_score=80,
                    contribution_info={
                        "score": 80,
                        "label": "지역 기여도 80점",
                        "description": "설명",
                        "formula": "공식",
                        "average_place_score": 80,
                        "local_consumption_bonus": 0,
                        "local_consumption_count": 0,
                        "place_count": 0,
                        "is_official_metric": False,
                    },
                    estimated_duration_text="반나절",
                    estimated_cost_text="0원~0원",
                    local_consumption_text="로컬 소비 0곳 포함",
                    local_consumption_points=[],
                    mobility={
                        "level": "low",
                        "label": "이동 난이도 낮음",
                        "summary": "요약",
                        "recommended_transport": "뚜벅이",
                    },
                    tags=["힐링", "반나절", "뚜벅이"],
                    metric_badges=["지역 기여도 80점", "로컬 소비 0곳", "장소 0곳"],
                    place_count=0,
                    place_count_text="장소 0곳",
                    place_preview_names=[],
                    place_preview=[],
                    route_preview_text="추천 장소 준비 중",
                    ai_reason_summary="추천 이유",
                )
            },
        )()

    monkeypatch.setattr(
        recommendations_endpoint,
        "create_recommendation",
        fake_create_recommendation,
    )

    response = client.post(
        "/api/v1/ai-recommendations",
        json={
            "duration": "반나절",
            "transportation": "도보",
            "travel_purpose": "힐링",
            "companion": "친구",
            "region": "단양군",
        },
    )

    assert response.status_code == 200
    assert captured_request is not None
    assert captured_request.data_source == "auto"


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


def test_score_recommendations_auto_source_falls_back_to_sample_region_when_empty() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "area_group": "강원도",
            "theme": "힐링",
            "travel_time": "반나절",
            "transport": "도보",
            "companion": "친구",
            "prefer_ai_region": False,
            "data_source": "auto",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["route_id"] == "route-pyeongchang-healing-half_day-walk-friends"
    assert data["sigungu"] == "평창군"
    assert data["place_count"] == 4
    assert data["estimated_cost_min"] > 0
    assert data["card"]["place_count_text"] == "장소 4곳"
    assert all(place["image_url"] for place in data["places"])


def test_ai_recommendation_detail_reuses_auto_source_for_custom_route_id() -> None:
    response = client.get(
        "/api/v1/ai-recommendations/route-pyeongchang-healing-half_day-walk-friends"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["route_id"] == "route-pyeongchang-healing-half_day-walk-friends"
    assert data["sigungu"] == "평창군"
    assert data["place_count"] == 4
    assert data["estimated_cost_min"] > 0
    assert [place["visit_order"] for place in data["places"]] == [1, 2, 3, 4]
    assert [place["order"] for place in data["places"]] == [1, 2, 3, 4]


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


def test_recommendations_endpoint_accepts_province_area_group_labels() -> None:
    gangwon_response = client.post(
        "/api/v1/recommendations",
        json={
            "area_group": "강원도",
            "theme": "힐링",
            "travel_time": "반나절",
            "transport": "도보",
            "companion": "친구",
            "data_source": "auto",
        },
    )
    gyeonggi_response = client.post(
        "/api/v1/recommendations",
        json={
            "area_group": "경기도",
            "theme": "힐링",
            "travel_time": "반나절",
            "transport": "도보",
            "companion": "친구",
            "data_source": "auto",
        },
    )

    assert gangwon_response.status_code == 200
    assert gyeonggi_response.status_code == 200

    gangwon_data = gangwon_response.json()
    gyeonggi_data = gyeonggi_response.json()
    assert gangwon_data["region"]["id"] == "region-pyeongchang"
    assert gangwon_data["sido"] == "강원특별자치도"
    assert gangwon_data["sigungu"] == "평창군"
    assert gyeonggi_data["region"]["id"] == "region-gapyeong"
    assert gyeonggi_data["sido"] == "경기도"
    assert gyeonggi_data["sigungu"] == "가평군"


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
