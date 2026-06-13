from dataclasses import dataclass
import json
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.recommendations import (
    AIReasonDetail,
    RecommendationSummary,
    RegionItem,
    RouteRecommendationPlace,
)


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
    fallback_result = build_rule_based_recommendation_reason(
        region=region,
        theme_label=theme_label,
        transport_label=transport_label,
        companion_label=companion_label,
        summary=summary,
        places=places,
    )
    if not _should_call_openai():
        return fallback_result

    try:
        return _build_openai_recommendation_reason(
            region=region,
            theme_label=theme_label,
            transport_label=transport_label,
            companion_label=companion_label,
            summary=summary,
            places=places,
            fallback_detail=fallback_result.detail,
        )
    except Exception:
        return fallback_result


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


def generate_ai_reason_detail(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> AIReasonDetail:
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


def _should_call_openai() -> bool:
    return bool(
        settings.openai_api_key
        and settings.llm_provider.strip().lower() == "openai"
    )


def _build_openai_recommendation_reason(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
    fallback_detail: AIReasonDetail,
) -> RecommendationReasonResult:
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
                    "content": (
                        "You write concise Korean travel route recommendation reasons for Tripick. "
                        "Use only the supplied selected places. Do not add new places or reorder them. "
                        "Return strict JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_openai_prompt(
                        region=region,
                        theme_label=theme_label,
                        transport_label=transport_label,
                        companion_label=companion_label,
                        summary=summary,
                        places=places,
                    ),
                },
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        },
        timeout=settings.llm_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    data = _parse_openai_json_content(content)

    reason_detail = AIReasonDetail(
        overview=_get_non_empty_string(data, "overview", fallback_detail.overview),
        route_design=_get_non_empty_string(
            data,
            "route_design",
            fallback_detail.route_design,
        ),
        local_contribution=_get_non_empty_string(
            data,
            "local_contribution",
            fallback_detail.local_contribution,
        ),
        traveler_fit=_get_non_empty_string(
            data,
            "traveler_fit",
            fallback_detail.traveler_fit,
        ),
        closing_tip=_get_non_empty_string(data, "closing_tip", fallback_detail.closing_tip),
        highlights=_get_highlights(data, fallback_detail.highlights),
        generation_source="llm_openai",
    )
    return RecommendationReasonResult(
        text=build_ai_reason_text(reason_detail),
        detail=reason_detail,
    )


def _build_openai_prompt(
    *,
    region: RegionItem,
    theme_label: str,
    transport_label: str,
    companion_label: str,
    summary: RecommendationSummary,
    places: list[RouteRecommendationPlace],
) -> str:
    place_lines = [
        (
            f"{place.order}. {place.name} | category={place.category} | "
            f"stay={place.stay_minutes}min | local_consumption={place.is_local_consumption} | "
            f"score={place.recommendation_score} | reason={place.reason} | "
            f"contribution={place.contribution_reason}"
        )
        for place in places
    ]
    return (
        "다음은 이미 점수 기반 추천 로직으로 선별된 장소 목록입니다. "
        "장소를 새로 고르거나 순서를 바꾸지 말고, 추천 이유 문장만 생성하세요.\n\n"
        f"지역: {region.sido} {region.sigungu}\n"
        f"테마: {theme_label}\n"
        f"이동수단: {transport_label}\n"
        f"동행: {companion_label}\n"
        f"예상 시간: {summary.duration_text}\n"
        f"예상 비용: {summary.cost_range_text}\n"
        f"지역 기여도: {summary.contribution_label}\n"
        f"로컬 소비: {summary.local_consumption_text}\n\n"
        "선별 장소:\n"
        + "\n".join(place_lines)
        + "\n\n"
        "아래 JSON 형식으로만 답하세요.\n"
        "{\n"
        '  "overview": "한두 문장",\n'
        '  "route_design": "동선 구성 이유",\n'
        '  "local_contribution": "지역 소비/기여 설명",\n'
        '  "traveler_fit": "사용자 조건 적합성 설명",\n'
        '  "closing_tip": "마무리 팁",\n'
        '  "highlights": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"]\n'
        "}"
    )


def _parse_openai_json_content(content: str) -> dict[str, Any]:
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("OpenAI recommendation reason response must be a JSON object.")
    return parsed


def _get_non_empty_string(
    data: dict[str, Any],
    key: str,
    fallback: str,
) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _get_highlights(
    data: dict[str, Any],
    fallback: list[str],
) -> list[str]:
    value = data.get("highlights")
    if not isinstance(value, list):
        return fallback
    highlights = [str(item).strip() for item in value if str(item).strip()]
    return highlights[:3] or fallback

