from app.schemas.recommendations import RecommendationRequest, RegionItem
from app.services import tour_api
from app.services.recommendations import create_recommendation, list_places


class FakeTourApiResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {
            "response": {
                "body": {
                    "items": {
                        "item": [
                            {
                                "contentid": "999001",
                                "contenttypeid": "39",
                                "title": "단양 로컬 맛집",
                                "addr1": "충청북도 단양군 단양읍",
                                "addr2": "시장길 1",
                                "mapx": "128.365889",
                                "mapy": "36.984784",
                                "firstimage": "https://example.com/food.jpg",
                            },
                            {
                                "contentid": "999002",
                                "contenttypeid": "12",
                                "title": "단양 강변공원",
                                "addr1": "충청북도 단양군",
                                "addr2": "",
                                "mapx": "128.369267",
                                "mapy": "36.984539",
                            },
                        ]
                    }
                }
            }
        }


class FakeTourPhotoApiResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {
            "response": {
                "body": {
                    "items": {
                        "item": [
                            {
                                "orgImage": "https://example.com/photo.jpg",
                                "thumbImage": "https://example.com/photo-thumb.jpg",
                            }
                        ]
                    }
                }
            }
        }


def test_fetch_tour_api_places_maps_items_to_place_candidates(monkeypatch) -> None:
    monkeypatch.setattr(tour_api.settings, "tour_api_service_key", "test-service-key")
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_base_url", None)
    monkeypatch.setattr(tour_api.httpx, "get", lambda *args, **kwargs: FakeTourApiResponse())
    region = RegionItem(
        id="region-danyang",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="단양군",
        is_population_decline=True,
    )

    places = tour_api.fetch_tour_api_places(region=region, theme="food", num_of_rows=10)

    assert len(places) == 2
    assert places[0].place_id == "tour-999001"
    assert places[0].name == "단양 로컬 맛집"
    assert places[0].source == "tour_api"
    assert places[0].image_url == "https://example.com/food.jpg"
    assert places[0].is_local_consumption is True
    assert "food" in places[0].theme_tags
    assert "nature" in places[1].theme_tags


def test_list_places_can_use_tour_api_source(monkeypatch) -> None:
    tour_api_place = tour_api.PlaceCandidate(
        place_id="tour-999001",
        region_id="region-danyang",
        name="단양 로컬 맛집",
        category="맛집",
        address="충청북도 단양군 단양읍 시장길 1",
        lat=36.984784,
        lng=128.365889,
        stay_minutes=60,
        estimated_cost_min=12000,
        estimated_cost_max=30000,
        local_contribution_score=88,
        theme_tags=("food", "revitalization", "walk"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=True,
        reason="한국관광공사 제공 장소입니다.",
        contribution_reason="지역 상권에 직접 기여할 수 있습니다.",
        source="tour_api",
    )
    monkeypatch.setattr(
        "app.services.recommendations.fetch_tour_api_places",
        lambda **kwargs: (tour_api_place,),
    )

    response = list_places(region_id="region-danyang", source="tour_api", theme="food")

    assert response.places[0].place_id == "tour-999001"
    assert response.places[0].source == "tour_api"
    assert response.places[0].tags


def test_fetch_tour_photo_image_url_returns_none_without_base_url(monkeypatch) -> None:
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_base_url", "")

    assert tour_api.fetch_tour_photo_image_url("단양") is None


def test_fetch_tour_photo_image_url_maps_first_photo_url(monkeypatch) -> None:
    captured_params = {}
    captured_url = ""

    def fake_get(*args, **kwargs):
        nonlocal captured_url
        captured_url = args[0]
        captured_params.update(kwargs.get("params", {}))
        return FakeTourPhotoApiResponse()

    monkeypatch.setattr(tour_api.settings, "tour_photo_api_base_url", "https://apis.data.go.kr/B551011/PhokoAwrdService")
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_search_endpoint", "phokoAwrdList")
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_service_key", "photo-service-key")
    monkeypatch.setattr(tour_api.httpx, "get", fake_get)

    image_url = tour_api.fetch_tour_photo_image_url("도담삼봉")

    assert image_url == "https://example.com/photo.jpg"
    assert captured_url == "https://apis.data.go.kr/B551011/PhokoAwrdService/phokoAwrdList"
    assert captured_params["serviceKey"] == "photo-service-key"
    assert captured_params["keyword"] == "도담삼봉"
    assert captured_params["arrange"] == "A"


def test_fetch_tour_photo_image_url_returns_none_without_base_url(monkeypatch) -> None:
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_base_url", "")

    assert tour_api.fetch_tour_photo_image_url("단양") is None


def test_fetch_tour_photo_image_url_maps_first_photo_url(monkeypatch) -> None:
    captured_params = {}
    captured_url = ""

    def fake_get(*args, **kwargs):
        nonlocal captured_url
        captured_url = args[0]
        captured_params.update(kwargs.get("params", {}))
        return FakeTourPhotoApiResponse()

    monkeypatch.setattr(tour_api.settings, "tour_photo_api_base_url", "https://apis.data.go.kr/B551011/PhokoAwrdService")
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_search_endpoint", "phokoAwrdList")
    monkeypatch.setattr(tour_api.settings, "tour_photo_api_service_key", "photo-service-key")
    monkeypatch.setattr(tour_api.httpx, "get", fake_get)

    image_url = tour_api.fetch_tour_photo_image_url("도담삼봉")

    assert image_url == "https://example.com/photo.jpg"
    assert captured_url == "https://apis.data.go.kr/B551011/PhokoAwrdService/phokoAwrdList"
    assert captured_params["serviceKey"] == "photo-service-key"
    assert captured_params["keyword"] == "도담삼봉"
    assert captured_params["arrange"] == "A"


def test_recommendation_falls_back_to_sample_when_tour_api_has_no_result(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.recommendations.fetch_tour_api_places",
        lambda **kwargs: (),
    )

    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="healing",
            travel_time="half_day",
            transport="walk",
            companion="friends",
            data_source="tour_api",
        )
    )

    assert response.source == "sample"
    assert response.places[0].source == "sample"


def test_recommendation_can_use_tour_api_candidates(monkeypatch) -> None:
    tour_api_place = tour_api.PlaceCandidate(
        place_id="tour-999001",
        region_id="region-danyang",
        name="단양 로컬 맛집",
        category="맛집",
        address="충청북도 단양군 단양읍 시장길 1",
        lat=36.984784,
        lng=128.365889,
        stay_minutes=60,
        estimated_cost_min=12000,
        estimated_cost_max=30000,
        local_contribution_score=88,
        theme_tags=("food", "revitalization", "walk"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=True,
        reason="한국관광공사 제공 장소입니다.",
        contribution_reason="지역 상권에 직접 기여할 수 있습니다.",
        source="tour_api",
    )
    monkeypatch.setattr(
        "app.services.recommendations.fetch_tour_api_places",
        lambda **kwargs: (tour_api_place,),
    )

    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="food",
            travel_time="3hours",
            transport="walk",
            companion="friends",
            data_source="tour_api",
        )
    )

    assert response.source == "tour_api"
    assert response.places[0].place_id == "tour-999001"
    assert response.places[0].source == "tour_api"
