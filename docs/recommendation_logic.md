# Tripick Recommendation Logic

이 문서는 Tripick MVP의 추천 로직을 회의, 발표, 프론트 연동 논의에서 설명할 수 있도록 정리한 문서입니다.
현재 추천 점수는 공식 공공 지표가 아니라 서비스 내부 MVP 점수입니다.

## Goal

추천 로직의 목표는 사용자가 선택한 지역, 테마, 여행 시간, 이동수단, 동행 조건에 맞춰 동선형 여행 코스를 만드는 것입니다.
단순히 인기 장소만 고르는 방식이 아니라, 지역 소비 장소와 체류 시간을 함께 고려해 지역 기여도를 높이는 방향으로 추천합니다.

## Main Flow

1. 사용자가 추천 조건을 보냅니다.
2. 요청값은 한국어 라벨과 내부 code를 모두 받을 수 있도록 정규화합니다.
3. 선택 지역을 기준으로 후보 장소를 불러옵니다.
4. 각 장소에 점수를 부여합니다.
5. 여행 시간 예산 안에 들어오는 장소를 고릅니다.
6. 선택된 장소를 원래 동선 순서 기준으로 정렬합니다.
7. 코스 전체의 지역 기여도, 예상 시간, 예상 비용, 로컬 소비 장소 수를 계산합니다.
8. 장소 사이 직선거리와 이동 난이도를 계산합니다.
9. 카드 응답과 상세 응답에 필요한 필드를 분리해서 반환합니다.

## Request Normalization

프론트 요청은 한국어 중심으로 받을 수 있습니다.
백엔드 내부에서는 기존 로직 재사용을 위해 code 값으로 변환해서 사용합니다.

| Type | Korean Label | Internal Code |
| --- | --- | --- |
| 테마 | 힐링 | `healing` |
| 테마 | 맛집 | `food` |
| 테마 | 뚜벅이 | `walk` |
| 테마 | 자연투어 | `nature` |
| 테마 | 로컬시장 | `local_market` |
| 테마 | 지역활성화 추천 | `revitalization` |
| 여행 시간 | 3시간 | `3hours` |
| 여행 시간 | 반나절 | `half_day` |
| 여행 시간 | 하루 | `full_day` |
| 여행 시간 | 1박 2일 | `overnight` |
| 이동수단 | 뚜벅이 | `walk` |
| 이동수단 | 자차 | `car` |
| 이동수단 | 대중교통 | `public_transport` |
| 동행 | 혼자 | `solo` |
| 동행 | 친구 | `friends` |
| 동행 | 가족 | `family` |
| 동행 | 연인 | `couple` |

## Place Scoring

장소별 추천 점수는 사용자 조건과 장소 메타데이터를 비교해서 계산합니다.

| Rule | Score |
| --- | ---: |
| 선택 테마가 장소 테마와 일치 | +35 |
| 선택 이동수단이 장소 이동수단 태그와 일치 | +20 |
| 선택 이동수단이 장소 이동수단 태그와 불일치 | -25 |
| 선택 동행 유형이 장소 동행 태그와 일치 | +10 |
| 장소 지역 기여도 반영 | `local_contribution_score * 0.2` |
| 맛집/로컬시장/지역활성화 테마에서 로컬 소비 장소 | +20 |
| 지역활성화 테마에서 지역 기여도 80점 이상 | +15 |

점수 사유는 상세 응답의 장소별 `score_reasons`에 포함됩니다.

## Time Budget

여행 시간 옵션별로 전체 시간 예산을 잡고, 이동/휴식 buffer를 제외한 나머지 시간 안에서 장소를 선택합니다.

| Travel Time | Total Budget | Buffer | Place Stay Budget |
| --- | ---: | ---: | ---: |
| `3hours` | 180분 | 30분 | 150분 |
| `half_day` | 320분 | 60분 | 260분 |
| `full_day` | 480분 | 90분 | 390분 |
| `overnight` | 900분 | 180분 | 720분 |

후보 장소는 점수와 장소별 지역 기여도를 기준으로 먼저 정렬합니다.
선택이 끝난 뒤에는 실제 동선처럼 보이도록 기존 후보 데이터의 원래 순서로 다시 정렬합니다.

## Route Contribution Score

코스의 `contribution_score`는 공식 공공 지표가 아니라 Tripick MVP 내부 점수입니다.
회의나 발표에서는 "공식 지역 활성화 지수"라고 설명하면 안 됩니다.

```text
지역 기여도 = 장소별 local_contribution_score 평균 + 로컬 소비 장소 수 * 3점
로컬 소비 보너스는 최대 10점
최종 점수는 최대 100점
```

예를 들어 장소 평균 점수가 80점이고 로컬 소비 장소가 2곳이면 다음처럼 계산합니다.

```text
80 + min(2 * 3, 10) = 86점
```

응답에는 `contribution_info`로 산식과 세부 값을 함께 내려줍니다.

## Local Consumption

로컬 소비 장소는 전통시장, 지역 식당, 로컬 카페, 특산물/체험 장소처럼 실제 지역 상권 소비로 이어질 수 있는 장소입니다.

응답에서는 다음 정보를 제공합니다.

| Field | Description |
| --- | --- |
| `local_consumption_count` | 코스에 포함된 로컬 소비 장소 수 |
| `local_consumption_points` | 로컬 소비 장소 목록 |
| `local_consumption_text` | 카드/상세 UI용 요약 문구 |

## Distance Calculation

장소 사이 거리는 현재 MVP 기준으로 좌표 간 직선거리를 계산합니다.
교통 경로 기반 실제 이동거리는 아닙니다.

계산 결과는 다음 필드로 내려갑니다.

| Field | Description |
| --- | --- |
| `route_legs` | 장소 사이 구간별 거리 |
| `total_distance_meters` | 전체 거리, meter |
| `total_distance_km` | 전체 거리, km |
| `total_distance_text` | UI 표시용 거리 |
| `distance_from_previous_*` | 각 장소의 이전 장소 기준 거리 |

카카오맵 경로 API나 대중교통 API가 붙으면 이후 실제 이동거리/시간 기반으로 교체할 수 있습니다.

## Mobility Level

`mobility`는 교통 API 없이 MVP 규칙으로 계산한 이동 난이도입니다.

| Transport | Low | Medium | High |
| --- | --- | --- | --- |
| 뚜벅이 | 전체 2.5km 이하, 최대 구간 1.2km 이하 | 전체 6km 이하, 최대 구간 3km 이하 | 그 외 |
| 대중교통 | 최대 구간 1.5km 이하 | 최대 구간 5km 이하 | 그 외 |
| 자차 | 전체 12km 이하 | 전체 30km 이하 | 그 외 |

응답에는 `level`, `label`, `summary`, `recommended_transport`가 포함됩니다.

## Route ID

추천 생성 시 저장과 상세조회에 사용할 수 있는 `route_id`를 발급합니다.

```text
route-{region_slug}-{theme}-{travel_time}-{transport}-{companion}
```

예시:

```text
route-danyang-healing-half_day-walk-friends
```

`recommendation_id`는 추천 결과 카드 자체의 ID이고, `route_id`는 상세조회와 저장 버튼에서 사용하는 동선 ID입니다.
프론트 저장 버튼은 `route_id`만 보내는 방식으로 정리했습니다.

## API Response Role

추천 응답은 카드와 상세를 분리합니다.

| API | Role | Main Fields |
| --- | --- | --- |
| `POST /api/v1/ai-recommendations` | 추천 카드 생성 | `route_id`, `title`, `summary`, `tags`, `metric_badges`, `place_preview`, `sido`, `sigungu` |
| `GET /api/v1/ai-recommendations/{route_id}` | 동선 상세 조회 | 전체 장소 목록, 좌표, AI 추천 이유, 거리, 이동 난이도, 지역 스토리 |
| `GET /api/v1/recommendations/today` | 오늘의 추천 | 카드와 상세 이동용 `route_id` |
| `POST /api/v1/routes/from-recommendation` | 추천 동선 저장 | 요청 body의 `route_id`로 저장 |

## Card Tags

카드의 `tags`는 피그마 카드 UI에 맞춰 3개 고정으로 내려줍니다.

```json
["힐링", "반나절", "뚜벅이"]
```

지역 기여도, 로컬 소비 장소 수, 장소 개수처럼 수치성 배지는 `metric_badges`로 분리합니다.

```json
["지역 기여도 86점", "로컬 소비 2곳", "장소 4곳"]
```

## Region And Place Story

MVP에서는 지역 설명과 장소 설명을 샘플 데이터 기반으로 생성합니다.

| Field | Description |
| --- | --- |
| `region_story` | 지역의 여행 맥락, 역사, 로컬 팁 |
| `place_story` | 장소별 추천 맥락 |
| `local_tip` | 장소 방문 시 로컬 소비나 체류로 연결되는 팁 |

TourAPI 상세 소개 데이터가 안정적으로 확보되면 `region_story`, `place_story`를 실제 관광정보 기반으로 확장할 수 있습니다.

## Current Limitations

현재 추천 로직은 MVP 구현입니다.

1. 실제 도로/대중교통 이동시간은 반영하지 않습니다.
2. 거리 계산은 좌표 기반 직선거리입니다.
3. 지역 기여도는 내부 점수이며 공식 통계 지표가 아닙니다.
4. 저장 동선은 기존 `routes`, `route_places` 구조를 유지합니다.
5. 상세한 추천 스냅샷 보존이 필요하면 이후 DB에 JSON snapshot 컬럼 또는 별도 테이블을 추가할 수 있습니다.

## Meeting Explanation

회의에서는 다음처럼 설명하면 됩니다.

```text
추천 로직은 현재 MVP 내부 점수 기반입니다.
사용자가 고른 테마, 이동수단, 동행 조건에 맞는 장소를 우선 점수화하고,
여행 시간 안에 들어오는 장소를 고른 뒤 실제 동선 순서로 정렬합니다.
지역 기여도 86점 같은 값은 공식 지표가 아니라,
코스에 포함된 장소들의 local_contribution_score 평균에 로컬 소비 장소 보너스를 더한 내부 점수입니다.
프론트에서는 카드 API와 상세조회 API를 분리해서,
카드에서는 3개 배지와 장소 미리보기만 보여주고 상세에서는 전체 장소, 거리, 이동 난이도, AI 추천 이유를 보여주면 됩니다.
```
