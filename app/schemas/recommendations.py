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
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    image_url: str
    description: str
    tags: list[str] = []
    category: str

class AIRecommendationResponse(BaseModel):
    title: str
    estimated_time: str
    places: list[RecommendedPlace]


class RegionItem(BaseModel):
    id: str
    area_group: str
    sido: str
    sigungu: str
    is_population_decline: bool


class RegionListResponse(BaseModel):
    regions: list[RegionItem]


class OptionItem(BaseModel):
    code: str
    label: str


class SelectionModeItem(BaseModel):
    code: str
    label: str
    description: str


class RegionGroupItem(BaseModel):
    area_group: OptionItem
    regions: list[RegionItem]


class RecommendationOptionsResponse(BaseModel):
    area_groups: list[OptionItem]
    themes: list[OptionItem]
    travel_times: list[OptionItem]
    transports: list[OptionItem]
    companions: list[OptionItem]


class SelectionOptionsResponse(RecommendationOptionsResponse):
    region_selection_modes: list[SelectionModeItem]
    regions_by_area_group: list[RegionGroupItem]


class RecommendationRequest(BaseModel):
    region_id: str | None = None
    area_group: str | None = None
    theme: str = Field(..., examples=["healing"])
    travel_time: str = Field(..., examples=["half_day"])
    transport: str = Field(..., examples=["walk"])
    companion: str = Field(..., examples=["friends"])
    prefer_ai_region: bool = False


class PlaceItem(BaseModel):
    place_id: str
    region_id: str
    name: str
    category: str
    address: str
    lat: float
    lng: float
    stay_minutes: int
    estimated_cost_min: int
    estimated_cost_max: int
    local_contribution_score: int
    theme_tags: list[str]
    transport_tags: list[str]
    companion_tags: list[str]
    is_local_consumption: bool
    reason: str
    contribution_reason: str
    image_url: str | None = None
    source: str


class PlaceListResponse(BaseModel):
    places: list[PlaceItem]


class RouteRecommendationPlace(BaseModel):
    order: int
    place_id: str
    name: str
    category: str
    address: str
    lat: float
    lng: float
    stay_minutes: int
    reason: str
    contribution_reason: str
    image_url: str | None = None
    estimated_cost_min: int
    estimated_cost_max: int
    local_contribution_score: int
    theme_tags: list[str]
    is_local_consumption: bool
    recommendation_score: int
    score_reasons: list[str]
    source: str


class RecommendationResponse(BaseModel):
    recommendation_id: str
    title: str
    region: RegionItem
    theme: str
    travel_time: str
    transport: str
    companion: str
    contribution_score: int
    estimated_duration_minutes: int
    estimated_cost_min: int
    estimated_cost_max: int
    local_consumption_count: int
    ai_reason: str
    places: list[RouteRecommendationPlace]
    is_saved: bool = False
