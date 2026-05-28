from fastapi import APIRouter, Depends, Query, status
from app.schemas.recommendations import (
    AIRecommendationRequest,
    AIRecommendationResponse,
    PlaceListResponse,
    RecommendationOptionsResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegionListResponse,
    SelectionOptionsResponse,
    TodayRecommendationResponse,
)
from app.core.jwt import get_current_user  
from app.services.recommendations import (
    create_recommendation,
    get_recommendation_options,
    get_selection_options,
    get_today_recommendation,
    list_places,
    list_regions,
)

router = APIRouter()


@router.get("/regions", response_model=RegionListResponse, summary="인구감소지역 목록")
def read_regions(
    area_group: str | None = Query(default=None),
) -> RegionListResponse:
    return list_regions(area_group=area_group)


@router.get("/places", response_model=PlaceListResponse, summary="MVP 장소 데이터 목록")
def read_places(
    region_id: str | None = Query(default=None),
) -> PlaceListResponse:
    return list_places(region_id=region_id)


@router.get(
    "/recommendations/options",
    response_model=RecommendationOptionsResponse,
    summary="추천 필터 선택지",
)
def read_recommendation_options() -> RecommendationOptionsResponse:
    return get_recommendation_options()


@router.get(
    "/recommendations/selection-options",
    response_model=SelectionOptionsResponse,
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
    response_model=AIRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="AI 맞춤 동선 추천 (Mock API)",
)
async def get_ai_recommendation(
    request_data: AIRecommendationRequest,
    current_user_id: str = Depends(get_current_user)
):    
    duration_text = request_data.duration.value
    transport_text = request_data.transportation.value
    purpose_text = request_data.travel_purpose.value
    companion_text = request_data.companion.value
    atmosphere_text = request_data.atmosphere.value if request_data.atmosphere else "기본적인"
    activity_text = request_data.activity_style.value if request_data.activity_style else "유연한"
    region_text = request_data.region if request_data.region else "선택 안 함"
    
    print(f"🤖 [AI 프롬프트 준비 완료] 지역: {region_text} | 동반자: {companion_text} | 목적: {purpose_text}")

    mock_response = {
        "title": f"[{region_text}] {companion_text}과 함께 떠나는 {purpose_text} 추천 코스",
        "estimated_time": f"총 예상 소요 시간: {duration_text}",
        "places": [
            {
                "visit_order": 1,
                "place_id": "place_jeonju_01",
                "name": f"{region_text} 감성 스팟 A",
                "address": f"{region_text} 중심가 123",
                "lat": 35.8149,
                "lng": 127.1494,
                "image_url": "https://images.unsplash.com/photo-1599812170327-02ba40989d2c",
                "description": f"{companion_text}과 함께 {atmosphere_text} 분위기를 만끽하며, {transport_text}(으)로 부담 없이 방문하기 좋은 첫 번째 장소입니다.",
                "tags": [atmosphere_text, "감성"],
                "category": "관광명소"
            },
            {
                "visit_order": 2,
                "place_id": "place_jeonju_01",
                "name": f"{region_text} 로컬 맛집 B",
                "address": f"{region_text} 맛집 거리 456",
                "lat": 35.8135,
                "lng": 127.152,
                "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24",
                "description": f"{purpose_text}에 딱 어울리는 스팟으로, {activity_text} 여행을 선호하는 분들에게 강력히 추천하는 코스입니다.",
                "tags": ["맛집", "로컬느낌"],
                "category": "식당"
            }
        ]
    }
    
    return mock_response
