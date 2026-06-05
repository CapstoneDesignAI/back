from app.data.danyang_places import list_danyang_mvp_places
from app.schemas.recommendations import RecommendationRequest
from app.services.recommendation_scoring import (
    ROUTE_BUFFER_MINUTES,
    TRAVEL_TIME_BUDGETS,
    build_recommendation_plan,
    score_place,
)


def test_travel_time_budget_constants_match_documented_mvp_policy() -> None:
    assert TRAVEL_TIME_BUDGETS == {
        "3hours": 180,
        "half_day": 320,
        "full_day": 480,
        "overnight": 900,
    }
    assert ROUTE_BUFFER_MINUTES == {
        "3hours": 30,
        "half_day": 60,
        "full_day": 90,
        "overnight": 180,
    }


def test_score_place_rewards_matching_theme_transport_and_companion() -> None:
    place = list_danyang_mvp_places()[0]
    request = RecommendationRequest(
        region_id="region-danyang",
        theme="healing",
        travel_time="half_day",
        transport="walk",
        companion="friends",
    )

    scored_place = score_place(request=request, place=place, original_order=0)

    assert scored_place.score == 79
    assert scored_place.score_reasons == (
        "theme_match",
        "transport_match",
        "companion_match",
        "local_contribution",
    )


def test_half_day_plan_keeps_full_danyang_demo_route() -> None:
    request = RecommendationRequest(
        region_id="region-danyang",
        theme="healing",
        travel_time="half_day",
        transport="walk",
        companion="friends",
    )

    plan = build_recommendation_plan(
        request=request,
        candidates=list_danyang_mvp_places(),
    )

    assert [item.place.name for item in plan.places] == [
        "도담삼봉",
        "단양구경시장",
        "카페산",
        "만천하스카이워크",
    ]
    assert plan.contribution_score == 86
    assert plan.estimated_duration_minutes == 320
    assert plan.estimated_cost_min == 35000
    assert plan.estimated_cost_max == 55000
    assert plan.local_consumption_count == 2


def test_route_contribution_score_uses_average_place_score_and_local_bonus() -> None:
    request = RecommendationRequest(
        region_id="region-danyang",
        theme="healing",
        travel_time="half_day",
        transport="walk",
        companion="friends",
    )

    plan = build_recommendation_plan(
        request=request,
        candidates=list_danyang_mvp_places(),
    )

    average_place_score = round(
        sum(item.place.local_contribution_score for item in plan.places)
        / len(plan.places)
    )
    local_bonus = min(plan.local_consumption_count * 3, 10)

    assert average_place_score == 80
    assert local_bonus == 6
    assert plan.contribution_score == average_place_score + local_bonus


def test_three_hour_plan_keeps_route_inside_time_budget() -> None:
    request = RecommendationRequest(
        region_id="region-danyang",
        theme="healing",
        travel_time="3hours",
        transport="walk",
        companion="friends",
    )

    plan = build_recommendation_plan(
        request=request,
        candidates=list_danyang_mvp_places(),
    )

    assert [item.place.name for item in plan.places] == ["도담삼봉", "단양구경시장"]
    assert plan.estimated_duration_minutes == 150
    assert plan.estimated_cost_min == 15000
    assert plan.estimated_cost_max == 30000

