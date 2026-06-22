from dataclasses import dataclass
import json
import os
import re

import httpx

from app.core.config import settings
from app.schemas.recommendations import (
    AIReasonDetail,
    RecommendationSummary,
    RegionItem,
    RouteRecommendationPlace,
)


ROUTE_RECOMMEND_REASON_PROMPT_TEMPLATE = """당신은 여행 심리 분석가이자 여행 큐레이터입니다.

당신의 역할은 사용자가 선택한 여행 취향을 바탕으로 단순히 장소를 설명하는 것이 아니라,
사용자가 지금 어떤 여행 경험을 원하는 사람인지 해석하고,
왜 이 여행 동선이 그 사람에게 잘 맞는지 설명하는 것입니다.

중요 규칙

1. 사용자가 선택한 옵션을 그대로 반복하지 마세요.

금지 예시:

* 자연을 좋아해서 이 코스를 추천합니다.
* 조용한 분위기를 원해서 추천합니다.

2. 사용자의 여행 취향을 바탕으로
   현재 어떤 감정이나 경험을 원하는 상태인지 추론하세요.

예시:

* 잠시 일상에서 벗어나고 싶어 함
* 새로운 자극보다 편안한 경험을 원함
* 유명 관광지보다 자기만의 발견을 즐김
* 바쁘게 이동하기보다 천천히 머무는 시간을 선호함

3. 추천 장소 하나하나를 설명하지 말고,
   전체 동선이 주는 경험을 설명하세요.

4. "좋다", "예쁘다", "유명하다" 같은 홍보성 표현은 사용하지 마세요.

5. 여행지 홍보 문구처럼 작성하지 말고,
   사용자에게 이야기하듯 작성하세요.

6. 사용자의 성격이나 MBTI를 단정하지 마세요.

7. 추천 장소의 특징보다
   사용자가 이 동선을 통해 어떤 감정을 느낄지에 집중하세요.

8. 4~6문장으로 작성하세요.

출력 형식

{{
"route_recommend_reason": "..."
}}

사용자 정보:
{user_preferences}

추천 동선 정보:
{route_info}
"""


@dataclass(frozen=True)
class RecommendationReasonResult:
    text: str
    detail: AIReasonDetail


def build_recommendation_reason(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> RecommendationReasonResult:
    fallback = build_rule_based_recommendation_reason(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    llm_reason = generate_llm_route_recommend_reason(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    if not llm_reason:
        return fallback

    return RecommendationReasonResult(
        text=llm_reason,
        detail=fallback.detail.model_copy(
            update={
                "overview": llm_reason,
                "generation_source": f"llm_{settings.llm_provider}",
            }
        ),
    )


def build_rule_based_recommendation_reason(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> RecommendationReasonResult:
    reason_detail = generate_ai_reason_detail(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    return RecommendationReasonResult(
        text=build_ai_reason_text(reason_detail),
        detail=reason_detail,
    )


def generate_llm_route_recommend_reason(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> str | None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return None

    try:
        prompt = build_route_recommend_reason_prompt(
            region=region,
            theme_label=theme_label,
            transport_label=transport_label,
            companion_label=companion_label,
            summary=summary,
            places=places,
        )
        if settings.llm_provider == "gemini":
            content = _request_gemini_route_reason(prompt)
        else:
            content = _request_openai_route_reason(prompt)
    except (AttributeError, httpx.HTTPError, KeyError, TypeError, ValueError):
        return None

    return _extract_route_recommend_reason(content)


def build_route_recommend_reason_prompt(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> str:
    user_preferences = {
        "theme": theme_label,
        "transport": transport_label,
        "companion": companion_label,
        "travel_duration": summary.duration_text,
        "expected_cost": summary.cost_range_text,
    }
    route_info = {
        "region": f"{region.sido} {region.sigungu}",
        "route_flow": [place.name for place in places],
        "place_count": len(places),
        "total_stay_minutes": sum(place.stay_minutes for place in places),
        "local_consumption": summary.local_consumption_text,
        "local_contribution": summary.contribution_label,
        "places": [
            {
                "order": place.order,
                "name": place.name,
                "category": place.category,
                "tags": place.tags,
                "is_local_consumption": place.is_local_consumption,
            }
            for place in places
        ],
    }
    return ROUTE_RECOMMEND_REASON_PROMPT_TEMPLATE.format(
        user_preferences=json.dumps(user_preferences, ensure_ascii=False),
        route_info=json.dumps(route_info, ensure_ascii=False),
    )


def _request_openai_route_reason(prompt: str) -> str | None:
    if not settings.openai_api_key:
        return None

    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You return only valid JSON in Korean.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
            "max_tokens": 500,
        },
        timeout=settings.llm_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _request_gemini_route_reason(prompt: str) -> str | None:
    if not settings.gemini_api_key:
        return None

    response = httpx.post(
        (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent"
        ),
        params={"key": settings.gemini_api_key},
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "다음 요청에 대해 JSON만 반환하세요.\n\n"
                                f"{prompt}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500,
                "responseMimeType": "application/json",
            },
        },
        timeout=settings.llm_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _extract_route_recommend_reason(content: str | None) -> str | None:
    if not content:
        return None

    cleaned_content = _strip_markdown_code_fence(content.strip())
    try:
        payload = json.loads(cleaned_content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned_content, flags=re.DOTALL)
        if not match:
            return None
        payload = json.loads(match.group(0))

    reason = payload.get("route_recommend_reason")
    if not isinstance(reason, str):
        return None

    reason = " ".join(reason.split())
    return reason or None


def _strip_markdown_code_fence(content: str) -> str:
    if not content.startswith("```"):
        return content

    return re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE)


def generate_ai_reason_detail(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> AIReasonDetail:
    if not places:
        return AIReasonDetail(
            overview=f"{region.sigungu}에서 {theme_label} 여행을 즐길 수 있는 코스를 준비하고 있습니다.",
            route_design=f"{transport_label} 조건과 {summary.duration_text} 일정에 맞는 동선을 제공할 예정입니다.",
            local_contribution=f"{region.sigungu} 지역 상권에 활력을 더하는 경험을 추천합니다.",
            traveler_fit=f"{companion_label} 여행에 맞춰 편안한 흐름을 만들었습니다.",
            closing_tip=f"{summary.cost_range_text} 정도의 소비를 예상할 수 있습니다.",
            highlights=[
                f"{theme_label} 테마 적합",
                summary.contribution_label,
            ],
            generation_source="rule_based_ai_ready",
        )

    local_places = [place for place in places if place.is_local_consumption]
    nature_places = [
        place
        for place in places
        if "자연투어" in place.tags or place.category in {"자연", "액티비티"}
    ]
    rest_places = [
        place
        for place in places
        if place.category in {"카페", "로컬시장"} or place.is_local_consumption
    ]

    representative_names = _join_names(nature_places[:2] or places[:2])
    local_names = _join_names(local_places)
    rest_names = _join_names(rest_places[:2])

    overview = (
        f"{region.sigungu}에서 {theme_label} 여행을 원하는 사용자에게 맞춰 "
        f"{representative_names} 중심의 지역 경험을 먼저 배치했습니다."
    )
    route_design = (
        f"동선은 {places[0].name}에서 시작해 {places[-1].name}까지 이어지며, "
        f"{transport_label} 조건과 {summary.duration_text} 안에 들어오도록 구성했습니다."
    )
    local_contribution = (
        f"{local_names}처럼 실제 소비가 일어나는 장소를 포함해 "
        f"{summary.local_consumption_text}이라는 목표를 반영했습니다."
        if local_places
        else "대표 방문지를 중심으로 지역 체류 시간을 늘릴 수 있게 구성했습니다."
    )
    traveler_fit = (
        f"{companion_label} 여행에서도 이동 피로가 커지지 않도록 "
        f"{rest_names}에서 쉬어갈 수 있는 흐름을 만들었습니다."
        if rest_places
        else f"{companion_label} 여행에 맞춰 장소 수와 체류시간을 과하지 않게 조정했습니다."
    )
    closing_tip = (
        f"{summary.cost_range_text} 정도의 소비를 예상할 수 있고, "
        f"{summary.contribution_label}으로 지역 상권 기여도가 높은 코스입니다."
    )

    return AIReasonDetail(
        overview=overview,
        route_design=route_design,
        local_contribution=local_contribution,
        traveler_fit=traveler_fit,
        closing_tip=closing_tip,
        highlights=[
            f"{theme_label} 테마 적합",
            summary.contribution_label,
            summary.local_consumption_text,
        ],
        generation_source="rule_based_ai_ready",
    )


def build_ai_reason_text(reason_detail: AIReasonDetail) -> str:
    return " ".join(
        [
            reason_detail.overview,
            reason_detail.route_design,
            reason_detail.local_contribution,
            reason_detail.traveler_fit,
        ]
    )


def _join_names(places: list[RouteRecommendationPlace]) -> str:
    names = [place.name for place in places]
    if not names:
        return "지역 장소"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f", {names[-1]}"
