from dataclasses import dataclass

from app.data.danyang_places import PlaceCandidate
from app.schemas.recommendations import RecommendationRequest


TRAVEL_TIME_BUDGETS = {
    "3hours": 180,
    "half_day": 320,
    "full_day": 480,
    "overnight": 900,
}

ROUTE_BUFFER_MINUTES = {
    "3hours": 30,
    "half_day": 60,
    "full_day": 90,
    "overnight": 180,
}


@dataclass(frozen=True)
class ScoredPlace:
    place: PlaceCandidate
    score: int
    score_reasons: tuple[str, ...]
    original_order: int


@dataclass(frozen=True)
class RecommendationPlan:
    places: tuple[ScoredPlace, ...]
    contribution_score: int
    estimated_duration_minutes: int
    estimated_cost_min: int
    estimated_cost_max: int
    local_consumption_count: int


def build_recommendation_plan(
    request: RecommendationRequest,
    candidates: tuple[PlaceCandidate, ...],
) -> RecommendationPlan:
    scored_places = tuple(
        score_place(request=request, place=place, original_order=index)
        for index, place in enumerate(candidates)
    )
    selected_places = _select_places(request=request, scored_places=scored_places)

    return RecommendationPlan(
        places=selected_places,
        contribution_score=_calculate_route_contribution_score(selected_places),
        estimated_duration_minutes=_calculate_duration(request, selected_places),
        estimated_cost_min=sum(item.place.estimated_cost_min for item in selected_places),
        estimated_cost_max=sum(item.place.estimated_cost_max for item in selected_places),
        local_consumption_count=sum(
            1 for item in selected_places if item.place.is_local_consumption
        ),
    )


def score_place(
    request: RecommendationRequest,
    place: PlaceCandidate,
    original_order: int,
) -> ScoredPlace:
    score = 0
    reasons: list[str] = []

    if request.theme in place.theme_tags:
        score += 35
        reasons.append("theme_match")

    if request.transport in place.transport_tags:
        score += 20
        reasons.append("transport_match")
    else:
        score -= 25
        reasons.append("transport_penalty")

    if request.companion in place.companion_tags:
        score += 10
        reasons.append("companion_match")

    score += round(place.local_contribution_score * 0.2)
    reasons.append("local_contribution")

    if request.theme in {"food", "local_market", "revitalization"} and place.is_local_consumption:
        score += 20
        reasons.append("local_consumption")

    if request.theme == "revitalization" and place.local_contribution_score >= 80:
        score += 15
        reasons.append("revitalization_priority")

    return ScoredPlace(
        place=place,
        score=score,
        score_reasons=tuple(reasons),
        original_order=original_order,
    )


def _select_places(
    request: RecommendationRequest,
    scored_places: tuple[ScoredPlace, ...],
) -> tuple[ScoredPlace, ...]:
    budget = TRAVEL_TIME_BUDGETS.get(request.travel_time, TRAVEL_TIME_BUDGETS["half_day"])
    buffer_minutes = ROUTE_BUFFER_MINUTES.get(
        request.travel_time,
        ROUTE_BUFFER_MINUTES["half_day"],
    )
    place_time_budget = max(budget - buffer_minutes, 0)

    ranked_places = sorted(
        scored_places,
        key=lambda item: (item.score, item.place.local_contribution_score),
        reverse=True,
    )

    selected: list[ScoredPlace] = []
    used_minutes = 0
    for item in ranked_places:
        if used_minutes + item.place.stay_minutes > place_time_budget:
            continue
        selected.append(item)
        used_minutes += item.place.stay_minutes

    if not selected and ranked_places:
        selected.append(ranked_places[0])

    return tuple(sorted(selected, key=lambda item: item.original_order))


def _calculate_route_contribution_score(selected_places: tuple[ScoredPlace, ...]) -> int:
    if not selected_places:
        return 0

    average_score = round(
        sum(item.place.local_contribution_score for item in selected_places)
        / len(selected_places)
    )
    local_consumption_bonus = min(
        sum(1 for item in selected_places if item.place.is_local_consumption) * 3,
        10,
    )
    return min(100, average_score + local_consumption_bonus)


def _calculate_duration(
    request: RecommendationRequest,
    selected_places: tuple[ScoredPlace, ...],
) -> int:
    buffer_minutes = ROUTE_BUFFER_MINUTES.get(
        request.travel_time,
        ROUTE_BUFFER_MINUTES["half_day"],
    )
    return sum(item.place.stay_minutes for item in selected_places) + buffer_minutes

