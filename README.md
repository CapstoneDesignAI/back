# TRIP:RE Backend

소멸 지역의 숨은 로컬 경험을 여행자 취향과 연결하는 TRIP:RE 백엔드입니다. FastAPI를 기반으로 카카오 로그인, 사용자 프로필, 추천 동선, 저장한 동선, 즐겨찾기 API를 제공합니다.

## Tech Stack

- Python 3.12+
- FastAPI
- Supabase
- Pydantic Settings
- python-jose
- pytest

## Quick Start

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Swagger 문서는 서버 실행 후 아래 주소에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

## Environment

로컬 개발에서는 `.env`가 없어도 테스트가 수집 단계에서 깨지지 않도록 기본값이 들어가 있습니다. 실제 Supabase와 카카오 로그인을 연결할 때는 아래 값을 `.env`에 설정합니다.

```env
JWT_SECRET_KEY=change-me
KAKAO_REST_API_KEY=
KAKAO_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/kakao/callback
KAKAO_FRONTEND_REDIRECT_URI=http://localhost:8081/auth/callback
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
TOUR_API_SERVICE_KEY=
TOUR_API_BASE_URL=https://apis.data.go.kr/B551011/KorService2
TOUR_API_SERVICE_VERSION=2
TOUR_API_MOBILE_OS=ETC
TOUR_API_MOBILE_APP=TRIP_RE
```

한국관광공사_국문 관광정보 서비스_GW 인증키는 `TOUR_API_SERVICE_KEY`에 넣습니다. 실제 키가 들어간 `.env`는 커밋하지 않고, 공유용 예시는 `.env.example`만 사용합니다.

## Project Structure

```text
app/
  api/
    api.py
    v1/
      auth/
      endpoints/
  core/
  data/
  db/
  schemas/
  services/
docs/
tests/
api/
  index.py
```

현재 API prefix는 `/api/v1`입니다. 새 endpoint는 `app/api/v1/endpoints` 아래에 만들고, `app/api/api.py`에서 router를 등록합니다.

## Main API

### Auth / User

```text
GET /api/v1/auth/kakao
GET /api/v1/auth/kakao/callback
GET /api/v1/users/me
```

### AI Recommendation

```text
GET /api/v1/regions
GET /api/v1/places?source=sample
GET /api/v1/places?source=tour_api&region_id=region-danyang&theme=food
GET /api/v1/recommendations/options
GET /api/v1/recommendations/selection-options
GET /api/v1/recommendations/today
POST /api/v1/recommendations
POST /api/v1/ai-recommendations
```

추천 API 상세 명세는 [docs/recommendation_api.md](docs/recommendation_api.md)를 확인합니다.

### Route History

```text
POST /api/v1/routes
GET /api/v1/routes
GET /api/v1/routes/{route_id}
DELETE /api/v1/routes/{route_id}
```

추천 결과 저장은 `POST /api/v1/recommendations` 응답의 `legacy_route_payload`를 `POST /api/v1/routes` body로 전달하는 방식입니다.

### Bookmark / Folder

```text
POST /api/v1/bookmarks
GET /api/v1/bookmarks
DELETE /api/v1/bookmarks/{bookmark_id}

POST /api/v1/folders
GET /api/v1/folders
PUT /api/v1/folders/{folder_id}
DELETE /api/v1/folders/{folder_id}
```

## AI Recommendation Flow

```text
앱 진입
-> 오늘의 추천 확인
-> 내 여행 찾기
-> 지역 선택 또는 AI 지역 추천
-> 테마 선택
-> 여행 시간, 이동수단, 동행 선택
-> 점수 기반 동선 추천
-> 지도 마커 확인
-> 지역 기여도 확인
-> 추천 히스토리에 저장
```

MVP 추천 데이터는 `app/data/danyang_places.py`에 있는 단양 장소 샘플을 기본으로 사용합니다. 한국관광공사 API 키가 있으면 `GET /api/v1/places?source=tour_api&region_id=region-danyang&theme=food`처럼 실시간 장소 후보를 조회할 수 있고, 추천 요청 body에 `"data_source": "tour_api"`를 넣으면 TourAPI 장소를 우선 사용합니다. API 키가 없거나 결과가 없으면 기존 샘플 데이터로 fallback됩니다.

## Recommendation Scoring

추천 점수는 아래 기준을 합산합니다.

| 기준 | 점수 |
| --- | --- |
| 선택 테마와 장소 태그 일치 | `+35` |
| 이동수단과 장소 이동 태그 일치 | `+20` |
| 이동수단 부적합 | `-25` |
| 동행 유형 일치 | `+10` |
| 장소 지역 기여도 | `local_contribution_score * 0.2` |
| 맛집/시장/활성화 테마에서 로컬 소비 장소 | `+20` |
| 지역활성화 테마에서 기여도 80 이상 | `+15` |

## Test

```powershell
python -m pytest -q
```

현재 추천 관련 테스트는 아래 흐름을 검증합니다.

- 추천 결과 응답 계약
- AI 추천 이유 응답
- 추천 히스토리 저장 payload
- 오늘의 추천 홈 카드 응답

## Git Workflow

작업 전에는 항상 최신 `dev`를 받은 뒤 작업 브랜치에 병합합니다.

```powershell
git switch dev
git pull origin dev
git switch feat/ai-recommendation-fix
git merge dev
```

작업 후 테스트를 통과시키고 커밋합니다.

```powershell
python -m pytest -q
git add .
git commit -m "Docs: 추천 API 문서 정리"
git push origin feat/ai-recommendation-fix
```
