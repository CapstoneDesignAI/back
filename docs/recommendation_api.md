# Tripick Recommendation API Contract

Tripick MVP 추천/동선 API 명세입니다. 프론트 메인 추천 API는 `POST /api/v1/ai-recommendations`이고, 카드 응답과 동선 상세 응답은 분리되어 있습니다.

추천 점수, 지역 기여도 산식, LLM 추천 이유 생성 방식은 [`recommendation_logic.md`](./recommendation_logic.md)를 참고합니다.

## API Prefix

모든 API는 기본 prefix `/api/v1` 아래에서 호출합니다.

## Endpoint Summary

```text
GET    /api/v1/regions
GET    /api/v1/places
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

`GET /api/v1/recommendations/options`, `GET /api/v1/recommendations/selection-options`는 내부 확인용/후순위 API로 유지하지만 Swagger 핵심 명세에서는 숨깁니다.

## Environment Variables

```env
TOUR_API_SERVICE_KEY=국문_관광정보_서비스_GW_키
TOUR_API_BASE_URL=https://apis.data.go.kr/B551011/KorService2
TOUR_API_SERVICE_VERSION=2
TOUR_API_MOBILE_OS=ETC
TOUR_API_MOBILE_APP=TRIPICK

TOUR_PHOTO_API_SERVICE_KEY=관광공모전_사진_수상작_정보_API_키
TOUR_PHOTO_API_BASE_URL=https://apis.data.go.kr/B551011/PhokoAwrdService
TOUR_PHOTO_API_SEARCH_ENDPOINT=phokoAwrdList
TOUR_PHOTO_API_MOBILE_OS=ETC
TOUR_PHOTO_API_MOBILE_APP=TRIPICK
TOUR_PHOTO_API_TIMEOUT_SECONDS=10

LLM_PROVIDER=openai
LLM_TIMEOUT_SECONDS=20
OPENAI_API_KEY=OpenAI_API_키
OPENAI_MODEL=gpt-4o-mini
```

실제 key 값은 GitHub, 공개 채널, 문서에 올리지 않고 로컬 `.env` 또는 Vercel 환경변수에만 등록합니다.

이미지는 기존 TourAPI `firstimage`, `firstimage2`를 우선 사용합니다. 두 값이 비어 있으면 `PhokoAwrdService/phokoAwrdList`를 키워드로 조회해 `orgImage`, `thumbImage`를 보조 이미지 소스로 사용합니다.

## Recommendation Flow

1. 홈에서 오늘의 추천 조회: `GET /recommendations/today`
2. 내 여행 찾기에서 조건 선택
3. 추천 카드 생성: `POST /ai-recommendations`
4. 동선 상세 조회: `GET /ai-recommendations/{route_id}`
5. 저장 버튼 클릭: `POST /routes/from-recommendation`
6. 저장한 동선 조회: `GET /routes`, `GET /routes/{saved_route_id}`

7. 홈 오늘의 추천 조회: `GET /api/v1/recommendations/today`
8. 내 여행 찾기 조건 선택
9. 추천 카드 생성: `POST /api/v1/ai-recommendations`
10. 동선 상세 조회: `GET /api/v1/ai-recommendations/{route_id}`
11. 저장 버튼 클릭: `POST /api/v1/routes/from-recommendation`
12. 저장한 동선 조회: `GET /api/v1/routes`, `GET /api/v1/routes/{saved_route_id}`

오늘의 추천을 저장하는 경우도 같은 흐름입니다.

- 오늘의 추천 응답의 `route_id`를 저장 API에 전달합니다.
- 추천 상세 화면은 `source_detail_api_path` 또는 `GET /api/v1/ai-recommendations/{route_id}`를 사용합니다.
- 저장된 DB 동선 상세 화면은 `saved_detail_api_path` 또는 `GET /api/v1/routes/{saved_route_id}`를 사용합니다.

## GET /api/v1/recommendations/today

홈 화면의 오늘의 추천 카드와 상세 이동 정보를 반환합니다.

### Header

인증 없음.

### Request

없음.

### Response 200

```json
{
  "today_date": "2026-06-05",
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
    "thumbnail_url": "https://tong.visitkorea.or.kr/cms/resource_photo/69/3414769_image2_1.jpg",
    "contribution_score": 86,
    "tags": ["힐링", "반나절", "자차"],
    "metric_badges": ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"],
    "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
    "route_preview_text": "도담삼봉 -> 단양구경시장 -> 카페산",
    "ai_reason_summary": "짧은 이동 안에 전망, 산책, 로컬 소비를 균형 있게 배치했어요."
  },
  "recommendation": {
    "...": "GET /api/v1/ai-recommendations/{route_id}와 같은 상세 응답"
  }
}
```

## POST /api/v1/ai-recommendations

프론트 메인 추천 카드 API입니다. 조건을 받아 카드 UI에 필요한 요약 정보만 반환합니다.

### Header

인증 없음.

### Request

한국어 중심 요청값을 사용합니다.

```json
{
  "duration": "반나절",
  "transportation": "뚜벅이",
  "travel_purpose": "힐링",
  "companion": "친구",
  "region": "단양군"
}
```

### Response 200

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
  "thumbnail_url": "https://tong.visitkorea.or.kr/cms/resource_photo/69/3414769_image2_1.jpg",
  "contribution_score": 86,
  "estimated_duration_text": "5시간 20분",
  "estimated_cost_text": "35,000원~55,000원",
  "local_consumption_text": "로컬 소비 장소 2곳 포함",
  "tags": ["힐링", "반나절", "뚜벅이"],
  "tags": ["힐링", "반나절", "뚜벅이"],
  "metric_badges": ["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"],
  "place_count": 4,
  "place_count_text": "장소 4곳",
  "place_preview_names": ["도담삼봉", "단양구경시장", "카페산"],
  "place_preview": [
    {
      "order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "category": "자연",
      "summary": "단양의 자연 경관을 먼저 체감할 수 있는 대표 장소입니다.",
      "tags": ["힐링", "자연투어", "뚜벅이"],
      "image_url": null,
      "lat": 36.984539,
      "lng": 128.369267,
      "is_local_consumption": false
    }
  ],
  "route_preview_text": "도담삼봉 -> 단양구경시장 -> 카페산",
  "ai_reason_summary": "짧은 이동 안에 전망, 산책, 로컬 소비를 균형 있게 배치했어요."
}
```

카드 응답에는 전체 `places`, `route_legs`, `legacy_route_payload`를 포함하지 않습니다. 전체 동선은 상세조회 API를 사용합니다.

## GET /api/v1/ai-recommendations/{route_id}

AI 추천 동선 상세조회 API입니다. 추천 카드의 `route_id`를 path parameter로 전달합니다.

### Header

인증 없음.

### Request

```text
GET /api/v1/ai-recommendations/route-danyang-healing-half_day-walk-friends
```

### Response 200

```json
{
  "recommendation_id": "sample-danyang-healing-half_day",
  "route_id": "route-danyang-healing-half_day-walk-friends",
  "title": "단양 힐링 로컬 코스",
  "subtitle": "충청북도 단양군에서 즐기는 반나절 여행",
  "sido": "충청북도",
  "sigungu": "단양군",
  "theme_label": "힐링",
  "travel_time_label": "반나절",
  "transport_label": "뚜벅이",
  "companion_label": "친구",
  "contribution_score": 86,
  "estimated_duration_minutes": 320,
  "estimated_cost_min": 35000,
  "estimated_cost_max": 55000,
  "local_consumption_count": 2,
  "place_count": 4,
  "total_stay_minutes": 260,
  "total_distance_meters": 12300,
  "total_distance_km": 12.3,
  "total_distance_text": "12.3km",
  "route_badges": ["힐링", "지역 기여도 86점", "로컬 소비 2곳"],
  "ai_reason": "이 코스는 단양의 대표 자연 관광지와 지역 상권을 함께 경험할 수 있도록 구성되었습니다.",
  "ai_reason_detail": {
    "overview": "단양의 자연 경관과 로컬 소비 장소를 균형 있게 묶은 코스입니다.",
    "route_design": "전망 명소 이후 시장과 카페를 배치해 이동 피로도를 낮췄습니다.",
    "local_contribution": "전통시장과 로컬 카페 방문으로 지역 소비가 발생합니다.",
    "traveler_fit": "반나절 일정과 뚜벅이 여행자에게 맞춘 동선입니다.",
    "closing_tip": "시장 방문 시간을 식사 시간대와 맞추면 더 자연스럽습니다.",
    "highlights": ["대표 자연 경관", "로컬 소비", "체류시간 증가"],
    "generation_source": "llm"
  },
  "places": [
    {
      "order": 1,
      "visit_order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "category": "자연",
      "address": "충북 단양군 매포읍 삼봉로 644",
      "lat": 36.984539,
      "lng": 128.369267,
      "stay_minutes": 50,
      "reason": "단양의 자연 경관을 먼저 체감할 수 있는 대표 장소입니다.",
      "contribution_reason": "지역의 첫 방문 만족도를 높여 이후 로컬 상권 방문으로 이어지게 합니다.",
      "place_story": "단양을 대표하는 자연 경관 명소입니다.",
      "local_tip": "방문 이후 가까운 전통시장이나 로컬 매장을 함께 둘러보면 좋습니다.",
      "image_url": null,
      "estimated_cost_min": 0,
      "estimated_cost_max": 5000,
      "local_contribution_score": 78,
      "tags": ["힐링", "자연투어", "뚜벅이"],
      "distance_from_previous_meters": null,
      "distance_from_previous_km": null,
      "distance_from_previous_text": null,
      "is_local_consumption": false,
      "recommendation_score": 92,
      "score_reasons": ["테마 일치", "이동수단 적합"],
      "source": "sample"
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
  "local_consumption_points": [
    {
      "order": 2,
      "place_id": "sample-danyang-market",
      "name": "단양구경시장",
      "category": "로컬시장",
      "summary": "지역 소비가 직접 발생하는 전통시장입니다.",
      "contribution_reason": "지역 소상공인 소비로 이어집니다.",
      "estimated_cost_min": 15000,
      "estimated_cost_max": 25000,
      "estimated_cost_text": "15,000원~25,000원",
      "lat": 36.984784,
      "lng": 128.365889
    }
  ],
  "mobility": {
    "level": "medium",
    "label": "이동 난이도 보통",
    "summary": "장소 간 거리가 있어 일부 구간은 대중교통 또는 차량 이동을 권장합니다.",
    "recommended_transport": "뚜벅이"
  },
  "contribution_info": {
    "score": 86,
    "label": "지역 기여도 86점",
    "description": "공식 공공 지표가 아니라 Tripick MVP 내부 추천 점수입니다.",
    "formula": "장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점, 최대 10점",
    "average_place_score": 80,
    "local_consumption_bonus": 6,
    "local_consumption_count": 2,
    "place_count": 4,
    "is_official_metric": false
  },
  "region_story": {
    "title": "단양 로컬 여행 이야기",
    "summary": "단양은 자연 경관과 전통시장, 전망 명소가 가까이 연결된 체류형 여행지입니다.",
    "history": "남한강 물길과 단양팔경을 중심으로 알려진 지역입니다.",
    "local_story": "대표 명소와 시장, 카페를 함께 배치해 방문이 지역 소비로 이어지도록 구성했습니다.",
    "local_tip": "시장과 로컬 카페를 함께 방문하면 지역 체류 효과를 만들 수 있습니다.",
    "source": "mvp_sample"
  },
  "legacy_route_payload": {
    "title": "단양 힐링 로컬 코스",
    "estimated_time": "5시간 20분",
    "places": []
  },
  "source": "sample",
  "is_saved": false
}
```

`map_markers`는 제거했습니다. 지도 마커는 `places[].lat`, `places[].lng`, `places[].order`, `places[].name`을 사용합니다.

## POST /api/v1/routes/from-recommendation

추천 카드/상세에서 받은 `route_id`만 전달해 동선을 저장합니다.

### Header

```http
Authorization: Bearer <jwt_token>
```

### Request

```json
{
  "route_id": "route-danyang-healing-half_day-walk-friends"
}
```

### Response 201

```json
{
  "message": "동선이 성공적으로 저장되었습니다.",
  "route_id": "saved-route-id",
  "saved_route_id": "saved-route-id",
  "source_route_id": "route-danyang-healing-half_day-walk-friends",
  "is_saved": true
}
```

## GET /api/v1/routes

내가 저장한 동선 목록을 조회합니다.

### Header

```http
Authorization: Bearer <jwt_token>
```

### Response 200

```json
[
  {
    "route_id": "saved-route-id",
    "title": "단양 힐링 로컬 코스",
    "created_at": "2026-06-05T15:00:00",
    "place_count": 4
  }
]
```

## GET /api/v1/routes/{route_id}

저장된 DB 동선 상세를 조회합니다. AI 추천 상세 응답과 완전히 같은 스키마는 아니며, 현재 DB `routes`, `route_places`, `places` 기준으로 저장된 정보만 반환합니다.

### Header

인증 없음.

### Response 200

```json
{
  "route_id": "saved-route-id",
  "title": "단양 힐링 로컬 코스",
  "created_at": "2026-06-05T15:00:00",
  "description": null,
  "tags": ["힐링", "로컬시장"],
  "places": [
    {
      "visit_order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "address": "충북 단양군 매포읍 삼봉로 644",
      "lat": 36.984539,
      "lng": 128.369267,
      "image_url": "",
      "description": "단양의 자연 경관을 먼저 체감할 수 있는 대표 장소입니다.",
      "tags": ["힐링", "자연투어"],
      "category": "자연"
    }
  ]
}
```

## GET /api/v1/places

후보 장소 데이터 확인용/후순위 API입니다. 프론트 추천 카드와 동선 상세 화면은 `ai-recommendations` 응답 안의 장소 정보를 사용하므로 일반 사용자 플로우에서 필수로 호출하지 않습니다.

### Query

| Query       | 설명                         | 기본값           |
| ----------- | ---------------------------- | ---------------- |
| `region_id` | 조회할 지역 id               | `region-danyang` |
| `source`    | `sample`, `tour_api`, `auto` | `sample`         |
| `theme`     | TourAPI 조회 시 테마 필터    | 없음             |
| `limit`     | TourAPI 조회 개수            | `20`             |

### Response 200

```json
{
  "places": [
    {
      "place_id": "sample-dodamsambong",
      "region_id": "region-danyang",
      "name": "도담삼봉",
      "category": "자연",
      "address": "충북 단양군 매포읍 삼봉로 644",
      "lat": 36.984539,
      "lng": 128.369267,
      "stay_minutes": 50,
      "estimated_cost_min": 0,
      "estimated_cost_max": 5000,
      "local_contribution_score": 78,
      "tags": ["힐링", "자연투어", "뚜벅이"],
      "is_local_consumption": false,
      "reason": "단양의 자연 경관을 먼저 체감할 수 있는 대표 장소입니다.",
      "contribution_reason": "지역의 첫 방문 만족도를 높입니다.",
      "image_url": null,
      "source": "sample"
    }
  ]
}
```

## 노션 명세서 수정 체크리스트

노션에는 아래 항목을 반영합니다.

1. `primary_badges`는 삭제하고 `tags`로 통일합니다.
2. `theme_tags`는 외부 응답에서 사용하지 않고 `tags`만 사용합니다.
3. `map_markers`는 삭제합니다. 지도는 `places`의 `lat`, `lng`를 사용합니다.
4. `POST /api/v1/ai-recommendations`는 카드 전용 응답입니다.
5. `GET /api/v1/ai-recommendations/{route_id}`는 상세 전용 응답입니다.
6. `GET /api/v1/recommendations/options`, `GET /api/v1/recommendations/selection-options`는 핵심 명세에서 제외하거나 내부 확인용으로 표시합니다.
7. 장소 목록 조회 `GET /api/v1/places`는 후보 장소 확인용/후순위 API로 표시합니다.
8. 환경변수의 앱 이름은 `TRIPICK`으로 표기합니다.
9. 사진 API는 `PhokoAwrdService/phokoAwrdList`와 `TOUR_PHOTO_API_SERVICE_KEY`를 사용한다고 표기합니다.
10. 지역 기여도는 공식 지표가 아니라 MVP 내부 추천 점수라고 표기합니다.

## Scoring Policy

장소 추천 점수는 아래 기준으로 계산합니다.

| 기준                                             | 점수                             |
| ------------------------------------------------ | -------------------------------- |
| 선택 테마와 장소 태그 일치                       | `+35`                            |
| 이동수단과 장소 이동 태그 일치                   | `+20`                            |
| 이동수단 불일치                                  | `-25`                            |
| 동행 유형 일치                                   | `+10`                            |
| 장소 지역 기여도 반영                            | `local_contribution_score * 0.2` |
| 맛집/로컬시장/지역활성화 테마에서 로컬 소비 장소 | `+20`                            |
| 지역활성화 테마에서 지역 기여도 80점 이상        | `+15`                            |

코스 전체 `contribution_score`는 공식 공공 지표가 아니라 MVP 내부 점수입니다.

```text
지역 기여도 = 장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점, 최대 10점
```
