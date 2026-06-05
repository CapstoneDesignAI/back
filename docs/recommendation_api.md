# Tripick Recommendation API Contract

추천 점수와 지역 기여도 산식의 자세한 설명은 [`recommendation_logic.md`](./recommendation_logic.md)를 참고합니다.

Tripick MVP 추천/동선 API 명세서입니다. 현재 프론트 메인 추천 API는 `POST /api/v1/ai-recommendations`이며, 카드 응답과 상세 응답은 분리되어 있습니다.

## API Prefix

모든 API는 기본 prefix `/api/v1` 아래에서 호출합니다.

## Endpoint Summary

```text
GET    /api/v1/regions
GET    /api/v1/places
GET    /api/v1/recommendations/options
GET    /api/v1/recommendations/selection-options
GET    /api/v1/recommendations/today
POST   /api/v1/recommendations
POST   /api/v1/ai-recommendations
GET    /api/v1/ai-recommendations/{route_id}

GET    /api/v1/routes
GET    /api/v1/routes/{route_id}
POST   /api/v1/routes
POST   /api/v1/routes/from-recommendation
DELETE /api/v1/routes/{route_id}
```

## Environment Variables

한국관광공사 국문 관광정보 서비스 GW 연동에 사용하는 환경변수입니다.

```env
TOUR_API_SERVICE_KEY=발급받은_서비스키
TOUR_API_BASE_URL=https://apis.data.go.kr/B551011/KorService2
TOUR_API_SERVICE_VERSION=2
TOUR_API_MOBILE_OS=ETC
TOUR_API_MOBILE_APP=TRIP_RE
```

실제 key 값은 GitHub, 공개 채널, 문서에 올리지 않고 Vercel 환경변수나 팀장님에게 안전하게 공유합니다.

## Recommendation Flow

### Today Recommendation Save Flow

오늘의 추천에서 받은 동선을 저장하고 다시 상세조회할 때는 아래 흐름을 사용합니다.

1. `GET /api/v1/recommendations/today`
   - `route_id`: 추천 원본 동선 ID
   - `detail_api_path`: 추천 상세 조회 API
   - `save_api_path`: 추천 동선 저장 API
2. 사용자가 저장 버튼 클릭
   - `POST /api/v1/routes/from-recommendation`
   - request body: `{ "route_id": today.route_id }`
3. 저장 응답
   - `source_route_id`: 추천 원본 동선 ID
   - `source_detail_api_path`: AI 추천 상세 조회 API
   - `saved_route_id`: DB에 저장된 동선 ID
   - `saved_detail_api_path`: 저장 동선 상세 조회 API

프론트에서 AI 추천 상세 화면을 다시 보여줄 때는 `source_detail_api_path`를 사용합니다.
저장된 DB 동선 상세 화면을 보여줄 때는 `saved_detail_api_path`를 사용합니다.

1. 홈에서 오늘의 추천 조회: `GET /recommendations/today`
2. 내 여행 찾기에서 조건 선택
3. 추천 카드 생성: `POST /ai-recommendations`
4. 동선 상세 조회: `GET /ai-recommendations/{route_id}`
5. 저장 버튼 클릭: `POST /routes/from-recommendation`
6. 저장한 동선 조회: `GET /routes`, `GET /routes/{saved_route_id}`

## GET /api/v1/recommendations/today

홈 화면의 “오늘의 추천 여행” 카드와 상세 이동 정보를 반환합니다.

### Response

```json
{
  "today_date": "2026-05-28",
  "section_title": "오늘의 추천 여행",
  "recommendation_id": "sample-danyang-healing-half_day",
  "route_id": "route-danyang-healing-half_day-car-friends",
  "detail_api_path": "/api/v1/ai-recommendations/route-danyang-healing-half_day-car-friends",
  "save_api_path": "/api/v1/routes/from-recommendation",
  "card": {
    "recommendation_id": "sample-danyang-healing-half_day",
    "route_id": "route-danyang-healing-half_day-car-friends",
    "title": "단양 힐링 로컬 코스",
    "subtitle": "충청북도 단양군에서 즐기는 반나절 여행",
    "summary": "도담삼봉부터 만천하스카이워크까지 이어지는 로컬 동선",
    "sido": "충청북도",
    "sigungu": "단양군",
    "region_label": "충청북도 단양군",
    "theme_label": "힐링",
    "primary_badges": ["힐링", "반나절", "자차"],
    "metric_badges": ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"],
    "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
    "route_preview_text": "도담삼봉 → 단양구경시장 → 카페산"
  },
  "recommendation": {
    "...": "GET /api/v1/ai-recommendations/{route_id}와 같은 상세 응답. card는 포함하지 않음"
  }
}
```

### Frontend Usage

| 화면 | 사용 필드 |
| --- | --- |
| 홈 오늘의 추천 카드 | `card.title`, `card.summary`, `card.primary_badges`, `card.metric_badges` |
| 상세 이동 | `route_id` 또는 `detail_api_path` |
| 저장 버튼 | `route_id`를 `POST /routes/from-recommendation`에 전달 |

## POST /api/v1/ai-recommendations

프론트 메인 추천 카드 API입니다. 조건을 받아 추천 카드에 필요한 요약 정보만 반환합니다.

### Request

한국어 중심 요청을 지원합니다.

```json
{
  "duration": "반나절",
  "transportation": "뚜벅이",
  "travel_purpose": "힐링",
  "companion": "친구",
  "region": "단양군"
}
```

### Response

`RecommendationCard` 형태입니다.

```json
{
  "recommendation_id": "sample-danyang-healing-half_day",
  "route_id": "route-danyang-healing-half_day-walk-friends",
  "title": "단양 힐링 로컬 코스",
  "subtitle": "충청북도 단양군에서 즐기는 반나절 여행",
  "summary": "도담삼봉부터 만천하스카이워크까지 이어지는 로컬 동선",
  "sido": "충청북도",
  "sigungu": "단양군",
  "region_label": "충청북도 단양군",
  "theme_label": "힐링",
  "contribution_score": 86,
  "estimated_duration_text": "5시간 20분",
  "estimated_cost_text": "35,000원~55,000원",
  "local_consumption_text": "로컬 소비 장소 2곳 포함",
  "primary_badges": ["힐링", "반나절", "뚜벅이"],
  "metric_badges": ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"],
  "place_count": 4,
  "place_count_text": "장소 4곳",
  "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
  "route_preview_text": "도담삼봉 → 단양구경시장 → 카페산",
  "ai_reason_summary": "짧은 이동 안에 전망, 산책, 로컬 소비를 균형 있게 배치했어요."
}
```

카드 응답에는 전체 장소 리스트, 지도 마커, 저장 payload가 포함되지 않습니다. 전체 동선은 상세조회 API를 사용합니다.

## GET /api/v1/ai-recommendations/{route_id}

추천 동선 상세조회 API입니다. 추천 카드의 `route_id`를 path parameter로 전달합니다.

### Example

```text
GET /api/v1/ai-recommendations/route-danyang-healing-half_day-walk-friends
```

### Response 주요 필드

```json
{
  "recommendation_id": "sample-danyang-healing-half_day",
  "route_id": "route-danyang-healing-half_day-walk-friends",
  "title": "단양 힐링 로컬 코스",
  "sido": "충청북도",
  "sigungu": "단양군",
  "region_story": {
    "title": "단양 로컬 여행 이야기",
    "summary": "단양은 남한강을 따라 이어지는 자연 경관과 전통시장, 전망 명소가 가까이 연결된 충북의 대표 체류형 여행지입니다.",
    "history": "단양은 삼봉 정도전의 이야기가 남아 있는 도담삼봉과 석문, 남한강 물길을 중심으로 형성된 산수 관광 자원이 잘 알려진 지역입니다.",
    "local_story": "힐링 코스에서는 도담삼봉에서 지역의 첫인상을 만들고, 시장과 로컬 카페를 함께 배치해 방문이 지역 소비로 이어지도록 구성했습니다.",
    "local_tip": "전망 명소 방문 전후로 단양구경시장이나 로컬 카페를 함께 들르면 짧은 일정에서도 지역 상권 체류 효과를 만들 수 있습니다.",
    "source": "mvp_sample"
  },
  "contribution_info": {
    "score": 86,
    "label": "지역 기여도 86점",
    "description": "지역 기여도는 공식 공공 지표가 아니라 Tripick MVP 내부 점수입니다. 코스에 포함된 장소들의 지역 기여도 평균에 로컬 소비 장소 보너스를 더해 계산합니다.",
    "formula": "장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점(최대 10점)",
    "average_place_score": 80,
    "local_consumption_bonus": 6,
    "local_consumption_count": 2,
    "place_count": 4,
    "is_official_metric": false
  },
  "mobility": {
    "level": "high",
    "label": "이동 난이도 높음",
    "summary": "장소 사이 거리가 길어 전체 코스를 도보로만 이동하기에는 부담이 큰 코스입니다.",
    "recommended_transport": "뚜벅이"
  },
  "local_consumption_points": [
    {
      "order": 2,
      "place_id": "sample-danyang-market",
      "name": "단양구경시장",
      "category": "로컬시장",
      "estimated_cost_text": "15,000원~25,000원",
      "lat": 36.984784,
      "lng": 128.365889
    }
  ],
  "route_legs": [
    {
      "order": 1,
      "from_place_id": "sample-dodamsambong",
      "from_name": "도담삼봉",
      "to_place_id": "sample-danyang-market",
      "to_name": "단양구경시장",
      "distance_meters": 304,
      "distance_km": 0.3,
      "distance_text": "304m"
    }
  ],
  "places": [
    {
      "order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "category": "자연",
      "stay_minutes": 50,
      "reason": "단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
      "contribution_reason": "지역의 첫 방문 만족도를 높여 이후 로컬 상권 방문으로 이어지게 합니다.",
      "place_story": "도담삼봉은 단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
      "local_tip": "방문 전후 가까운 전통시장이나 로컬 매장을 함께 둘러보면 더 좋은 동선이 됩니다.",
      "distance_from_previous_text": null
    }
  ],
  "map_markers": [
    {
      "order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "category": "자연",
      "lat": 36.984539,
      "lng": 128.369267
    }
  ],
  "legacy_route_payload": {
    "...": "기존 POST /routes 저장 호환용 payload"
  },
  "is_saved": false
}
```

## POST /api/v1/recommendations

점수 기반 추천 전체 응답을 반환하는 기존 API입니다. 내부 추천 로직 확인, 테스트, 레거시 연동용으로 유지합니다. 프론트 메인 추천 카드는 `POST /ai-recommendations`를 우선 사용합니다.

요청 필드는 code와 한국어 label을 모두 받을 수 있습니다.

```json
{
  "region_id": "단양군",
  "theme": "힐링",
  "travel_time": "반나절",
  "transport": "뚜벅이",
  "companion": "친구",
  "data_source": "sample"
}
```

## GET /api/v1/places

> 내부 확인용/후순위 API입니다. 프론트 추천 카드와 동선 상세 화면은
> `POST /api/v1/ai-recommendations`, `GET /api/v1/ai-recommendations/{route_id}`
> 응답에 포함된 장소 정보를 사용하므로 이 API를 필수로 호출하지 않습니다.

장소 데이터 목록을 조회합니다. 기본값은 단양 MVP 샘플 데이터입니다.

| Query | 설명 | 기본값 |
| --- | --- | --- |
| `region_id` | 조회할 지역 id | `region-danyang` |
| `source` | `sample`, `tour_api`, `auto` | `sample` |
| `theme` | 테마별 TourAPI 필터 힌트 | 없음 |
| `limit` | TourAPI 조회 개수 | `20` |

```text
GET /api/v1/places?source=tour_api&region_id=region-danyang&theme=food&limit=10
```

TourAPI 응답이 비어 있거나 실패하면 샘플 데이터로 fallback합니다.

## Selection Options

> 내부 확인용/후순위 API입니다. 프론트에서 선택지 문구를 직접 반영하기로 했기 때문에
> 노션/Swagger 핵심 API 명세에서는 제외합니다. 기존 확인 흐름을 위해 endpoint 자체는 유지합니다.

```text
GET /api/v1/recommendations/options
GET /api/v1/recommendations/selection-options
```

`selection-options`는 내 여행 찾기 화면에서 필요한 선택지를 한 번에 반환합니다.

| 화면 요소 | 응답 필드 |
| --- | --- |
| 지역 직접 선택 / AI 지역 추천 | `region_selection_modes` |
| 권역 선택 | `area_groups` |
| 권역별 인구감소지역 | `regions_by_area_group` |
| 테마 선택 | `themes` |
| 여행 시간 선택 | `travel_times` |
| 이동수단 선택 | `transports` |
| 동행 선택 | `companions` |

## Save Route

### Recommended Save API

저장 버튼은 이 API를 사용합니다. 프론트는 추천 카드 또는 상세 응답의 `route_id`만 보내면 됩니다.

```http
POST /api/v1/routes/from-recommendation
```

```json
{
  "route_id": "route-danyang-healing-half_day-walk-friends"
}
```

```json
{
  "message": "동선이 성공적으로 저장되었습니다.",
  "route_id": "saved-route-id",
  "saved_route_id": "saved-route-id",
  "source_route_id": "route-danyang-healing-half_day-walk-friends",
  "source_detail_api_path": "/api/v1/ai-recommendations/route-danyang-healing-half_day-walk-friends",
  "saved_detail_api_path": "/api/v1/routes/saved-route-id",
  "is_saved": true
}
```

필드 의미:

| 필드 | 의미 |
| --- | --- |
| `source_route_id` | 추천 카드/상세조회에서 받은 원본 추천 동선 ID |
| `saved_route_id` | DB `routes` 테이블에 저장된 동선 ID |
| `route_id` | 기존 호환용 필드. `saved_route_id`와 동일 |
| `source_detail_api_path` | AI 추천 상세 화면 재조회용 API |
| `saved_detail_api_path` | 저장된 DB 동선 상세 조회용 API |
| `is_saved` | 저장 성공 여부 |

### Legacy Save API

기존 방식도 유지합니다.

```http
POST /api/v1/routes
```

body에는 추천 상세 응답의 `legacy_route_payload`를 전달합니다.

## Saved Route History

```text
GET    /api/v1/routes
GET    /api/v1/routes/{saved_route_id}
DELETE /api/v1/routes/{saved_route_id}
```

현재 저장 DB 구조는 기존 `routes`, `route_places` 테이블을 유지합니다. 따라서 저장 후 조회는 저장된 동선/장소 중심으로 반환됩니다. `region_story`, `mobility`, `contribution_info`까지 저장 후 그대로 보존하려면 이후 JSON snapshot 컬럼 또는 별도 테이블 추가가 필요합니다.

## Scoring Policy

장소 추천 점수는 아래 기준으로 계산합니다.

| 기준 | 점수 |
| --- | --- |
| 선택 테마와 장소 태그 일치 | `+35` |
| 이동수단과 장소 이동 태그 일치 | `+20` |
| 이동수단 불일치 | `-25` |
| 동행 유형 일치 | `+10` |
| 장소 지역 기여도 | `local_contribution_score * 0.2` |
| 맛집/로컬시장/지역활성화 테마에서 로컬 소비 장소 | `+20` |
| 지역활성화 테마에서 기여도 80점 이상 | `+15` |

코스의 `contribution_score`는 공식 공공 지표가 아니라 MVP 내부 점수입니다.

```text
지역 기여도 = 장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점(최대 10점)
```

단양 힐링 코스 예시:

```text
장소 평균 80점 + 로컬 소비 2곳 보너스 6점 = 지역 기여도 86점
```

## Frontend Mapping

| 화면 | API | 주요 필드 |
| --- | --- | --- |
| 홈 오늘의 추천 | `GET /recommendations/today` | `card`, `route_id`, `detail_api_path` |
| 추천 카드 | `POST /ai-recommendations` | `title`, `summary`, `primary_badges`, `metric_badges`, `place_preview_names` |
| 동선 상세 | `GET /ai-recommendations/{route_id}` | `ai_reason`, `places`, `route_legs`, `map_markers`, `region_story` |
| 지도 탭 | `GET /ai-recommendations/{route_id}` | `map_markers`, `places[].lat`, `places[].lng` |
| 저장 버튼 | `POST /routes/from-recommendation` | request `route_id`, response `saved_route_id` |
| 저장한 동선 | `GET /routes` | `route_id`, `title`, `created_at`, `place_count` |
