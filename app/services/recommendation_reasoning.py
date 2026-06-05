from dataclasses import dataclass

from app.schemas.recommendations import (
    AIReasonDetail,
    RecommendationSummary,
    RegionItem,
    RouteRecommendationPlace,
)


@dataclass(frozen=True)
class RecommendationReasonResult:
    text: str
    detail: AIReasonDetail


def build_recommendation_reason(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> RecommendationReasonResult:
    return build_rule_based_recommendation_reason(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )


def build_rule_based_recommendation_reason(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> RecommendationReasonResult:
    reason_detail = generate_ai_reason_detail(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    return RecommendationReasonResult(
        text=build_ai_reason_text(reason_detail),
        detail=reason_detail,
    )


def generate_ai_reason_detail(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> AIReasonDetail:
    local_places = [place for place in places if place.is_local_consumption]
    nature_places = [
        place
        for place in places
        if "자연투어" in place.tags or place.category in {"자연", "액티비티"}
    ]
    rest_places = [
        place
        for place in places
        if place.category in {"카페", "로컬시장"} or place.is_local_consumption
    ]

    representative_names = _join_names(nature_places[:2] or places[:2])
    local_names = _join_names(local_places)
    rest_names = _join_names(rest_places[:2])

    overview = (
        f"{region.sigungu}에서 {theme_label} 여행을 원하는 사용자에게 맞춰 "
        f"{representative_names} 중심의 지역 경험을 먼저 배치했습니다."
    )
    route_design = (
        f"동선은 {places[0].name}에서 시작해 {places[-1].name}까지 이어지며, "
        f"{transport_label} 조건과 {summary.duration_text} 안에 들어오도록 구성했습니다."
    )
    local_contribution = (
        f"{local_names}처럼 실제 소비가 일어나는 장소를 포함해 "
        f"{summary.local_consumption_text}이라는 목표를 반영했습니다."
        if local_places
        else "대표 방문지를 중심으로 지역 체류 시간을 늘릴 수 있게 구성했습니다."
    )
    traveler_fit = (
        f"{companion_label} 여행에서도 이동 피로가 커지지 않도록 "
        f"{rest_names}에서 쉬어갈 수 있는 흐름을 만들었습니다."
        if rest_places
        else f"{companion_label} 여행에 맞춰 장소 수와 체류시간을 과하지 않게 조정했습니다."
    )
    closing_tip = (
        f"{summary.cost_range_text} 정도의 소비를 예상할 수 있고, "
        f"{summary.contribution_label}으로 지역 상권 기여도가 높은 코스입니다."
    )

    return AIReasonDetail(
        overview=overview,
        route_design=route_design,
        local_contribution=local_contribution,
        traveler_fit=traveler_fit,
        closing_tip=closing_tip,
        highlights=[
            f"{theme_label} 테마 적합",
            summary.contribution_label,
            summary.local_consumption_text,
        ],
        generation_source="rule_based_ai_ready",
    )


def build_ai_reason_text(reason_detail: AIReasonDetail) -> str:
    return " ".join(
        [
            reason_detail.overview,
            reason_detail.route_design,
            reason_detail.local_contribution,
            reason_detail.traveler_fit,
        ]
    )


def _join_names(places: list[RouteRecommendationPlace]) -> str:
    names = [place.name for place in places]
    if not names:
        return "지역 장소"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f", {names[-1]}"

