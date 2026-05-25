from fastapi import APIRouter, Depends, status
from app.schemas.recommendations import AIRecommendationRequest, AIRecommendationResponse
from app.core.jwt import get_current_user  

router = APIRouter()

@router.post(
    "/ai-recommendations",
    response_model=AIRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="AI 맞춤 동선 추천 (Mock API)",
)
async def get_ai_recommendation(
    request_data: AIRecommendationRequest,
    # current_user_id: str = Depends(get_current_user)
):
    current_user_id = "임시_테스트_유저_ID"
    print(f"🔒 인증에 성공한 유저 UUID: {current_user_id}")
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
                "name": f"{region_text} 감성 스팟 A",
                "address": f"{region_text} 중심가 123",
                "description": f"{companion_text}과 함께 {atmosphere_text} 분위기를 만끽하며, {transport_text}(으)로 부담 없이 방문하기 좋은 첫 번째 장소입니다."
            },
            {
                "visit_order": 2,
                "name": f"{region_text} 로컬 맛집 B",
                "address": f"{region_text} 맛집 거리 456",
                "description": f"{purpose_text}에 딱 어울리는 스팟으로, {activity_text} 여행을 선호하는 분들에게 강력히 추천하는 코스입니다."
            }
        ]
    }
    
    return mock_response