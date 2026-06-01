from enum import Enum
from pydantic import BaseModel, Field, field_validator

# 선택지 정의
class DurationType(str, Enum):
    THREE_HOURS = "3시간"
    SHORT = "1~2시간"
    HALF_DAY = "반나절"
    ONE_DAY = "하루"
    TWO_DAYS = "1박2일"
    THREE_DAYS = "2박3일"
    ETC = "기타"

class TransportType(str, Enum):
    PUBLIC = "대중교통"
    CAR = "자차"
    WALKER = "뚜벅이"
    WALK = "도보"
    BIKE = "자전거"

class PurposeType(str, Enum):
    HEALING = "힐링"
    FOOD = "맛집"
    DATE = "데이트"
    TRENDY = "인스타감성"
    NATURE = "자연/풍경"
    NATURE_TOUR = "자연투어"
    LOCAL = "현지경험"
    LOCAL_MARKET = "로컬시장"
    HISTORIC = "역사/문화"
    REVITALIZATION = "지역활성화 추천"

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


REGION_ID_ALIASES = {
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

AREA_GROUP_ALIASES = {
    "강원권": "gangwon",
    "충청권": "chungcheong",
    "전라권": "jeolla",
    "경상권": "gyeongsang",
    "수도권 근교": "near_capital",
}

THEME_ALIASES = {
    "힐링": "healing",
    "맛집": "food",
    "뚜벅이": "walk",
    "도보": "walk",
    "자연투어": "nature",
    "자연/풍경": "nature",
    "로컬시장": "local_market",
    "현지경험": "local_market",
    "역사/문화": "revitalization",
    "지역활성화 추천": "revitalization",
}

TRAVEL_TIME_ALIASES = {
    "3시간": "3hours",
    "1~2시간": "3hours",
    "반나절": "half_day",
    "하루": "full_day",
    "1박2일": "overnight",
    "1박 2일": "overnight",
    "2박3일": "overnight",
    "기타": "half_day",
}

TRANSPORT_ALIASES = {
    "뚜벅이": "walk",
    "도보": "walk",
    "자차": "car",
    "대중교통": "public_transport",
    "자전거": "walk",
}

COMPANION_ALIASES = {
    "혼자": "solo",
    "친구": "friends",
    "연인": "couple",
    "가족": "family",
    "부모님": "family",
    "아이와 함께": "family",
    "반려동물과 함께": "friends",
    "동아리/단체": "friends",
}

AI_DURATION_ALIASES = {
    "3hours": "3시간",
    "3시간": "3시간",
    "1~2시간": "1~2시간",
    "half_day": "반나절",
    "반나절": "반나절",
    "full_day": "하루",
    "하루": "하루",
    "overnight": "1박2일",
    "1박2일": "1박2일",
    "1박 2일": "1박2일",
    "2박3일": "2박3일",
    "기타": "기타",
}

AI_TRANSPORT_ALIASES = {
    "walk": "뚜벅이",
    "뚜벅이": "뚜벅이",
    "도보": "도보",
    "car": "자차",
    "자차": "자차",
    "public_transport": "대중교통",
    "대중교통": "대중교통",
    "자전거": "자전거",
}

AI_PURPOSE_ALIASES = {
    "healing": "힐링",
    "힐링": "힐링",
    "food": "맛집",
    "맛집": "맛집",
    "데이트": "데이트",
    "인스타감성": "인스타감성",
    "nature": "자연투어",
    "자연투어": "자연투어",
    "자연/풍경": "자연/풍경",
    "local_market": "로컬시장",
    "로컬시장": "로컬시장",
    "현지경험": "현지경험",
    "revitalization": "지역활성화 추천",
    "지역활성화 추천": "지역활성화 추천",
    "역사/문화": "역사/문화",
}

AI_COMPANION_ALIASES = {
    "solo": "혼자",
    "혼자": "혼자",
    "friends": "친구",
    "친구": "친구",
    "couple": "연인",
    "연인": "연인",
    "family": "가족",
    "가족": "가족",
    "부모님": "부모님",
    "아이와 함께": "아이와 함께",
    "반려동물과 함께": "반려동물과 함께",
    "동아리/단체": "동아리/단체",
}


def _normalize_text_alias(value, aliases: dict[str, str]):
    if isinstance(value, str):
        stripped_value = value.strip()
        return aliases.get(stripped_value, stripped_value)
    return value

class AIRecommendationRequest(BaseModel):
    duration: DurationType = Field(..., description="여행 소요 시간")
    transportation: TransportType = Field(..., description="이동 수단")
    travel_purpose: PurposeType = Field(..., description="여행 목적")
    companion: CompanionType = Field(..., description="여행 동반자")
    atmosphere: AtmosphereType | None = Field(None, description="선호 분위기")
    activity_style: ActivityStyle | None = Field(None, description="활동 스타일")
    region: str | None = Field(None, description="여행 목적지")

    @field_validator("duration", mode="before")
    @classmethod
    def normalize_duration(cls, value):
        return _normalize_text_alias(value, AI_DURATION_ALIASES)

    @field_validator("transportation", mode="before")
    @classmethod
    def normalize_transportation(cls, value):
        return _normalize_text_alias(value, AI_TRANSPORT_ALIASES)

    @field_validator("travel_purpose", mode="before")
    @classmethod
    def normalize_travel_purpose(cls, value):
        return _normalize_text_alias(value, AI_PURPOSE_ALIASES)

    @field_validator("companion", mode="before")
    @classmethod
    def normalize_companion(cls, value):
        return _normalize_text_alias(value, AI_COMPANION_ALIASES)

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
    data_source: str = Field(default="sample", examples=["sample", "supabase", "tour_api"])

    @field_validator("region_id", mode="before")
    @classmethod
    def normalize_region_id(cls, value):
        return _normalize_text_alias(value, REGION_ID_ALIASES)

    @field_validator("area_group", mode="before")
    @classmethod
    def normalize_area_group(cls, value):
        return _normalize_text_alias(value, AREA_GROUP_ALIASES)

    @field_validator("theme", mode="before")
    @classmethod
    def normalize_theme(cls, value):
        return _normalize_text_alias(value, THEME_ALIASES)

    @field_validator("travel_time", mode="before")
    @classmethod
    def normalize_travel_time(cls, value):
        return _normalize_text_alias(value, TRAVEL_TIME_ALIASES)

    @field_validator("transport", mode="before")
    @classmethod
    def normalize_transport(cls, value):
        return _normalize_text_alias(value, TRANSPORT_ALIASES)

    @field_validator("companion", mode="before")
    @classmethod
    def normalize_recommendation_companion(cls, value):
        return _normalize_text_alias(value, COMPANION_ALIASES)


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
    tags: list[str]
    is_local_consumption: bool
    reason: str
    contribution_reason: str
    image_url: str | None = None
    source: str


class PlaceListResponse(BaseModel):
    places: list[PlaceItem]


class RouteRecommendationPlace(BaseModel):
    order: int
    visit_order: int
    place_id: str
    name: str
    category: str
    address: str
    lat: float
    lng: float
    stay_minutes: int
    reason: str
    contribution_reason: str
    place_story: str
    local_tip: str
    image_url: str | None = None
    estimated_cost_min: int
    estimated_cost_max: int
    local_contribution_score: int
    tags: list[str]
    distance_from_previous_meters: int | None = None
    distance_from_previous_km: float | None = None
    distance_from_previous_text: str | None = None
    is_local_consumption: bool
    recommendation_score: int
    score_reasons: list[str]
    source: str


class RecommendationSummary(BaseModel):
    contribution_label: str
    duration_text: str
    cost_range_text: str
    local_consumption_text: str


class RouteLeg(BaseModel):
    order: int
    from_place_id: str
    from_name: str
    to_place_id: str
    to_name: str
    distance_meters: int
    distance_km: float
    distance_text: str


class MobilityInfo(BaseModel):
    level: str
    label: str
    summary: str
    recommended_transport: str


class ContributionInfo(BaseModel):
    score: int
    label: str
    description: str
    formula: str
    average_place_score: int
    local_consumption_bonus: int
    local_consumption_count: int
    place_count: int
    is_official_metric: bool


class LocalConsumptionPoint(BaseModel):
    order: int
    place_id: str
    name: str
    category: str
    summary: str
    contribution_reason: str
    estimated_cost_min: int
    estimated_cost_max: int
    estimated_cost_text: str
    lat: float
    lng: float


class RecommendationSavePayload(BaseModel):
    title: str
    estimated_time: str
    places: list[RecommendedPlace]


class AIReasonDetail(BaseModel):
    overview: str
    route_design: str
    local_contribution: str
    traveler_fit: str
    closing_tip: str
    highlights: list[str]
    generation_source: str


class RecommendationPlacePreview(BaseModel):
    order: int
    place_id: str
    name: str
    category: str
    summary: str
    tags: list[str]
    image_url: str | None = None
    lat: float
    lng: float
    is_local_consumption: bool


class RecommendationCard(BaseModel):
    recommendation_id: str
    route_id: str
    title: str
    subtitle: str
    summary: str
    sido: str
    sigungu: str
    region_label: str
    theme_label: str
    region_story: RegionStory
    thumbnail_url: str | None = None
    contribution_score: int
    contribution_info: ContributionInfo
    estimated_duration_text: str
    estimated_cost_text: str
    local_consumption_text: str
    primary_badges: list[str]
    metric_badges: list[str]
    place_count: int
    place_count_text: str
    place_preview_names: list[str]
    place_preview: list[RecommendationPlacePreview]
    route_preview_text: str
    ai_reason_summary: str


class TodayRecommendationCard(RecommendationCard):
    pass


class RecommendationResponse(BaseModel):
    recommendation_id: str
    route_id: str
    title: str
    subtitle: str
    region: RegionItem
    sido: str
    sigungu: str
    region_story: RegionStory
    theme: str
    theme_label: str
    travel_time: str
    travel_time_label: str
    transport: str
    transport_label: str
    companion: str
    companion_label: str
    contribution_score: int
    contribution_info: ContributionInfo
    estimated_duration_minutes: int
    estimated_cost_min: int
    estimated_cost_max: int
    local_consumption_count: int
    local_consumption_points: list[LocalConsumptionPoint]
    place_count: int
    total_stay_minutes: int
    total_distance_meters: int
    total_distance_km: float
    total_distance_text: str
    mobility: MobilityInfo
    route_badges: list[str]
    summary: RecommendationSummary
    card: RecommendationCard
    ai_reason: str
    ai_reason_detail: AIReasonDetail
    places: list[RouteRecommendationPlace]
    map_markers: list[RouteMapMarker]
    legacy_route_payload: RecommendationSavePayload
    source: str = "sample"
    is_saved: bool = False


class RecommendationDetailResponse(BaseModel):
    recommendation_id: str
    route_id: str
    title: str
    subtitle: str
    region: RegionItem
    sido: str
    sigungu: str
    region_story: RegionStory
    theme: str
    theme_label: str
    travel_time: str
    travel_time_label: str
    transport: str
    transport_label: str
    companion: str
    companion_label: str
    contribution_score: int
    contribution_info: ContributionInfo
    estimated_duration_minutes: int
    estimated_cost_min: int
    estimated_cost_max: int
    local_consumption_count: int
    local_consumption_points: list[LocalConsumptionPoint]
    place_count: int
    total_stay_minutes: int
    total_distance_meters: int
    total_distance_km: float
    total_distance_text: str
    mobility: MobilityInfo
    route_badges: list[str]
    summary: RecommendationSummary
    ai_reason: str
    ai_reason_detail: AIReasonDetail
    places: list[RouteRecommendationPlace]
    map_markers: list[RouteMapMarker]
    legacy_route_payload: RecommendationSavePayload
    source: str = "sample"
    is_saved: bool = False


class TodayRecommendationResponse(BaseModel):
    today_date: str
    section_title: str
    recommendation_id: str
    route_id: str
    detail_api_path: str
    save_api_path: str
    card: TodayRecommendationCard
    recommendation: RecommendationDetailResponse