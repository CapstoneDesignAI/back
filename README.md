# back

FastAPI 백엔드 시작용 기본 구조입니다.

## Structure

```text
back/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── .env.example
└── pyproject.toml
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

헬스체크:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Kakao Login

`.env` example:

```bash
KAKAO_REST_API_KEY=your_rest_api_key
KAKAO_CLIENT_SECRET=your_client_secret
KAKAO_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/kakao/callback
```

Endpoints:

```bash
GET /api/v1/auth/kakao/login
GET /api/v1/auth/kakao/callback?code=...
```

현재는 카카오 인가 코드 교환과 사용자 정보 조회까지 구현되어 있고, 서비스 자체 JWT 발급/회원가입 연결은 다음 단계에서 붙이면 됩니다.
