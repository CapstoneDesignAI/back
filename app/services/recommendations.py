from app.data.danyang_places import PlaceCandidate, list_danyang_mvp_places
from app.schemas.recommendations import (
    OptionItem,
    PlaceItem,
    PlaceListResponse,
    RecommendationOptionsResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegionGroupItem,
    RegionItem,
    RegionListResponse,
    RouteRecommendationPlace,
    SelectionModeItem,
    SelectionOptionsResponse,
)
from app.services.recommendation_scoring import ScoredPlace, build_recommendation_plan


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


def get_today_recommendation() -> RecommendationResponse:
    request = RecommendationRequest(
        region_id="region-danyang",
        theme="healing",
        travel_time="half_day",
        transport="car",
        companion="friends",
    )
    return create_recommendation(request)


def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    region = _resolve_region(request)
    plan = build_recommendation_plan(
        request=request,
        candidates=list_danyang_mvp_places(),
    )
    places = [
        _to_recommended_place(order=index + 1, scored_place=scored_place)
        for index, scored_place in enumerate(plan.places)
    ]

    return RecommendationResponse(
        recommendation_id=(
            f"sample-{region.id.removeprefix('region-')}-{request.theme}-{request.travel_time}"
        ),
        title=f"{region.sigungu.replace('군', '')} {_get_option_label(OPTIONS.themes, request.theme)} 로컬 코스",
        region=region,
        theme=request.theme,
        travel_time=request.travel_time,
        transport=request.transport,
        companion=request.companion,
        contribution_score=plan.contribution_score,
        estimated_duration_minutes=plan.estimated_duration_minutes,
        estimated_cost_min=plan.estimated_cost_min,
        estimated_cost_max=plan.estimated_cost_max,
        local_consumption_count=plan.local_consumption_count,
        ai_reason=(
            f"이 코스는 {region.sigungu}의 장소를 "
            f"{_get_option_label(OPTIONS.themes, request.theme)} 테마와 "
            f"{_get_option_label(OPTIONS.transports, request.transport)} 이동수단에 맞춰 "
            "점수화한 뒤 구성했습니다. 지역 기여도가 높은 장소와 로컬 소비 장소를 "
            "함께 포함해 여행 만족도와 지역 상권 기여를 동시에 높이도록 설계했습니다."
        ),
        places=places,
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
        is_local_consumption=place.is_local_consumption,
        recommendation_score=scored_place.score,
        score_reasons=list(scored_place.score_reasons),
        source=place.source,
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

