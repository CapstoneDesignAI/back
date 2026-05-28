from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.data.danyang_places import PlaceCandidate, list_danyang_mvp_places
from app.schemas.recommendations import (
    OptionItem,
    PlaceItem,
    PlaceListResponse,
    RecommendedPlace,
    RecommendationOptionsResponse,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationSavePayload,
    RecommendationSummary,
    RegionGroupItem,
    RegionItem,
    RegionListResponse,
    RouteRecommendationPlace,
    RouteMapMarker,
    SelectionModeItem,
    SelectionOptionsResponse,
    TodayRecommendationCard,
    TodayRecommendationResponse,
)
from app.services.recommendation_scoring import (
    RecommendationPlan,
    ScoredPlace,
    build_recommendation_plan,
)
from app.services.recommendation_reasoning import (
    build_ai_reason_text,
    generate_ai_reason_detail,
)


REGIONS = [
    RegionItem(
        id="region-danyang",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="단양군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-okcheon",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="옥천군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-goesan",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="괴산군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-yeongdong",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="영동군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-boeun",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="보은군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-jecheon",
        area_group="chungcheong",
        sido="충청북도",
        sigungu="제천시",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-buyeo",
        area_group="chungcheong",
        sido="충청남도",
        sigungu="부여군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-seocheon",
        area_group="chungcheong",
        sido="충청남도",
        sigungu="서천군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-cheongyang",
        area_group="chungcheong",
        sido="충청남도",
        sigungu="청양군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-taean",
        area_group="chungcheong",
        sido="충청남도",
        sigungu="태안군",
        is_population_decline=True,
    ),
]

OPTIONS = RecommendationOptionsResponse(
    area_groups=[
        OptionItem(code="gangwon", label="강원권"),
        OptionItem(code="chungcheong", label="충청권"),
        OptionItem(code="jeolla", label="전라권"),
        OptionItem(code="gyeongsang", label="경상권"),
        OptionItem(code="near_capital", label="수도권 근교"),
    ],
    themes=[
        OptionItem(code="healing", label="힐링"),
        OptionItem(code="food", label="맛집"),
        OptionItem(code="walk", label="뚜벅이"),
        OptionItem(code="nature", label="자연투어"),
        OptionItem(code="local_market", label="로컬시장"),
        OptionItem(code="revitalization", label="지역활성화 추천"),
    ],
    travel_times=[
        OptionItem(code="3hours", label="3시간"),
        OptionItem(code="half_day", label="반나절"),
        OptionItem(code="full_day", label="하루"),
        OptionItem(code="overnight", label="1박 2일"),
    ],
    transports=[
        OptionItem(code="walk", label="뚜벅이"),
        OptionItem(code="car", label="자차"),
        OptionItem(code="public_transport", label="대중교통"),
    ],
    companions=[
        OptionItem(code="solo", label="혼자"),
        OptionItem(code="friends", label="친구"),
        OptionItem(code="family", label="가족"),
        OptionItem(code="couple", label="연인"),
    ],
)

REGION_SELECTION_MODES = [
    SelectionModeItem(
        code="direct",
        label="지역을 직접 선택할래요",
        description="권역과 인구감소지역을 직접 고르는 방식입니다.",
    ),
    SelectionModeItem(
        code="ai_recommendation",
        label="AI가 지역부터 추천해줬으면 좋겠어요",
        description="테마와 조건을 바탕으로 어울리는 지역을 먼저 추천받는 방식입니다.",
    ),
]


def list_regions(area_group: str | None = None) -> RegionListResponse:
    regions = REGIONS
    if area_group:
        regions = [region for region in REGIONS if region.area_group == area_group]
    return RegionListResponse(regions=regions)


def list_places(region_id: str | None = None) -> PlaceListResponse:
    places = list_danyang_mvp_places()
    if region_id:
        places = tuple(place for place in places if place.region_id == region_id)
    return PlaceListResponse(places=[_to_place_item(place) for place in places])


def get_recommendation_options() -> RecommendationOptionsResponse:
    return OPTIONS


def get_selection_options() -> SelectionOptionsResponse:
    return SelectionOptionsResponse(
        region_selection_modes=REGION_SELECTION_MODES,
        area_groups=OPTIONS.area_groups,
        regions_by_area_group=_group_regions_by_area_group(),
        themes=OPTIONS.themes,
        travel_times=OPTIONS.travel_times,
        transports=OPTIONS.transports,
        companions=OPTIONS.companions,
    )


def get_today_recommendation(
    reference_date: date | None = None,
) -> TodayRecommendationResponse:
    request = RecommendationRequest(
        region_id="region-danyang",
        theme="healing",
        travel_time="half_day",
        transport="car",
        companion="friends",
    )
    recommendation = create_recommendation(request)
    today = reference_date or datetime.now(ZoneInfo("Asia/Seoul")).date()

    return TodayRecommendationResponse(
        today_date=today.isoformat(),
        card=_to_today_card(recommendation),
        recommendation=recommendation,
    )


def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    region = _resolve_region(request)
    theme_label = _get_option_label(OPTIONS.themes, request.theme)
    travel_time_label = _get_option_label(OPTIONS.travel_times, request.travel_time)
    transport_label = _get_option_label(OPTIONS.transports, request.transport)
    companion_label = _get_option_label(OPTIONS.companions, request.companion)
    plan = build_recommendation_plan(
        request=request,
        candidates=list_danyang_mvp_places(),
    )
    places = [
        _to_recommended_place(order=index + 1, scored_place=scored_place)
        for index, scored_place in enumerate(plan.places)
    ]
    summary = _build_summary(plan)
    ai_reason_detail = generate_ai_reason_detail(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    ai_reason = build_ai_reason_text(ai_reason_detail)

    return RecommendationResponse(
        recommendation_id=(
            f"sample-{region.id.removeprefix('region-')}-{request.theme}-{request.travel_time}"
        ),
        title=f"{region.sigungu.replace('군', '')} {theme_label} 로컬 코스",
        subtitle=f"{region.sido} {region.sigungu}에서 즐기는 {travel_time_label} 여행",
        region=region,
        theme=request.theme,
        theme_label=theme_label,
        travel_time=request.travel_time,
        travel_time_label=travel_time_label,
        transport=request.transport,
        transport_label=transport_label,
        companion=request.companion,
        companion_label=companion_label,
        contribution_score=plan.contribution_score,
        estimated_duration_minutes=plan.estimated_duration_minutes,
        estimated_cost_min=plan.estimated_cost_min,
        estimated_cost_max=plan.estimated_cost_max,
        local_consumption_count=plan.local_consumption_count,
        place_count=len(places),
        total_stay_minutes=sum(place.stay_minutes for place in places),
        route_badges=_build_route_badges(plan, theme_label),
        summary=summary,
        ai_reason=ai_reason,
        ai_reason_detail=ai_reason_detail,
        places=places,
        map_markers=[_to_map_marker(place) for place in places],
        legacy_route_payload=_to_legacy_route_payload(
            title=f"{region.sigungu.replace('군', '')} {theme_label} 로컬 코스",
            summary=summary,
            places=places,
        ),
    )


def _to_place_item(place: PlaceCandidate) -> PlaceItem:
    return PlaceItem(
        place_id=place.place_id,
        region_id=place.region_id,
        name=place.name,
        category=place.category,
        address=place.address,
        lat=place.lat,
        lng=place.lng,
        stay_minutes=place.stay_minutes,
        estimated_cost_min=place.estimated_cost_min,
        estimated_cost_max=place.estimated_cost_max,
        local_contribution_score=place.local_contribution_score,
        theme_tags=list(place.theme_tags),
        transport_tags=list(place.transport_tags),
        companion_tags=list(place.companion_tags),
        is_local_consumption=place.is_local_consumption,
        reason=place.reason,
        contribution_reason=place.contribution_reason,
        image_url=place.image_url,
        source=place.source,
    )


def _to_recommended_place(
    order: int,
    scored_place: ScoredPlace,
) -> RouteRecommendationPlace:
    place = scored_place.place
    return RouteRecommendationPlace(
        order=order,
        visit_order=order,
        place_id=place.place_id,
        name=place.name,
        category=place.category,
        address=place.address,
        lat=place.lat,
        lng=place.lng,
        stay_minutes=place.stay_minutes,
        reason=place.reason,
        contribution_reason=place.contribution_reason,
        image_url=place.image_url,
        estimated_cost_min=place.estimated_cost_min,
        estimated_cost_max=place.estimated_cost_max,
        local_contribution_score=place.local_contribution_score,
        theme_tags=list(place.theme_tags),
        tags=list(place.theme_tags),
        is_local_consumption=place.is_local_consumption,
        recommendation_score=scored_place.score,
        score_reasons=list(scored_place.score_reasons),
        source=place.source,
    )


def _build_summary(plan: RecommendationPlan) -> RecommendationSummary:
    return RecommendationSummary(
        contribution_label=f"지역 기여도 {plan.contribution_score}점",
        duration_text=_format_duration(plan.estimated_duration_minutes),
        cost_range_text=f"{plan.estimated_cost_min:,}원~{plan.estimated_cost_max:,}원",
        local_consumption_text=f"로컬 소비 장소 {plan.local_consumption_count}곳 포함",
    )


def _build_route_badges(plan: RecommendationPlan, theme_label: str) -> list[str]:
    badges = [theme_label, f"지역 기여도 {plan.contribution_score}점"]
    if plan.local_consumption_count:
        badges.append(f"로컬 소비 {plan.local_consumption_count}곳")
    if plan.estimated_duration_minutes <= 180:
        badges.append("짧은 코스")
    elif plan.estimated_duration_minutes <= 360:
        badges.append("반나절 코스")
    else:
        badges.append("여유 코스")
    return badges


def _to_legacy_route_payload(
    title: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> RecommendationSavePayload:
    return RecommendationSavePayload(
        title=title,
        estimated_time=f"총 예상 소요 시간: {summary.duration_text}",
        places=[
            RecommendedPlace(
                visit_order=place.visit_order,
                place_id=place.place_id,
                name=place.name,
                address=place.address,
                lat=place.lat,
                lng=place.lng,
                image_url=place.image_url or "",
                description=place.reason,
                tags=place.tags,
                category=place.category,
            )
            for place in places
        ],
    )


def _to_map_marker(place: RouteRecommendationPlace) -> RouteMapMarker:
    return RouteMapMarker(
        order=place.order,
        place_id=place.place_id,
        name=place.name,
        category=place.category,
        lat=place.lat,
        lng=place.lng,
    )


def _to_today_card(
    recommendation: RecommendationResponse,
) -> TodayRecommendationCard:
    region_label = f"{recommendation.region.sido} {recommendation.region.sigungu}"
    return TodayRecommendationCard(
        recommendation_id=recommendation.recommendation_id,
        title=recommendation.title,
        subtitle=recommendation.subtitle,
        region_label=region_label,
        theme_label=recommendation.theme_label,
        contribution_score=recommendation.contribution_score,
        estimated_duration_text=recommendation.summary.duration_text,
        estimated_cost_text=recommendation.summary.cost_range_text,
        local_consumption_text=recommendation.summary.local_consumption_text,
        primary_badges=recommendation.route_badges[:3],
        place_preview_names=[place.name for place in recommendation.places[:3]],
    )


def _resolve_region(request: RecommendationRequest) -> RegionItem:
    if request.region_id:
        for region in REGIONS:
            if region.id == request.region_id:
                return region

    if request.area_group:
        for region in REGIONS:
            if region.area_group == request.area_group:
                return region

    return REGIONS[0]


def _group_regions_by_area_group() -> list[RegionGroupItem]:
    grouped_regions: list[RegionGroupItem] = []
    for area_group in OPTIONS.area_groups:
        regions = [region for region in REGIONS if region.area_group == area_group.code]
        grouped_regions.append(
            RegionGroupItem(
                area_group=area_group,
                regions=regions,
            )
        )
    return grouped_regions


def _get_option_label(options: list[OptionItem], code: str) -> str:
    for option in options:
        if option.code == code:
            return option.label
    return code


def _format_duration(minutes: int) -> str:
    hours, remaining_minutes = divmod(minutes, 60)
    if hours and remaining_minutes:
        return f"{hours}시간 {remaining_minutes}분"
    if hours:
        return f"{hours}시간"
    return f"{remaining_minutes}분"

