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
HWACHEON_REGION_ID = "region-hwacheon"

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

HWACHEON_MVP_PLACES: tuple[PlaceCandidate, ...] = (
    PlaceCandidate(
        place_id="sample-hwacheon-market",
        region_id=HWACHEON_REGION_ID,
        name="화천시장",
        category="로컬시장",
        address="강원특별자치도 화천군 화천읍 중앙로4길 13-10",
        lat=38.1038803150246,
        lng=127.705579051823,
        stay_minutes=60,
        estimated_cost_min=12000,
        estimated_cost_max=25000,
        local_contribution_score=95,
        theme_tags=("food", "local_market", "walk", "revitalization"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=True,
        reason="화천 읍내 상권과 지역 먹거리를 가장 직접적으로 만날 수 있는 장소입니다.",
        contribution_reason="시장 식사와 간식 소비가 지역 소상공인 매출로 이어집니다.",
    ),
    PlaceCandidate(
        place_id="sample-hwacheon-coffee-museum",
        region_id=HWACHEON_REGION_ID,
        name="산천어커피박물관",
        category="박물관",
        address="강원특별자치도 화천군 화천읍 상승로2길 21",
        lat=38.1059776668268,
        lng=127.703765858068,
        stay_minutes=50,
        estimated_cost_min=5000,
        estimated_cost_max=12000,
        local_contribution_score=78,
        theme_tags=("healing", "food", "walk", "revitalization"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=True,
        reason="읍내에서 짧게 쉬며 실내 관람과 커피 테마를 함께 즐기기 좋습니다.",
        contribution_reason="관람과 카페형 소비가 읍내 체류 시간을 늘립니다.",
    ),
    PlaceCandidate(
        place_id="sample-hwacheon-sancheoneo-festival",
        region_id=HWACHEON_REGION_ID,
        name="얼음나라화천 산천어축제",
        category="축제",
        address="강원특별자치도 화천군 화천읍 산천어길 137",
        lat=38.11262462757998,
        lng=127.70988097815085,
        stay_minutes=80,
        estimated_cost_min=10000,
        estimated_cost_max=30000,
        local_contribution_score=88,
        theme_tags=("nature", "local_market", "revitalization"),
        transport_tags=("walk", "car", "public_transport"),
        companion_tags=("friends", "family", "couple"),
        is_local_consumption=True,
        reason="화천을 대표하는 계절형 콘텐츠로 지역 정체성을 강하게 느낄 수 있습니다.",
        contribution_reason="축제 방문은 체험비와 주변 상권 소비로 연결됩니다.",
    ),
    PlaceCandidate(
        place_id="sample-hwacheon-bungeoseom",
        region_id=HWACHEON_REGION_ID,
        name="붕어섬",
        category="자연",
        address="강원특별자치도 화천군 화천읍 하리 165",
        lat=38.096811574777,
        lng=127.693828245676,
        stay_minutes=70,
        estimated_cost_min=0,
        estimated_cost_max=10000,
        local_contribution_score=72,
        theme_tags=("healing", "nature", "walk"),
        transport_tags=("walk", "car"),
        companion_tags=("solo", "friends", "family", "couple"),
        is_local_consumption=False,
        reason="물길과 산책 동선을 함께 즐길 수 있어 화천의 자연 분위기를 느끼기 좋습니다.",
        contribution_reason="읍내 방문 후 자연 관광지로 이동해 지역 내 체류 반경을 넓힙니다.",
    ),
    PlaceCandidate(
        place_id="sample-hwacheon-baegamsan-cablecar",
        region_id=HWACHEON_REGION_ID,
        name="백암산케이블카",
        category="케이블카",
        address="강원특별자치도 화천군 화천읍 백암산로 1285-89",
        lat=38.259463956418884,
        lng=127.74068808037532,
        stay_minutes=90,
        estimated_cost_min=10000,
        estimated_cost_max=20000,
        local_contribution_score=76,
        theme_tags=("nature", "healing", "revitalization"),
        transport_tags=("car",),
        companion_tags=("friends", "family", "couple"),
        is_local_consumption=False,
        reason="DMZ 접경 산악 경관을 높은 시야에서 조망할 수 있는 대표 전망 코스입니다.",
        contribution_reason="유료 관광 콘텐츠 이용과 원거리 이동으로 지역 관광 소비를 넓힙니다.",
    ),
    PlaceCandidate(
        place_id="sample-hwacheon-peace-dam-culture-center",
        region_id=HWACHEON_REGION_ID,
        name="K-water 평화의댐 물문화관",
        category="전시관",
        address="강원특별자치도 화천군 화천읍 동촌리 2922-2",
        lat=38.2139968768316,
        lng=127.846355629331,
        stay_minutes=70,
        estimated_cost_min=0,
        estimated_cost_max=10000,
        local_contribution_score=70,
        theme_tags=("nature", "healing", "revitalization"),
        transport_tags=("car",),
        companion_tags=("friends", "family", "couple"),
        is_local_consumption=False,
        reason="평화의댐 일대 풍경과 접경 지역의 이야기를 함께 이해할 수 있는 장소입니다.",
        contribution_reason="외곽 관광지 방문을 통해 화천군 전역으로 여행 동선을 확장합니다.",
    ),
)


def list_danyang_mvp_places() -> tuple[PlaceCandidate, ...]:
    return DANYANG_MVP_PLACES


def list_hwacheon_mvp_places() -> tuple[PlaceCandidate, ...]:
    return HWACHEON_MVP_PLACES
