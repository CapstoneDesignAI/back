from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints import routes as routes_endpoint
from app.services import odsay_service, route_service


client = TestClient(app)


def test_get_transportation_segments_maps_odsay_response(monkeypatch) -> None:
    captured_params = {}

    def fake_get_route_detail(route_id: str):
        assert route_id == "route-id"
        return {
            "route_id": "route-id",
            "title": "테스트 동선",
            "created_at": "2026-06-04T00:00:00",
            "places": [
                {
                    "visit_order": 1,
                    "name": "청량리",
                    "address": "서울 동대문구",
                    "lat": 37.5801,
                    "lng": 127.0469,
                },
                {
                    "visit_order": 2,
                    "name": "영월역",
                    "address": "강원 영월군",
                    "lat": 37.1825,
                    "lng": 128.4617,
                },
            ],
        }

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "result": {
                    "path": [
                        {
                            "info": {
                                "totalTime": 160,
                                "payment": 18200,
                                "busTransitCount": 1,
                                "subwayTransitCount": 0,
                                "firstStartStation": "청량리",
                                "lastEndStation": "영월역",
                                "totalDistance": 100,
                            },
                            "subPath": [
                                {
                                    "trafficType": 2,
                                    "lane": [{"busNo": "무궁화호"}],
                                }
                            ],
                        }
                    ]
                }
            }

    def fake_httpx_get(url, params, timeout):
        captured_params.update(params)
        return FakeResponse()

    monkeypatch.setattr(odsay_service.settings, "odsay_api_key", "test-key")
    monkeypatch.setattr(route_service, "get_route_detail", fake_get_route_detail)
    monkeypatch.setattr(odsay_service.httpx, "get", fake_httpx_get)

    result = odsay_service.get_transportation_segments("route-id")

    assert result is not None
    assert captured_params["SX"] == 127.0469
    assert captured_params["SY"] == 37.5801
    assert captured_params["EX"] == 128.4617
    assert captured_params["EY"] == 37.1825
    assert result.available is True
    assert result.title == "🚌 대중교통 가능"
    assert result.totalTimeText == "2시간 40분"
    assert result.summaryText == "총 2시간 40분 · 환승 1회"
    assert result.firstStart == "청량리"
    assert result.lastArrival == "영월역"
    assert result.details[0].payment == 18200
    assert result.details[0].transport == "무궁화호"
    assert result.details[0].distance == "100m"
    assert result.details[0].transferTimeText == "2시간 40분"


def test_get_transportation_segments_recommends_car_without_api_key(monkeypatch) -> None:
    def fake_get_route_detail(route_id: str):
        return {
            "route_id": route_id,
            "title": "테스트 동선",
            "created_at": "2026-06-04T00:00:00",
            "places": [
                {"visit_order": 1, "name": "출발지", "lat": 37.0, "lng": 127.0},
                {"visit_order": 2, "name": "도착지", "lat": 37.1, "lng": 127.1},
            ],
        }

    monkeypatch.setattr(odsay_service.settings, "odsay_api_key", None)
    monkeypatch.setattr(route_service, "get_route_detail", fake_get_route_detail)

    result = odsay_service.get_transportation_segments("route-id")

    assert result is not None
    assert result.available is False
    assert result.title == "🚗 자차 추천"
    assert result.details[0].transport == "자차"


def test_get_transportation_segments_can_use_recommendation_route_id(monkeypatch) -> None:
    monkeypatch.setattr(odsay_service.settings, "odsay_api_key", None)
    monkeypatch.setattr(route_service, "get_route_detail", lambda route_id: None)

    result = odsay_service.get_transportation_segments(
        "route-danyang-healing-half_day-walk-friends"
    )

    assert result is not None
    assert result.firstStart == "도담삼봉"
    assert result.details[0].start == "도담삼봉"
    assert result.details[0].arrival == "단양구경시장"


def test_route_transportation_endpoint_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(routes_endpoint, "get_transportation_segments", lambda route_id: None)

    response = client.get("/api/v1/routes/unknown-route/transportation")

    assert response.status_code == 404
