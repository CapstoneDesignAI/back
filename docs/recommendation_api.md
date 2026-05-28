# Recommendation API Contract

TRIP:RE MVP 추천 API 계약서입니다. 기존 `POST /api/v1/ai-recommendations` Mock API는 유지하고, 실제 프로토타입 화면은 점수 기반 추천 API를 우선 사용합니다.

## MVP User Flow

```text
홈
-> 오늘의 추천
-> 내 여행 찾기
-> 지역 선택 또는 AI 지역 추천
-> 테마 선택
-> 여행 시간, 이동수단, 동행 선택
-> AI 동선 추천
-> 지도에서 동선 확인
-> 지역 기여도 확인
-> 추천 히스토리에 저장
```

## Endpoints

```text
GET /api/v1/regions
GET /api/v1/places
GET /api/v1/recommendations/options
GET /api/v1/recommendations/selection-options
GET /api/v1/recommendations/today
POST /api/v1/recommendations
POST /api/v1/ai-recommendations

POST /api/v1/routes
GET /api/v1/routes
GET /api/v1/routes/{route_id}
DELETE /api/v1/routes/{route_id}
```

## GET /api/v1/recommendations/today

홈 화면의 `[오늘의 추천]` 카드에서 바로 사용할 수 있는 요약 응답과, 카드를 눌렀을 때 상세 화면으로 넘길 전체 추천 결과를 함께 반환합니다.

### Response

```json
{
  "today_date": "2026-05-28",
  "card": {
    "recommendation_id": "sample-danyang-healing-half_day",
    "title": "단양 힐링 로컬 코스",
    "subtitle": "충청북도 단양군에서 즐기는 반나절 여행",
    "region_label": "충청북도 단양군",
    "theme_label": "힐링",
    "contribution_score": 86,
    "estimated_duration_text": "5시간 20분",
    "estimated_cost_text": "35,000원~55,000원",
    "local_consumption_text": "로컬 소비 장소 2곳 포함",
    "primary_badges": ["힐링", "지역 기여도 86점", "로컬 소비 2곳"],
    "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"]
  },
  "recommendation": {
    "...": "POST /api/v1/recommendations 응답과 동일한 상세 추천 결과"
  }
}
```

### Frontend Usage

| 화면 | 사용 필드 |
| --- | --- |
| 홈 오늘의 추천 카드 | `card.title`, `card.contribution_score`, `card.estimated_duration_text` |
| 홈 카드 장소 미리보기 | `card.place_preview_names` |
| 추천 결과 상세 이동 | `recommendation` 객체 전체 |

## POST /api/v1/recommendations

지역, 테마, 여행 조건을 받아 점수 기반으로 동선형 추천 결과를 반환합니다.

### Request

```json
{
  "region_id": "region-danyang",
  "theme": "healing",
  "travel_time": "half_day",
  "transport": "walk",
  "companion": "friends",
  "prefer_ai_region": false
}
```

### Request Fields

| 필드 | 설명 | 예시 |
| --- | --- | --- |
| `region_id` | 직접 선택한 인구감소지역 id | `region-danyang` |
| `area_group` | 권역만 선택했을 때 사용하는 값 | `chungcheong` |
| `theme` | 여행 테마 | `healing` |
| `travel_time` | 여행 시간 | `3hours`, `half_day`, `full_day`, `overnight` |
| `transport` | 이동수단 | `walk`, `car`, `public_transport` |
| `companion` | 동행 | `solo`, `friends`, `family`, `couple` |
| `prefer_ai_region` | AI 지역 추천 선택 여부 | `true`, `false` |

### Response Shape

```json
{
  "recommendation_id": "sample-danyang-healing-half_day",
  "title": "단양 힐링 로컬 코스",
  "subtitle": "충청북도 단양군에서 즐기는 반나절 여행",
  "region": {
    "id": "region-danyang",
    "area_group": "chungcheong",
    "sido": "충청북도",
    "sigungu": "단양군",
    "is_population_decline": true
  },
  "theme": "healing",
  "theme_label": "힐링",
  "travel_time": "half_day",
  "travel_time_label": "반나절",
  "transport": "walk",
  "transport_label": "뚜벅이",
  "companion": "friends",
  "companion_label": "친구",
  "contribution_score": 86,
  "estimated_duration_minutes": 320,
  "estimated_cost_min": 35000,
  "estimated_cost_max": 55000,
  "local_consumption_count": 2,
  "place_count": 4,
  "total_stay_minutes": 260,
  "route_badges": ["힐링", "지역 기여도 86점", "로컬 소비 2곳", "반나절 코스"],
  "summary": {
    "contribution_label": "지역 기여도 86점",
    "duration_text": "5시간 20분",
    "cost_range_text": "35,000원~55,000원",
    "local_consumption_text": "로컬 소비 장소 2곳 포함"
  },
  "ai_reason": "이 코스는 단양군의 장소를 힐링 테마와 뚜벅이 이동수단에 맞춰 점수화한 뒤 구성했습니다.",
  "ai_reason_detail": {
    "overview": "추천 코스 전체 설명",
    "route_design": "동선 구성 이유",
    "local_contribution": "지역 기여도와 로컬 소비 설명",
    "traveler_fit": "사용자 조건과 맞는 이유",
    "closing_tip": "예상 소비와 여행 팁",
    "highlights": ["힐링 테마 적합", "지역 기여도 86점", "로컬 소비 장소 2곳 포함"],
    "generation_source": "rule_based_ai_ready"
  },
  "places": [
    {
      "order": 1,
      "visit_order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "category": "자연",
      "address": "충청북도 단양군 매포읍 삼봉로 644",
      "lat": 36.984539,
      "lng": 128.369267,
      "stay_minutes": 50,
      "reason": "단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
      "contribution_reason": "지역의 첫 방문 만족도를 높여 이후 로컬 상권 방문으로 이어지게 합니다.",
      "image_url": null,
      "estimated_cost_min": 0,
      "estimated_cost_max": 5000,
      "local_contribution_score": 68,
      "theme_tags": ["healing", "nature", "walk", "revitalization"],
      "tags": ["healing", "nature", "walk", "revitalization"],
      "is_local_consumption": false,
      "recommendation_score": 79,
      "score_reasons": ["theme_match", "transport_match", "companion_match", "local_contribution"],
      "source": "sample"
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
    "title": "단양 힐링 로컬 코스",
    "estimated_time": "총 예상 소요 시간: 5시간 20분",
    "places": [
      {
        "visit_order": 1,
        "place_id": "sample-dodamsambong",
        "name": "도담삼봉",
        "address": "충청북도 단양군 매포읍 삼봉로 644",
        "lat": 36.984539,
        "lng": 128.369267,
        "image_url": "",
        "description": "단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
        "tags": ["healing", "nature", "walk", "revitalization"],
        "category": "자연"
      }
    ]
  },
  "source": "sample",
  "is_saved": false
}
```

## Frontend Field Mapping

| 화면 | 사용 필드 |
| --- | --- |
| 추천 결과 상단 | `title`, `subtitle`, `summary`, `contribution_score` |
| 동선 리스트 | `places[].visit_order`, `places[].name`, `places[].category`, `places[].stay_minutes`, `places[].reason` |
| AI 추천 이유 | `ai_reason`, `ai_reason_detail`, `places[].contribution_reason` |
| 지도 탭 | `map_markers[].order`, `map_markers[].name`, `map_markers[].lat`, `map_markers[].lng` |
| 추천 히스토리 저장 | `legacy_route_payload` |

## Recommendation History

추천 결과 저장은 기존 동선 API를 사용합니다.

### Save

`POST /api/v1/recommendations` 응답의 `legacy_route_payload`를 그대로 `POST /api/v1/routes` body로 전달합니다.

```json
{
  "title": "단양 힐링 로컬 코스",
  "estimated_time": "총 예상 소요 시간: 5시간 20분",
  "places": [
    {
      "visit_order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "address": "충청북도 단양군 매포읍 삼봉로 644",
      "lat": 36.984539,
      "lng": 128.369267,
      "image_url": "",
      "description": "단양의 자연 경관을 먼저 체감할 수 있는 대표 전망 장소입니다.",
      "tags": ["healing", "nature", "walk", "revitalization"],
      "category": "자연"
    }
  ]
}
```

저장 성공 응답:

```json
{
  "message": "동선이 성공적으로 저장되었습니다.",
  "route_id": "saved-route-id"
}
```

### List

```text
GET /api/v1/routes
```

### Detail

```text
GET /api/v1/routes/{route_id}
```

### Delete

```text
DELETE /api/v1/routes/{route_id}
```

## Selection Options

`GET /api/v1/recommendations/selection-options`는 내 여행 찾기 화면에서 필요한 선택지를 한 번에 반환합니다.

| 화면 요소 | 응답 필드 |
| --- | --- |
| 지역 직접 선택 / AI 지역 추천 | `region_selection_modes` |
| 권역 선택 | `area_groups` |
| 권역별 인구감소지역 | `regions_by_area_group` |
| 테마 선택 | `themes` |
| 여행 시간 선택 | `travel_times` |
| 이동수단 선택 | `transports` |
| 동행 선택 | `companions` |

## Scoring Policy

| 기준 | 점수 |
| --- | --- |
| 선택 테마와 장소 태그 일치 | `+35` |
| 이동수단과 장소 이동 태그 일치 | `+20` |
| 이동수단 부적합 | `-25` |
| 동행 유형 일치 | `+10` |
| 장소 지역 기여도 | `local_contribution_score * 0.2` |
| 맛집/로컬시장/지역활성화 테마에서 로컬 소비 장소 | `+20` |
| 지역활성화 테마에서 기여도 80 이상 | `+15` |

## Data Source

현재 장소 데이터는 `source=sample`인 단양 MVP 샘플 데이터입니다. 한국관광공사 API 적재 이후에도 프론트 응답 구조는 유지하고, 장소 단위 `source`를 `tour_api`로 확장합니다.
