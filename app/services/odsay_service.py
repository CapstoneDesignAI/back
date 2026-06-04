from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.schemas.routes import RouteTransportationDetail, RouteTransportationResponse
from app.services import route_service


@dataclass
class TransportationLeg:
    available: bool
    total_minutes: int
    transfer_count: int
    detail: RouteTransportationDetail


def get_transportation_segments(route_id: str) -> RouteTransportationResponse | None:
    route = route_service.get_route_detail(route_id)
    if not route:
        return None

    places = sorted(route["places"], key=lambda place: place["visit_order"])
    if len(places) < 2:
        place_name = places[0]["name"] if places else ""
        return RouteTransportationResponse(
            available=False,
            title="🚗 자차 추천",
            totalTimeText="",
            summaryText="이동 구간 없음",
            firstStart=place_name,
            lastArrival=place_name,
            details=[],
        )

    legs = []
    for start_place, arrival_place in zip(places, places[1:]):
        legs.append(_build_leg(start_place, arrival_place))

    available = any(leg.available for leg in legs)
    total_minutes = sum(leg.total_minutes for leg in legs)
    transfer_count = sum(leg.transfer_count for leg in legs)
    details = [leg.detail for leg in legs]

    return RouteTransportationResponse(
        available=available,
        title="🚌 대중교통 가능" if available else "🚗 자차 추천",
        totalTimeText=_format_minutes(total_minutes) if total_minutes else "",
        summaryText=(
            f"총 {_format_minutes(total_minutes)}분 · 환승 {transfer_count}회"
            if available
            else "대중교통 경로 없음 · 자차 이동 추천"
        ),
        firstStart=details[0].start,
        lastArrival=details[-1].arrival,
        details=details,
    )


def _build_leg(start_place: dict, arrival_place: dict) -> TransportationLeg:
    if not settings.odsay_api_key:
        return _car_recommendation_leg(
            start_place=start_place,
            arrival_place=arrival_place,
            detail_text="ODsay API 키가 설정되지 않아 자차 이동을 추천합니다.",
        )

    try:
        odsay_data = _request_public_transport_route(start_place, arrival_place)
    except Exception as exc:
        print(f"❌ ODsay 대중교통 조회 중 에러 발생: {exc}")
        return _car_recommendation_leg(
            start_place=start_place,
            arrival_place=arrival_place,
            detail_text="대중교통 조회에 실패해 자차 이동을 추천합니다.",
        )

    path = _select_recommended_path(odsay_data)
    if not path:
        return _car_recommendation_leg(
            start_place=start_place,
            arrival_place=arrival_place,
            detail_text="대중교통 경로가 없어 자차 이동을 추천합니다.",
        )

    info = path.get("info") or {}
    sub_paths = path.get("subPath") or []
    total_time = _to_int(info.get("totalTime"))
    transfer_count = _calculate_transfer_count(info)
    payment = _to_int(info.get("payment"))
    transport = _extract_main_transport(sub_paths)
    distance_meters = _to_int(info.get("totalDistance"))
    first_start = info.get("firstStartStation") or start_place["name"]
    last_arrival = info.get("lastEndStation") or arrival_place["name"]

    return TransportationLeg(
        available=True,
        total_minutes=total_time,
        transfer_count=transfer_count,
        detail=RouteTransportationDetail(
            start=first_start,
            arrival=last_arrival,
            transferTimeText=_format_minutes(total_time),
            transferCount=transfer_count,
            payment=payment,
            transport=transport,
            distance=_format_distance(distance_meters),
            detailText=f"{last_arrival} 도착 후 택시 또는 도보 이동 추천",
        ),
    )


def _request_public_transport_route(start_place: dict, arrival_place: dict) -> dict:
    response = httpx.get(
        f"{settings.odsay_api_base_url.rstrip('/')}/searchPubTransPathT",
        params={
            "SX": start_place["lng"],
            "SY": start_place["lat"],
            "EX": arrival_place["lng"],
            "EY": arrival_place["lat"],
            "apiKey": settings.odsay_api_key,
            "output": "json",
            "lang": 0,
            "OPT": 0,
        },
        timeout=8.0,
    )
    response.raise_for_status()
    return response.json()


def _select_recommended_path(odsay_data: dict) -> dict | None:
    result = odsay_data.get("result") or {}
    paths = result.get("path") or []
    if not paths:
        return None

    return min(
        paths,
        key=lambda path: _to_int((path.get("info") or {}).get("totalTime")),
    )


def _calculate_transfer_count(info: dict) -> int:
    return _to_int(info.get("busTransitCount")) + _to_int(info.get("subwayTransitCount"))


def _extract_main_transport(sub_paths: list[dict]) -> str:
    for sub_path in sub_paths:
        traffic_type = _to_int(sub_path.get("trafficType"))
        if traffic_type == 1:
            lanes = sub_path.get("lane") or []
            if lanes:
                return lanes[0].get("name") or "지하철"
            return "지하철"
        if traffic_type == 2:
            lanes = sub_path.get("lane") or []
            if lanes:
                return lanes[0].get("busNo") or lanes[0].get("name") or "버스"
            return "버스"
    return "대중교통"


def _car_recommendation_leg(
    start_place: dict,
    arrival_place: dict,
    detail_text: str,
) -> TransportationLeg:
    return TransportationLeg(
        available=False,
        total_minutes=0,
        transfer_count=0,
        detail=RouteTransportationDetail(
            start=start_place["name"],
            arrival=arrival_place["name"],
            transferTimeText="",
            transferCount=0,
            payment=0,
            transport="자차",
            distance="",
            detailText=detail_text,
        ),
    )


def _format_minutes(minutes: int) -> str:
    if minutes <= 0:
        return "0분"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours and remaining_minutes:
        return f"{hours}시간 {remaining_minutes}분"
    if hours:
        return f"{hours}시간"
    return f"{remaining_minutes}분"


def _format_distance(distance_meters: int) -> str:
    if distance_meters >= 1000:
        return f"{distance_meters / 1000:.1f}km"
    if distance_meters > 0:
        return f"{distance_meters}m"
    return ""


def _to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
