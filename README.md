# TRIP:RE Backend

소멸 지역의 숨은 로컬 경험을 여행자 취향과 연결하는 TRIP:RE 백엔드입니다. FastAPI를 기반으로 카카오 로그인, 사용자 프로필, 추천 동선, 저장한 동선, 즐겨찾기 API를 제공합니다.

## Tech Stack

- Python 3.12+
- FastAPI
- Supabase
- Pydantic Settings
- python-jose
- pytest

# Tripick

## 📖 프로젝트 소개

즉흥성(Spontaneity)’과 ‘맥락(Context)’을 중심으로 설계된 AI 여행 에이전트

<br/>

## 🚀 기술 스택

### 💻 Frontend

<div>
  <img src="https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>
  <img src="https://img.shields.io/badge/Expo-000020?style=for-the-badge&logo=expo&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white"/>
  <img src="https://img.shields.io/badge/Zustand-553830?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/React_Query-FF4154?style=for-the-badge&logo=reactquery&logoColor=white"/>
</div>

<br/>

### 💻 Backend

<div>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Vector_DB-000000?style=for-the-badge"/>
</div>

<br/>

### 🤝 협업 툴

<div>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white">
  <img src="https://img.shields.io/badge/Figma-EF2D5E?style=for-the-badge&logo=figma&logoColor=white">
  <img src="https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black">
  <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white">
  <img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">
  <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white">
</div>

## 👥 팀원

| <a href=https://github.com/shuding0307><img src="https://avatars.githubusercontent.com/u/129826514?v=4" width=100px/><br/><sub><b>@shuding0307</b></sub></a><br/> | <a href=https://github.com/ProgrammerDavid1><img src="https://avatars.githubusercontent.com/u/161571242?v=4" width=100px/><br/><sub><b>@ProgrammerDavid1</b></sub></a><br/> | <a href=https://github.com/ddufls><img src="https://avatars.githubusercontent.com/u/153452513?v=4" width=100px/><br/><sub><b>@ddufls</b></sub></a><br/> |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------: |
|                                                                              이수현                                                                               |                                                                                   박준석                                                                                    |                                                                         김수린                                                                          |

<br/>

## Recommendation Scoring

추천 점수는 아래 기준을 합산합니다.

| 기준                                     | 점수                             |
| ---------------------------------------- | -------------------------------- |
| 선택 테마와 장소 태그 일치               | `+35`                            |
| 이동수단과 장소 이동 태그 일치           | `+20`                            |
| 이동수단 부적합                          | `-25`                            |
| 동행 유형 일치                           | `+10`                            |
| 장소 지역 기여도                         | `local_contribution_score * 0.2` |
| 맛집/시장/활성화 테마에서 로컬 소비 장소 | `+20`                            |
| 지역활성화 테마에서 기여도 80 이상       | `+15`                            |

## Test

```powershell
python -m pytest -q
```

현재 추천 관련 테스트는 아래 흐름을 검증합니다.

- 추천 결과 응답 계약
- AI 추천 이유 응답
- 추천 히스토리 저장 payload
- 오늘의 추천 홈 카드 응답

<hr/>

## 📑 프로젝트 규칙

#### 작업해야할 내용들은 모두 canvan board에 작성하고 issue로 연결한 후 그 작업에 해당하는 브랜치를 새로 파서 작업 진행

### Branch Strategy

> - main / dev 브랜치 기본 생성(main은 배포 branch, dev는 개발 브랜치)
> - main과 dev로 직접 push 제한
> - 작업 브랜치 명은 canvan으로 팠던 issue 번호에 맞게 (ex. 커밋 접투사/#이슈번호 => style/#30 or feat/#32)
>   <br/>

### Git Convention

> 1. 적절한 커밋 접두사 작성
> 2. 커밋 메시지 내용 작성

> | 접두사     | 설명                           |
> | ---------- | ------------------------------ |
> | Feat :     | 새로운 기능 구현               |
> | Add :      | 에셋 파일 추가                 |
> | Fix :      | 버그 수정                      |
> | Docs :     | 문서 추가 및 수정              |
> | Style :    | 스타일링 작업                  |
> | Refactor : | 코드 리팩토링 (동작 변경 없음) |
> | Test :     | 테스트                         |
> | Deploy :   | 배포                           |
> | Conf :     | 빌드, 환경 설정                |
> | Chore :    | 기타 작업                      |
>
> <br/>

### Git Workflow

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

</br>

### Pull Request

> ### Title
>
> - 제목은 'Feat : 홈 페이지 구현'과 같이 작성합니다.

> ### PR Type
>
> - [ ] FEAT: 새로운 기능 구현
> - [ ] ADD : 에셋 파일 추가
> - [ ] FIX: 버그 수정
> - [ ] DOCS: 문서 추가 및 수정
> - [ ] STYLE: 포맷팅 변경
> - [ ] REFACTOR: 코드 리팩토링
> - [ ] TEST: 테스트 관련
> - [ ] DEPLOY: 배포 관련
> - [ ] CONF: 빌드, 환경 설정
> - [ ] CHORE: 기타 작업

### Communication Rules

#### 📌 회의 관련

> - 정기 회의 : 매주 월요일 오후 8시 30분
