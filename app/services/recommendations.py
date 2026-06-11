from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.geo import calculate_distance_in_meters
from app.data.danyang_places import PlaceCandidate, list_danyang_mvp_places
from app.schemas.recommendations import (
    ContributionInfo,
    LocalConsumptionPoint,
    MobilityInfo,
    OptionItem,
    PlaceItem,
    PlaceListResponse,
    RecommendedPlace,
    RecommendationOptionsResponse,
    RecommendationCard,
    RecommendationDetailResponse,
    RecommendationPlacePreview,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationSavePayload,
    RecommendationSummary,
    RegionGroupItem,
    RegionItem,
    RegionListResponse,
    RegionStory,
    RouteRecommendationPlace,
    RouteLeg,
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
    build_recommendation_reason,
)
from app.services.place_repository import fetch_place_candidates_from_supabase
from app.services.tour_api import fetch_tour_api_places, fetch_tour_photo_image_url


REGIONS = [
    # 충청권 (Chungcheong)
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
    # 강원권 (Gangwon)
    RegionItem(
        id="region-pyeongchang",
        area_group="gangwon",
        sido="강원특별자치도",
        sigungu="평창군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-yangyang",
        area_group="gangwon",
        sido="강원특별자치도",
        sigungu="양양군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-yeongwol",
        area_group="gangwon",
        sido="강원특별자치도",
        sigungu="영월군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-gangwon-goseong",
        area_group="gangwon",
        sido="강원특별자치도",
        sigungu="고성군",
        is_population_decline=True,
    ),
    # 전라권 (Jeolla)
    RegionItem(
        id="region-muju",
        area_group="jeolla",
        sido="전북특별자치도",
        sigungu="무주군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-damyang",
        area_group="jeolla",
        sido="전라남도",
        sigungu="담양군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-sinan",
        area_group="jeolla",
        sido="전라남도",
        sigungu="신안군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-wando",
        area_group="jeolla",
        sido="전라남도",
        sigungu="완도군",
        is_population_decline=True,
    ),
    # 경상권 (Gyeongsang)
    RegionItem(
        id="region-andong",
        area_group="gyeongsang",
        sido="경상북도",
        sigungu="안동시",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-namhae",
        area_group="gyeongsang",
        sido="경상남도",
        sigungu="남해군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-hadong",
        area_group="gyeongsang",
        sido="경상남도",
        sigungu="하동군",
        is_population_decline=True,
    ),
    # 수도권 근교 (Near Capital)
    RegionItem(
        id="region-gapyeong",
        area_group="near_capital",
        sido="경기도",
        sigungu="가평군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-ganghwa",
        area_group="near_capital",
        sido="인천광역시",
        sigungu="강화군",
        is_population_decline=True,
    ),
    RegionItem(
        id="region-ongjin",
        area_group="near_capital",
        sido="인천광역시",
        sigungu="옹진군",
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

TAG_LABELS = {
    "healing": "힐링",
    "food": "맛집",
    "walk": "뚜벅이",
    "nature": "자연투어",
    "local_market": "로컬시장",
    "revitalization": "지역활성화 추천",
    "3hours": "3시간",
    "half_day": "반나절",
    "full_day": "하루",
    "overnight": "1박 2일",
    "car": "자차",
    "public_transport": "대중교통",
    "solo": "혼자",
    "friends": "친구",
    "family": "가족",
    "couple": "연인",
}

DEFAULT_REGION_IMAGE_URLS = {
    "region-danyang": "https://tong.visitkorea.or.kr/cms/resource_photo/69/3414769_image2_1.jpg",
}


def list_regions(area_group: str | None = None) -> RegionListResponse:
    regions = REGIONS
    if area_group:
        regions = [region for region in REGIONS if region.area_group == area_group]
    return RegionListResponse(regions=regions)


def list_places(
    region_id: str | None = None,
    source: str = "sample",
    theme: str | None = None,
    limit: int = 20,
) -> PlaceListResponse:
    region = _resolve_region_by_id(region_id) if region_id else REGIONS[0]
    places = _get_candidate_places(region=region, source=source, theme=theme, limit=limit)
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
    today = reference_date or _today_in_korea()
    
    # 날짜를 기반으로 지역을 순환 선택 (단양 외 다른 지역도 노출되도록)
    region_index = today.day % len(REGIONS)
    selected_region = REGIONS[region_index]

    request = RecommendationRequest(
        region_id=selected_region.id,
        theme="healing",
        travel_time="half_day",
        transport="car",
        companion="friends",
    )
    recommendation = create_recommendation(request)

    # 데이터가 없어 장소가 비어있다면, 안전하게 단양(샘플 데이터 있음)으로 폴백
    if not recommendation.places and selected_region.id != "region-danyang":
        request.region_id = "region-danyang"
        recommendation = create_recommendation(request)

    return TodayRecommendationResponse(
        today_date=today.isoformat(),
        section_title="오늘의 추천 여행",
        recommendation_id=recommendation.recommendation_id,
        route_id=recommendation.route_id,
        detail_api_path=f"/api/v1/ai-recommendations/{recommendation.route_id}",
        save_api_path="/api/v1/routes/from-recommendation",
        card=_to_today_card(recommendation),
        recommendation=_to_detail_response(recommendation),
    )


def _today_in_korea() -> date:
    try:
        korea_timezone = ZoneInfo("Asia/Seoul")
    except ZoneInfoNotFoundError:
        korea_timezone = timezone(timedelta(hours=9))
    return datetime.now(korea_timezone).date()


def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    region = _resolve_region(request)
    theme_label = _get_option_label(OPTIONS.themes, request.theme)
    travel_time_label = _get_option_label(OPTIONS.travel_times, request.travel_time)
    transport_label = _get_option_label(OPTIONS.transports, request.transport)
    companion_label = _get_option_label(OPTIONS.companions, request.companion)
    candidate_places = _get_candidate_places(
        region=region,
        source=request.data_source,
        theme=request.theme,
    )
    plan = build_recommendation_plan(
        request=request,
        candidates=candidate_places,
    )
    places = [
        _to_recommended_place(order=index + 1, scored_place=scored_place)
        for index, scored_place in enumerate(plan.places)
    ]
    _apply_image_fallbacks(region=region, places=places)
    route_legs = _build_route_legs(places)
    total_distance_meters = sum(leg.distance_meters for leg in route_legs)
    mobility = _build_mobility_info(
        transport=request.transport,
        transport_label=transport_label,
        total_distance_meters=total_distance_meters,
        route_legs=route_legs,
    )
    contribution_info = _build_contribution_info(plan=plan, places=places)
    local_consumption_points = _build_local_consumption_points(places)
    region_story = _build_region_story(
        region=region,
        theme_label=theme_label,
        places=places,
    )
    summary = _build_summary(plan)
    reason_result = build_recommendation_reason(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    ai_reason = reason_result.text
    ai_reason_detail = reason_result.detail
    recommendation_id = _build_recommendation_id(
        region=region,
        theme=request.theme,
        travel_time=request.travel_time,
    )
    route_id = _build_route_id(
        region=region,
        theme=request.theme,
        travel_time=request.travel_time,
        transport=request.transport,
        companion=request.companion,
    )
    title = f"{region.sigungu.replace('군', '')} {theme_label} 로컬 코스"
    card = _build_recommendation_card(
        recommendation_id=recommendation_id,
        route_id=route_id,
        title=title,
        subtitle=f"{region.sido} {region.sigungu}에서 즐기는 {travel_time_label} 여행",
        region=region,
        theme_label=theme_label,
        region_story=region_story,
        travel_time_label=travel_time_label,
        transport_label=transport_label,
        mobility=mobility,
        contribution_info=contribution_info,
        local_consumption_points=local_consumption_points,
        plan=plan,
        summary=summary,
        ai_reason=ai_reason,
        places=places,
    )

    return RecommendationResponse(
        recommendation_id=recommendation_id,
        route_id=route_id,
        title=title,
        subtitle=card.subtitle,
        region=region,
        sido=region.sido,
        sigungu=region.sigungu,
        region_story=region_story,
        theme=request.theme,
        theme_label=theme_label,
        travel_time=request.travel_time,
        travel_time_label=travel_time_label,
        transport=request.transport,
        transport_label=transport_label,
        companion=request.companion,
        companion_label=companion_label,
        contribution_score=plan.contribution_score,
        contribution_info=contribution_info,
        estimated_duration_minutes=plan.estimated_duration_minutes,
        estimated_cost_min=plan.estimated_cost_min,
        estimated_cost_max=plan.estimated_cost_max,
        local_consumption_count=plan.local_consumption_count,
        local_consumption_points=local_consumption_points,
        place_count=len(places),
        total_stay_minutes=sum(place.stay_minutes for place in places),
        total_distance_meters=total_distance_meters,
        total_distance_km=_to_distance_km(total_distance_meters),
        total_distance_text=_format_distance(total_distance_meters),
        mobility=mobility,
        route_badges=_build_route_badges(plan, theme_label),
        summary=summary,
        card=card,
        ai_reason=ai_reason,
        ai_reason_detail=ai_reason_detail,
        places=places,
        route_legs=route_legs,
        legacy_route_payload=_to_legacy_route_payload(
            title=title,
            summary=summary,
            places=places,
        ),
        source=_resolve_response_source(candidate_places),
    )


def get_recommendation_detail(route_id: str) -> RecommendationResponse | None:
    request = _parse_route_id(route_id)
    if request is None:
        return None
    return create_recommendation(request)


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
        tags=_to_tag_labels(place.theme_tags),
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
        place_story=_build_place_story(place),
        local_tip=_build_place_local_tip(place),
        image_url=place.image_url,
        estimated_cost_min=place.estimated_cost_min,
        estimated_cost_max=place.estimated_cost_max,
        local_contribution_score=place.local_contribution_score,
        tags=_to_tag_labels(place.theme_tags),
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


def _build_route_legs(places: list[RouteRecommendationPlace]) -> list[RouteLeg]:
    route_legs: list[RouteLeg] = []
    if not places:
        return route_legs

    places[0].distance_from_previous_meters = None
    places[0].distance_from_previous_km = None
    places[0].distance_from_previous_text = None

    for index in range(1, len(places)):
        previous_place = places[index - 1]
        current_place = places[index]
        distance_meters = round(
            calculate_distance_in_meters(
                previous_place.lat,
                previous_place.lng,
                current_place.lat,
                current_place.lng,
            )
        )
        distance_km = _to_distance_km(distance_meters)
        distance_text = _format_distance(distance_meters)

        current_place.distance_from_previous_meters = distance_meters
        current_place.distance_from_previous_km = distance_km
        current_place.distance_from_previous_text = distance_text
        route_legs.append(
            RouteLeg(
                order=index,
                from_place_id=previous_place.place_id,
                from_name=previous_place.name,
                to_place_id=current_place.place_id,
                to_name=current_place.name,
                distance_meters=distance_meters,
                distance_km=distance_km,
                distance_text=distance_text,
            )
        )

    return route_legs


def _build_mobility_info(
    *,
    transport: str,
    transport_label: str,
    total_distance_meters: int,
    route_legs: list[RouteLeg],
) -> MobilityInfo:
    max_leg_distance = max((leg.distance_meters for leg in route_legs), default=0)

    if transport == "walk":
        if total_distance_meters <= 2500 and max_leg_distance <= 1200:
            level = "low"
            label = "이동 난이도 낮음"
            summary = "주요 장소 간 거리가 짧아 뚜벅이 이동으로도 부담이 적은 코스입니다."
        elif total_distance_meters <= 6000 and max_leg_distance <= 3000:
            level = "medium"
            label = "이동 난이도 보통"
            summary = "일부 구간 이동 거리가 있어 도보와 짧은 대중교통 이동을 함께 고려하면 좋습니다."
        else:
            level = "high"
            label = "이동 난이도 높음"
            summary = "장소 사이 거리가 길어 전체 코스를 도보로만 이동하기에는 부담이 큰 코스입니다."
    elif transport == "public_transport":
        if max_leg_distance <= 1500:
            level = "low"
            label = "이동 난이도 낮음"
            summary = "장소 간 이동 거리가 짧아 대중교통과 짧은 도보를 함께 쓰기 좋은 코스입니다."
        elif max_leg_distance <= 5000:
            level = "medium"
            label = "이동 난이도 보통"
            summary = "대중교통 이용은 가능하지만 일부 구간은 환승이나 도보 이동을 고려해야 합니다."
        else:
            level = "high"
            label = "이동 난이도 높음"
            summary = "장소 간 거리가 길어 대중교통만으로는 이동 부담이 있을 수 있습니다."
    else:
        if total_distance_meters <= 12000:
            level = "low"
            label = "이동 난이도 낮음"
            summary = "자차 기준으로 장소 간 이동 부담이 크지 않은 코스입니다."
        elif total_distance_meters <= 30000:
            level = "medium"
            label = "이동 난이도 보통"
            summary = "자차 이동을 전제로 하면 무리 없이 소화할 수 있는 거리의 코스입니다."
        else:
            level = "high"
            label = "이동 난이도 높음"
            summary = "자차 기준으로도 이동 거리가 긴 편이라 여유 있는 일정이 필요합니다."

    return MobilityInfo(
        level=level,
        label=label,
        summary=summary,
        recommended_transport=transport_label,
    )


def _build_contribution_info(
    *,
    plan: RecommendationPlan,
    places: list[RouteRecommendationPlace],
) -> ContributionInfo:
    if places:
        average_place_score = round(
            sum(place.local_contribution_score for place in places) / len(places)
        )
    else:
        average_place_score = 0
    local_consumption_bonus = min(plan.local_consumption_count * 3, 10)

    return ContributionInfo(
        score=plan.contribution_score,
        label=f"지역 기여도 {plan.contribution_score}점",
        description=(
            "지역 기여도는 공식 공공 지표가 아니라 Tripick MVP 내부 점수입니다. "
            "코스에 포함된 장소들의 지역 기여도 평균에 로컬 소비 장소 보너스를 더해 계산합니다."
        ),
        formula="장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점(최대 10점)",
        average_place_score=average_place_score,
        local_consumption_bonus=local_consumption_bonus,
        local_consumption_count=plan.local_consumption_count,
        place_count=len(places),
        is_official_metric=False,
    )


def _build_local_consumption_points(
    places: list[RouteRecommendationPlace],
) -> list[LocalConsumptionPoint]:
    return [
        LocalConsumptionPoint(
            order=place.order,
            place_id=place.place_id,
            name=place.name,
            category=place.category,
            summary=place.reason,
            contribution_reason=place.contribution_reason,
            estimated_cost_min=place.estimated_cost_min,
            estimated_cost_max=place.estimated_cost_max,
            estimated_cost_text=(
                f"{place.estimated_cost_min:,}원~{place.estimated_cost_max:,}원"
            ),
            lat=place.lat,
            lng=place.lng,
        )
        for place in places
        if place.is_local_consumption
    ]


def _build_region_story(
    *,
    region: RegionItem,
    theme_label: str,
    places: list[RouteRecommendationPlace],
) -> RegionStory:
    if region.id == "region-danyang":
        return RegionStory(
            title="단양 로컬 여행 이야기",
            summary=(
                "단양은 남한강을 따라 이어지는 자연 경관과 전통시장, 전망 명소가 "
                "가까이 연결된 충북의 대표 체류형 여행지입니다."
            ),
            history=(
                "단양은 삼봉 정도전의 이야기가 남아 있는 도담삼봉과 석문, "
                "남한강 물길을 중심으로 형성된 산수 관광 자원이 잘 알려진 지역입니다."
            ),
            local_story=(
                f"{theme_label} 코스에서는 {places[0].name if places else '대표 명소'}에서 "
                "지역의 첫인상을 만들고, 시장과 로컬 카페를 함께 배치해 방문이 지역 소비로 "
                "이어지도록 구성했습니다."
            ),
            local_tip=(
                "전망 명소 방문 전후로 단양구경시장이나 로컬 카페를 함께 들르면 "
                "짧은 일정에서도 지역 상권 체류 효과를 만들 수 있습니다."
            ),
            source="mvp_sample",
        )

    return RegionStory(
        title=f"{region.sigungu} 로컬 여행 이야기",
        summary=f"{region.sigungu}의 대표 장소와 로컬 소비 지점을 함께 엮은 여행 코스입니다.",
        history=f"{region.sigungu}의 지역 자원과 생활권을 함께 경험할 수 있도록 구성했습니다.",
        local_story=(
            f"{theme_label} 테마에 맞는 장소와 지역 소비 장소를 함께 추천해 "
            "여행 만족도와 지역 기여를 동시에 고려했습니다."
        ),
        local_tip="대표 관광지와 로컬 상권을 같은 동선 안에서 함께 방문해보세요.",
        source="mvp_sample",
    )


def _build_place_story(place: PlaceCandidate) -> str:
    return f"{place.name}은 {place.reason}"


def _build_place_local_tip(place: PlaceCandidate) -> str:
    if place.is_local_consumption:
        return "이 장소에서는 식사, 카페, 간식 등 실제 지역 상권 소비로 이어질 수 있습니다."
    if place.estimated_cost_min > 0:
        return "유료 체험이나 입장 후 주변 로컬 상권을 함께 방문하면 지역 체류 효과가 커집니다."
    return "방문 전후 가까운 전통시장이나 로컬 매장을 함께 둘러보면 더 좋은 동선이 됩니다."


def _build_recommendation_card(
    *,
    recommendation_id: str,
    route_id: str,
    title: str,
    subtitle: str,
    region: RegionItem,
    theme_label: str,
    region_story: RegionStory,
    travel_time_label: str,
    transport_label: str,
    mobility: MobilityInfo,
    contribution_info: ContributionInfo,
    local_consumption_points: list[LocalConsumptionPoint],
    plan: RecommendationPlan,
    summary: RecommendationSummary,
    ai_reason: str,
    places: list[RouteRecommendationPlace],
) -> RecommendationCard:
    preview_places = places[:3]
    route_preview_text = _build_route_preview_text(preview_places)
    thumbnail_url = _resolve_route_thumbnail(region=region, places=places)
    return RecommendationCard(
        recommendation_id=recommendation_id,
        route_id=route_id,
        title=title,
        subtitle=subtitle,
        summary=_build_card_summary(region=region, places=places),
        sido=region.sido,
        sigungu=region.sigungu,
        region_label=f"{region.sido} {region.sigungu}",
        theme_label=theme_label,
        region_story=region_story,
        thumbnail_url=thumbnail_url,
        contribution_score=plan.contribution_score,
        contribution_info=contribution_info,
        estimated_duration_text=summary.duration_text,
        estimated_cost_text=summary.cost_range_text,
        local_consumption_text=summary.local_consumption_text,
        local_consumption_points=local_consumption_points,
        mobility=mobility,
        tags=_build_card_tags(
            theme_label=theme_label,
            travel_time_label=travel_time_label,
            transport_label=transport_label,
        ),
        metric_badges=_build_metric_badges(
            plan=plan,
            place_count=len(places),
        ),
        place_count=len(places),
        place_count_text=f"장소 {len(places)}곳",
        place_preview_names=[place.name for place in preview_places],
        place_preview=[
            RecommendationPlacePreview(
                order=place.order,
                place_id=place.place_id,
                name=place.name,
                category=place.category,
                summary=place.reason,
                tags=place.tags[:2],
                image_url=_resolve_place_image_url(
                    place=place,
                    region=region,
                ),
                lat=place.lat,
                lng=place.lng,
                is_local_consumption=place.is_local_consumption,
            )
            for place in preview_places
        ],
        route_preview_text=route_preview_text,
        ai_reason_summary=ai_reason[:80],
    )


def _apply_image_fallbacks(
    *,
    region: RegionItem,
    places: list[RouteRecommendationPlace],
) -> None:
    keyword_image_cache: dict[str, str | None] = {}
    for place in places:
        place.image_url = _resolve_place_image_url(
            place=place,
            region=region,
            keyword_image_cache=keyword_image_cache,
        )


def _resolve_route_thumbnail(
    *,
    region: RegionItem,
    places: list[RouteRecommendationPlace],
) -> str | None:
    return next(
        (place.image_url for place in places if place.image_url),
        DEFAULT_REGION_IMAGE_URLS.get(region.id),
    )


def _resolve_place_image_url(
    *,
    place: RouteRecommendationPlace,
    region: RegionItem,
    keyword_image_cache: dict[str, str | None] | None = None,
) -> str | None:
    return (
        place.image_url
        or _resolve_keyword_place_image_url(
            place=place,
            region=region,
            keyword_image_cache=keyword_image_cache,
        )
        or DEFAULT_REGION_IMAGE_URLS.get(region.id)
    )


def _resolve_keyword_place_image_url(
    *,
    place: RouteRecommendationPlace,
    region: RegionItem,
    keyword_image_cache: dict[str, str | None] | None = None,
) -> str | None:
    keywords = (place.name, f"{region.sigungu} {place.name}")
    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
        if keyword_image_cache is not None and keyword in keyword_image_cache:
            image_url = keyword_image_cache[keyword]
        else:
            image_url = fetch_tour_photo_image_url(keyword)
            if keyword_image_cache is not None:
                keyword_image_cache[keyword] = image_url
        if image_url:
            return image_url
    return None


def _to_today_card(
    recommendation: RecommendationResponse,
) -> TodayRecommendationCard:
    return TodayRecommendationCard.model_validate(recommendation.card.model_dump())


def _to_detail_response(
    recommendation: RecommendationResponse,
) -> RecommendationDetailResponse:
    return RecommendationDetailResponse.model_validate(
        recommendation.model_dump(exclude={"card"})
    )


def _build_recommendation_id(
    *,
    region: RegionItem,
    theme: str,
    travel_time: str,
) -> str:
    region_slug = region.id.removeprefix("region-")
    return f"sample-{region_slug}-{theme}-{travel_time}"


def _build_route_id(
    *,
    region: RegionItem,
    theme: str,
    travel_time: str,
    transport: str,
    companion: str,
) -> str:
    region_slug = region.id.removeprefix("region-")
    return f"route-{region_slug}-{theme}-{travel_time}-{transport}-{companion}"


def _parse_route_id(route_id: str) -> RecommendationRequest | None:
    parts = route_id.split("-")
    if len(parts) not in {4, 6} or parts[0] != "route":
        return None

    region_id = f"region-{parts[1]}"
    if _resolve_region_by_id(region_id).id != region_id:
        return None

    theme = parts[2]
    travel_time = parts[3]
    transport = parts[4] if len(parts) == 6 else "walk"
    companion = parts[5] if len(parts) == 6 else "friends"

    valid_themes = {option.code for option in OPTIONS.themes}
    valid_travel_times = {option.code for option in OPTIONS.travel_times}
    valid_transports = {option.code for option in OPTIONS.transports}
    valid_companions = {option.code for option in OPTIONS.companions}
    if (
        theme not in valid_themes
        or travel_time not in valid_travel_times
        or transport not in valid_transports
        or companion not in valid_companions
    ):
        return None

    return RecommendationRequest(
        region_id=region_id,
        theme=theme,
        travel_time=travel_time,
        transport=transport,
        companion=companion,
    )


def _build_card_tags(
    *,
    theme_label: str,
    travel_time_label: str,
    transport_label: str,
) -> list[str]:
    return [theme_label, travel_time_label, transport_label]


def _to_tag_labels(tag_codes: tuple[str, ...] | list[str]) -> list[str]:
    return [TAG_LABELS.get(tag_code, tag_code) for tag_code in tag_codes]


def _build_metric_badges(
    *,
    plan: RecommendationPlan,
    place_count: int,
) -> list[str]:
    return [
        f"지역 기여도 {plan.contribution_score}점",
        f"로컬 소비 {plan.local_consumption_count}곳",
        f"장소 {place_count}곳",
    ]


def _build_card_summary(
    *,
    region: RegionItem,
    places: list[RouteRecommendationPlace],
) -> str:
    if len(places) >= 2:
        return f"{places[0].name}부터 {places[-1].name}까지 이어지는 로컬 동선"
    if places:
        return f"{region.sigungu}의 {places[0].name}을 중심으로 즐기는 로컬 동선"
    return f"{region.sigungu}에서 즐기는 로컬 동선"


def _build_route_preview_text(places: list[RouteRecommendationPlace]) -> str:
    if not places:
        return "추천 장소 준비 중"
    return " → ".join(place.name for place in places)


def _get_candidate_places(
    region: RegionItem,
    source: str = "sample",
    theme: str | None = None,
    limit: int = 20,
) -> tuple[PlaceCandidate, ...]:
    if source in {"supabase", "db", "auto"}:
        try:
            supabase_places = fetch_place_candidates_from_supabase(
                region=region,
                theme=theme,
                limit=max(limit, 100),
            )
        except Exception:
            supabase_places = ()
        if supabase_places:
            return supabase_places

    if source in {"tour_api", "auto"}:
        try:
            tour_api_places = fetch_tour_api_places(
                region=region,
                theme=theme,
                num_of_rows=limit,
            )
        except Exception:
            tour_api_places = ()
        if tour_api_places:
            return tour_api_places

    # 단양인 경우에만 샘플 데이터 제공, 그 외 지역은 빈 결과 반환 (Tour API 연동 활성화됨)
    if region.id == "region-danyang":
        return list_danyang_mvp_places()
    
    return ()


def _resolve_response_source(places: tuple[PlaceCandidate, ...]) -> str:
    if not places:
        return "sample"
    place_sources = {place.source for place in places}
    if place_sources == {"tour_api"}:
        return "tour_api"
    if place_sources == {"sample"}:
        return "sample"
    if place_sources == {"manual"}:
        return "supabase"
    if "tour_api" in place_sources:
        return "supabase"
    return "sample"


def _resolve_region_by_id(region_id: str | None) -> RegionItem:
    if region_id:
        for region in REGIONS:
            if region.id == region_id:
                return region
    return REGIONS[0]


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


def _to_distance_km(distance_meters: int) -> float:
    return round(distance_meters / 1000, 1)


def _format_distance(distance_meters: int) -> str:
    if distance_meters < 1000:
        return f"{distance_meters}m"
    return f"{_to_distance_km(distance_meters):.1f}km"
