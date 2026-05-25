from enum import Enum
from pydantic import BaseModel, Field

# 선택지 정의
class DurationType(str, Enum):
    SHORT = "1~2시간"
    HALF_DAY = "반나절"
    ONE_DAY = "하루"
    TWO_DAYS = "1박2일"
    THREE_DAYS = "2박3일"
    ETC = "기타"

class TransportType(str, Enum):
    PUBLIC = "대중교통"
    CAR = "자차"
    WALK = "도보"
    BIKE = "자전거"

class PurposeType(str, Enum):
    HEALING = "힐링"
    DATE = "데이트"
    TRENDY = "인스타감성"
    NATURE = "자연/풍경"
    LOCAL = "현지경험"
    HISTORIC = "역사/문화"

class CompanionType(str, Enum):
    ALONE = "혼자"
    FRIENDS = "친구"
    COUPLE = "연인"
    FAMILY = "가족"
    PARENTS = "부모님"
    WITH_KIDS = "아이와 함께"
    WITH_PET = "반려동물과 함께"
    GROUP = "동아리/단체"

class AtmosphereType(str, Enum):
    QUIET = "조용한"
    EMOTIONAL = "감성적인"
    LIVELY = "활기찬"
    LOCAL_VIBE = "로컬 느낌"
    HIP = "힙한 분위기"

class ActivityStyle(str, Enum):
    DYNAMIC = "액티비티/활동적"
    STATIC = "정적/잔잔함"

class AIRecommendationRequest(BaseModel):
    duration: DurationType = Field(..., description="여행 소요 시간")
    transportation: TransportType = Field(..., description="이동 수단")
    travel_purpose: PurposeType = Field(..., description="여행 목적")
    companion: CompanionType = Field(..., description="여행 동반자")
    atmosphere: AtmosphereType | None = Field(None, description="선호 분위기")
    activity_style: ActivityStyle | None = Field(None, description="활동 스타일")
    region: str | None = Field(None, description="여행 목적지")

class RecommendedPlace(BaseModel):
    visit_order: int
    name: str
    address: str
    description: str

class AIRecommendationResponse(BaseModel):
    title: str
    estimated_time: str
    places: list[RecommendedPlace]