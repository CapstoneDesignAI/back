import json as json_module

from app.core.config import settings
from app.schemas.recommendations import RecommendationRequest
from app.services import recommendation_reasoning
from app.services.recommendations import create_recommendation


def test_ai_reason_detail_falls_back_to_rule_based_when_openai_key_is_missing() -> None:
    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="healing",
            travel_time="half_day",
            transport="walk",
            companion="friends",
        )
    )

    assert response.ai_reason
    assert response.ai_reason_detail.generation_source == "rule_based_ai_ready"
    assert response.ai_reason_detail.highlights


def test_ai_reason_detail_can_be_generated_by_openai(monkeypatch) -> None:
    class FakeOpenAIResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": json_module.dumps(
                                {
                                    "overview": "LLM overview",
                                    "route_design": "LLM route design",
                                    "local_contribution": "LLM local contribution",
                                    "traveler_fit": "LLM traveler fit",
                                    "closing_tip": "LLM closing tip",
                                    "highlights": ["LLM highlight"],
                                }
                            )
                        }
                    }
                ]
            }

    def fake_post(url, *, headers, json, timeout):
        assert url == "https://api.openai.com/v1/chat/completions"
        assert headers["Authorization"] == "Bearer test-openai-key"
        assert "test-openai-key" not in str(json)
        assert timeout == settings.llm_timeout_seconds
        return FakeOpenAIResponse()

    monkeypatch.setattr(settings, "openai_api_key", "test-openai-key")
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(recommendation_reasoning.httpx, "post", fake_post)

    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="healing",
            travel_time="half_day",
            transport="walk",
            companion="friends",
        )
    )

    assert response.ai_reason_detail.generation_source == "llm_openai"
    assert response.ai_reason_detail.overview == "LLM overview"
    assert response.ai_reason_detail.highlights == ["LLM highlight"]
    assert "LLM overview" in response.ai_reason


def test_ai_reason_detail_falls_back_when_openai_call_fails(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        raise RuntimeError("network failure")

    monkeypatch.setattr(settings, "openai_api_key", "test-openai-key")
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(recommendation_reasoning.httpx, "post", fake_post)

    response = create_recommendation(
        RecommendationRequest(
            region_id="region-danyang",
            theme="healing",
            travel_time="half_day",
            transport="walk",
            companion="friends",
        )
    )

    assert response.ai_reason
    assert response.ai_reason_detail.generation_source == "rule_based_ai_ready"
