from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceCandidate:
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
    theme_tags: tuple[str, ...]
    transport_tags: tuple[str, ...]
    companion_tags: tuple[str, ...]
    is_local_consumption: bool
    reason: str
    contribution_reason: str
    image_url: str | None = None
    source: str = "sample"


DANYANG_REGION_ID = "region-danyang"

DANYANG_MVP_PLACES: tuple[PlaceCandidate, ...] = (
    PlaceCandidate(
        place_id="sample-dodamsambong",
        region_id=DANYANG_REGION_ID,
        name="도담삼봉",
        category="자연",
        address="충청북도 단양군 매포읍 삼봉로 644",
        lat=36.984539,
        lng=128.369267,
        stay_minutes=50,
        estimated_cost_min=0,
        estimated_cost_max=5000,
        local_contribution_score=68,
        theme_tags=("healing", "nature", "walk", "revitalization"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=False,
        reason="단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
        contribution_reason="지역의 첫 방문 만족도를 높여 이후 로컬 상권 방문으로 이어지게 합니다.",
    ),
    PlaceCandidate(
        place_id="sample-danyang-market",
        region_id=DANYANG_REGION_ID,
        name="단양구경시장",
        category="로컬시장",
        address="충청북도 단양군 단양읍 도전5길 31",
        lat=36.984784,
        lng=128.365889,
        stay_minutes=70,
        estimated_cost_min=15000,
        estimated_cost_max=25000,
        local_contribution_score=95,
        theme_tags=("food", "local_market", "walk", "revitalization"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=True,
        reason="지역 먹거리와 소상공인 매장을 함께 경험할 수 있는 장소입니다.",
        contribution_reason="식사와 간식 소비가 지역 상권 매출로 직접 연결됩니다.",
    ),
    PlaceCandidate(
        place_id="sample-cafe-sann",
        region_id=DANYANG_REGION_ID,
        name="카페산",
        category="카페",
        address="충청북도 단양군 가곡면 두산길 196-86",
        lat=37.024255,
        lng=128.395729,
        stay_minutes=60,
        estimated_cost_min=10000,
        estimated_cost_max=15000,
        local_contribution_score=82,
        theme_tags=("healing", "nature", "food", "revitalization"),
        transport_tags=("car",),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=True,
        reason="전망과 휴식을 함께 제공해 여행 피로도를 낮추는 중간 지점입니다.",
        contribution_reason="카페 체류를 통해 지역 내 머무는 시간을 늘립니다.",
    ),
    PlaceCandidate(
        place_id="sample-mancheonha",
        region_id=DANYANG_REGION_ID,
        name="만천하스카이워크",
        category="액티비티",
        address="충청북도 단양군 적성면 옷바위길 10",
        lat=36.966326,
        lng=128.343638,
        stay_minutes=80,
        estimated_cost_min=10000,
        estimated_cost_max=10000,
        local_contribution_score=74,
        theme_tags=("nature", "healing", "revitalization"),
        transport_tags=("car", "public_transport"),
        companion_tags=("friends", "family", "couple"),
        is_local_consumption=False,
        reason="전망, 사진, 액티비티 요소를 갖춘 마무리 관광지입니다.",
        contribution_reason="유료 관광지 방문과 주변 소비 가능성을 함께 높입니다.",
    ),
)


def list_danyang_mvp_places() -> tuple[PlaceCandidate, ...]:
    return DANYANG_MVP_PLACES

