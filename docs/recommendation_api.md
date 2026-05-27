# Recommendation API Contract

TRIP:RE MVP 추천 API 계약입니다. 기존 `POST /api/v1/ai-recommendations` Mock API는 유지하고, 준석님 점수 기반 추천 API를 아래 경로로 추가합니다.

## Endpoints

```text
GET /api/v1/regions
GET /api/v1/places
GET /api/v1/recommendations/options
GET /api/v1/recommendations/selection-options
GET /api/v1/recommendations/today
POST /api/v1/recommendations
POST /api/v1/ai-recommendations
```

## POST /api/v1/recommendations

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

### Response

```json
{
  "recommendation_id": "sample-danyang-healing-half_day",
  "title": "단양 힐링 로컬 코스",
  "contribution_score": 86,
  "estimated_duration_minutes": 320,
  "estimated_cost_min": 35000,
  "estimated_cost_max": 55000,
  "local_consumption_count": 2,
  "places": [
    {
      "order": 1,
      "place_id": "sample-dodamsambong",
      "name": "도담삼봉",
      "lat": 36.984539,
      "lng": 128.369267,
      "recommendation_score": 79,
      "score_reasons": [
        "theme_match",
        "transport_match",
        "companion_match",
        "local_contribution"
      ],
      "source": "sample"
    }
  ],
  "is_saved": false
}
```

## Scoring Policy

| Criterion | Score |
| --- | --- |
| 선택 테마가 장소 태그와 일치 | `+35` |
| 이동수단이 장소 이동 태그와 일치 | `+20` |
| 이동수단이 맞지 않음 | `-25` |
| 동행 유형이 장소 동행 태그와 일치 | `+10` |
| 장소 지역 기여도 | `local_contribution_score * 0.2` |
| 맛집/로컬시장/지역활성화 테마에서 로컬 소비 장소 | `+20` |
| 지역활성화 테마에서 기여도 80점 이상 | `+15` |

현재 장소 데이터는 `source=sample`인 단양 MVP 데이터입니다. 한국관광공사 API 적재 후 같은 응답 구조에서 `source=tour_api` 데이터로 확장합니다.

