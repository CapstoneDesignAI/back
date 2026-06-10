from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.recommendations import (
    AIRecommendationRequest,
    PlaceListResponse,
    RecommendationCard,
    RecommendationDetailResponse,
    RecommendationOptionsResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegionListResponse,
    SelectionOptionsResponse,
    TodayRecommendationResponse,
)
from app.services.recommendations import (
    create_recommendation,
    get_recommendation_detail,
    get_recommendation_options,
    get_selection_options,
    get_today_recommendation,
    list_places,
    list_regions,
)

router = APIRouter()

AI_DURATION_MAP = {
    "3시간": "3hours",
    "1~2시간": "3hours",
    "반나절": "half_day",
    "하루": "full_day",
    "1박2일": "overnight",
    "2박3일": "overnight",
    "기타": "half_day",
}

AI_TRANSPORT_MAP = {
    "도보": "walk",
    "뚜벅이": "walk",
    "자차": "car",
    "대중교통": "public_transport",
    "자전거": "walk",
}

AI_PURPOSE_MAP = {
    "힐링": "healing",
    "맛집": "food",
    "데이트": "healing",
    "인스타감성": "healing",
    "자연/풍경": "nature",
    "자연투어": "nature",
    "현지경험": "local_market",
    "로컬시장": "local_market",
    "역사/문화": "revitalization",
    "지역활성화 추천": "revitalization",
}

AI_COMPANION_MAP = {
    "혼자": "solo",
    "친구": "friends",
    "연인": "couple",
    "가족": "family",
    "부모님": "family",
    "아이와 함께": "family",
    "반려동물과 함께": "friends",
    "동아리/단체": "friends",
}

AI_REGION_MAP = {
    "단양": "region-danyang",
    "단양군": "region-danyang",
    "충청북도 단양군": "region-danyang",
    "옥천": "region-okcheon",
    "옥천군": "region-okcheon",
    "괴산": "region-goesan",
    "괴산군": "region-goesan",
    "영동": "region-yeongdong",
    "영동군": "region-yeongdong",
    "보은": "region-boeun",
    "보은군": "region-boeun",
    "제천": "region-jecheon",
    "제천시": "region-jecheon",
    "부여": "region-buyeo",
    "부여군": "region-buyeo",
    "서천": "region-seocheon",
    "서천군": "region-seocheon",
    "청양": "region-cheongyang",
    "청양군": "region-cheongyang",
    "태안": "region-taean",
    "태안군": "region-taean",
}


@router.get("/regions", response_model=RegionListResponse, summary="인구감소지역 목록")
def read_regions(
    area_group: str | None = Query(default=None),
) -> RegionListResponse:
    return list_regions(area_group=area_group)


@router.get(
    "/places",
    response_model=PlaceListResponse,
    summary="후보 장소 데이터 확인용 목록",
    description=(
        "추천 API가 사용하는 후보 장소 데이터를 확인하는 보조 API입니다. "
        "프론트 추천 카드/상세 화면은 ai-recommendations 응답의 장소 정보를 사용하므로 "
        "일반 사용자 플로우에서 필수로 호출할 필요는 없습니다."
    ),
)
def read_places(
    region_id: str | None = Query(default=None),
    source: str = Query(default="sample", pattern="^(sample|supabase|db|tour_api|auto)$"),
    theme: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> PlaceListResponse:
    return list_places(region_id=region_id, source=source, theme=theme, limit=limit)


@router.get(
    "/recommendations/options",
    response_model=RecommendationOptionsResponse,
    description="프론트 핵심 플로우에서 직접 호출하지 않는 내부 확인용/후순위 API입니다.",
    include_in_schema=False,
    summary="추천 필터 선택지",
)
def read_recommendation_options() -> RecommendationOptionsResponse:
    return get_recommendation_options()


@router.get(
    "/recommendations/selection-options",
    response_model=SelectionOptionsResponse,
    description="프론트에서 선택지 문구를 직접 반영하기로 하여 Swagger 핵심 명세에서는 숨깁니다.",
    include_in_schema=False,
    summary="내 여행 찾기 화면 선택지",
)
def read_selection_options() -> SelectionOptionsResponse:
    return get_selection_options()


@router.get(
    "/recommendations/today",
    response_model=TodayRecommendationResponse,
    summary="오늘의 추천",
)
def read_today_recommendation() -> TodayRecommendationResponse:
    return get_today_recommendation()


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="점수 기반 동선 추천",
)
def recommend_route(request: RecommendationRequest) -> RecommendationResponse:
    return create_recommendation(request)

@router.post(
    "/ai-recommendations",
    response_model=RecommendationCard,
    status_code=status.HTTP_200_OK,
    summary="AI 맞춤 동선 추천 카드",
)
async def get_ai_recommendation(request_data: AIRecommendationRequest) -> RecommendationCard:
    recommendation = create_recommendation(_to_recommendation_request(request_data))
    return recommendation.card


@router.get(
    "/ai-recommendations/{route_id}",
    response_model=RecommendationDetailResponse,
    summary="AI 추천 동선 상세 조회",
)
def read_ai_recommendation_detail(route_id: str) -> RecommendationDetailResponse:
    recommendation = get_recommendation_detail(route_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="추천 동선을 찾을 수 없습니다.")
    return recommendation

@router.get(
    "/ai-recommendations/{route_id}",
    response_model=RecommendationDetailResponse,
    summary="AI 추천 동선 상세 조회",
)
def read_ai_recommendation_detail(route_id: str) -> RecommendationDetailResponse:
    recommendation = get_recommendation_detail(route_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="추천 동선을 찾을 수 없습니다.")
    return recommendation


def _to_recommendation_request(request_data: AIRecommendationRequest) -> RecommendationRequest:
    region_text = (request_data.region or "").strip()
    return RecommendationRequest(
        region_id=AI_REGION_MAP.get(region_text, "region-danyang"),
        theme=AI_PURPOSE_MAP.get(request_data.travel_purpose.value, "healing"),
        travel_time=AI_DURATION_MAP.get(request_data.duration.value, "half_day"),
        transport=AI_TRANSPORT_MAP.get(request_data.transportation.value, "walk"),
        companion=AI_COMPANION_MAP.get(request_data.companion.value, "friends"),
        prefer_ai_region=not bool(region_text),
        data_source="auto",
    )
